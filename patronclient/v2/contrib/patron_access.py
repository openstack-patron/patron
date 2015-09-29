# add by Wu Luo

from patronclient import base
from patronclient.i18n import _
from patronclient.openstack.common import cliutils
from patronclient import utils
import os
import json


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

    def setpolicy(self, **kwargs):
        """
        patron setpolicy
        """
        return self.api.client.post("/os-patron-access/setpolicy", **kwargs)


    def getpolicy(self, **kwargs):
        """
        patron setpolicy
        """
        return self.api.client.get("/os-patron-access/getpolicy", **kwargs)

    def setlabel(self, **kwargs):
        """
        patron setpolicy
        """
        return self.api.client.post("/os-patron-access/setlabel", **kwargs)


    def getlabel(self, **kwargs):
        """
        patron setpolicy
        """
        return self.api.client.get("/os-patron-access/getlabel", **kwargs)


@cliutils.arg(
    '--op',
    metavar='<op>',
    help=_('User op for example:\n\tcompute_extension:admin_actions'))
def do_verify(cs, args):
    """patron verify. Args:op. For example:\n\tcompute_extension:admin_actions"""
    ans = cs.patron_access.verify(json = {'op': args.op})
    print ans

@cliutils.arg(
    '--file',
    metavar='<file>',
    help=_('User policy file path'))
def do_setpolicy(cs, args):
    """patron setpolicy. Args:policy."""
    #check file exists?
    if os.path.exists(args.file) and os.path.isfile(args.file) :
        policy = open(args.file, 'r')
        obj = dict(json.loads(policy.read()))
        ans = cs.patron_access.setpolicy(json = {'policy': obj})
        print ans
    else :
        print 'ERROR: file not exists'

def do_getpolicy(cs, args):
    """patron setpolicy. Args:policy."""
    ans = cs.patron_access.getpolicy()
    print ans

@cliutils.arg(
    '--label',
    metavar='<label>',
    help=_('User label'))
def do_setlabel(cs, args):
    """patron setlabel. Args:label."""
    ans = cs.patron_access.setlabel(json = {'label': args.label})
    print ans

def do_getlabel(cs, args):
    """patron setlabel"""
    ans = cs.patron_access.getlabel()
    print ans

