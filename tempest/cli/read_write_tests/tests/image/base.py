from tempest import cli
from tempest.cli import read_write_tests
from tempest import config
from tempest.openstack.common import log as logging

from tempest.cli.read_write_tests.cli_services import glance_client

CONF = config.CONF

class ClientTestBase(read_write_tests.ClientTestBase):

    @classmethod
    def setUpClass(cls):
        super(ClientTestBase, cls).setUpClass()
        cls.client = cls.glance_client = glance_client.BaseGlanceClient()
        cls.images = []

    @classmethod
    def tearDownClass(cls):
        for image in cls.images:
            cls.client.delete_image(image)
        super(ClientTestBase, cls).tearDownClass()

    @classmethod
    def create_image(cls, name, disk_format, container_format, **kwargs):
        cls.result = cls.client.create_image(name, disk_format, container_format, **kwargs)
        image_id = cls.result["image"]["id"]
        cls.images.append(image_id)
        return cls.result









