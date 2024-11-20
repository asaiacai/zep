"""Jobset backend for sky"""
import subprocess
import tempfile
import typing
from typing import Any, Dict, Optional, Tuple, Union

import colorama

from sky import backends
from sky import global_user_state
from sky import sky_logging
from sky.adaptors import docker
from sky.backends import backend_utils
from sky.backends import docker_utils
from sky.data import storage as storage_lib
from sky.utils import rich_utils
from sky.utils import ux_utils

if typing.TYPE_CHECKING:
    from sky import resources
    from sky import task as task_lib

Path = str

logger = sky_logging.init_logger(__name__)

class JobsetResourceHandle(str, backends.ResourceHandle):
    """The name of the cluster/container prefixed with the handle prefix."""
    pass


class JobsetBackend(backends.Backend['LocalDockerResourceHandle']):
    """A backend for running tasks with k8s jobsets
    """

    NAME = 'jobset'