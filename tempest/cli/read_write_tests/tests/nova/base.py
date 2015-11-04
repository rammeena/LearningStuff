from tempest import cli
from tempest.cli import read_write_tests
from tempest import config
from tempest.openstack.common import log as logging

from tempest.cli.read_write_tests.cli_services import compute_client

CONF = config.CONF

class ClientTestBase(read_write_tests.ClientTestBase):

    @classmethod
    def setUpClass(cls):
        super(ClientTestBase, cls).setUpClass()
        cls.client = cls.compute_client = compute_client.BaseComputeClient()
        cls.servers = []

    @classmethod
    def tearDownClass(cls):
        for server in cls.servers:
            cls.compute_client.delete_server(server)
            cls.compute_client.wait_for_server_termination(server)
        super(ClientTestBase, cls).tearDownClass()

    @classmethod
    def create_server(cls, name=None, image=None, flavor=None):
        cls.result = cls.compute_client.create_server(name=name, image=image, flavor=flavor)
        server_id = cls.result["server"]["id"]
        cls.servers.append(server_id)
        return cls.result









