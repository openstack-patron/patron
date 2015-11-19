"""
Added by puyangsky
Dict for parse path_info URL into rule
"""
import re
from oslo_log import log as logging

import op_map.nova_op_map
import op_map.glance_op_map
import op_map.neutron_op_map
import op_map.cinder_op_map
import op_map.heat_op_map
import op_map.ceilometer_op_map

LOG = logging.getLogger(__name__)

# The mappings from URL path to op.
# This mappings can be sorted, duplicate-removed and formatted by:
# from pprint import pprint
# pprint(path_op_map)

# The below op map is added by human.
path_op_map = \
{(8774, '/v2', '/extensions', 'GET', ''): (),
 (8774, '/v2', '/flavors', 'POST', ''): ('compute_extension:flavormanage',
                                              'compute_extension:flavor_swap',
                                              'compute_extension:flavor_rxtx',
                                              'compute_extension:flavor_access',
                                              'compute_extension:flavorextradata',
                                              'compute_extension:flavor_disabled'),
 (8774, '/v2', '/flavors/%NAME%', 'DELETE', ''): ('compute_extension:flavormanage',),
 (8774, '/v2', '/flavors/%NAME%', 'GET', ''): ('compute_extension:flavor_swap',
                                                    'compute_extension:flavor_rxtx',
                                                    'compute_extension:flavor_access',
                                                    'compute_extension:flavorextradata',
                                                    'compute_extension:flavor_disabled'),
 (8774, '/v2', '/flavors/%NAME%/os-extra_specs', 'GET', ''): ('compute_extension:flavorextraspecs:index',),
 (8774, '/v2', '/flavors/detail', 'GET', ''): ('compute_extension:flavor_swap',
                                                    'compute_extension:flavor_rxtx',
                                                    'compute_extension:flavor_access',
                                                    'compute_extension:flavorextradata',
                                                    'compute_extension:flavor_disabled'),
 (8774, '/v2', '/flavors?is_public=%VALUE%', 'GET', ''): (),
 (8774, '/v2', '/images', 'GET', ''): (),
 (8774, '/v2', '/images/%UUID%', 'GET', ''): ('compute_extension:image_size',
                                                   'compute_extension:disk_config'),
 (8774, '/v2', '/images/detail', 'GET', ''): ('compute_extension:image_size',
                                                   'compute_extension:disk_config'),
 (8774, '/v2', '/limits', 'GET', ''): (),
 (8774, '/v2', '/os-aggregates', 'GET', ''): ('compute_extension:aggregates',),
 (8774, '/v2', '/os-aggregates', 'POST', ''): ('compute_extension:aggregates',),
 (8774, '/v2', '/os-aggregates/%NAME%', 'DELETE', ''): ('compute_extension:aggregates',),
 (8774, '/v2', '/os-aggregates/%NAME%', 'GET', ''): ('compute_extension:aggregates',),
 (8774, '/v2', '/os-aggregates/%NAME%/action', 'POST', 'host'): ('compute_extension:aggregates',),
 (8774, '/v2', '/os-availability-zone/detail', 'GET', ''): ('compute_extension:availability_zone:detail',),
 (8774, '/v2', '/os-certificates/root', 'GET', ''): ('compute_extension:certificates',),
 (8774, '/v2', '/os-cloudpipe', 'GET', ''): ('compute_extension:cloudpipe',
                                                  'compute:get_all'),
 (8774, '/v2', '/os-floating-ip-dns', 'GET', ''): ('compute_extension:floating_ip_dns',),
 (8774, '/v2', '/os-floating-ip-pools', 'GET', ''): ('compute_extension:floating_ip_pools',),
 (8774, '/v2', '/os-floating-ips', 'GET', ''): ('compute_extension:floating_ips',),
 (8774, '/v2', '/os-floating-ips', 'POST', ''): ('compute_extension:floating_ips',),
 (8774, '/v2', '/os-floating-ips-bulk', 'GET', ''): ('compute_extension:floating_ips_bulk',),
 (8774, '/v2', '/os-hosts', 'GET', ''): ('compute_extension:hosts',),
 (8774, '/v2', '/os-hosts/%NAME%', 'GET', ''): (),
 (8774, '/v2', '/os-hypervisors', 'GET', ''): ('compute_extension:hypervisors',),
 (8774, '/v2', '/os-hypervisors/%NAME%', 'GET', ''): ('compute_extension:hypervisors',),
 (8774, '/v2', '/os-hypervisors/%NAME%/servers', 'GET', ''): ('compute_extension:hypervisors',),
 (8774, '/v2', '/os-hypervisors/%NAME%/uptime', 'GET', ''): ('compute_extension:hypervisors',),
 (8774, '/v2', '/os-hypervisors/detail', 'GET', ''): ('compute_extension:hypervisors',),
 (8774, '/v2', '/os-keypairs', 'GET', ''): ('compute_extension:keypairs:index',),
 (8774, '/v2', '/os-keypairs', 'POST', ''): ('compute_extension:keypairs:create',),
 (8774, '/v2', '/os-keypairs/%NAME%', 'DELETE', ''): ('compute_extension:keypairs:delete',),
 (8774, '/v2', '/os-keypairs/%NAME%', 'GET', ''): ('compute_extension:keypairs:show',),
 (8774, '/v2', '/os-migrations', 'GET', ''): ('compute_extension:migrations:index',),
 (8774, '/v2', '/os-networks', 'GET', ''): ('compute_extension:networks:view',),
 (8774, '/v2', '/os-quota-sets/%ID%', 'DELETE', ''): ('compute_extension:quotas:delete',),
 (8774, '/v2', '/os-quota-sets/%ID%', 'GET', ''): ('compute_extension:quotas:show',),
 (8774, '/v2', '/os-quota-sets/%ID%', 'PUT', ''): ('compute_extension:quotas:update',),
 (8774, '/v2', '/os-quota-sets/%ID%/defaults', 'GET', ''): ('compute_extension:quotas:show',),
 (8774, '/v2', '/os-security-group-default-rules', 'GET', ''): ('compute_extension:security_groups',
                                                                     'compute_extension:security_group_default_rules'),
 (8774, '/v2', '/os-security-groups', 'GET', ''): ('compute_extension:security_groups',),
 (8774, '/v2', '/os-security-groups', 'POST', ''): ('compute_extension:security_groups',),
 (8774, '/v2', '/os-security-groups/%UUID%', 'DELETE', ''): ('compute_extension:security_groups',),
 (8774, '/v2', '/os-security-groups/%UUID%', 'PUT', ''): ('compute_extension:security_groups',),
 (8774, '/v2', '/os-server-external-events', 'POST', ''): ('compute_extension:os-server-external-events:create',),
 (8774, '/v2', '/os-server-groups', 'GET', ''): ('compute_extension:server_groups',),
 (8774, '/v2', '/os-server-groups', 'POST', ''): ('compute_extension:server_groups',),
 (8774, '/v2', '/os-server-groups/%UUID%', 'DELETE', ''): ('compute_extension:server_groups',),
 (8774, '/v2', '/os-server-groups/%UUID%', 'GET', ''): ('compute_extension:server_groups',),
 (8774, '/v2', '/os-services', 'GET', ''): ('compute_extension:services',),
 (8774, '/v2', '/os-services/disable', 'PUT', ''): ('compute_extension:services',),
 (8774, '/v2', '/os-services/enable', 'PUT', ''): ('compute_extension:services',),
 (8774, '/v2', '/os-simple-tenant-usage/%ID%', 'GET', ''): ('compute_extension:simple_tenant_usage:show',),
 (8774, '/v2', '/os-simple-tenant-usage?start=%VALUE%&end=%VALUE%&detailed=%VALUE%', 'GET', ''): ('compute_extension:simple_tenant_usage:list',),
 (8774, '/v2', '/os-tenant-networks', 'GET', ''): ('compute_extension:os-tenant-networks',),
 (8774, '/v2', '/os-tenant-networks', 'POST', ''): ('compute_extension:os-tenant-networks',),
 (8774, '/v2', '/os-tenant-networks/%UUID%', 'DELETE', ''): ('compute_extension:os-tenant-networks',),
 (8774, '/v2', '/os-tenant-networks/%UUID%', 'GET', ''): ('compute_extension:os-tenant-networks',),
 (8774, '/v2', '/servers', 'POST', ''): ('compute_extension:disk_config',
                                              'compute:create',
                                              'compute:create:attach_network',
                                              'compute_extension:security_groups',
                                              'compute_extension:security_groups'),
 (8774, '/v2', '/servers/%UUID%', 'DELETE', ''): ('compute:get',
                                                       'compute:delete'),
 (8774, '/v2', '/servers/%UUID%', 'GET', ''): ('compute:get',
                                                    'compute_extension:security_groups',
                                                    'compute_extension:security_groups',
                                                    'compute_extension:keypairs',
                                                    'compute_extension:hide_server_addresses',
                                                    'compute_extension:extended_volumes',
                                                    'compute_extension:config_drive',
                                                    'compute_extension:server_usage',
                                                    'compute_extension:extended_status',
                                                    'compute_extension:extended_server_attributes',
                                                    'compute_extension:extended_ips_mac',
                                                    'compute_extension:extended_ips',
                                                    'compute_extension:extended_availability_zone',
                                                    'compute_extension:disk_config'),
 (8774, '/v2', '/servers/%UUID%', 'PUT', ''): ('compute_extension:disk_config',
                                                    'compute:get'),
 (8774, '/v2', '/servers/%UUID%/action', 'POST', 'addSecurityGroup'): ('compute_extension:security_groups',
                                                                            'compute:get',
                                                                            'compute:security_groups:add_to_instance'),
 (8774, '/v2', '/servers/%UUID%/action', 'POST', 'changePassword'): ('compute:get',
                                                                          'compute:set_admin_password'),
 (8774, '/v2', '/servers/%UUID%/action', 'POST', 'confirmResize'): ('compute:get',
                                                                         'compute:confirm_resize'),
 (8774, '/v2', '/servers/%UUID%/action', 'POST', 'createImage'): ('compute:get',
                                                                       'compute:snapshot'),
 (8774, '/v2', '/servers/%UUID%/action', 'POST', 'evacuate'): ('compute_extension:evacuate',
                                                                    'compute:get'),
 (8774, '/v2', '/servers/%UUID%/action', 'POST', 'lock'): ('compute_extension:admin_actions:lock',
                                                                'compute:get',
                                                                'compute:lock'),
 (8774, '/v2', '/servers/%UUID%/action', 'POST', 'migrate'): ('compute_extension:admin_actions:migrate',
                                                                   'compute:get',
                                                                   'compute:resize'),
 (8774, '/v2', '/servers/%UUID%/action', 'POST', 'os-getConsoleOutput'): ('compute_extension:console_output',
                                                                               'compute:get',
                                                                               'compute:get_console_output'),
 (8774, '/v2', '/servers/%UUID%/action', 'POST', 'os-getSerialConsole'): ('compute_extension:consoles',
                                                                               'compute:get',
                                                                               'compute:get_serial_console'),
 (8774, '/v2', '/servers/%UUID%/action', 'POST', 'os-migrateLive'): ('compute_extension:admin_actions:migrateLive',
                                                                          'compute:get'),
 (8774, '/v2', '/servers/%UUID%/action', 'POST', 'os-resetState'): ('compute_extension:admin_actions:resetState',
                                                                         'compute:get'),
 (8774, '/v2', '/servers/%UUID%/action', 'POST', 'os-start'): ('compute:start',),
 (8774, '/v2', '/servers/%UUID%/action', 'POST', 'os-stop'): ('compute:stop',),
 (8774, '/v2', '/servers/%UUID%/action', 'POST', 'pause'): ('compute_extension:admin_actions:pause',
                                                                 'compute:get',
                                                                 'compute:pause'),
 (8774, '/v2', '/servers/%UUID%/action', 'POST', 'reboot'): ('compute:get',
                                                                  'compute:reboot'),
 (8774, '/v2', '/servers/%UUID%/action', 'POST', 'removeSecurityGroup'): ('compute_extension:security_groups',
                                                                               'compute:get',
                                                                               'compute:security_groups:remove_from_instance'),
 (8774, '/v2', '/servers/%UUID%/action', 'POST', 'rescue'): ('compute_extension:rescue',
                                                                  'compute:get',
                                                                  'compute:rescue'),
 (8774, '/v2', '/servers/%UUID%/action', 'POST', 'resetNetwork'): ('compute_extension:admin_actions:resetNetwork',
                                                                        'compute:get',
                                                                        'compute:reset_network'),
 (8774, '/v2', '/servers/%UUID%/action', 'POST', 'resize'): ('compute_extension:disk_config',
                                                                  'compute:get',
                                                                  'compute:resize'),
 (8774, '/v2', '/servers/%UUID%/action', 'POST', 'restore'): ('compute_extension:deferred_delete',
                                                                   'compute:get',
                                                                   'compute:restore'),
 (8774, '/v2', '/servers/%UUID%/action', 'POST', 'resume'): ('compute_extension:admin_actions:resume',
                                                                  'compute:get',
                                                                  'compute:resume'),
 (8774, '/v2', '/servers/%UUID%/action', 'POST', 'revertResize'): ('compute:get',
                                                                        'compute:revert_resize'),
 (8774, '/v2', '/servers/%UUID%/action', 'POST', 'shelve'): ('compute_extension:shelve',
                                                                  'compute:get',
                                                                  'compute:shelve'),
 (8774, '/v2', '/servers/%UUID%/action', 'POST', 'shelveOffload'): ('compute_extension:shelveOffload',
                                                                         'compute:get',
                                                                         'compute:shelve_offload'),
 (8774, '/v2', '/servers/%UUID%/action', 'POST', 'suspend'): ('compute_extension:admin_actions:suspend',
                                                                   'compute:get',
                                                                   'compute:suspend'),
 (8774, '/v2', '/servers/%UUID%/action', 'POST', 'unlock'): ('compute_extension:admin_actions:unlock',
                                                                  'compute:get',
                                                                  'compute:unlock'),
 (8774, '/v2', '/servers/%UUID%/action', 'POST', 'unpause'): ('compute_extension:admin_actions:unpause',
                                                                   'compute:get',
                                                                   'compute:unpause'),
 (8774, '/v2', '/servers/%UUID%/action', 'POST', 'unrescue'): ('compute_extension:rescue',
                                                                    'compute:get',
                                                                    'compute:unrescue'),
 (8774, '/v2', '/servers/%UUID%/action', 'POST', 'unshelve'): ('compute_extension:unshelve',
                                                                    'compute:get',
                                                                    'compute:unshelve'),
 (8774, '/v2', '/servers/%UUID%/diagnostics', 'GET', ''): ('compute_extension:server_diagnostics',
                                                                'compute:get',
                                                                'compute:get_diagnostics'),
 (8774, '/v2', '/servers/%UUID%/os-instance-actions', 'GET', ''): ('compute:get',
                                                                        'compute_extension:instance_actions'),
 (8774, '/v2', '/servers/%UUID%/os-interface', 'GET', ''): ('compute_extension:attach_interfaces',
                                                                 'compute:get'),
 (8774, '/v2', '/servers/%UUID%/os-interface', 'POST', ''): ('compute_extension:attach_interfaces',
                                                                  'compute:get',
                                                                  'compute:attach_interface'),
 (8774, '/v2', '/servers/%UUID%/os-security-groups', 'GET', ''): ('compute_extension:security_groups',
                                                                       'compute:get'),
 (8774, '/v2', '/servers/%UUID%/os-server-password', 'GET', ''): ('compute_extension:server_password',
                                                                       'compute:get'),
 (8774, '/v2', '/servers/detail', 'GET', ''): ('compute:get_all',
                                                    'compute_extension:security_groups',
                                                    'compute_extension:security_groups',
                                                    'compute_extension:keypairs',
                                                    'compute_extension:hide_server_addresses',
                                                    'compute_extension:extended_volumes',
                                                    'compute_extension:config_drive',
                                                    'compute_extension:server_usage',
                                                    'compute_extension:extended_status',
                                                    'compute_extension:extended_server_attributes',
                                                    'compute_extension:extended_ips_mac',
                                                    'compute_extension:extended_ips',
                                                    'compute_extension:extended_availability_zone',
                                                    'compute_extension:disk_config'),
 (8774, '/v2', '/servers?all_tenants=%VALUE%&name=%VALUE%', 'GET', ''): ('compute:get_all',),
 (8774, '/v2', '/servers?name=%VALUE%', 'GET', ''): ('compute:get_all',),
 (9292, '/v2', '/schemas/image', 'GET', ''): ('get_images',),
 (9292, '/v2', '/images?limit=%VALUE%', 'GET', ''): ('get_images',),
 (9292, '/v2', '/images?marker=%VALUE%&limit=%VALUE%', 'GET', ''): ('get_images',),
 (9292, '/v2', '/images/%UUID%', 'GET', ''): ('get_image',),
 (9696, '/v2.0', '/networks', 'GET', ''): ('get_network',),
 (9696, '/v2.0', '/subnets?fields=%VALUE%&fields=%VALUE%&id=%VALUE%&id=%VALUE%', 'GET', ''): ('get_network',),
 (9696, '/v2.0', '/networks', 'GET', ''): ('get_network',),
 (9696, '/v2.0', '/networks?fields=%VALUE%&id=%VALUE%', 'GET', ''): ('get_network',),
 (9696, '/v2.0', '/networks/%UUID%', 'GET', ''): ('get_network',),
 (8777, '/v2', '/meters', 'GET', ''): (),}

