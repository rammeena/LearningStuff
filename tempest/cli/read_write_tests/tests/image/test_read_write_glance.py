import logging
import re
import testtools

from tempest import config
from tempest.cli.read_write_tests.tests.image import base
from tempest.common.utils import data_utils


CONF = config.CONF
LOG = logging.getLogger(__name__)


class GlanceClientWriteTest(base.ClientTestBase):
    """Tests for Nova CLI client."""

    @classmethod
    def setUpClass(cls):
        if not CONF.service_available.glance:
            msg = ("%s skipped as Glance is not available" % cls.__name__)
            raise cls.skipException(msg)
        super(GlanceClientWriteTest, cls).setUpClass()

        name = data_utils.rand_name('Image')
        cls.file_loc = '/home/raies/cirros-0.3.1-x86_64-disk.img'
        cls.image = cls.create_image(name, disk_format="aki",
                                     container_format="aki",
                                     file=cls.file_loc)
        cls.image_id = cls.image["image"]["id"]
        cls.client.wait_for_image_status(cls.image_id, 'active')
    
    def test_create_image(self):
        name = data_utils.rand_name('Image')
        image = self.create_image(name, disk_format="aki",
                                  container_format="aki",
                                  file=self.file_loc)
        image_id = image["image"]["id"]
        self.client.wait_for_image_status(image_id, 'active')

    def test_list_images(self):
        result = self.client.list_images()
        images= result["images"]
        found = any([i for i in images if i['ID'] == self.image_id])
        self.assertTrue(found)

    def test_get_image(self):
        result = self.client.get_image(self.image_id)
        for key in ['id', 'name']:
            self.assertEqual(result["image"][key], self.image["image"][key])
