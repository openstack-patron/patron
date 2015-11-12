# add by Wu Luo
# /%(project_id)s/access_control_verify/%(user_id)s/resource/%(res_id)s/action/%(action)s/ ->patron
# /%(project_id)s/os-patron-access/

"""The patron access extension."""

import webob

from patron.api.openstack import extensions
from patron import policy
from patron.api.openstack import wsgi
from patron import context as patron_context
from patron import exception
from patron.i18n import _
from patron import objects

from oslo_serialization import jsonutils

import os

# os-patron-access/op/{op}
class PatronAccessController(object):
    """Controller for Cell resources."""

    def __init__(self, ext_mgr):
        self.ext_mgr = ext_mgr

    def getpolicy(self, req):
        all_the_text = '>>>>>>>>> enter PatronAccessController:getpolicy\n'
        file_object = open('/var/log/patron/mylog.txt', 'a+')
        file_object.write(all_the_text)
        file_object.close()
        return {'action': 'getpolicy'}

    def setpolicy(self, req):

        #get project_id
        try:
            project_id = req.environ['patron.context'].project_id
        except KeyError:
            return {'action': 'setpolicy', 'res': False}

        #directory exists
        dir = '/etc/patron/custom_policy/%s/' % project_id
        if not os.path.exists(dir):
            os.makedirs(dir)

        #metadata file path
        metadata_path = '/etc/patron/custom_policy/%s/metadata.json' % project_id

        # get policy file content
        try:
            body = jsonutils.loads(req.body)
            if body != None:
                policy = dict(body.get('policy', None))
                if policy != None:
                    # write into metadata.json
                    metadata_fp = open(metadata_path, 'w')
                    metadata_fp.write(jsonutils.dumps(policy, indent=4).replace("    ", "\t"))
                    metadata_fp.close()
                    # find content key
                    for (k, v) in policy.items():
                        if type(v) == dict and\
                            not (v.has_key('built-in') and v['built-in'].lower() == 'True'.lower()) and\
                            v.has_key('content') and v['content'] != '':
                            filename = '/etc/patron/custom_policy/%s/%s.json' % (project_id, k)
                            fp = open(filename, 'w')
                            fp.write(jsonutils.dumps(v['content'], indent=4).replace("    ", "\t"))
                            fp.close()
                    return {'action': 'setpolicy', 'res': True}
                return {'action': 'setpolicy', 'res': False}
        except ValueError or KeyError:
            return {'action': 'setpolicy', 'res': False}

    def getlabel(self, req):
        all_the_text = '>>>>>>>>> enter PatronAccessController:getlabel\n'
        file_object = open('/var/log/patron/mylog.txt', 'a+')
        file_object.write(all_the_text)
        file_object.close()
        return {'action': 'getlabel'}

    def setlabel(self, req):
        all_the_text = '>>>>>>>>> enter PatronAccessController:setlabel\n'
        file_object = open('/var/log/patron/mylog.txt', 'a+')
        file_object.write(all_the_text)
        file_object.close()
        return {'action': 'setlabel'}


    def verify(self, req):
        """Return all cells in detail."""
        all_the_text = '>>>>>>>>> enter PatronAccessController:verify\n'
        file_object = open('/var/log/patron/mylog.txt', 'a+')
        file_object.write(all_the_text)

        file_object.write("\npatron.context:\n")
        try:
            # context: used as the security context of the subject for Patron.
            context = req.environ['patron.context']
            for d,x in context.to_dict().items():
                file_object.write("%s = %s\n" % (d, x))
        except KeyError:
            file_object.write("null\n")
            return {'res': False}

        op = None

        #parse patron.body
        try:
            body = jsonutils.loads(req.body)
            if body != None:
                target = body.get('target', None)
                op = body.get('op', None)
                file_object.write("\npatron.target:\n")
                if target != None:
                    if isinstance(target, dict):
                        for d,x in target.items():
                            file_object.write("%s = %s\n" % (d, x))
                    # then it is a list-wrapped dict collection.
                    else:
                        for target_item in target:
                            for d,x in target_item.items():
                                file_object.write("%s = %s\n" % (d, x))

                else:
                    file_object.write("None\n")
        except ValueError or KeyError:
            target = dict()
            target['project_id'] = context.project_id
            target['user_id'] = context.user_id

        file_object.write("\npatron.op:\n")
        # op: used as the access control rule name for Patron.
        if op != None:
            file_object.write(op)
        else:
            file_object.write("None\n")

        file_object.write("\n")
        file_object.close()

        # If "op" is not valid, then deny the access.
        if op == None or op == "None":
            return {'command': 'verify',
                    'op': op,
                    'res': False}
        # If "op" is "", it means no need to check policy, we should just grant the access.
        elif op == "":
            return {'command': 'verify',
                    'op': op,
                    'context.project_id': context.project_id,
                    'context.user_id': context.user_id,
                    'res': True}

        # Test patron's functionality by returning False altogether.
        # return {'command': 'verify',
        #         'op': op,
        #         'res': False}

        try:
            res = policy.enforce(context, op, target, bypass=False)
            if res != False:
                res = True
            return {'command': 'verify',
                    'op': op,
                    'context.project_id': context.project_id,
                    'context.user_id': context.user_id,
                    'res': res}
        except Exception:
            # Policy doesn't allow "op" to be performed. (HTTP 403)
            return {'command': 'verify',
                    'op': op,
                    'context.project_id': context.project_id,
                    'context.user_id': context.user_id,
                    'exception': Exception,
                    'reason': "Policy doesn't allow [%s] to be performed. (HTTP 403)" % op,
                    'res': False}


class Patron_access(extensions.ExtensionDescriptor):
    """Enables cells-related functionality such as adding neighbor cells,
    listing neighbor cells, and getting the capabilities of the local cell.
    """

    name = "PatronAccess"
    alias = "os-patron-access"
    namespace = "http://docs.openstack.org/compute/ext/cells/api/v1.1"
    updated = "2015-07-24T17:20:00Z"

    def get_resources(self):
        coll_actions = {
                'verify': 'GET',
                'getpolicy': 'GET',
                'setpolicy': 'POST',
                'getlabel': 'GET',
                'setlabel': 'POST',
                }
        memb_actions = {
                'capacities': 'GET',
                }

        #/%(project_id)s/os-patron-access/
        res = extensions.ResourceExtension('os-patron-access',
                controller=PatronAccessController(self.ext_mgr), collection_actions=coll_actions,
                member_actions=memb_actions)




        # res = extensions.ResourceExtension('os-patron-access/{user_id}/resource/{res_id}/action',
        #         controller=PatronAccessController(self.ext_mgr), collection_actions=coll_actions,
        #         member_actions=memb_actions)
        return [res]

