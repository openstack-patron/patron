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
{('GET', u'/%ID%/flavors/%SRCID%', ''): ('compute_extension:flavor_swap',
                                         'compute_extension:flavor_rxtx',
                                         'compute_extension:flavor_access',
                                         'compute_extension:flavorextradata',
                                         'compute_extension:flavor_disabled'),
 ('GET', u'/%ID%/images', ''): (),
 ('GET', u'/%ID%/images/%UUID%', ''): ('compute_extension:image_size',
                                       'compute_extension:disk_config'),
 ('GET', u'/%ID%/images/detail', ''): ('compute_extension:image_size',
                                       'compute_extension:disk_config'),
 ('GET', u'/%ID%/limits', ''): (),
 ('GET', u'/%ID%/os-aggregates', ''): ('compute_extension:aggregates',),
 ('GET', u'/%ID%/os-aggregates/%SRCID%', ''): ('compute_extension:aggregates',),
 ('GET', u'/%ID%/os-availability-zone/detail', ''): ('compute_extension:availability_zone:detail',),
 ('GET', u'/%ID%/os-cloudpipe', ''): ('compute_extension:cloudpipe',
                                      'compute:get_all'),
 ('GET', u'/%ID%/os-floating-ip-dns', ''): ('compute_extension:floating_ip_dns',),
 ('GET', u'/%ID%/os-hosts', ''): ('compute_extension:hosts',),
 ('GET', u'/%ID%/os-hosts/compute1', ''): (),
 ('GET', u'/%ID%/os-hypervisors', ''): ('compute_extension:hypervisors',),
 ('GET', u'/%ID%/os-hypervisors/%SRCID%/uptime', ''): ('compute_extension:hypervisors',),
 ('GET', u'/%ID%/os-hypervisors/compute1/servers', ''): ('compute_extension:hypervisors',),
 ('GET', u'/%ID%/os-hypervisors/detail', ''): ('compute_extension:hypervisors',),
 ('GET', u'/%ID%/os-hypervisors/statistics', ''): ('compute_extension:hypervisors',),
 ('GET', u'/%ID%/os-keypairs', ''): ('compute_extension:keypairs:index',),
 ('GET', u'/%ID%/os-keypairs/%KEYNAME%', ''): ('compute_extension:keypairs:show',),
 ('GET', u'/%ID%/os-networks', ''): ('compute_extension:networks:view',),
 ('GET', u'/%ID%/os-services', ''): ('compute_extension:services',),
 ('GET', u'/%ID%/os-tenant-networks', ''): ('compute_extension:os-tenant-networks',),
 ('GET', u'/%ID%/os-tenant-networks/%UUID%', ''): ('compute_extension:os-tenant-networks',),
 ('GET', u'/%ID%/servers', ''): ('compute:get_all',),
 ('GET', u'/%ID%/servers/%UUID%', ''): ('compute:get',
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
 ('GET', u'/%ID%/servers/%UUID%/diagnostics', ''): ('compute_extension:server_diagnostics',
                                                    'compute:get',
                                                    'compute:get_diagnostics'),
 ('GET', u'/%ID%/servers/%UUID%/os-instance-actions', u''): ('compute:get',
                                                             'compute_extension:instance_actions'),
 ('GET', u'/%ID%/servers/%UUID%/os-interface', ''): ('compute_extension:attach_interfaces',
                                                     'compute:get'),
 ('GET', u'/%ID%/servers/%UUID%/os-security-groups', ''): ('compute_extension:security_groups',
                                                           'compute:get'),
 ('GET', u'/%ID%/servers/%UUID%/os-server-password', ''): ('compute_extension:server_password',
                                                           'compute:get'),
 ('GET', u'/%ID%/servers/detail', ''): ('compute:get_all',
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
 ('POST', u'/%ID%/os-aggregates', ''): ('compute_extension:aggregates',),
 ('POST', u'/%ID%/os-keypairs', ''): ('compute_extension:keypairs:create',),
 ('POST', u'/%ID%/os-server-external-events', ''): ('compute_extension:os-server-external-events:create',),
 ('POST', u'/%ID%/servers', ''): ('compute_extension:disk_config',
                                  'compute:create',
                                  'compute:create:attach_network',
                                  'compute_extension:security_groups',
                                  'compute_extension:security_groups'),
 ('POST', u'/%ID%/servers/%UUID%/action', u'{"addSecurityGroup": {"name": "demosecgroup"}}'): ('compute_extension:security_groups',
                                                                                               'compute:get',
                                                                                               'compute:security_groups:add_to_instance'),
 ('POST', u'/%ID%/servers/%UUID%/action', u'{"createImage": {"name": "demoimage1", "metadata": {}}}'): ('compute:get',
                                                                                                        'compute:snapshot'),
 ('POST', u'/%ID%/servers/%UUID%/action', u'{"evacuate": {"onSharedStorage": false}}'): ('compute_extension:evacuate',
                                                                                         'compute:get'),
 ('POST', u'/%ID%/servers/%UUID%/action', u'{"migrate": null}'): ('compute_extension:admin_actions:migrate',
                                                                  'compute:get',
                                                                  'compute:resize'),
 ('POST', u'/%ID%/servers/%UUID%/action', u'{"os-getConsoleOutput": {"length": null}}'): ('compute_extension:console_output',
                                                                                          'compute:get',
                                                                                          'compute:get_console_output'),
 ('POST', u'/%ID%/servers/%UUID%/action', u'{"os-getSerialConsole": {"type": "serial"}}'): ('compute_extension:consoles',
                                                                                            'compute:get',
                                                                                            'compute:get_serial_console'),
 ('POST', u'/%ID%/servers/%UUID%/action', u'{"os-migrateLive": {"disk_over_commit": false, "block_migration": false, "host": null}}'): ('compute_extension:admin_actions:migrateLive',
                                                                                                                                        'compute:get'),
 ('POST', u'/%ID%/servers/%UUID%/action', u'{"os-resetState": {"state": "error"}}'): ('compute_extension:admin_actions:resetState',
                                                                                      'compute:get'),
 ('POST', u'/%ID%/servers/%UUID%/action', u'{"removeSecurityGroup": {"name": "demosecgroup"}}'): ('compute_extension:security_groups',
                                                                                                  'compute:get',
                                                                                                  'compute:security_groups:remove_from_instance'),
 ('POST', u'/%ID%/servers/%UUID%/action', u'{"rescue": null}'): ('compute_extension:rescue',
                                                                 'compute:get',
                                                                 'compute:rescue'),
 ('POST', u'/%ID%/servers/%UUID%/action', u'{"resetNetwork": null}'): ('compute_extension:admin_actions:resetNetwork',
                                                                       'compute:get',
                                                                       'compute:reset_network'),
 ('POST', u'/%ID%/servers/%UUID%/action', u'{"shelve": null}'): ('compute_extension:shelve',
                                                                 'compute:get',
                                                                 'compute:shelve'),
 ('POST', u'/%ID%/servers/%UUID%/action', u'{"shelveOffload": null}'): ('compute_extension:shelveOffload',
                                                                        'compute:get',
                                                                        'compute:shelve_offload'),
 ('POST', u'/%ID%/servers/%UUID%/os-interface', ''): ('compute_extension:attach_interfaces',
                                                      'compute:get',
                                                      'compute:attach_interface'),
 ('PUT', u'/%ID%/os-services/disable', ''): ('compute_extension:services',),
 ('PUT', u'/%ID%/os-services/enable', ''): ('compute_extension:services',)}


# Editted by puyangsky
def parse_path(req_path_info):
    id_pattern = "[0-9a-f]{32}"
    uuid_patern = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    sourceid_patern = "[0-9]{1}"
    path = ""
    paths = req_path_info[1:].split("/")

    for i in range(len(paths)):
        if re.match(id_pattern, paths[i]):
            paths[i] = "%ID%"
        if re.match(uuid_patern, paths[i]):
            paths[i] = "%UUID%"
        if re.match(sourceid_patern, paths[i]):
            paths[i] = "%SRCID%"
        if i < (len(paths)-1) and paths[i] == "os-keypairs" and len(paths[i+1]) != 0:
            paths[i+1] = "%KEYNAME%"
        path += "/"
        path += paths[i]
    return path

# Editted by puyangsky
def parse_inner_anction(req_innner_action, req_path_info):
    if re.search(r"action", req_path_info):
        parsed_inner_action = req_innner_action
    else:
        parsed_inner_action = ""
    return parsed_inner_action

def parse(req_method, path_info, req_inner_action):
    path = parse_path(path_info)
    inner_action = parse_inner_anction(req_inner_action, path_info)
    try:
        op = path_op_map[(req_method, path, inner_action)]
    except KeyError:
        return "KEY_ERROR"
    op = op[0]
    return op

"""
path = "/2326ca177bf541e297e454eff1357693/os-services/enable"
print parse("GET", path,"")
"""