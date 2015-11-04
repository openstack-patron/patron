#Add by lwyeluo

"""
Common Middleware which is used to realize Access Control by communicating with Patron.

"""

from oslo_config import cfg
from oslo_log import log as logging
from oslo_middleware import request_id
from oslo_serialization import jsonutils
import webob.dec
import webob.exc

# Customize AEM for different services.
import inspect
import os
service_name = os.path.basename(inspect.stack()[-1][1]).split('-')[0]
if service_name == "nova":
    from nova import wsgi
elif service_name == "glance":
    from glance.common import wsgi
elif service_name == "neutron":
    from neutron import wsgi
else:
    raise Exception("AEM: Invalid service: %r!!" % service_name)

from patronclient import client
from keystoneclient import session

import importlib
import re
import patron_parse
from patron_cache import PatronCache

LOG = logging.getLogger(__name__)

class PatronVerify (wsgi.Middleware):

    @classmethod
    def get_tenant_by_id(cls, context, id):
        return {"id": id}

    def get_template_path_info(self, req_path_info, key_calls, key_ids):
        id_pattern = "[0-9a-f]{32}"
        uuid_patern = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
        value_patern = "=([^&]*)(&|$)"

        path_info_list = req_path_info.strip("/").split("/")

        for i in range(len(path_info_list) - 1):
            if path_info_list[i] in key_calls and path_info_list[i + 1] != "detail":
                key_ids[path_info_list[i]] = path_info_list[i + 1]
                if re.match(id_pattern, path_info_list[i + 1]) != None:
                    path_info_list[i + 1] = "%ID%"
                elif re.match(uuid_patern, path_info_list[i + 1]) != None:
                    path_info_list[i + 1] = "%UUID%"
                else:
                    path_info_list[i + 1] = "%NAME%"
        template_path_info = "/" + "/".join(path_info_list)
        # Translate '/%ID%/flavors?is_public=None' to '/%ID%/flavors?is_public=%VALUE%'
        template_path_info = re.sub(value_patern, "=%VALUE%&", template_path_info)
        template_path_info = template_path_info.strip("&")
        return template_path_info

    def get_templated_inner_action(self, req_path_info, req_inner_action):
        action_word_pattern = "{\"([A-Za-z-]*)\":"
        if req_path_info.endswith("/action"):
            re_res = re.search(action_word_pattern, req_inner_action)
            if re_res != None:
                action_word = re_res.group(1)
            else:
                action_word = "Inner Action Word Error!!"
            return action_word
        else:
            return ""

    def url_to_op_and_target(self, caller_project_id, context, req_server_port, req_api_version, req_method, req_path_info, req_inner_action):
        key_calls = {
            # nova
            "servers": "nova.objects.instance.Instance.get_by_uuid(uuid)",
            "os-interface": "nova.objects.virtual_interface.VirtualInterface.get_by_uuid(uuid)",
            "os-keypairs": "nova.objects.keypair.KeyPair.get_by_name(user_id, name)",
            "os-aggregates": "nova.objects.aggregate.Aggregate.get_by_id(id)",
            "os-networks": "nova.network.neutronv2.api.API.get(id)", # "nova.objects.network.Network.get_by_id(uuid)"
            "os-tenant-networks": "nova.network.neutronv2.api.API.get(id)",
            "os-quota-sets": "nova.quota.QUOTAS.get_project_quotas(id)",
            "os-simple-tenant-usage": "nova.api.patron_verify.PatronVerify.get_tenant_by_id(id)",
            "os-instance-actions": "nova.objects.instance.Instance.get_by_uuid(uuid)", # although "instance_action" has its own object, we still use "instance" as the object here
            "os-hosts": "nova.compute.api.HostAPI.instance_get_all_by_host(name)",
            "os-hypervisors": "nova.compute.api.HostAPI.compute_node_search_by_hypervisor(name)",
            "os-security-groups": "nova.objects.security_group.SecurityGroup.get(id)",
            "os-server-groups": "nova.objects.instance_group.InstanceGroup.get_by_uuid(uuid)",
            "os-migrations": "nova.objects.migraton.Migration.get_by_id(id)",
            "flavors": "nova.objects.flavor.Flavor.get_by_id(id)",
            # glance
            "images": "glance.db.sqlalchemy.api.image_get(uuid)",
            # neutron
            "networks": "",
            "volumes": ""
        }
        key_ids = {}
        key_ids["project_id"] = caller_project_id

        template_path_info = self.get_template_path_info(req_path_info, key_calls, key_ids)
        template_inner_action = self.get_templated_inner_action(req_path_info, req_inner_action)

        if key_ids.has_key("servers"):
            key_name = "servers"
        else:
            key_name = None
            for tmp_key_name in key_ids.keys():
                if tmp_key_name != "project_id":
                    key_name = tmp_key_name
                    break

        # target : is used to act as the security context of the object for Patron.
        # if no target is needed, can do it as: target = None
        # target = {'project_id': 'fake_project_id', 'user_id': "fake_user_id"}
        if key_name != None and key_calls[key_name] != "":
            (module_name, class_name, method_name) = key_calls[key_name].rsplit(".", 2)
            (method_name, param_name) = method_name.split("(", 1)
            param_list = param_name.replace(")", "").replace(" ", "").split(",")
            mod = importlib.import_module(module_name)
            param_values = []
            for param in param_list:
                if param == "id" or param == "uuid" or param == "name":
                    param_values.append(key_ids[key_name])
                else:
                    param_values.append(getattr(context, param))
            method_obj = getattr(getattr(mod, class_name), method_name)
            try:
                target = method_obj(context, *param_values)
            # the method is then a instance method, first instantiate the class.
            except TypeError:
                method_obj = getattr(getattr(mod, class_name)(), method_name)
                target = method_obj(context, *param_values)
        else:
            method_obj = None
            target = None

        LOG.info("key_ids = %r, key_name = %r, template_path_info = %r, method_obj = %r",
                 key_ids, key_name, template_path_info, method_obj)

        # op : is used as the security operation for Patron.
        # op = "compute_extension:admin_actions"
        op = patron_parse.parse(req_server_port, req_api_version, req_method, req_path_info, template_inner_action, template_path_info)

        return (op, target)

    @webob.dec.wsgify(RequestClass=wsgi.Request)
    def __call__(self, req):
        cache_enabled = True
        LOG.info("\n!!!!!!!!!!!!!!!!!! This is PatronVerify Middleware\n")

        # For debug use to generate five-element tuple: (req_port, req_api_version, req_method, req_path_info, req_inner_action)
        # This is also used for op mapping collection.
        # req_port = req.server_port
        # req_api_version = req.script_name
        # req_method = req.method
        # req_path_info = req.path_info
        # req_inner_action = req.text
        # f = open('/var/log/tempest/tempest.log','a+')
        # f.write("\n### req_port = %r, req_api_version = %r, req_method = %r, req_path_info = %r, req_inner_action = %r, op=" % (req_port, req_api_version, req_method, req_path_info, req_inner_action))
        # f.close()
        # return self.application

        caller_project_id = req.headers.get('X_PROJECT_ID')
        caller_user_id = req.headers.get('X_USER_ID')
        caller_project_name = req.headers.get('X_PROJECT_NAME')
        caller_user_name = req.headers.get('X_USER_NAME')
        if caller_project_id is None or caller_user_id is None or caller_project_name is None or caller_user_name is None:
            LOG.info("AEM: Either one of (caller_project_id, caller_user_id, caller_project_name, caller_user_name) not found in request")
            return webob.exc.HTTPUnauthorized()

        if service_name == "nova":
            caller_context = req.environ['nova.context']
        elif service_name == "glance":
            caller_context = req.context
        elif service_name == "neutron":
            caller_context = req.context
        else:
            raise Exception("AEM: Invalid caller context!!")

        # if 'X_TENANT_ID' in req.headers:
        #     # This is the new header since Keystone went to ID/Name
        #     project_id = req.headers['X_TENANT_ID']
        # else:
        #     # This is for legacy compatibility
        #     project_id = req.headers['X_TENANT']
        # req_id = req.environ.get(request_id.ENV_REQUEST_ID)

        # Get the auth token
        auth_token = req.headers.get('X_AUTH_TOKEN',
                                     req.headers.get('X_STORAGE_TOKEN'))

        # NOTE(jamielennox): This is a full auth plugin set by auth_token
        # middleware in newer versions.
        user_auth_plugin = req.environ.get('keystone.token_auth')

        ########################################################################################################
        # Check policy against patron node
        # Edited by veotax

        # First collect the tuple vector.
        # tuple vector ::= {req_server_port, req_api_version, req_method, req_path_info, req_inner_action)
        req_server_port = req.server_port
        req_method = req.method

        # Eventually, req_path_info will look like:
        # /85c8848b1dd64c7ebb2c5baeb12e25c3/flavors?is_public=None

        # Use different logic to parse path_info for different services.
        if service_name == "nova" or service_name == "neutron":
            req_api_version = req.script_name
            req_path_info = req.path_info
        else: # for glance.
            (s1, s2, s3) = req.path_info.split("/", 2)
            req_api_version = "/" + s2
            req_path_info = "/" + s3

        id_start_pattern = "^/[0-9a-f]{32}"
        req_path_info = re.sub(id_start_pattern, "", req_path_info)
        json_end_pattern = ".json$"
        req_path_info = re.sub(json_end_pattern, "", req_path_info)
        if req.query_string != "":
            req_path_info = req_path_info+ "?" + req.query_string

        # if req.is_body_readable:
        #     for d, x in req.json.items():
        #         req_inner_action = d
        #         break
        # else:
        #     req_inner_action = ""
        req_inner_action = req.text

        # Show path vectors.
        LOG.info("req_server_port = %r, req_api_version = %r, req_method = %r, req_path_info = %r, req_inner_action = %r",
                 req_server_port, req_api_version, req_method, req_path_info, req_inner_action)

        # Handle wipe-cache function call.
        pattern = re.compile("/os-aem-access/wipecache")
        match = pattern.match(req_path_info)
        if match:
            try:
                body = jsonutils.loads(req.body)
                if body != None:
                    wipercache_id = body.get('project-id', None)
                    if caller_project_id == wipercache_id:
                        # our policy for future usage, but now...
                        PatronCache.wipecache(caller_project_id)
                        return webob.exc.HTTPOk()
                    else:
                        return webob.exc.HTTPForbidden()
                else:
                    PatronCache.wipecache(caller_project_id)
                    return webob.exc.HTTPOk()
            except KeyError:
                PatronCache.wipecache(caller_project_id)
                return webob.exc.HTTPOk()

        # Map the path_info and req_inner_action to op and target for Patron.
        (op, target) = self.url_to_op_and_target(caller_project_id, caller_context, req_server_port, req_api_version, req_method, req_path_info, req_inner_action)
        if op == "KEY_ERROR":
            # If the mappings failed to find an op, we return the rare HTTP 412 error, to let the user know this is the error position.
            return webob.exc.HTTPPreconditionFailed()

        # Get the subject SID.
        subject_sid = caller_project_id + ":" + caller_user_id
        # Get the object SID.
        if target == None:
            object_sid = "None"
        else:
            object_sid = ""
            try:
                object_sid += target["project_id"] + ":"
            # KeyError, NotImplementedError, AttributeError
            except:
                object_sid += "None" + ":"
            try:
                object_sid += target["uuid"]
            # KeyError, NotImplementedError, AttributeError
            except:
                try:
                    object_sid += str(target["id"])
                except:
                    object_sid += "None"
        LOG.info("op = %r, subject_sid = %r, object_sid = %r", op, subject_sid, object_sid)

        # Check the cache first for (op, context_project_id, target_project_id) pair.
        if cache_enabled:
            result = PatronCache.get_from_cache(op, subject_sid, object_sid)
        else:
            result = None

        # If cache fails to be hit, then make a normal request.
        if result != None:
            LOG.info(">>>>>>>>>>>>>>Cache has been hit for (op = %r, subject_sid = %r, object_sid = %r), result = %r",
                     op, subject_sid, object_sid, result)
        else:
            # 1) User/Password request way
            # auth_url = "http://controller:5000/v2.0/"
            # patron_client = client.Client("2",
            #                               user_name,
            #                               "123",
            #                               project_name,
            #                               auth_url,
            #                               service_type="access")

            # 2) Session request way
            sess = session.Session(auth=user_auth_plugin)
            patron_client = client.Client("2",
                                  session=sess,
                                  service_type="access")

            response = patron_client.patrons.verify(json = {'target': target, 'op': op})
            result = response[1]['res']
            if cache_enabled:
                LOG.info("Cache was missed, requested result = %r, saved to cache..", result)
                PatronCache.save_to_cache(op, subject_sid, object_sid, result)
                #LOG.info(">>>>>get cache info:%r", PatronCache.get_from_cache(op, subject_sid, object_sid))
            else:
                LOG.info("Cache was disabled, requested result = %r", result)

        if result != True:
            LOG.error("Access is **denied** by patron: res = %r, user_name = %r, auth_token = %r, project_name = %r, auth_plugin = %r",
                      result, caller_user_name, auth_token, caller_project_name, user_auth_plugin)
            return webob.exc.HTTPForbidden()
        else:
            LOG.info("Access is **permitted** by patron: res = %r, user_name = %r, auth_token = %r, project_name = %r, auth_plugin = %r",
                      result, caller_user_name, auth_token, caller_project_name, user_auth_plugin)

        # for test
        PatronCache.get_memory()

        return self.application
