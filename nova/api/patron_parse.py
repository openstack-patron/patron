"""
Added by puyangsky
Dict for parse path_info URL into rule
"""
import re

# The mappings from URL path to op.
# This mappings can be sorted, duplicate-removed and formatted by:
# from pprint import pprint
# pprint(path_op_map)
path_op_map = \
{(8774, '/v2', u'/%ID%/flavors/%NAME%', 'GET', ''): ('compute_extension:flavor_swap',
                                                     'compute_extension:flavor_rxtx',
                                                     'compute_extension:flavor_access',
                                                     'compute_extension:flavorextradata',
                                                     'compute_extension:flavor_disabled'),
 (8774, '/v2', u'/%ID%/images', 'GET', ''): (),
 (8774, '/v2', u'/%ID%/images/%UUID%', 'GET', ''): ('compute_extension:image_size',
                                                    'compute_extension:disk_config'),
 (8774, '/v2', u'/%ID%/images/detail', 'GET', ''): ('compute_extension:image_size',
                                                    'compute_extension:disk_config'),
 (8774, '/v2', u'/%ID%/limits', 'GET', ''): (),
 (8774, '/v2', u'/%ID%/os-aggregates', 'GET', ''): ('compute_extension:aggregates',),
 (8774, '/v2', u'/%ID%/os-aggregates', 'POST', ''): ('compute_extension:aggregates',),
 (8774, '/v2', u'/%ID%/os-aggregates/%NAME%', 'DELETE', ''): ('compute_extension:aggregates',),
 (8774, '/v2', u'/%ID%/os-aggregates/%NAME%', 'GET', ''): ('compute_extension:aggregates',),
 (8774, '/v2', u'/%ID%/os-availability-zone/detail', 'GET', ''): ('compute_extension:availability_zone:detail',),
 (8774, '/v2', u'/%ID%/os-cloudpipe', 'GET', ''): ('compute_extension:cloudpipe',
                                                   'compute:get_all'),
 (8774, '/v2', u'/%ID%/os-floating-ip-dns', 'GET', ''): ('compute_extension:floating_ip_dns',),
 (8774, '/v2', u'/%ID%/os-hosts', 'GET', ''): ('compute_extension:hosts',),
 (8774, '/v2', u'/%ID%/os-hosts/compute1', 'GET', ''): (),
 (8774, '/v2', u'/%ID%/os-hypervisors', 'GET', ''): ('compute_extension:hypervisors',),
 (8774, '/v2', u'/%ID%/os-hypervisors/%NAME%/uptime', 'GET', ''): ('compute_extension:hypervisors',),
 (8774, '/v2', u'/%ID%/os-hypervisors/compute1/servers', 'GET', ''): ('compute_extension:hypervisors',),
 (8774, '/v2', u'/%ID%/os-hypervisors/detail', 'GET', ''): ('compute_extension:hypervisors',),
 (8774, '/v2', u'/%ID%/os-hypervisors/statistics', 'GET', ''): ('compute_extension:hypervisors',),
 (8774, '/v2', u'/%ID%/os-keypairs', 'GET', ''): ('compute_extension:keypairs:index',),
 (8774, '/v2', u'/%ID%/os-keypairs', 'POST', ''): ('compute_extension:keypairs:create',),
 (8774, '/v2', u'/%ID%/os-keypairs/%NAME%', 'GET', ''): ('compute_extension:keypairs:show',),
 (8774, '/v2', u'/%ID%/os-networks', 'GET', ''): ('compute_extension:networks:view',),
 (8774, '/v2', u'/%ID%/os-server-external-events', 'POST', ''): ('compute_extension:os-server-external-events:create',),
 (8774, '/v2', u'/%ID%/os-services', 'GET', ''): ('compute_extension:services',),
 (8774, '/v2', u'/%ID%/os-services/disable', 'PUT', ''): ('compute_extension:services',),
 (8774, '/v2', u'/%ID%/os-services/enable', 'PUT', ''): ('compute_extension:services',),
 (8774, '/v2', u'/%ID%/os-tenant-networks', 'GET', ''): ('compute_extension:os-tenant-networks',),
 (8774, '/v2', u'/%ID%/os-tenant-networks/%UUID%', 'GET', ''): ('compute_extension:os-tenant-networks',),
 (8774, '/v2', u'/%ID%/servers', 'GET', ''): ('compute:get_all',),
 (8774, '/v2', u'/%ID%/servers', 'POST', ''): ('compute_extension:disk_config',
                                               'compute:create',
                                               'compute:create:attach_network',
                                               'compute_extension:security_groups',
                                               'compute_extension:security_groups'),
 (8774, '/v2', u'/%ID%/servers/%UUID%', 'GET', ''): ('compute:get',
                                                     'compute_extension:security_groups',
                                                     'compute_extension:security_groups',
                                                     'compute_extension:keypairs',
                                                     'compute_extension:extended_volumes',
                                                     'compute_extension:config_drive',
                                                     'compute_extension:server_usage',
                                                     'compute_extension:extended_status',
                                                     'compute_extension:extended_server_attributes',
                                                     'compute_extension:extended_ips_mac',
                                                     'compute_extension:extended_ips',
                                                     'compute_extension:extended_availability_zone',
                                                     'compute_extension:disk_config'),
 (8774, '/v2', u'/%ID%/servers/%UUID%/action', 'POST', u'{"addSecurityGroup": {"name": "demo-secgroup1"}}'): ('compute_extension:security_groups',
                                                                                                              'compute:get',
                                                                                                              'compute:security_groups:add_to_instance'),
 (8774, '/v2', u'/%ID%/servers/%UUID%/action', 'POST', u'{"createImage": {"name": "demo-image1", "metadata": {}}}'): ('compute:get',
                                                                                                                      'compute:snapshot'),
 (8774, '/v2', u'/%ID%/servers/%UUID%/action', 'POST', u'{"evacuate": {"onSharedStorage": false}}'): ('compute_extension:evacuate',
                                                                                                      'compute:get'),
 (8774, '/v2', u'/%ID%/servers/%UUID%/action', 'POST', u'{"migrate": null}'): ('compute_extension:admin_actions:migrate',
                                                                               'compute:get',
                                                                               'compute:resize'),
 (8774, '/v2', u'/%ID%/servers/%UUID%/action', 'POST', u'{"os-getConsoleOutput": {"length": null}}'): ('compute_extension:console_output',
                                                                                                       'compute:get',
                                                                                                       'compute:get_console_output'),
 (8774, '/v2', u'/%ID%/servers/%UUID%/action', 'POST', u'{"os-getSerialConsole": {"type": "serial"}}'): ('compute_extension:consoles',
                                                                                                         'compute:get',
                                                                                                         'compute:get_serial_console'),
 (8774, '/v2', u'/%ID%/servers/%UUID%/action', 'POST', u'{"os-migrateLive": {"disk_over_commit": false, "block_migration": false, "host": null}}'): ('compute_extension:admin_actions:migrateLive',
                                                                                                                                                     'compute:get'),
 (8774, '/v2', u'/%ID%/servers/%UUID%/action', 'POST', u'{"os-resetState": {"state": "error"}}'): ('compute_extension:admin_actions:resetState',
                                                                                                   'compute:get'),
 (8774, '/v2', u'/%ID%/servers/%UUID%/action', 'POST', u'{"removeSecurityGroup": {"name": "demo-secgroup1"}}'): ('compute_extension:security_groups',
                                                                                                                 'compute:get',
                                                                                                                 'compute:security_groups:remove_from_instance'),
 (8774, '/v2', u'/%ID%/servers/%UUID%/action', 'POST', u'{"rescue": null}'): ('compute_extension:rescue',
                                                                              'compute:get',
                                                                              'compute:rescue'),
 (8774, '/v2', u'/%ID%/servers/%UUID%/action', 'POST', u'{"resetNetwork": null}'): ('compute_extension:admin_actions:resetNetwork',
                                                                                    'compute:get',
                                                                                    'compute:reset_network'),
 (8774, '/v2', u'/%ID%/servers/%UUID%/action', 'POST', u'{"shelve": null}'): ('compute_extension:shelve',
                                                                              'compute:get',
                                                                              'compute:shelve'),
 (8774, '/v2', u'/%ID%/servers/%UUID%/action', 'POST', u'{"shelveOffload": null}'): ('compute_extension:shelveOffload',
                                                                                     'compute:get',
                                                                                     'compute:shelve_offload'),
 (8774, '/v2', u'/%ID%/servers/%UUID%/diagnostics', 'GET', ''): ('compute_extension:server_diagnostics',
                                                                 'compute:get',
                                                                 'compute:get_diagnostics'),
 (8774, '/v2', u'/%ID%/servers/%UUID%/os-instance-actions', 'GET', u''): ('compute:get',
                                                                          'compute_extension:instance_actions'),
 (8774, '/v2', u'/%ID%/servers/%UUID%/os-interface', 'GET', ''): ('compute_extension:attach_interfaces',
                                                                  'compute:get'),
 (8774, '/v2', u'/%ID%/servers/%UUID%/os-interface', 'POST', ''): ('compute_extension:attach_interfaces',
                                                                   'compute:get',
                                                                   'compute:attach_interface'),
 (8774, '/v2', u'/%ID%/servers/%UUID%/os-security-groups', 'GET', ''): ('compute_extension:security_groups',
                                                                        'compute:get'),
 (8774, '/v2', u'/%ID%/servers/%UUID%/os-server-password', 'GET', ''): ('compute_extension:server_password',
                                                                        'compute:get'),
 (8774, '/v2', u'/%ID%/servers/detail', 'GET', ''): ('compute:get_all',
                                                     'compute_extension:security_groups',
                                                     'compute_extension:security_groups',
                                                     'compute_extension:keypairs',
                                                     'compute_extension:extended_volumes',
                                                     'compute_extension:config_drive',
                                                     'compute_extension:server_usage',
                                                     'compute_extension:extended_status',
                                                     'compute_extension:extended_server_attributes',
                                                     'compute_extension:extended_ips_mac',
                                                     'compute_extension:extended_ips',
                                                     'compute_extension:extended_availability_zone',
                                                     'compute_extension:disk_config')}



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
        return "KEY_ERROR"
    try:
        op = op[0]
    except IndexError:
        return "INDEX_ERROR"
    return op

"""
path = "/2326ca177bf541e297e454eff1357693/os-services/enable"
print parse("GET", path,"")
"""