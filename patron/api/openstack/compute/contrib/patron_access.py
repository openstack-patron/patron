# add by lwyeluo
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

# os-patron-access/{user_id}/resource/{res_id}/action
class PatronAccessController(object):
    """Controller for Cell resources."""

    def __init__(self, ext_mgr):
        self.ext_mgr = ext_mgr

    def verify(self, req,  rule):
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

        file_object.write("\npatron.target:\n")
        try:
            # target: used as the security context of the object for Patron.
            target = jsonutils.loads(req.body)
            if target != None:
                for d,x in target.items():
                    file_object.write("%s = %s\n" % (d, x))
        except KeyError:
            file_object.write("null\n")

        file_object.write("\nrule:\n")
        # rule: used as the access control rule name for Patron.
        file_object.write(rule)

        file_object.write("\n")
        file_object.close()

        try:
            res = policy.enforce(context, rule,
                        {'project_id': context.project_id,
                         'user_id': context.user_id})
            if res != False:
                res = True
            return {'action': 'verify', 'rule': rule, 'project_id': context.project_id, 'user_id': context.user_id, 'res': res}
        except Exception:
            return {'res': False}


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

        # /%(project_id)s/os-patron-access/%(user_id)s/resource/%(res_id)s/action/%(action)s/
        # .../action/{rule}/

        res = extensions.ResourceExtension('os-patron-access/rule/{rule}',
                controller=PatronAccessController(self.ext_mgr), collection_actions=coll_actions,
                member_actions=memb_actions)

        # res = extensions.ResourceExtension('os-patron-access/{user_id}/resource/{res_id}/action',
        #         controller=PatronAccessController(self.ext_mgr), collection_actions=coll_actions,
        #         member_actions=memb_actions)
        return [res]

