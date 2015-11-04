import logging
import re
import testtools
import time
import os

from tempest import cli
from tempest import exceptions
from tempest.cli import read_write_tests
from tempest.cli.read_write_tests.cli_services import base
from tempest import config
from tempest.common.utils import data_utils
from tempest.common import waiters
from tempest.common.utils import misc as misc_utils


CONF = config.CONF
LOG = logging.getLogger(__name__)


class BaseTelemetryClient(read_write_tests.ClientTestBase):
    """
    Base client class
    """
    def __init__(self):
        self.service = CONF.image.catalog_type
        self.build_interval = CONF.compute.build_interval
        self.build_timeout = CONF.compute.build_timeout
        self.base = base.CliClientBase()

#################################################################################################
    def list_resources(self, query_string=None):
        """List all available resources."""
        if query_string:
            query_string = '--query ' + query_string
        resources = self.ceilometer('resource-list', params_list=[query_string])
        resources = self.base.list_table2dict(resource, "resources")
        return resources

    def list_meters(self, query_string=None):
        """List all available meters."""
        if query_string:
            query_string = '--query ' + query_string
        meters = self.ceilometer('meter-list', params_list=[query_string])
        meters = self.base.list_table2dict(resource, "meters")
        return meters

    def list_alarms(self, query_string=None):
        """List all available alarms."""
        p_list = []
        if query_string:
            query_string = '--query ' + query_string
            p_list.append[query_string]
        alarms = self.ceilometer('alarm-list', params_list=p_list)
        alarms = self.base.list_table2dict(alarms, "alarms")
        return alarms

    def list_statistics(self, meter, period=None, query_string=None):
        """List statistics for a given meter"""
        p_list = []
        p_list.append("--meter %s" % meter)
        if period:
            period = '--period ' + period
            p_list.append(period)
        if query_string:
            query_string = '--query ' + query_string
            p_list.append(query_string)
        statistics = self.ceilometer('statistics', params_list=p_list)
        statistics = self.base.list_table2dict(statistics, "statistics")
        return statistics

    def list_samples(self, meter, query_string=None):
        """List samples for a given meter."""
        p_list = []
        p_list.append("--meter %s" % meter)
        if query_string:
            query_string = '--query ' + query_string
            p_list.append(query_string)
        samples = self.ceilometer('sample-list ', params_list=p_list)
        samples = self.base.list_table2dict(samples, "samples")
        return samples

    def get_resource(self, resource_id):
        """show a given resource"""
        resource = self.ceilometer('resource-show', params_list=[resource_id])
        resource = self.base.list_table2dict(resource, "resource")
        return resource

    def get_alarm(self, alarm_id):
        """show a given alarm"""
        alarm = self.ceilometer('alarm-show', params_list=["-a %s" % alarm_id])
        alarm = self.base.create_table2dict(alarm, "alarm")
        return alarm

    def delete_alarm(self, alarm_id):
        """delete a given alarm"""
        self.ceilometer('alarm-delete', params_list=["-a %s" % alarm_id])

    def create_alarm_thershold(self, **kwargs):
        """
        Creates a thershold oriented alarm.
        """
        p_list = []
        for k,v in kwargs.iteritems():
            if "_" in k:
                k = str(k).replace("_", "-")
            item = '--' + k + ' ' + v
            p_list.append(item)
        result = self.ceilometer('alarm-threshold-create', params_list=p_list)
        result = self.base.create_table2dict(result, "alarm")
        return result

    def update_alarm_threshold(self, alarm_id, **kwargs):
        """Update a given tenant."""
        p_list = []
        for k,v in kwargs.iteritems():
            if "_" in k:
                k = str(k).replace("_", "-")
            item = '--' + k + ' ' + v
            p_list.append(item)
        alarm_id_string = "-a %s" % alarm_id
        p_list.append(alarm_id_string)
        result = self.ceilometer('alarm-update', params_list=p_list)
        result = self.base.create_table2dict(result, "alarm")
        return result

    def get_alarm_state(self, alarm_id):
        p_list = []
        alarm_id_string = "-a %s" % alarm_id
        p_list.append(alarm_id_string)
        result = self.ceilometer('alarm-state-get', params_list=p_list)
        result = self.base.create_table2dict(result, "alarm")
        return result

    def set_alarm_state(self, alarm_id, alarm_state):
        if alarm_state in ['ok', 'alarm', 'insufficient_data']:
            p_list = []
            alarm_id_string = "-a %s" % alarm_id
            alarm_state_string = "--state %s" % alarm_state
            p_list.append(alarm_id_string)
            p_list.append(alarm_state_string)
            result = self.ceilometer('alarm-state-set', params_list=p_list)
            result = self.base.create_table2dict(result, "alarm")
            return result
        else:
            raise ValueError('Wrong alarm state is passed')

    def create_sample(self, resource_id, meter_name, meter_type, meter_unit,
                      sample_volume, **kwargs):
        p_list = []
        resource_id_string = "-r %s" % resource_id
        meter_name_string = "-m %s" % meter_name
        meter_type_string = "--meter-type %s" % meter_type
        meter_type_string = "--meter-uni %s" % meter_unit
        sample_volume_string = "--sample-volume %s" % sample_volume
        for item in [resource_id_string, meter_name_string, meter_type_string,
                     meter_type_string, sample_volume_string]:
            p_list.append(item)
        for k,v in kwargs.iteritems():
            if "_" in k:
                k = str(k).replace("_", "-")
            item = '--' + k + ' ' + v
            p_list.append(item)
        result = self.ceilometer('sample-create', params_list=p_list)
        result = self.base.create_table2dict(result, "sample")
        return result
