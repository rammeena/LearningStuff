import logging
import re
import testtools

from tempest import config
from tempest.cli.read_write_tests.tests.identity import base
from tempest.common.utils import data_utils

CONF = config.CONF
LOG = logging.getLogger(__name__)

class KeystoneClientWriteTest(base.ClientTestBase):
    """Tests for Keystone CLI client."""

    @classmethod
    def setUpClass(cls):
        super(KeystoneClientWriteTest, cls).setUpClass()
        cls.user = cls.create_user()
        cls.role = cls.create_role()
        cls.tenant = cls.create_tenant()
    
    def _delete_user(self, user_id):
        # deletes a given user if it exists
        users = self.client.list_users()["users"]
        found = any([i for i in users if i['id'] == user_id])
        if found:
            self.client.delete_user(user_id)
        else:
            LOG.info('Given user has already been deleted')

    def _delete_role(self, role_id):
        # deletes a given role if it exists
        roles = self.client.list_roles()["roles"]
        found = any([i for i in roles if i['id'] == role_id])
        if found:
            self.client.delete_role(role_id)
        else:
            LOG.info('Given role has already been deleted')

    def _delete_tenant(self, tenant_id):
        # deletes a given tenant if it exists
        tenants = self.client.list_tenants()["tenants"]
        found = any([i for i in tenants if i['id'] == tenant_id])
        if found:
            self.client.delete_tenant(tenant_id)
        else:
            LOG.info('Given tenant has already been deleted')

    def test_create_list_get_update_delete_user(self):
        # Create user
        user = self.client.create_user()
        created_user = user["user"]
        self.addCleanup(self._delete_user, created_user['id'])
        # List user
        users = self.client.list_users()["users"]
        found = any([i for i in users if i['id'] == created_user['id']])
        self.assertTrue(found)
        # get user
        user = self.client.get_user(created_user['id'])
        for key in ['id', 'name']:
            self.assertEqual(user['user'][key], created_user[key])
        # update user
        self.client.update_user(created_user['id'], name='Update-User')
        user = self.client.get_user(created_user['id'])
        self.assertEqual(user['user']['name'], 'Update-User')
        # Delete user
        self.client.delete_user(created_user['id'])
        # Check if deleted user exists
        users = self.client.list_users()
        found = any([i for i in users["users"] if i['id'] == created_user['id']])
        self.assertFalse(found)

    def test_create_list_get_update_delete_role(self):
        # Create role
        created_role = self.client.create_role()["role"]
        self.addCleanup(self._delete_role, created_role['id'])
        # List role
        roles = self.client.list_roles()["roles"]
        found = any([i for i in roles if i['id'] == created_role['id']])
        self.assertTrue(found)
        # get role
        role = self.client.get_role(created_role['id'])
        for key in ['id', 'name']:
            self.assertEqual(role['role'][key], created_role[key])
        # Delete role
        self.client.delete_role(created_role['id'])
        # Check if deleted role exists
        roles = self.client.list_roles()
        found = any([i for i in roles["roles"] if i['id'] == created_role['id']])
        self.assertFalse(found)

 
    def test_create_list_get_update_delete_tenant(self):
        # Create tenant
        tenant = self.client.create_tenant()
        created_tenant = tenant["tenant"]
        self.addCleanup(self._delete_tenant, created_tenant['id'])
        # List tenant
        users = self.client.list_tenants()["tenants"]
        found = any([i for i in users if i['id'] == created_tenant['id']])
        self.assertTrue(found)
        # get tenant
        tenant = self.client.get_tenant(created_tenant['id'])
        for key in ['id', 'name']:
            self.assertEqual(tenant['tenant'][key], created_tenant[key])
        # update tenant
        self.client.update_tenant(created_tenant['id'], name='Update-tenant')
        tenant = self.client.get_tenant(created_tenant['id'])
        self.assertEqual(tenant['tenant']['name'], 'Update-tenant')
        # Delete tenant
        self.client.delete_tenant(created_tenant['id'])
        # Check if deleted tenant exists
        tenants = self.client.list_tenants()
        found = any([i for i in tenants["tenants"] if i['id'] == created_tenant['id']])
        self.assertFalse(found)
