#    Copyright 2013 IBM Corp.
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

import mock
from oslo_serialization import jsonutils
from oslo_utils import timeutils

from nova import db
from nova import exception
from nova import objects
from nova.objects import aggregate
from nova.objects import service
from nova.tests.unit.objects import test_compute_node
from nova.tests.unit.objects import test_objects

NOW = timeutils.utcnow().replace(microsecond=0)
fake_service = {
    'created_at': NOW,
    'updated_at': None,
    'deleted_at': None,
    'deleted': False,
    'id': 123,
    'host': 'fake-host',
    'binary': 'fake-service',
    'topic': 'fake-service-topic',
    'report_count': 1,
    'disabled': False,
    'disabled_reason': None,
    }

OPTIONAL = ['availability_zone', 'compute_node']


class _TestServiceObject(object):
    def supported_hv_specs_comparator(self, expected, obj_val):
        obj_val = [inst.to_list() for inst in obj_val]
        self.json_comparator(expected, obj_val)

    def pci_device_pools_comparator(self, expected, obj_val):
        obj_val = obj_val.obj_to_primitive()
        self.json_loads_comparator(expected, obj_val)

    def json_loads_comparator(self, expected, obj_val):
        # NOTE(edleafe): This is necessary because the dumps() version of the
        # PciDevicePoolList doesn't maintain ordering, so the output string
        # doesn't always match.
        self.assertEqual(jsonutils.loads(expected), obj_val)

    def comparators(self):
        return {'stats': self.json_comparator,
                'host_ip': self.str_comparator,
                'supported_hv_specs': self.supported_hv_specs_comparator,
                'pci_device_pools': self.pci_device_pools_comparator}

    def subs(self):
        return {'supported_hv_specs': 'supported_instances',
                'pci_device_pools': 'pci_stats'}

    def _test_query(self, db_method, obj_method, *args, **kwargs):
        self.mox.StubOutWithMock(db, db_method)
        db_exception = kwargs.pop('db_exception', None)
        if db_exception:
            getattr(db, db_method)(self.context, *args, **kwargs).AndRaise(
                db_exception)
        else:
            getattr(db, db_method)(self.context, *args, **kwargs).AndReturn(
                fake_service)
        self.mox.ReplayAll()
        obj = getattr(service.Service, obj_method)(self.context, *args,
                                                   **kwargs)
        if db_exception:
            self.assertIsNone(obj)
        else:
            self.compare_obj(obj, fake_service, allow_missing=OPTIONAL)

    def test_get_by_id(self):
        self._test_query('service_get', 'get_by_id', 123)

    def test_get_by_host_and_topic(self):
        self._test_query('service_get_by_host_and_topic',
                         'get_by_host_and_topic', 'fake-host', 'fake-topic')

    def test_get_by_host_and_binary(self):
        self._test_query('service_get_by_host_and_binary',
                         'get_by_host_and_binary', 'fake-host', 'fake-binary')

    def test_get_by_host_and_binary_raises(self):
        self._test_query('service_get_by_host_and_binary',
                         'get_by_host_and_binary', 'fake-host', 'fake-binary',
                         db_exception=exception.HostBinaryNotFound(
                             host='fake-host', binary='fake-binary'))

    def test_get_by_compute_host(self):
        self._test_query('service_get_by_compute_host', 'get_by_compute_host',
                         'fake-host')

    def test_get_by_args(self):
        self._test_query('service_get_by_host_and_binary', 'get_by_args',
                         'fake-host', 'fake-binary')

    def test_create(self):
        self.mox.StubOutWithMock(db, 'service_create')
        db.service_create(self.context, {'host': 'fake-host'}).AndReturn(
            fake_service)
        self.mox.ReplayAll()
        service_obj = service.Service(context=self.context)
        service_obj.host = 'fake-host'
        service_obj.create()
        self.assertEqual(fake_service['id'], service_obj.id)

    def test_recreate_fails(self):
        self.mox.StubOutWithMock(db, 'service_create')
        db.service_create(self.context, {'host': 'fake-host'}).AndReturn(
            fake_service)
        self.mox.ReplayAll()
        service_obj = service.Service(context=self.context)
        service_obj.host = 'fake-host'
        service_obj.create()
        self.assertRaises(exception.ObjectActionError, service_obj.create)

    def test_save(self):
        self.mox.StubOutWithMock(db, 'service_update')
        db.service_update(self.context, 123, {'host': 'fake-host'}).AndReturn(
            fake_service)
        self.mox.ReplayAll()
        service_obj = service.Service(context=self.context)
        service_obj.id = 123
        service_obj.host = 'fake-host'
        service_obj.save()

    @mock.patch.object(db, 'service_create',
                       return_value=fake_service)
    def test_set_id_failure(self, db_mock):
        service_obj = service.Service(context=self.context)
        service_obj.create()
        self.assertRaises(exception.ReadOnlyFieldError, setattr,
                          service_obj, 'id', 124)

    def _test_destroy(self):
        self.mox.StubOutWithMock(db, 'service_destroy')
        db.service_destroy(self.context, 123)
        self.mox.ReplayAll()
        service_obj = service.Service(context=self.context)
        service_obj.id = 123
        service_obj.destroy()

    def test_destroy(self):
        # The test harness needs db.service_destroy to work,
        # so avoid leaving it broken here after we're done
        orig_service_destroy = db.service_destroy
        try:
            self._test_destroy()
        finally:
            db.service_destroy = orig_service_destroy

    def test_get_by_topic(self):
        self.mox.StubOutWithMock(db, 'service_get_all_by_topic')
        db.service_get_all_by_topic(self.context, 'fake-topic').AndReturn(
            [fake_service])
        self.mox.ReplayAll()
        services = service.ServiceList.get_by_topic(self.context, 'fake-topic')
        self.assertEqual(1, len(services))
        self.compare_obj(services[0], fake_service, allow_missing=OPTIONAL)

    @mock.patch('nova.db.service_get_all_by_binary')
    def test_get_by_binary(self, mock_get):
        mock_get.return_value = [fake_service]
        services = service.ServiceList.get_by_binary(self.context,
                                                     'fake-binary')
        self.assertEqual(1, len(services))
        mock_get.assert_called_once_with(self.context, 'fake-binary')

    def test_get_by_host(self):
        self.mox.StubOutWithMock(db, 'service_get_all_by_host')
        db.service_get_all_by_host(self.context, 'fake-host').AndReturn(
            [fake_service])
        self.mox.ReplayAll()
        services = service.ServiceList.get_by_host(self.context, 'fake-host')
        self.assertEqual(1, len(services))
        self.compare_obj(services[0], fake_service, allow_missing=OPTIONAL)

    def test_get_all(self):
        self.mox.StubOutWithMock(db, 'service_get_all')
        db.service_get_all(self.context, disabled=False).AndReturn(
            [fake_service])
        self.mox.ReplayAll()
        services = service.ServiceList.get_all(self.context, disabled=False)
        self.assertEqual(1, len(services))
        self.compare_obj(services[0], fake_service, allow_missing=OPTIONAL)

    def test_get_all_with_az(self):
        self.mox.StubOutWithMock(db, 'service_get_all')
        self.mox.StubOutWithMock(aggregate.AggregateList,
                                 'get_by_metadata_key')
        db.service_get_all(self.context, disabled=None).AndReturn(
            [dict(fake_service, topic='compute')])
        agg = aggregate.Aggregate(context=self.context)
        agg.name = 'foo'
        agg.metadata = {'availability_zone': 'test-az'}
        agg.create()
        agg.hosts = [fake_service['host']]
        aggregate.AggregateList.get_by_metadata_key(self.context,
            'availability_zone', hosts=set(agg.hosts)).AndReturn([agg])
        self.mox.ReplayAll()
        services = service.ServiceList.get_all(self.context, set_zones=True)
        self.assertEqual(1, len(services))
        self.assertEqual('test-az', services[0].availability_zone)

    def test_compute_node(self):
        fake_compute_node = objects.ComputeNode._from_db_object(
            self.context, objects.ComputeNode(),
            test_compute_node.fake_compute_node)
        self.mox.StubOutWithMock(objects.ComputeNodeList, 'get_all_by_host')
        objects.ComputeNodeList.get_all_by_host(
            self.context, 'fake-host').AndReturn(
                [fake_compute_node])
        self.mox.ReplayAll()
        service_obj = service.Service(id=123, host="fake-host",
                                      binary="nova-compute")
        service_obj._context = self.context
        self.assertEqual(service_obj.compute_node,
                         fake_compute_node)
        # Make sure it doesn't re-fetch this
        service_obj.compute_node

    def test_load_when_orphaned(self):
        service_obj = service.Service()
        service_obj.id = 123
        self.assertRaises(exception.OrphanedObjectError,
                          getattr, service_obj, 'compute_node')

    @mock.patch.object(objects.ComputeNodeList, 'get_all_by_host')
    def test_obj_make_compatible_for_compute_node(self, get_all_by_host):
        service_obj = objects.Service(context=self.context)
        fake_service_dict = fake_service.copy()
        fake_compute_obj = objects.ComputeNode(host=fake_service['host'])
        get_all_by_host.return_value = [fake_compute_obj]

        service_obj.obj_make_compatible(fake_service_dict, '1.9')
        self.assertEqual(
            fake_compute_obj.obj_to_primitive(target_version='1.10'),
            fake_service_dict['compute_node'])

    @mock.patch.object(objects.ComputeNodeList, 'get_all_by_host')
    def test_obj_make_compatible_with_juno_computes(self, get_all_by_host):
        service_obj = objects.Service(
            context=self.context, **fake_service)
        service_obj.binary = 'nova-compute'
        fake_service_dict = fake_service.copy()
        fake_service_dict['binary'] = 'nova-compute'
        fake_compute_obj = objects.ComputeNode(host=fake_service['host'])
        get_all_by_host.return_value = [fake_compute_obj]

        # Juno versions :
        #   Service : 1.4
        #   ComputeNode : 1.5
        service_obj.obj_make_compatible(fake_service_dict, '1.4')
        self.assertEqual(
            '1.5',
            fake_service_dict['compute_node']['nova_object.version'])


class TestServiceObject(test_objects._LocalTest,
                        _TestServiceObject):
    pass


class TestRemoteServiceObject(test_objects._RemoteTest,
                              _TestServiceObject):
    pass
