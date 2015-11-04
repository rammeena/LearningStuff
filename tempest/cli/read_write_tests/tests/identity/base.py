from tempest import cli
from tempest.cli import read_write_tests
from tempest import config
from tempest.openstack.common import log as logging

from tempest.cli.read_write_tests.cli_services import keystone_client

CONF = config.CONF

class ClientTestBase(read_write_tests.ClientTestBase):

    @classmethod
    def setUpClass(cls):
        super(ClientTestBase, cls).setUpClass()
        cls.client = cls.keystone_client = keystone_client.BaseKeystoneClient()
        cls.users = []
        cls.roles = []
        cls.tenants = []

    @classmethod
    def tearDownClass(cls):
        for role in cls.roles:
            cls.keystone_client.delete_role(role)
        for user in cls.users:
            cls.keystone_client.delete_user(user)
        for tenant in cls.tenants:
            cls.keystone_client.delete_tenant(tenant)

        super(ClientTestBase, cls).tearDownClass()

    @classmethod
    def create_user(cls):
        cls.result = cls.keystone_client.create_user()
        user_id = cls.result["user"]["id"]
        cls.users.append(user_id)
        return cls.result

    @classmethod
    def create_role(cls):
        cls.result = cls.keystone_client.create_role()
        role_id = cls.result["role"]["id"]
        cls.roles.append(role_id)
        return cls.result

    @classmethod
    def create_tenant(cls):
        cls.result = cls.keystone_client.create_tenant()
        tenant_id = cls.result["tenant"]["id"]
        cls.tenants.append(tenant_id)
        return cls.result
