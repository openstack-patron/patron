
# op map for ceilometer.
op_map = \
{(8777, '/v2', '/alarms', 'GET', ''): ('telemetry:get_alarms', 'segregation'),
 (8777, '/v2', '/alarms', 'POST', ''): ('telemetry:create_alarm',
                                        'segregation'),
 (8777, '/v2', '/alarms/%UUID%', 'DELETE', ''): ('telemetry:delete_alarm',
                                                 'segregation'),
 (8777, '/v2', '/alarms/%UUID%', 'GET', ''): ('segregation',
                                              'telemetry:get_alarm'),
 (8777, '/v2', '/alarms/%UUID%', 'PUT', ''): ('segregation',
                                              'telemetry:change_alarm'),
 (8777, '/v2', '/alarms/%UUID%/history', 'GET', ''): ('segregation',
                                                      'telemetry:alarm_history'),
 (8777, '/v2', '/alarms/%UUID%/state', 'GET', ''): ('segregation',
                                                    'telemetry:get_alarm_state'),
 (8777, '/v2', '/alarms/%UUID%/state', 'PUT', ''): ('telemetry:change_alarm_state',
                                                    'segregation'),
 (8777, '/v2', '/alarms?q.field=%VALUE%&q.op=%VALUE%&q.type=%VALUE%&q.value=%VALUE%', 'GET', ''): ('telemetry:get_alarms',
                                                                                                   'segregation'),
 (8777, '/v2', '/meters/image.download?q.op=%VALUE%&q.value=%VALUE%&q.field=%VALUE%', 'GET', ''): ('segregation',
                                                                                                   'telemetry:get_samples'),
 (8777, '/v2', '/meters/image.size?q.op=%VALUE%&q.value=%VALUE%&q.field=%VALUE%', 'GET', ''): ('segregation',
                                                                                               'telemetry:get_samples')}