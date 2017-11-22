import jsonschema

from rally.common import logging
from rally import consts
from rally import exceptions as rally_exceptions
from rally.plugins.openstack import scenario
from rally.plugins.openstack.scenarios.nova import utils as nova_utils
from rally.task import types
from rally.task import validation

""" Scenarios for Nipa.Cloud Snapshot. """


@types.convert(image={"type": "glance_image"},
               flavor={"type": "nova_flavor"})
@validation.add("image_valid_on_flavor", flavor_param="flavor",
                image_param="image")
@validation.add("required_services", services=[consts.Service.NOVA,
                                               consts.Service.GLANCE])
@validation.add("required_platform", platform="openstack", users=True)
@scenario.configure(context={"cleanup@openstack": ["nova", "glance"]},
                    name="NipaCloud.take_and_delete_snapshot",
                    platform="openstack")
class TakeAndDeleteSnapshot(nova_utils.NovaScenario):

    def run(self, image, flavor, force_delete=False):
        """Boot a server, make its snapshot and delete both.

        :param image: image to be used to boot an instance
        :param flavor: flavor to be used to boot an instance
        :param force_delete: True if force_delete should be used
        :param kwargs: Optional additional arguments for server creation
        """

        server = self._boot_server(image, flavor)
        self.sleep_between(15, 15)
        image = self._create_image(server)
        self.sleep_between(15, 15)
        self._delete_server(server, force=force_delete)
        self._delete_image(image)

@types.convert(image={"type": "glance_image"},
               flavor={"type": "nova_flavor"})
@validation.add("image_valid_on_flavor", flavor_param="flavor",
                image_param="image")
@validation.add("required_services", services=[consts.Service.NOVA,
                                               consts.Service.GLANCE])
@validation.add("required_platform", platform="openstack", users=True)
@scenario.configure(context={"cleanup@openstack": ["nova", "glance"]},
                    name="NipaCloud.boot_by_snapshot",
                    platform="openstack")
class BootBySnapshot(nova_utils.NovaScenario):

    def run(self, image, flavor, force_delete=False):
        """Boot a server, make its snapshot and delete both.

        :param image: image to be used to boot an instance
        :param flavor: flavor to be used to boot an instance
        :param force_delete: True if force_delete should be used
        :param kwargs: Optional additional arguments for server creation
        """

        server = self._boot_server(image, flavor)
        self.sleep_between(15, 15)
        snapshot = self._create_image(server)
        self.sleep_between(15, 15)
        self._delete_server(server, force=force_delete)
        self.sleep_between(15, 15)
        server = self._boot_server(snapshot, flavor)
        self.sleep_between(15, 15)
        self._delete_server(server, force=force_delete)
        self._delete_image(snapshot)