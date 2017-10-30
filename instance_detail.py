from rally import consts
from rally.plugins.openstack import scenario
from rally.plugins.openstack.scenarios.nova import utils as nova_utils
from rally.task import types
from rally.task import validation

"""Scenario for Nipa.Cloud Instance's Service."""

@types.convert(image={"type": "glance_image"},
               flavor={"type": "nova_flavor"},
               to_flavor={"type": "nova_flavor"})
@validation.add("image_valid_on_flavor", flavor_param="flavor",
                image_param="image")
@validation.add("required_services", services=(consts.Service.NOVA))
@validation.add("required_platform", platform="openstack", users=True)
@scenario.configure(context={"cleanup@openstack": ["nova"]},
                    name="NipaCloud.resize_instance", platform="openstack")
class ResizeInstance(nova_utils.NovaScenario):

    def run(self, image, flavor, to_flavor, confirm=True, force_delete=False):
        """Boot a server, then resize and delete it.

        This test will confirm the resize by default,
        or revert the resize if confirm is set to false.

        :param image: image to be used to boot an instance
        :param flavor: flavor to be used to boot an instance
        :param to_flavor: flavor to be used to resize the booted instance
        :param force_delete: True if force_delete should be used
        :param kwargs: Optional additional arguments for server creation
        """
        server = self._boot_server(image, flavor)
        self._stop_server(server)
        self._resize(server, to_flavor)
        if confirm:
            self._resize_confirm(server, "SHUTOFF")
        else:
            self._resize_revert(server, "SHUTOFF")
        self._boot_server(image, flavor)
        self._delete_server(server, force=force_delete)


@types.convert(image={"type": "glance_image"},
               flavor={"type": "nova_flavor"})
@validation.add("image_valid_on_flavor", flavor_param="flavor",
                image_param="image")
@validation.add("required_services", services=(consts.Service.NOVA))
@validation.add("required_platform", platform="openstack", users=True)
@scenario.configure(context={"cleanup@openstack": ["nova"]},
                    name="NipaCloud.power_off_instance", platform="openstack")
class PowerOffInstance(nova_utils.NovaScenario):

    def run(self, image, flavor, force_delete=False):
        server = self._boot_server(image, flavor)
        self._stop_server(server)
        self._start_server(server)
        self._delete_server(server, force=force_delete)


@types.convert(image={"type": "glance_image"},
               flavor={"type": "nova_flavor"})
@validation.add("image_valid_on_flavor", flavor_param="flavor",
                image_param="image")
@validation.add("required_services", services=(consts.Service.NOVA))
@validation.add("required_platform", platform="openstack", users=True)
@scenario.configure(context={"cleanup@openstack": ["nova"]},
                    name="NipaCloud.soft_reboot_instance", platform="openstack")
class SoftRebootInstance(nova_utils.NovaScenario):

    def run(self, image, flavor, force_delete=False):
        server = self._boot_server(image, flavor)
        self._soft_reboot_server(server)
        self._delete_server(server, force=force_delete)


@types.convert(image={"type": "glance_image"},
               flavor={"type": "nova_flavor"})
@validation.add("image_valid_on_flavor", flavor_param="flavor",
                image_param="image")
@validation.add("required_services", services=(consts.Service.NOVA))
@validation.add("required_platform", platform="openstack", users=True)
@scenario.configure(context={"cleanup@openstack": ["nova"]},
                    name="NipaCloud.hard_reboot_instance", platform="openstack")
class HardRebootInstance(nova_utils.NovaScenario):

    def run(self, image, flavor, force_delete=False): 
        server = self._boot_server(image, flavor)
        self._reboot_server(server)
        self._delete_server(server, force=force_delete)


@types.convert(image={"type": "glance_image"},
               flavor={"type": "nova_flavor"})
@validation.add("image_valid_on_flavor", flavor_param="flavor",
                image_param="image")
@validation.add("required_services", services=(consts.Service.NOVA))
@validation.add("required_platform", platform="openstack", users=True)
@scenario.configure(context={"cleanup@openstack": ["nova"]},
                    name="NipaCloud.destroy_instance", platform="openstack")
class DestroyInstance(nova_utils.NovaScenario):
    def run(self, image, flavor):
        server = self._boot_server(image, flavor)
        self._delete_server(server, force=True)