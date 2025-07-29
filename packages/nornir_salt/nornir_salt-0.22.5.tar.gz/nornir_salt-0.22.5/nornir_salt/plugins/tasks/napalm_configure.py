"""
napalm_configure
################

This task plugin uses ``nornir-napalm`` ``napalm_configure`` task
to configuration commands to devices over SSH or Telnet.

``napalm_configure`` exists as part of ``nornir_salt`` repository to facilitate
per-host configuration rendering performed by SALT prior to running the task.

Dependencies:

* `nornir-napalm module <https://pypi.org/project/nornir-napalm/>`_ required

napalm_configure sample usage
=============================

Code to invoke ``napalm_configure`` task::

    from nornir import InitNornir
    from nornir_salt.plugins.tasks import napalm_configure

    nr = InitNornir(config_file="config.yaml")

    output = nr.run(
        task=napalm_configure,
        commands=["interface loopback 0", "description 'configured by script'"]
    )

napalm_configure returns
========================

Returns Nornir results object with individual tasks names set
equal to commands sent to device.

napalm_configure reference
==========================

.. autofunction:: nornir_salt.plugins.tasks.napalm_configure.napalm_configure
"""
import logging
from nornir.core.task import Result, Task
from nornir_salt.utils import cfg_form_commands
from nornir_salt.utils.pydantic_models import model_napalm_configure
from nornir_salt.utils.yangdantic import ValidateFuncArgs

try:
    from nornir_napalm.plugins.tasks import napalm_configure as nornir_napalm_configure

    HAS_NAPALM = True
except ImportError:
    HAS_NAPALM = False
    nornir_napalm_configure = None

log = logging.getLogger(__name__)


@ValidateFuncArgs(model_napalm_configure, mixins=[nornir_napalm_configure])
def napalm_configure(task: Task, config=None, **kwargs):
    """
    Nornir Task function to send configuration to devices using
    ``nornir_napalm.plugins.tasks.napalm_configure`` plugin.

    :param kwargs: any additional arguments to use with
      ``nornir_napalm.plugins.tasks.napalm_configure`` plugin
    :param config: (str or list) configuration string or list of commands to send to device
    :return result: Nornir result object with task execution results
    """
    # run sanity check
    if not HAS_NAPALM:
        return Result(
            host=task.host,
            failed=True,
            exception="No nornir_napalm found, is it installed?",
        )

    config = cfg_form_commands(task=task, config=config, multiline=True)

    # push config to device
    task.run(
        task=nornir_napalm_configure,
        configuration=config,
        name="napalm_configure",
        **kwargs
    )

    # set skip_results to True, for ResultSerializer to ignore
    # results for grouped task itself, which are usually None
    return Result(host=task.host, skip_results=True)
