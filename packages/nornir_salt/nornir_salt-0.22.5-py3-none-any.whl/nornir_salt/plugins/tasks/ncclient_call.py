"""
ncclient_call
#############

`Ncclient <https://github.com/ncclient>`_ is a popular library to interact with
devices using NETCONF, this plugin is a wrapper around ncclient connection
manager object.

NETCONF protocol has a specific set of RPC calls available for use, rather
than coding separate task for each of them, ``ncclient_call`` made to execute
any arbitrary method supported by manager object plus a set of additional
helper methods to extend Ncclient library functionality.

ncclient_call sample usage
==========================

Sample code to run ``ncclient_call`` task::

    from nornir import InitNornir
    from nornir_salt.plugins.tasks import ncclient_call

    nr = InitNornir(config_file="config.yaml")

    output = nr.run(
        task=ncclient_call,
        call="get_config",
        source="running"
    )

ncclient_call returns
=====================

Returns XML text string by default, but can return XML data transformed
in JSON, YAML or Python format.

ncclient_call reference
=======================

.. autofunction:: nornir_salt.plugins.tasks.ncclient_call.ncclient_call

additional methods reference
============================

ncclient_call - dir
-------------------
.. autofunction:: nornir_salt.plugins.tasks.ncclient_call._call_dir

ncclient_call - help
--------------------
.. autofunction:: nornir_salt.plugins.tasks.ncclient_call._call_help

ncclient_call - server_capabilities
-----------------------------------

.. autofunction:: nornir_salt.plugins.tasks.ncclient_call._call_server_capabilities

ncclient_call - connected
-------------------------

.. autofunction:: nornir_salt.plugins.tasks.ncclient_call._call_connected

ncclient_call - transaction
---------------------------

.. autofunction:: nornir_salt.plugins.tasks.ncclient_call._call_transaction
"""
import traceback
import logging
import time

from fnmatch import fnmatchcase
from nornir.core.task import Result, Task
from nornir_salt.plugins.connections.NcclientPlugin import CONNECTION_NAME
from nornir_salt.utils.pydantic_models import model_ncclient_call
from nornir_salt.utils.yangdantic import ValidateFuncArgs

log = logging.getLogger(__name__)

try:
    import lxml.etree as etree  # nosec

    HAS_LXML = True
except ImportError:
    HAS_LXML = False

try:
    from ncclient.manager import OPERATIONS

    HAS_NCCLIENT = True
except ImportError:
    HAS_NCCLIENT = False

try:
    # this import should work for ncclient >=0.6.10
    from ncclient.operations import GenericRPC

except ImportError:
    # for ncclient<0.6.10 need to reconstruct GenericRPC class
    if HAS_NCCLIENT:

        from ncclient.operations import RPC

        class GenericRPC(RPC):
            def request(self, data, *args, **kwargs):
                """
                :param data: (str) rpc xml string

                Testing:

                * Arista cEOS - not working, transport session closed error
                * Cisco IOS-XR - working
                """
                ele = etree.fromstring(data.encode("UTF-8"))  # nosec
                return self._request(ele)


def _form_result(result) -> str:
    """
    Helper function to extract XML string results from Ncclient
    response.

    :param result: (obj) Ncclient RPC call result object
    """
    if hasattr(result, "_root"):
        result = etree.tostring(result._root, pretty_print=True).decode()
    elif isinstance(result, (list, dict, bool)):
        pass
    else:
        result = str(result)

    return result


