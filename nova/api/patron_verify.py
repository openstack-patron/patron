#Add by Luo Wu

"""
Common Middleware which is used to realize Access Control by communicating with Patron.

"""

from oslo_config import cfg
from oslo_log import log as logging
from oslo_middleware import request_id
from oslo_serialization import jsonutils
import webob.dec
import webob.exc

from nova import context
from nova.i18n import _
from nova.openstack.common import versionutils
from nova import wsgi

from patronclient import client
from keystoneclient import session

from nova.api.patron_cache import PatronCache

LOG = logging.getLogger(__name__)

class PatronVerify (wsgi.Middleware):

    def url_to_op_and_target(self, path_info, req_inner_action):
        # op : is used as the security operation for Patron.
        op = "compute_extension:admin_actions"
        # target : is used to act as the security context of the object for Patron.
        # if no target is needed, can do it as: target = None
        # target = {'project_id': 'fake_project_id', 'user_id': "fake_user_id"}
        target = None
        return (op, target)

    @webob.dec.wsgify(RequestClass=wsgi.Request)
    def __call__(self, req):
        cache_enabled = False
        LOG.info("\n!!!!!!!!!!!!!!!!!! This is PatronVerify Middleware\n")

        user_id = req.headers.get('X_USER')
        user_id = req.headers.get('X_USER_ID', user_id)
        if user_id is None:
            LOG.debug("Neither X_USER_ID nor X_USER found in request")
            return webob.exc.HTTPUnauthorized()

        if 'X_TENANT_ID' in req.headers:
            # This is the new header since Keystone went to ID/Name
            project_id = req.headers['X_TENANT_ID']
        else:
            # This is for legacy compatibility
            project_id = req.headers['X_TENANT']
        project_name = req.headers.get('X_TENANT_NAME')
        user_name = req.headers.get('X_USER_NAME')

        req_id = req.environ.get(request_id.ENV_REQUEST_ID)

        # Get the auth token
        auth_token = req.headers.get('X_AUTH_TOKEN',
                                     req.headers.get('X_STORAGE_TOKEN'))

        # NOTE(jamielennox): This is a full auth plugin set by auth_token
        # middleware in newer versions.
        user_auth_plugin = req.environ.get('keystone.token_auth')

        ########################################################################################################
        # Check policy against patron node
        # Edited by Yang Luo

        req_path_info = req.path_info
        if req.is_body_readable:
            for d, x in req.json.items():
                req_inner_action = d
                break
        else:
            req_inner_action = ""

        # Show req_path_info and req_inner_action.
        LOG.info("req_path_info = %r", req_path_info)
        LOG.info("req_inner_action = %r", req_inner_action)

        # Map the path_info and req_inner_action to op and target for Patron.
        (op, target) = self.url_to_op_and_target(req_path_info, req_inner_action)

        # Get the subject SID.
        subject_sid = req.environ['nova.context'].project_id + ":" + req.environ['nova.context'].user_id
        # Get the object SID.
        if target == None:
            object_sid = "None"
        else:
            object_sid = target["project_id"] + ":" + target["server_id"]
        LOG.info("op = %r, subject_sid = %r, object_sid = %r", op, subject_sid, object_sid)

        # Check the cache first for (op, context_project_id, target_project_id) pair.
        if cache_enabled:
            result = PatronCache.get_from_cache(op, subject_sid, object_sid)
        else:
            result = None

        # If cache fails to be hit, then make a normal request.
        if result != None:
            LOG.info("Cache has been hit for (op = %r, subject_sid = %r, object_sid = %r), result = %r",
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

            response = patron_client.patrons.verify(op, json = target)
            result = response[1]['res']
            if cache_enabled:
                LOG.info("Cache was missed, requested result = %r, saved to cache..", result)
                PatronCache.save_to_cache(op, subject_sid, object_sid, result)
            else:
                LOG.info("Cache was disabled, requested result = %r", result)

        if result != True:
            LOG.error("Access is **denied** by patron: res = %r, user_name = %r, auth_token = %r, project_name = %r, auth_plugin = %r",
                      result, user_name, auth_token, project_name, user_auth_plugin)
            return webob.exc.HTTPForbidden()
        else:
            LOG.info("Access is **permitted** by patron: res = %r, user_name = %r, auth_token = %r, project_name = %r, auth_plugin = %r",
                      result, user_name, auth_token, project_name, user_auth_plugin)

        return self.application
