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

from tempest_lib import decorators
from tempest_lib import exceptions

from patronclient.tests.functional import base


class SimpleReadOnlypatronclientTest(base.ClientTestBase):

    """
    read only functional python-patronclient tests.

    This only exercises client commands that are read only.
    """

    def test_admin_fake_action(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.patron,
                          'this-does-patron-exist')

    # NOTE(jogo): Commands in order listed in 'patron help'

    def test_admin_absolute_limites(self):
        self.patron('absolute-limits')
        self.patron('absolute-limits', params='--reserved')

    def test_admin_aggregate_list(self):
        self.patron('aggregate-list')

    def test_admin_availability_zone_list(self):
        self.assertIn("internal", self.patron('availability-zone-list'))

    def test_admin_cloudpipe_list(self):
        self.patron('cloudpipe-list')

    def test_admin_credentials(self):
        self.patron('credentials')

    # "Neutron does not provide this feature"
    def test_admin_dns_domains(self):
        self.patron('dns-domains')

    @decorators.skip_because(bug="1157349")
    def test_admin_dns_list(self):
        self.patron('dns-list')

    def test_admin_endpoints(self):
        self.patron('endpoints')

    def test_admin_flavor_acces_list(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.patron,
                          'flavor-access-list')
        # Failed to get access list for public flavor type
        self.assertRaises(exceptions.CommandFailed,
                          self.patron,
                          'flavor-access-list',
                          params='--flavor m1.tiny')

    def test_admin_flavor_list(self):
        self.assertIn("Memory_MB", self.patron('flavor-list'))

    def test_admin_floating_ip_bulk_list(self):
        self.patron('floating-ip-bulk-list')

    def test_admin_floating_ip_list(self):
        self.patron('floating-ip-list')

    def test_admin_floating_ip_pool_list(self):
        self.patron('floating-ip-pool-list')

    def test_admin_host_list(self):
        self.patron('host-list')

    def test_admin_hypervisor_list(self):
        self.patron('hypervisor-list')

    def test_admin_image_list(self):
        self.patron('image-list')

    @decorators.skip_because(bug="1157349")
    def test_admin_interface_list(self):
        self.patron('interface-list')

    def test_admin_keypair_list(self):
        self.patron('keypair-list')

    def test_admin_list(self):
        self.patron('list')
        self.patron('list', params='--all-tenants 1')
        self.patron('list', params='--all-tenants 0')
        self.assertRaises(exceptions.CommandFailed,
                          self.patron,
                          'list',
                          params='--all-tenants bad')

    def test_admin_network_list(self):
        self.patron('network-list')

    def test_admin_rate_limits(self):
        self.patron('rate-limits')

    def test_admin_secgroup_list(self):
        self.patron('secgroup-list')

    @decorators.skip_because(bug="1157349")
    def test_admin_secgroup_list_rules(self):
        self.patron('secgroup-list-rules')

    def test_admin_server_group_list(self):
        self.patron('server-group-list')

    def test_admin_servce_list(self):
        self.patron('service-list')

    def test_admin_usage(self):
        self.patron('usage')

    def test_admin_usage_list(self):
        self.patron('usage-list')

    def test_admin_volume_list(self):
        self.patron('volume-list')

    def test_admin_volume_snapshot_list(self):
        self.patron('volume-snapshot-list')

    def test_admin_volume_type_list(self):
        self.patron('volume-type-list')

    def test_admin_help(self):
        self.patron('help')

    def test_admin_list_extensions(self):
        self.patron('list-extensions')

    def test_admin_net_list(self):
        self.patron('net-list')

    def test_agent_list(self):
        self.patron('agent-list')
        self.patron('agent-list', flags='--debug')

    def test_migration_list(self):
        self.patron('migration-list')
        self.patron('migration-list', flags='--debug')

    # Optional arguments:

    def test_admin_version(self):
        self.patron('', flags='--version')

    def test_admin_debug_list(self):
        self.patron('list', flags='--debug')

    def test_admin_timeout(self):
        self.patron('list', flags='--timeout %d' % 10)

    def test_admin_timing(self):
        self.patron('list', flags='--timing')
