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
from tempest.common.utils import misc as misc_utils


CONF = config.CONF
LOG = logging.getLogger(__name__)


class BaseGlanceClient(read_write_tests.ClientTestBase):
    """
    Base client class
    """
    def __init__(self):
        self.service = CONF.image.catalog_type
        self.build_interval = CONF.compute.build_interval
        self.build_timeout = CONF.compute.build_timeout
        self.base = base.CliClientBase()

##########################################################################################
    def delete_image(self, image_id):
        self.glance('image-delete', params_list=[image_id])

    def list_images(self):
        """List all the created images."""
        image_list = self.glance('image-list')
        image_list = self.base.list_table2dict(image_list, "images")
        return image_list

    def get_image(self, image_id):
        """Returns the details of a single image."""
        image = self.glance('image-show', params_list=[image_id])
        image = self.base.create_table2dict(image, "image")
        return image

    def update_image(self, image_id, new_name=None, **kwargs):
        """Update a given tenant."""
        p_list = []
        for k,v in kwargs.iteritems():
            if "_" in k:
                k = str(k).replace("_", "-")
            item = '--' + k + ' ' + v
            p_list.append(item)
        if new_name:
            new_name = "--name %s" % new_name
        p_list.append(new_name)
        p_list.append(image_id)
        self.glance('image-update', params_list=p_list)

    def create_image(self, name, disk_format, container_format, **kwargs):
        """
        Creates a new image in glance.
        """
        p_list = []
        for k,v in kwargs.iteritems():
            if "_" in k:
                k = str(k).replace("_", "-")
            item = '--' + k + ' ' + v
            p_list.append(item)
        name = "--name %s" % name
        container_format = "--container-format %s" % container_format
        disk_format = "--disk-format %s" % disk_format
        p_list.append(disk_format)
        p_list.append(container_format)
        p_list.append(name)
        result = self.glance('image-create', params_list=p_list)
        result = self.base.create_table2dict(result, "image")
        return result

###########################################################################################
    def _get_image_status(self, image_id):
        image = self.get_image(image_id)["image"]
        status = image['status']
        return status

    def wait_for_image_status(self, image_id, status):
        """Waits for a Image to reach a given status."""
        start_time = time.time()
        old_value = value = self._get_image_status(image_id)
        while True:
            dtime = time.time() - start_time
            time.sleep(self.build_interval)
            if value != old_value:
                LOG.info('Value transition from "%s" to "%s"'
                         'in %d second(s).', old_value,
                         value, dtime)
            if value == status:
                return value

            if value == 'killed':
                raise exceptions.ImageKilledException(image_id=image_id,
                                                      status=status)
            if dtime > self.build_timeout:
                message = ('Time Limit Exceeded! (%ds)'
                           'while waiting for %s, '
                           'but we got %s.' %
                           (self.build_timeout, status, value))
                caller = misc_utils.find_test_caller()
                if caller:
                    message = '(%s) %s' % (caller, message)
                raise exceptions.TimeoutException(message)
            time.sleep(self.build_interval)
            old_value = value
            value = self._get_image_status(image_id)

    def is_resource_deleted(self, resource_id):
        try:
            self.get_image(resource_id)
        except Exception:
            return True
        return False

    def wait_for_resource_deletion(self, resource_id):
        """Waits for a resource to be deleted."""
        start_time = int(time.time())
        while True:
            if self.is_resource_deleted(resource_id):
                return
            if int(time.time()) - start_time >= self.build_timeout:
                raise exceptions.TimeoutException
            time.sleep(self.build_interval)
