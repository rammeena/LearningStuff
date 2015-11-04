from tempest import config
from tempest.openstack.common import log as logging

CONF = config.CONF


def param_evaluate(module):
        """Evaluate param and flags based on client"""
#        flags = ' --endpoint-type %s' % CONF.module.endpoint_type
	flags = getattr(CONF, module).endpoint_type
        print flags
        print CONF

param_evaluate("glance")

