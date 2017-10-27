import jsonschema

from rally.common import logging
from rally import consts
from rally.plugins import scenario 
from rally.plugins.openstack.nova import utils as nova_utils
from rally.plugins.openstack.neutron import utils as neutron_utils
from rally.task import types
from rally.task import validtion

"""step
    1. mutilple instance
    2. image
    3. flavor
    4. security group
    5. keypair
    6. floating IP"""