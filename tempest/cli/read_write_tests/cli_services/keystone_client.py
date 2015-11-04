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


CONF = config.CONF
LOG = logging.getLogger(__name__)


class BaseKeystoneClient(read_write_tests.ClientTestBase):
    """
    Base client class
    """
    def __init__(self):
        self.base = base.CliClientBase()

#########################################################################################
################################## USER SPECIFIC ########################################
#########################################################################################
    def delete_user(self, user_id):
        self.keystone('user-delete', params_list=[user_id])

    def list_users(self):
        """List all the created users."""
        user_list = self.keystone('user-list')
        user_list = self.base.list_table2dict(user_list, "users")
        return user_list

    def get_user(self, user_id):
        """Returns the details of a single user."""
        user = self.keystone('user-get', params_list=[user_id])
        user = self.base.create_table2dict(user, "user")
        return user

    def update_user(self, user_id, **kwargs):
        """Update a given user."""
        p_list = []
        for k,v in kwargs.iteritems():
            item = '--' + k + ' ' + v
            p_list.append(item)
        p_list.append(user_id)
        self.keystone('user-update', params_list=p_list)

    def create_user(self, name=None, **kwargs):
        """
        Creates a new User.
        """
        if name is None:
            name = data_utils.rand_name("Test-User") 
        p_list = []
        for k,v in kwargs.iteritems():
            item = '--' + k + ' ' + v
            p_list.append(item)
        name_item = '--name ' + name
        p_list.append(name_item)
        result = self.keystone('user-create', params_list=p_list)
        result = self.base.create_table2dict(result, "user")
        return result
#########################################################################################
################################## ROLE SPECIFIC ########################################
#########################################################################################
    def delete_role(self, role_id):
        self.keystone('role-delete', params_list=[role_id])

    def list_roles(self):
        """List all the created roles."""
        roles_list = self.keystone('role-list')
        roles_list = self.base.list_table2dict(roles_list, "roles")
        return roles_list

    def get_role(self, role_id):
        """Returns the details of a single Role."""
        role = self.keystone('role-get', params_list=[role_id])
        role = self.base.create_table2dict(role, "role")
        return role

    def create_role(self, name=None):
        """
        Creates a new User.
        """
        if name is None:
            name = data_utils.rand_name("Test-Role") 
        result = self.keystone('role-create', params_list=["--name %s" % name])
        result = self.base.create_table2dict(result, "role")
        return result
#########################################################################################
################################# USER ROLE SPECIFIC ####################################
#########################################################################################
    def user_role_add(self, user_id, role_id, **kwargs):
        p_list = ["--user %s" % user_id, "--role %s" % role_id]
        for k,v in kwargs.iteritems():
            item = '--' + k + ' ' + v
            p_list.append(item)
        self.keystone('user-role-add', params_list=p_list)

    def user_role_list(self, **kwargs):
        # must be called as user_role_list(name=<name>, tenant=<tenant>)
        p_list = []
        for k,v in kwargs.iteritems():
            item = '--' + k + ' ' + v
            p_list.append(item)
        self.keystone('user-role-list', params_list=p_list)

    def user_role_remove(self, user_id, role_id, **kwargs):
        p_list = ["--user %" % user_id, "--role %s" % role_id,]
        for k,v in kwargs.iteritems():
            item = '--' + k + ' ' + v
            p_list.append(item)
        self.keystone('user-role-remove', params_list=p_list)
#########################################################################################
####################################### GENERIC #########################################
#########################################################################################
    def bootstrap(self, password, name="admin", role="admin", tenant="admin"):
        p_list = ["--pass %s" % password,
                  "--user-name %s" % name,
                  "--role-name %s" % role,
                  "--tenant-name %s" % role]
        self.keystone('user-role-add', params_list=p_list)
#########################################################################################
################################## TENANT SPECIFIC ######################################
#########################################################################################
    def delete_tenant(self, tenant_id):
        """Delete the given tenant."""
        self.keystone('tenant-delete', params_list=[tenant_id])

    def list_tenants(self):
        """List all the created tenants."""
        tenant_list = self.keystone('tenant-list')
        tenant_list = self.base.list_table2dict(tenant_list, "tenants")
        return tenant_list

    def get_tenant(self, tenant_id):
        """Returns the details of a single tenant."""
        tenant = self.keystone('tenant-get', params_list=[tenant_id])
        tenant = self.base.create_table2dict(tenant, "tenant")
        return tenant

    def update_tenant(self, tenant_id, **kwargs):
        """Update a given tenant."""
        p_list = []
        for k,v in kwargs.iteritems():
            item = '--' + k + ' ' + v
            p_list.append(item)
        p_list.append(tenant_id)
        self.keystone('tenant-update', params_list=p_list)

    def create_tenant(self, name=None, **kwargs):
        """
        Creates a new Tenant.
        """
        if name is None:
            name = data_utils.rand_name("Test-Tenant")
        p_list = []
        for k,v in kwargs.iteritems():
            item = '--' + k + ' ' + v
            p_list.append(item)
        name_item = '--name ' + name
        p_list.append(name_item)
        result = self.keystone('tenant-create', params_list=p_list)
        result = self.base.create_table2dict(result, "tenant")
        return result
