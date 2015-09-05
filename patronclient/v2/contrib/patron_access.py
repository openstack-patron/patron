# Copyright 2013 Rackspace Hosting
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from patronclient import base
from patronclient.i18n import _
from patronclient.openstack.common import cliutils
from patronclient import utils


class PatronResource(base.Resource):
    def __repr__(self):
        return "<PatronResource: %s>" % self.name


class PatronAccessManager(base.Manager):
    resource_class = PatronResource

    def verify(self, rule):
        """
        patron verify
        """
        # os-patron-access/123/resource/456/action/verify
        return self.api.client.get("/os-patron-access/rule/%s/verify" % rule)


@cliutils.arg(
    '--rule',
    metavar='<rule>',
    help=_('User rule.For example:\n\tcompute_extension:admin_actions'))
def do_verify(cs, args):
    """patron verify. Args:rule. For example:\n\tcompute_extension:admin_actions"""
    ans = cs.patron_access.verify(args.rule)
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
