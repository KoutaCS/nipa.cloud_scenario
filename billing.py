import jsonschema

from rally.common import logging
from rally import consts
from rally import exceptions as rally_exceptions
from rally.plugins.openstack import scenario
from rally.plugins.openstack.scenarios.cinder import utils as cinder_utils
from rally.plugins.openstack.scenarios.neutron import utils as neutron_utils
from rally.plugins.openstack.scenarios.nova import utils
from rally.task import types
from rally.task import validation

"""Scenario for Billing Checking""" 

LOG = logging.getLogger(__name__)

@types.convert(image={"type": "glance_image"},
               flavor={"type": "nova_flavor"})
@validation.add("image_valid_on_flavor", flavor_param="flavor",
                image_param="image")
@validation.add("required_services", services=[consts.Service.NOVA])
@validation.add("required_platform", platform="openstack", users=True)
@scenario.configure(context={"cleanup@openstack": ["nova"]},
                    name="NipaCloudBilling.no_payment",
                    platform="openstack")
class NoPayment(utils.NovaScenario):

    def run(self, image, flavor, force_delete=False):
        """Boot a server, pause and lock it, then delete it.
        :param image: image to be used to boot an instance
        :param flavor: flavor to be used to boot an instance
        :param force_delete: True if force_delete should be used
        """
        server = self._boot_server(image, flavor)
        self._pause_server(server)
        self._lock_server(server)
        self._delete_server(server, force=force_delete)


@types.convert(image={"type": "glance_image"},
               flavor={"type": "nova_flavor"})
@validation.add("image_valid_on_flavor", flavor_param="flavor",
                image_param="image")
@validation.add("required_services", services=[consts.Service.NOVA])
@validation.add("required_platform", platform="openstack", users=True)
@scenario.configure(context={"cleanup@openstack": ["nova"]},
                    name="NipaCloudBilling.continue_payment",
                    platform="openstack")
class ContinuePayment(utils.NovaScenario):

    def run(self, image, flavor, force_delete=False):
        """Create a server, pause, unpause and then delete it
        :param image: image to be used to boot an instance
        :param flavor: flavor to be used to boot an instance
        :param force_delete: True if force_delete should be used
        """
        server = self._boot_server(image, flavor)
        self._pause_server(server)
        self._lock_server(server)
        self._unlock_server(server)
        self._unpause_server(server)
        self._delete_server(server, force=force_delete)