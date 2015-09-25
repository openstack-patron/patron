# add by Wu Luo

from patronclient import base
from patronclient.i18n import _
from patronclient.openstack.common import cliutils
from patronclient import utils


class AEMResource(base.Resource):
    def __repr__(self):
        return "<PatronResource: %s>" % self.name


class AEMAccessManager(base.Manager):
    resource_class = AEMResource

    def wipecache(self, **kwargs):
        """
        patron setpolicy
        """
        return self.api.client.put("/os-aem-access/wipecache", **kwargs)


@cliutils.arg(
    '--id',
    metavar='<id>',
    help=_('project id'))
def do_wipecache(cs, args):
    """patron verify. Args:op. For example:\n\tcompute_extension:admin_actions"""
    ans = cs.aem_access.wipecache(json={'project-id': args.id})
    print ans