def _call_transaction(manager, *args, **kwargs):
    """
    Function to edit device configuration in a reliable fashion using
    capabilities advertised by NETCONF server.

    :param target: (str) name of datastore to edit configuration for, if no
        ``target`` argument provided and device supports candidate datastore uses
        ``candidate`` datastore, uses ``running`` datastore otherwise
    :param config: (str) configuration to apply
    :param confirmed: (bool) if True (default) uses commit confirmed
    :param commit_final_delay: (int) time to wait before doing final commit after
        commit confirmed, default is 1 second
    :param confirm_delay: (int) device commit confirmed rollback delay, default 60 seconds
    :param validate: (bool) if True (default) validates candidate configuration before commit
    :param edit_rpc: (str) name of edit configuration RPC, options are - "edit_config"
        (default), "load_configuration" (juniper devices only)
    :param edit_arg: (dict) dictionary of arguments to use with configuration edit RPC
    :param commit_arg: (dict) dictionary of commit RPC arguments used with first commit call
    :returns result: (list) list of steps performed with details

    Function work flow:

    1. Lock target configuration datastore
    2. If server supports it - Discard previous changes if any
    3. Perform configuration edit using RPC specified in ``edit_rpc`` argument
    4. If server supports it - validate configuration if ``validate`` argument is True
    5. Do commit operation:

        1. If server supports it - do commit operation if ``confirmed`` argument is False
        2. If server supports it - do commit confirmed if ``confirmed`` argument is True
           using ``confirm_delay`` timer with ``commit_arg`` argument
        3. If confirmed commit requested, wait for ``commit_final_delay`` timer before
           sending final commit, final commit does not use ``commit_arg`` arguments

    6. Unlock target configuration datastore
    7. If server supports it - discard all changes if any of steps 3, 4, 5 or 7 fail
    8. Return results list of dictionaries keyed by step name
    """
    result = []
    failed = False
    edit_rpc = kwargs.get("edit_rpc", "edit_config")
    commit_arg = kwargs.get("commit_arg", {})
    commit_final_delay = int(kwargs.get("commit_final_delay", 1))

    # ncclient expects timeout to be a string
    confirm_delay = str(kwargs.get("confirm_delay", 60))

    # get capabilities
    can_validate = ":validate" in manager.server_capabilities
    can_commit_confirmed = ":confirmed-commit" in manager.server_capabilities
    has_candidate_datastore = ":candidate" in manager.server_capabilities

    # decide on target configuration datastore
    target = kwargs.get("target", "candidate" if has_candidate_datastore else "running")

    # form edit RPC arguments
    edit_arg = kwargs.get("edit_arg", {})
    edit_arg["config"] = kwargs["config"]
    edit_arg["target"] = target

    # execute transaction
    with manager.locked(target=target):
        if has_candidate_datastore and target == "candidate":
            r = manager.discard_changes()
            result.append({"discard_changes": _form_result(r)})
        try:
            r = getattr(manager, edit_rpc)(**edit_arg)
            result.append({edit_rpc: _form_result(r)})
            # validate configuration
            if can_validate and kwargs.get("validate", True):
                r = manager.validate(source=target)
                result.append({"validate": _form_result(r)})
            if target == "candidate" and has_candidate_datastore:
                # run commit confirmed
                if can_commit_confirmed and kwargs.get("confirmed", True):
                    commit_arg["confirmed"] = True
                    commit_arg.setdefault("timeout", confirm_delay)
                    # try runing commit confirmed using RFC6241 standart
                    try:
                        pid = "dob04041989"
                        r = manager.commit(**commit_arg, persist=pid)
                        result.append({"commit_confirmed": _form_result(r)})
                        # run final commit
                        time.sleep(commit_final_delay)
                        r = manager.commit(confirmed=True, persist_id=pid)
                        result.append({"commit": _form_result(r)})
                    # Ncclient juniper driver uses juniper custom RPC for
                    # commit and throws TypeError for "persist" argument
                    except TypeError:
                        r = manager.commit(**commit_arg)
                        result.append({"commit_confirmed": _form_result(r)})
                        # run final commit
                        time.sleep(commit_final_delay)
                        r = manager.commit()
                        result.append({"commit": _form_result(r)})
                # run normal commit
                else:
                    r = manager.commit(**commit_arg)
                    result.append({"commit": _form_result(r)})
        except:
            tb = traceback.format_exc()
            log.error(f"nornir_salt:ncclient_call transaction error: {tb}")
            result.append({"error": tb})
            if has_candidate_datastore and target == "candidate":
                r = manager.discard_changes()
                result.append({"discard_changes": _form_result(r)})
            failed = True

    return result, failed


def _call_server_capabilities(manager, capab_filter=None, *args, **kwargs):
    """
    Helper function to get server capabilities

    :param capa_filter: (str) glob filter to filter capabilities
    """
    if capab_filter:
        return (
            [
                c
                for c in manager.server_capabilities
                if fnmatchcase(c, str(capab_filter))
            ],
            False,
        )
    return [c for c in manager.server_capabilities], False


def _call_connected(manager, *args, **kwargs):
    """Helper function to get connected status"""
    return manager.connected, False


def _call_dir(manager, *args, **kwargs):
    """Function to return a list of available methods/operations"""
    methods = (
        list(dir(manager))
        + list(manager._vendor_operations.keys())
        + list(OPERATIONS.keys())
        + ["dir", "help", "transaction"]
    )
    result = sorted(
        [m for m in set(methods) if (not m.startswith("_") and not m.isupper())]
    )
    return result, False


def _call_help(manager, method_name, *args, **kwargs):
    """
    Helper function to return docstring for requested method

    :param method_name: (str) name of method or function to return docstring for
    """
    if f"_call_{method_name}" in globals():
        function_obj = globals()[f"_call_{method_name}"]
    else:
        function_obj = getattr(manager, method_name)
    h = function_obj.__doc__ if hasattr(function_obj, "__doc__") else ""
    return h, False


@ValidateFuncArgs(model_ncclient_call)
def ncclient_call(task: Task, call: str, *args, **kwargs) -> Result:
    """
    Task to handle a call of NCClient manager object methods

    :param call: (str) ncclient manager object method to call
    :param arg: (list) any ``*args`` to use with call method
    :param kwargs: (dict) any ``**kwargs`` to use with call method
    """
    # run sanity check
    if not HAS_NCCLIENT:
        return Result(
            host=task.host, failed=True, exception="No Ncclient found, is it installed?"
        )

    # initiate parameters
    failed = False
    task.name = call

    # get rendered data if any
    if "__task__" in task.host.data:
        kwargs.update(task.host.data["__task__"])

    # check if filter formed properly - as per
    # https://ncclient.readthedocs.io/en/latest/manager.html#filter-params
    # filter should be a tuple of (type, criteria)
    if kwargs.get("filter"):
        if isinstance(kwargs["filter"], list):
            kwargs["filter"] = tuple(kwargs["filter"])
        elif isinstance(kwargs["filter"], str):
            kwargs["filter"] = tuple([kwargs.pop("ftype", "subtree"), kwargs["filter"]])

    # get Ncclient NETCONF connection object
    manager = task.host.get_connection(CONNECTION_NAME, task.nornir.config)

    # add generic RPC operation to Ncclient manager object to support RPC call
    manager._vendor_operations.setdefault("rpc", GenericRPC)

    log.debug(
        f"nornir_salt:ncclient_call '{call}' with args: '{args}'; kwargs: '{kwargs}'"
    )

    # check if need to call one of helper function
    if "_call_{}".format(call) in globals():
        result, failed = globals()[f"_call_{call}"](manager, *args, **kwargs)
    # call manager object method otherwise
    else:
        result = getattr(manager, call)(*args, **kwargs)

    return Result(host=task.host, result=_form_result(result), failed=failed)
