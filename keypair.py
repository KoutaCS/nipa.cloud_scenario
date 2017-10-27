from rally.common import logging
from rally import consts
from rally.plugins.openstack import scenario
from rally.plugins.openstack.scenarios.nova import utils as nova_utils
from rally.task import types
from rally.task import validation

"""Scenarios for Nipa.Cloud Keypair."""

@validation.add("required_services", services=[consts.Service.NOVA])
@validation.add("required_platform", platform="openstack", users=True)
@scenario.configure(context={"cleanup@openstack": ["nova"]},
                    name="NipaCloud.create_and_delete_keypair",
                    platform="openstack")
class CreateAndDeleteKeypair(nova_utils.NovaScenario):

    def run(self, **kwargs):
        """Create a keypair with random name and delete keypair.

        This scenario creates a keypair and then delete that keypair.

        :param kwargs: Optional additional arguments for keypair creation
        """

        keypair = self._create_keypair(**kwargs)
        self._delete_keypair(keypair)


@types.convert(image={"type": "glance_image"},
               flavor={"type": "nova_flavor"})
@validation.add("image_valid_on_flavor", flavor_param="flavor",
                image_param="image")
@validation.add("required_services", services=[consts.Service.NOVA])
@validation.add("required_platform", platform="openstack", users=True)
@scenario.configure(context={"cleanup@openstack": ["nova"]},
                    name="NipaCloud.boot_with_keypair",
                    platform="openstack")
class BootWithKeypair(nova_utils.NovaScenario):

    @logging.log_deprecated_args(
        "'server_kwargs' has been renamed 'boot_server_kwargs'",
        "0.3.2", ["server_kwargs"], once=True)
    def run(self, image, flavor, boot_server_kwargs=None,
            server_kwargs=None, **kwargs):
        """Boot and delete server with keypair.

        Plan of this scenario:
         - create a keypair
         - boot a VM with created keypair
         - delete server
         - delete keypair

        :param image: ID of the image to be used for server creation
        :param flavor: ID of the flavor to be used for server creation
        :param boot_server_kwargs: Optional additional arguments for VM
                                   creation
        :param server_kwargs: Deprecated alias for boot_server_kwargs
        :param kwargs: Optional additional arguments for keypair creation
        """

        boot_server_kwargs = boot_server_kwargs or server_kwargs or {}

        keypair = self._create_keypair(**kwargs)
        server = self._boot_server(image, flavor,
                                   key_name=keypair,
                                   **boot_server_kwargs)
        self._delete_server(server)
        self._delete_keypair(keypair)