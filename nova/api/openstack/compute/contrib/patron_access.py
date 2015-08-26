# add by lwyeluo
# /%(project_id)s/access_control_verify/%(user_id)s/resource/%(res_id)s/action/%(action)s/ ->patron
# /%(project_id)s/os-patron-access/

"""The patron access extension."""

import webob

from nova.api.openstack import extensions
from nova.api.openstack import wsgi
from nova import context as nova_context
from nova import exception
from nova.i18n import _
from nova import objects

# os-patron-access/{user_id}/resource/{res_id}/action
class PatronAccessController(object):
    """Controller for Cell resources."""

    def __init__(self, ext_mgr):
        self.ext_mgr = ext_mgr

    def detail(self, req, user_id, res_id):
        """Return all cells in detail."""
        all_the_text = '>>>>>>>>> enter PatronAccessController:detail\n'
        file_object = open('mylog.txt', 'a+')
        file_object.write(all_the_text)
        file_object.close()
        ctxt = req.environ['nova.context']
        return {'action': 'detail', 'user_id': user_id, 'res_id': res_id, 'ans': 'OK'}

    def verify(self, req,  user_id, res_id):
        """Return all cells in detail."""
        all_the_text = '>>>>>>>>> enter PatronAccessController:verify\n'
        file_object = open('mylog.txt', 'a+')
        file_object.write(all_the_text)
        file_object.close()
        ctxt = req.environ['nova.context']
        return {'action': 'verify', 'user_id': user_id, 'res_id': res_id, 'ans': 'OK'}

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
                'detail': 'GET',
                'verify': 'GET',
                'info': 'GET',
                'sync_instances': 'POST',
                'capacities': 'GET',
                }
        memb_actions = {
                'capacities': 'GET',
                }

        # /%(project_id)s/os-patron-access/%(user_id)s/resource/%(res_id)s/action/%(action)s/

        res = extensions.ResourceExtension('os-patron-access/{user_id}/resource/{res_id}/action',
                controller=PatronAccessController(self.ext_mgr), collection_actions=coll_actions,
                member_actions=memb_actions)
        return [res]