# Load op maps for all services
# These op maps are automatically generated by Tempest commands.
path_op_map.update(op_map.nova_op_map.op_map)
path_op_map.update(op_map.glance_op_map.op_map)
path_op_map.update(op_map.neutron_op_map.op_map)
path_op_map.update(op_map.cinder_op_map.op_map)
path_op_map.update(op_map.heat_op_map.op_map)
path_op_map.update(op_map.ceilometer_op_map.op_map)
LOG.info("Op map has been loaded!!")
#LOG.info("Path op map: %r", (path_op_map))

# Editted by puyangsky
def parse_inner_anction(req_innner_action, req_path_info):
    if re.search("action", req_path_info):
        parsed_inner_action = req_innner_action
    else:
        parsed_inner_action = ""
    return parsed_inner_action

def parse(req_server_port, req_api_version, req_method, path_info, req_inner_action, template_path_info):
    inner_action = parse_inner_anction(req_inner_action, path_info)
    try:
        op = path_op_map[(req_server_port, req_api_version, template_path_info, req_method, inner_action)]
    except KeyError:
        LOG.info("KEY_ERROR, failed to find the key: %r", (req_server_port, req_api_version, template_path_info, req_method, inner_action))
        return "KEY_ERROR"
    try:
        op = op[0]
    except IndexError:
        return ""
    return op

"""
path = "/2326ca177bf541e297e454eff1357693/os-services/enable"
print parse("GET", path,"")
"""