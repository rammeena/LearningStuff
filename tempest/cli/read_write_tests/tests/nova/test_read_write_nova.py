import logging
import re
import testtools

from tempest import config
from tempest.cli import read_write_tests
from tempest.cli.read_write_tests.tests.nova import base
from tempest.common.utils import data_utils


CONF = config.CONF
LOG = logging.getLogger(__name__)


class NovaClientWriteTest(base.ClientTestBase):
    """Tests for Nova CLI client."""

    @classmethod
    def setUpClass(cls):
        if not CONF.service_available.nova:
            msg = ("%s skipped as Compute is not available" % cls.__name__)
            raise cls.skipException(msg)
        super(NovaClientWriteTest, cls).setUpClass()

        cls.name = data_utils.rand_name('Server')
        cls.image = CONF.compute.image_ref
        cls.server = cls.create_server(name=cls.name, image=cls.image)
        cls.server_id = cls.server["server"]["id"]
        cls.client.wait_for_server_status(cls.server_id, 'ACTIVE')
    
    def test_create_server(self):
        name = data_utils.rand_name('Server')
        server = self.create_server()
        server_id = server["server"]["id"]
        self.client.wait_for_server_status(server_id, 'ACTIVE')

    def test_list_servers(self):
        result = self.client.list_servers()
        servers= result["servers"]
        found = any([i for i in servers if i['ID'] == self.server_id])
        self.assertTrue(found)

    def test_list_servers_with_given_status(self):
        status = "ACTIVE"
        result = self.client.list_servers(status=status)
        servers= result["servers"]
        found = any([i for i in servers if i['ID'] == self.server_id])
        self.assertTrue(found)
        self.assertEqual(status, [i['Status'] for i in servers if i['ID'] == self.server_id][-1])

    def test_list_servers_with_given_flavor(self):
        flavor_id = CONF.compute.flavor_ref
        result = self.client.list_servers(flavor=flavor_id)
        servers= result["servers"]
        found = any([i for i in servers if i['ID'] == self.server_id])
        self.assertTrue(found)

    def test_list_servers_with_given_name_regex(self):
        name_regex = "Server-*" 
        result = self.client.list_servers(name=name_regex)
        servers= result["servers"]
        found = any([i for i in servers if i['ID'] == self.server_id])
        self.assertTrue(found)
        self.assertEqual(self.name, [i['Name'] for i in servers if i['ID'] == self.server_id][-1])

    def test_list_servers_with_given_image(self):
        image = CONF.compute.image_ref
        result = self.client.list_servers(image=image)
        servers= result["servers"]
        found = any([i for i in servers if i['ID'] == self.server_id])
        self.assertTrue(found)

    def test_list_minimal(self):
        servers = self.client.list_servers_minimal()['servers']
        found = any([i for i in servers if i['ID'] == self.server_id])

    def test_list_servers_filtered_with_a_given_tenant(self):
        tenant = "admin" 
        result = self.client.list_servers(tenant=tenant)
        servers= result["servers"]
        found = any([i for i in servers if i['ID'] == self.server_id])
        self.assertTrue(found)

    def test_server_meta_set_delete(self):
        # Create a server
        name = data_utils.rand_name('Server')
        image = CONF.compute.image_ref
        server = self.create_server(name=name, image=image)
        server_id = server['server']['id']
        self.client.wait_for_server_status(server_id, 'ACTIVE')
        # Set metadata
        self.client.server_meta_set(server_id, new_meta="server_meta")
        # verify metadata set
        result = self.client.get_server(server_id)['server']
        output_metadata = result['metadata']
        self.assertIn("server_meta", output_metadata)
        # Delete set metadata
        self.client.server_meta_delete(server_id, key="new_meta")
        # verify metadata delete
        result = self.client.get_server(server_id)['server']
        output_metadata = result['metadata']
        self.assertNotIn("new_meta", output_metadata)

    def test_get_server(self):
        result = self.client.get_server(self.server_id)
        for key in ['id', 'name', 'user_id']:
            self.assertEqual(result["server"][key], self.server["server"][key])

    def test_rename_server(self):
        # Create a server
        name = data_utils.rand_name('Server')
        server = self.create_server()
        server_id = server["server"]["id"]
        self.client.wait_for_server_status(server_id, 'ACTIVE')
        # Rename server
        new_name = data_utils.rand_name('Server')
        self.client.rename_server(server_id, new_name)
        # Validate rename
        updated_server = self.client.get_server(server_id)
        self.assertEqual(updated_server["server"]["name"], new_name)
