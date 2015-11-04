import time

from tempest.common.utils import data_utils
from tempest import config
from tempest import exceptions
from tempest.openstack.common import timeutils
from tempest.cli import read_write_tests
from tempest.cli.read_write_tests.cli_services import telemetry_client
from tempest.cli.read_write_tests.cli_services import compute_client
import tempest.test

CONF = config.CONF


class ClientTestBase(read_write_tests.ClientTestBase):

    @classmethod
    def setUpClass(cls):
        super(ClientTestBase, cls).setUpClass()
        cls.servers_client = compute_client.BaseComputeClient()
        cls.client = cls.telemetry_client = telemetry_client.BaseTelemetryClient()
        cls.nova_notifications = ['memory', 'vcpus', 'disk.root.size',
                                  'disk.ephemeral.size']
        cls.server_ids = []
        cls.alarm_ids = []

    @classmethod
    def create_alarm(cls, **kwargs):
        body = cls.telemetry_client.create_alarm_thershold(
            name=data_utils.rand_name('telemetry_alarm'), **kwargs)
        cls.alarm_ids.append(body["alarm"]['alarm_id'])
        return body

    @classmethod
    def create_server(cls):
        body = cls.servers_client.create_server(
            data_utils.rand_name('ceilometer-instance'))
        cls.servers_client.wait_for_server_status(body['server']['id'], 'ACTIVE')
        cls.server_ids.append(body['server']['id'])
        return body

    @staticmethod
    def cleanup_resources(method, list_of_ids):
        for resource_id in list_of_ids:
            try:
                method(resource_id)
            except exceptions.NotFound:
                pass

    @classmethod
    def tearDownClass(cls):
        cls.cleanup_resources(cls.telemetry_client.delete_alarm, cls.alarm_ids)
        cls.cleanup_resources(cls.servers_client.delete_server, cls.server_ids)
        super(ClientTestBase, cls).tearDownClass()

    def await_samples(self, metric, query):
        """
        This method is to wait for sample to add it to database.
        There are long time delays when using Postgresql (or Mysql)
        database as ceilometer backend
        """
        timeout = CONF.compute.build_timeout
        start = timeutils.utcnow()
        while timeutils.delta_seconds(start, timeutils.utcnow()) < timeout:
            body = self.telemetry_client.list_samples(metric, query_string=query)
            if body:
                return body
            time.sleep(CONF.compute.build_interval)

        raise exceptions.TimeoutException(
            'Sample for metric:%s with query:%s has not been added to the '
            'database within %d seconds' % (metric, query,
                                            CONF.compute.build_timeout))
