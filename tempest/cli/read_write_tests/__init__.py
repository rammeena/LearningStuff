from tempest import cli
from tempest import config
from tempest.openstack.common import log as logging

CONF = config.CONF

class ClientTestBase(cli.ClientTestBase):

    def _param_evaluate(self, flag_list, params_list, module):
        """Evaluate param and flags based on client"""
        flags = ''
        params = ''
        if flag_list:
            for flag in flag_list:
                flags += str(flag) + ' '
        if module != "keystone":
            if module in ["compute", "network", "volume", "sahara"]:
                flags += ' --endpoint-type %s' % getattr(CONF, module).endpoint_type
            else:
                flags += ' --os-endpoint-type %s' % getattr(CONF, module).endpoint_type


        if params_list:
            for param in params_list:
                params += str(param) + ' '
        return flags, params

    def cinder(self, action, flag_list=None, params_list=None, admin=True, fail_ok=False):
        """Executes cinder command for the given action."""
        flags, params = self._param_evaluate(flag_list, params_list, module="volume")
        return self.cmd_with_auth('cinder', action, flags, params, admin, fail_ok)

    def nova(self, action, flag_list=None, params_list=None, admin=True, fail_ok=False):
        """Executes nova command for the given action."""
        flags, params = self._param_evaluate(flag_list, params_list, module="compute")

        return self.cmd_with_auth('nova', action, flags, params, admin, fail_ok=False)

    def keystone(
        self,
        action,
        flag_list=None,
        params_list=None,
        admin=True,
        fail_ok=False
    ):
        """Executes keystone command for the given action."""
        flags, params = self._param_evaluate(flag_list, params_list, module="keystone")
        return self.cmd_with_auth('keystone', action, flags, params, admin, fail_ok)

    def glance(self, action, flag_list=None, params_list=None, admin=True, fail_ok=False):
        """Executes glance command for the given action."""
        flags, params = self._param_evaluate(flag_list, params_list, module="image")
        return self.cmd_with_auth('glance', action, flags, params, admin, fail_ok)

    def ceilometer(
        self,
        action,
        flag_list=None,
        params_list=None,
        admin=True,
        fail_ok=False
    ):
        """Executes ceilometer command for the given action."""
        flags, params = self._param_evaluate(flag_list, params_list, module="telemetry")
        return self.cmd_with_auth('ceilometer', action, flags, params, admin, fail_ok)

    def neutron(
        self,
        action,
        flag_list=None,
        params_list=None,
        admin=True,
        fail_ok=False
    ):
        """Executes neutron command for the given action."""
        flags, params = self._param_evaluate(flag_list, params_list, module="network")
        return self.cmd_with_auth('neutron', action, flags, params, admin, fail_ok)
