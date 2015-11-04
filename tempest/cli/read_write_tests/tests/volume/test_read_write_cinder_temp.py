import logging

from tempest import config
from tempest.cli.read_write_tests.tests.volume import base
from tempest.common.utils import data_utils

CONF = config.CONF
LOG = logging.getLogger(__name__)

class CinderClientWriteTest(base.ClientTestBase):
    """Tests for Cinder CLI client."""

    @classmethod
    def setUpClass(cls):
        if not CONF.service_available.cinder:
            msg = ("%s skipped as Cinder is not available" % cls.__name__)
            raise cls.skipException(msg)
        super(CinderClientWriteTest, cls).setUpClass()
        cls.name = data_utils.rand_name('Volume')
        cls.volume = cls.create_volume(cls.name, 1)
        cls.volume_id = cls.volume["volume"]["id"]
        cls.client.wait_for_volume_status(cls.volume_id, 'available')

    def test_cinder_type_create(self):
        result = self.cinder('type-list')
        print result
"""        volumes = result["volumes"]
        is_volume_exist = len([i for i in volumes if i['ID'] == volume_id and i["Status"] == 'available']) > 0
        self.assertEqual(is_volume_exist, True)
"""
  
"""    def _verify_volume_created(self, volume_id):
        result = self.client.list_volumes()
        volumes = result["volumes"]
        is_volume_exist = len([i for i in volumes if i['ID'] == volume_id and i["Status"] == 'available']) > 0
        self.assertEqual(is_volume_exist, True)

    def test_create_volume(self):
        name = data_utils.rand_name('Volume')
        volume = self.create_volume(name, 1)
        volume_id = volume["volume"]["id"]
        self.client.wait_for_volume_status(volume_id, 'available')
        self._verify_volume_created(volume_id)

    def test_list_volumes(self):
        result = self.client.list_volumes()
        volumes = result["volumes"]
        is_volume_exist = len([i for i in volumes if i['ID'] == self.volume_id]) > 0
        self.assertEqual(is_volume_exist, True)

    def test_get_volume(self):
        result = self.client.get_volume(self.volume_id)
        for key in ['id', 'name', 'availability_zone']:
            self.assertEqual(result["volume"][key], self.volume["volume"][key])

    def test_rename_volume(self):
        name = data_utils.rand_name('Volume')
        volume = self.create_volume(name, 1)
        volume_id = volume["volume"]["id"]
        self.client.wait_for_volume_status(volume_id, 'available')

        new_name = data_utils.rand_name('Volume')
        self.client.rename_volume(volume_id, new_name)
        result = self.client.get_volume(volume_id)

        self.assertEqual(result["volume"]["name"], new_name)
"""
