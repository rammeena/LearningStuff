import testtools

from tempest.cli.read_write_tests.tests.ceilometer import base
from tempest import config
from tempest import test

CONF = config.CONF


class TelemetryNotificationCLITest(base.ClientTestBase):

    @classmethod
    def setUpClass(cls):
        if CONF.telemetry.too_slow_to_test:
            raise cls.skipException("Ceilometer feature for fast work mysql "
                                    "is disabled")
        super(TelemetryNotificationCLITest, cls).setUpClass()

    @testtools.skipIf(not CONF.service_available.nova,
                      "Nova is not available.")
    def test_check_nova_notification(self):

        body = self.create_server()
        query = "resource=%s" % body["server"]["id"]
        for metric in self.nova_notifications:
            self.await_samples(metric, query)
