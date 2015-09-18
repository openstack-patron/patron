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

# os-patron-access/op/{op}
class PatronAccessController(object):
    """Controller for Cell resources."""

    def __init__(self, ext_mgr):
        self.ext_mgr = ext_mgr

    def verify(self, req,  op):
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

        file_object.write("\npatron.target:\n")
        try:
            # target: used as the security context of the object for Patron.
            target = jsonutils.loads(req.body)
            if target != None:
                for d,x in target.items():
                    file_object.write("%s = %s\n" % (d, x))
        except ValueError:
            # No target found, so we use the subject itself as target.
            file_object.write("null\n")
            target = dict()
            target['project_id'] = context.project_id
            target['user_id'] = context.user_id

        file_object.write("\npatron.op:\n")
        # op: used as the access control rule name for Patron.
        file_object.write(op)

        file_object.write("\n")
        file_object.close()

        # If "op" is not valid, then deny the access.
        if op == None or op == "" or op == "None":
            return {'command': 'verify',
                    'op': op,
                    'res': False}

        try:
            res = policy.enforce(context, op, target)
            if res != False:
                res = True
            return {'command': 'verify',
                    'op': op,
                    'context.project_id': context.project_id,
                    'context.user_id': context.user_id,
                    'target.project_id': target['project_id'],
                    'res': res}
        except Exception:
            # Policy doesn't allow "op" to be performed. (HTTP 403)
            return {'command': 'verify',
                    'op': op,
                    'context.project_id': context.project_id,
                    'context.user_id': context.user_id,
                    'target.project_id': target['project_id'],
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
                }
        memb_actions = {
                'capacities': 'GET',
                }

        # /%(project_id)s/os-patron-access/op/%(op)s/
        res = extensions.ResourceExtension('os-patron-access/op/{op}',
                controller=PatronAccessController(self.ext_mgr), collection_actions=coll_actions,
                member_actions=memb_actions)

        # res = extensions.ResourceExtension('os-patron-access/{user_id}/resource/{res_id}/action',
        #         controller=PatronAccessController(self.ext_mgr), collection_actions=coll_actions,
        #         member_actions=memb_actions)
        return [res]

