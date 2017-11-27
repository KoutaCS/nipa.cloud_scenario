import jsonschema

from rally.common import logging
from rally import consts
from rally import exceptions as rally_exceptions
from rally.plugins.openstack import scenario
from rally.plugins.openstack.scenarios.nova import utils as nova_utils
from rally.task import types
from rally.task import validation

"""Scenario for Billing Checking page""" 

LOG = logging.getLogger(__name__)

@types.convert(image={"type": "glance_image"},
               flavor={"type": "nova_flavor"})
@validation.add("image_valid_on_flavor", flavor_param="flavor",
                image_param="image")
@validation.add("required_services", services=[consts.Service.NOVA])
@validation.add("required_platform", platform="openstack", users=True)
@scenario.configure(context={"cleanup@openstack": ["nova"]},
                    name="NipaCloud.billing_no_payment",
                    platform="openstack")
class BillingNoPayment(nova_utils.NovaScenario):

    def run(self, image, flavor, force_delete=False):
        """Boot a server, pause and lock it, unlock then delete it.
        :param image: image to be used to boot an instance
        :param flavor: flavor to be used to boot an instance
        :param force_delete: True if force_delete should be used
        """
        server = self._boot_server(image, flavor)
        self.sleep_between(5, 5)
        self._pause_server(server)
        self.sleep_between(5, 5)
        self._lock_server(server)
        self.sleep_between(5, 5)
        self._unlock_server(server)
        self.sleep_between(5, 5)
        self._delete_server(server, force=force_delete)


@types.convert(image={"type": "glance_image"},
               flavor={"type": "nova_flavor"})
@validation.add("image_valid_on_flavor", flavor_param="flavor",
                image_param="image")
@validation.add("required_services", services=[consts.Service.NOVA])
@validation.add("required_platform", platform="openstack", users=True)
@scenario.configure(context={"cleanup@openstack": ["nova"]},
                    name="NipaCloud.billing_continue_payment",
                    platform="openstack")
class BillingContinuePayment(nova_utils.NovaScenario):

    def run(self, image, flavor, force_delete=False):
        """Create a server, pause, unpause and then delete it
        :param image: image to be used to boot an instance
        :param flavor: flavor to be used to boot an instance
        :param force_delete: True if force_delete should be used
        """
        server = self._boot_server(image, flavor)
        self.sleep_between(5, 5)
        self._pause_server(server)
        self.sleep_between(5, 5)
        self._lock_server(server)
        self.sleep_between(5, 5)
        self._unlock_server(server)
        self.sleep_between(5, 5)
        self._unpause_server(server)
        self.sleep_between(5, 5)
        self._delete_server(server, force=force_delete)