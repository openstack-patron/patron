# add by Wu Luo

from patronclient import base
from patronclient.i18n import _
from patronclient.openstack.common import cliutils
from patronclient import utils


class PatronResource(base.Resource):
    def __repr__(self):
        return "<PatronResource: %s>" % self.name


class PatronAccessManager(base.Manager):
    resource_class = PatronResource

    def verify(self, **kwargs):
        """
        patron verify
        """
        # pattern : "/os-patron-access/op/compute_extension:admin_actions/verify"
        return self.api.client.get("/os-patron-access/verify", **kwargs)


@cliutils.arg(
    '--op',
    metavar='<op>',
    help=_('User op for example:\n\tcompute_extension:admin_actions'))
def do_verify(cs, args):
    """patron verify. Args:op. For example:\n\tcompute_extension:admin_actions"""
    ans = cs.patron_access.verify({'op': args.op})
    print ans

# @cliutils.arg(
#     '--user_id',
#     metavar='<user_id>',
#     help=_('User id.'))
# @cliutils.arg(
#     '--resource_id',
#     metavar='<resource_id>',
#     help=_('Resource id.'))
# def do_verify(cs, args):
#     """patron verify"""
#     ans = cs.patron_access.verify(args.user_id, args.resource_id)
#     print ans
