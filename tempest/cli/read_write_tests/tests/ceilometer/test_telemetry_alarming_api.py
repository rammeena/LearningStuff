import testtools
import logging

from tempest.cli.read_write_tests.tests.ceilometer import base
from tempest import config
from tempest import test

CONF = config.CONF
LOG = logging.getLogger(__name__)

from tempest.common.utils import data_utils


class TelemetryAlarmingCLITest(base.ClientTestBase):

    @classmethod
    def setUpClass(cls):
        super(TelemetryAlarmingCLITest, cls).setUpClass()
        cls.alarm = cls.create_alarm(meter_name='cpu_utils',
                                     comparison_operator='gt',
                                     threshold='80.0',
                                     period='70')
        cls.alarm_id = cls.alarm['alarm']['alarm_id']

    def _delete_alarm(self, alarm_id):
        # deletes a given alarm if it exists
        alarms = self.client.list_alarms()["alarms"]
        found = any([i for i in alarms if i['Alarm ID'] == alarm_id])
        if found:
            self.client.delete_alarm(alarm_id)
        else:
            LOG.info('Given alarm has already been deleted')

    def test_alarm_list(self):
        # List alarms
        alarm_list = self.telemetry_client.list_alarms()
        # Verify created alarm in the list
        found = any([i for i in alarm_list['alarms'] if i['Alarm ID'] == self.alarm_id])
        self.assertTrue(found)

    def test_create_update_get_delete_alarm(self):
        # Create an alarm
        alarm_name = data_utils.rand_name('telemetry_alarm')
        body = self.client.create_alarm_thershold(name=alarm_name,
                                                  meter_name='cpu',
                                                  comparison_operator='gt',
                                                  threshold='90.0',
                                                  period='60')
        self.addCleanup(self._delete_alarm, body['alarm']['alarm_id'])
        self.assertEqual(alarm_name, body['alarm']['name'])
        alarm_id = body['alarm']['alarm_id']
        # Update alarm with new rule and new name
        alarm_name_new = data_utils.rand_name('telemetry-alarm-update')
        updated_body = self.client.update_alarm_threshold(alarm_id,
                                                          name=alarm_name_new,
                                                          comparison_operator='eq',
                                                          threshold='70.0',
                                                          period='80')
        self.assertEqual(alarm_name_new, updated_body['alarm']['name'])
        self.assertEqual('eq', updated_body['alarm']['comparison_operator'])

        # Get and verify details of an alarm after update
        body = self.client.get_alarm(alarm_id)
        self.assertEqual(alarm_name_new, body['alarm']['name'])
        self.assertEqual('70.0', body['alarm']['threshold'])
        self.assertEqual('80', body['alarm']['period'])
        # Delete alarm and verify if deleted
        self.client.delete_alarm(alarm_id)
        # Check if deleted alarm exists
        alarms = self.client.list_alarms()
        found = any([i for i in alarms["alarms"] if i['Alarm ID'] == alarm_id])
        self.assertFalse(found)


    @test.attr(type="gate")
    def test_set_get_alarm_state(self):
        alarm_states = ['ok', 'alarm', 'insufficient data']
        alarm = self.create_alarm(meter_name='cpu_utils',
                                  comparison_operator='gt',
                                  threshold='80.0',
                                  period='70')['alarm']
        # Set alarm state and verify
        new_state =\
            [elem for elem in alarm_states if elem != alarm['state']][0]
        state = self.client.set_alarm_state(alarm['alarm_id'], new_state)
        self.assertEqual(new_state, state['alarm']['state'])
        # Get alarm state and verify
        state = self.client.get_alarm_state(alarm['alarm_id'])
        self.assertEqual(new_state, state['alarm']['state'])
