"""
TestsProcessor Plugin
#####################

It is often required to validate network devices state against certain
criteria, test functions designed to address most common use cases in
that area.

Majority of available checks help to implement simple approach of
"if this then that" logic, for instance, if output contains this
pattern then test failed.

Dependencies:

* Nornir 3.0 and beyond
* `Cerberus module <https://pypi.org/project/Cerberus/>`_ for ``CerberusTest`` function

Test functions returns Nornir ``Result`` object and make use of these attributes:

* ``name`` - name of the test
* ``task`` - name of the task
* ``result`` -  test result ``PASS``, ``FAIL`` or ``ERROR``
* ``success`` - test success status True (PASS) or False (FAIL or ERROR)
* ``exception`` - description of failure reason
* ``test`` - test type to perform e.g. ``contains``, ``custom``, ``cerberus`` etc.
* ``criteria`` - criteria that failed the test e.g. pattern or string
* ``failed`` - this attribute not used by test functions to signal any status
  and should always be False

Running tests
=============

Running tests as simple as defining a list of dictionaries - test suite - each dictionary
represents single test definition. Reference to a particular test function API for
description of test function specific arguments it supports.

These are arguments/keys each test dictionary may contain:

* ``test`` - mandatory, name of test function to run
* ``name`` - optional, name of the test, if not provided derived from task, test and criteria arguments
* ``task`` - optional, name of the task to check results for or list of task names to use with custom
  test function, ``task`` parameter might be omitted if ``use_all_tasks`` is set to true
* ``err_msg`` - optional, error message string to use for exception in case of test failure
* ``path`` - optional, dot separated string representing path to data to test within results
* ``report_all`` - optional, boolean, default is False, if ``path`` evaluates to a list of items
  and ``report_all`` set to True, reports all tests, even successful ones
* ``use_all_tasks`` - optional, boolean to indicate if need to supply all task results to the test function

To simplify test functions calls, ``TestsProcessor`` implements these set of aliases
for ``test`` argument:

* ``contains`` calls ``ContainsTest``
* ``!contains`` or ``ncontains`` calls ``ContainsTest`` with  kwargs: ``{"revert": True}``
* ``contains_lines`` calls ``ContainsLinesTest``
* ``!contains_lines`` or ``ncontains_lines`` calls ``ContainsLinesTest`` with kwargs: ``{"revert": True}``
* ``contains_re`` calls ``ContainsTest`` with kwargs: ``{"use_re": True}``
* ``!contains_re`` or ``ncontains_re`` calls ``ContainsTest`` with kwargs: ``{"revert": True, "use_re": True}``
* ``equal`` calls ``EqualTest``
* ``!equal`` calls or ``nequal`` calls ``EqualTest`` with kwargs: ``{"revert": True}``
* ``cerberus`` calls ``CerberusTest``
* ``custom`` calls ``CustomFunctionTest``
* ``eval`` calls ``EvalTest``

In addition to aliases, ``test`` argument can reference actual test functions names:

* ``ContainsTest`` calls ``ContainsTest``
* ``ContainsLinesTest`` calls ``ContainsLinesTest``
* ``EqualTest`` calls ``EqualTest``
* ``CerberusTest`` calls ``CerberusTest``
* ``CustomFunctionTest`` calls ``CustomFunctionTest``
* ``EvalTest`` calls ``EvalTest``

Sample code to run tests::

    import pprint

    from nornir import InitNornir
    from nornir_salt.plugins.processors import TestsProcessor
    from nornir_salt.plugins.functions import ResultSerializer
    from nornir_salt.plugins.tasks import netmiko_send_commands

    nr = InitNornir(config_file="nornir.yaml")

    tests = [
        {
            "name": "Test NTP config",
            "task": "show run | inc ntp",
            "test": "contains",
            "pattern": "ntp server 7.7.7.8",
        },
        {
            "name": "Test Logging config",
            "task": "show run | inc logging",
            "test": "contains_lines",
            "pattern": ["logging host 1.1.1.1", "logging host 1.1.1.2"]
        },
        {
            "name": "Test BGP peers state",
            "task": "show bgp ipv4 unicast summary",
            "test": "!contains_lines",
            "pattern": ["Idle", "Active", "Connect"]
        },
        {
            "task": "show run | inc ntp",
            "name": "Test NTP config",
            "expr": "assert '7.7.7.8' in result, 'NTP server 7.7.7.8 not in config'",
            "test": "eval",
        }
    ]

    nr_with_tests = nr.with_processors([
        TestsProcessor(tests, remove_tasks=True)
    ])

    # netmiko_send_commands maps commands to sub-task names
    results = nr_with_tests.run(
        task=netmiko_send_commands,
        commands=[
            "show run | inc ntp",
            "show run | inc logging",
            "show bgp ipv4 unicast summary"
        ]
    )

    results_dictionary = ResultSerializer(results, to_dict=False, add_details=False)

    pprint.pprint(results_dictionary)

    # should print something like:
    #
    # [{'host': 'IOL1', 'name': 'Test NTP config', 'result': 'PASS'},
    # {'host': 'IOL1', 'name': 'Test Logging config', 'result': 'PASS'},
    # {'host': 'IOL1', 'name': 'Test BGP peers state', 'result': 'FAIL'},
    # {'host': 'IOL2', 'name': 'Test NTP config', 'result': 'PASS'},
    # {'host': 'IOL2', 'name': 'Test Logging config', 'result': 'PASS'},
    # {'host': 'IOL2', 'name': 'Test BGP peers state', 'result': 'PASS'}]

Notes on ``path`` attribute. ``path`` attribute allows to run tests against portions
of overall results, but works only if results are structured data, e.g. nested dictionary
or list of dictionaries. For example::

    import pprint
    from nornir import InitNornir
    from nornir_salt.plugins.processors import TestsProcessor
    from nornir_salt.plugins.functions import ResultSerializer
    from nornir_salt.plugins.tasks import nr_test

    nr = InitNornir(config_file="nornir.yaml")

    tests = [
        {
            "test": "eval",
            "task": "show run interface",
            "name": "Test MTU config",
            "path": "interfaces.*",
            "expr": "assert result['mtu'] > 9000, '{} MTU less then 9000'.format(result['interface'])"
        }
    ]

    nr_with_tests = nr.with_processors([
        TestsProcessor(tests, remove_tasks=True)
    ])

    # nr_test function echoes back ret_data_per_host as task results
    output = nr_with_tests.run(
        task=nr_test,
        ret_data_per_host={
            "IOL1": {
                "interfaces":  [
                    {"interface": "Gi1", "mtu": 1500},
                    {"interface": "Gi2", "mtu": 9200},
                ]
            },
            "IOL2": {
                "interfaces":  [
                    {"interface": "Eth1/9", "mtu": 9600}
                ]
            }
        },
        name="show run interface"
    )

    check_result = ResultSerializer(output, add_details=True, to_dict=False)
    # pprint.pprint(check_result)
    # [{'changed': False,
    #   'criteria': '',
    #   'diff': '',
    #   'exception': 'Gi1 MTU less then 9000',
    #   'failed': True,
    #   'host': 'IOL1',
    #   'name': 'Test MTU config',
    #   'result': 'FAIL',
    #   'success': False,
    #   'task': 'show run interface',
    #   'test': 'eval'},
    #  {'changed': False,
    #   'criteria': '',
    #   'diff': '',
    #   'exception': None,
    #   'failed': False,
    #   'host': 'IOL2',
    #   'name': 'Test MTU config',
    #   'result': 'PASS',
    #   'success': True,
    #   'task': 'show run interface',
    #   'test': 'eval'}]

In above example path ``interfaces.*`` tells ``TestsProcessor`` to retrieve data from
results under ``interfaces`` key, single star ``*`` symbol tells to iterate over list
items, instead of star, list item index can be given as well, e.g. ``interfaces.0``.

Using Tests Suite Templates
===========================

Starting with Nornir-Salt version 0.16.0 support added to dynamically
render hosts' tests suites from hosts' data using Jinja2 templates
YAML formatted strings.

.. warning:: Nornir-Salt tasks coded to make use of per-host
    commands - ``netmiko_send_commands``, ``scrapli_send_commands``,
    ``pyats_send_commands``, ``napalm_send_commands`` - custom task
    plugins can make use of ``host.data["__task__"]["commands"]``
    commands list to produce per host commands output. This is required
    for TestsProcessor to work, as sub-task should be named after
    cli commands they containing results for.

Given hosts' Nornir inventory data content::

    hosts:
      IOL1:
        data:
          interfaces_test:
          - admin_status: is up
            description: Description
            line_status: line protocol is up
            mtu: IP MTU 9200
            name: Ethernet1
          - admin_status: is up
            description: Description
            line_status: line protocol is up
            mtu: IP MTU 65535
            name: Loopback1
          software_version: cEOS
      IOL2:
        data:
          software_version: cEOS

Sample code to run test suite Jinja2 template::

    import pprint

    from nornir import InitNornir
    from nornir_salt.plugins.processors import TestsProcessor
    from nornir_salt.plugins.functions import ResultSerializer
    from nornir_salt.plugins.tasks import netmiko_send_commands

    nr = InitNornir(config_file="nornir.yaml")

    tests = [
        '''
    - task: "show version"
      test: contains
      pattern: "{{ host.software_version }}"
      name: check ceos version

    {% for interface in host.interfaces_test %}
    - task: "show interface {{ interface.name }}"
      test: contains_lines
      pattern:
        - {{ interface.admin_status }}
        - {{ interface.line_status }}
        - {{ interface.mtu }}
        - {{ interface.description }}
      name: check interface {{ interface.name }} status
    {% endfor %}
    ''',
        {
            "name": "Test NTP config",
            "task": "show run | inc ntp",
            "test": "contains",
            "pattern": "ntp server 7.7.7.8",
        }
    ]

    nr_with_tests = nr.with_processors([
        TestsProcessor(tests)
    ])

    results = nr_with_tests.run(
        task=netmiko_send_commands
    )

    results_dictionary = ResultSerializer(results, to_dict=False, add_details=False)

    pprint.pprint(results_dictionary)

    # should print something like:

    # [{'host': 'IOL1', 'name': 'show version', 'result': 'PASS'},
    # {'host': 'IOL2', 'name': 'show version', 'result': 'PASS'},
    # {'host': 'IOL1', 'name': 'show interface Ethernet1', 'result': 'PASS'},
    # {'host': 'IOL1', 'name': 'show interface Ethernet2', 'result': 'PASS'},
    # {'host': 'IOL1', 'name': 'show run | inc ntp', 'result': 'PASS'},
    # {'host': 'IOL2', 'name': 'show run | inc ntp', 'result': 'PASS'}]

Test suite template rendered using individual host's data
forming per-host test suite. CLI show commands to collect
from host device automatically extracted from per-host
test suite. For example, for above data these are commands
collected from devices:

- **ceos1** - "show version", "show interface Ethernet1",
  "show interface Ethernet2", "show run | inc ntp"
- **ceos2** - "show version", "show run | inc ntp"

Collected show commands output tested using rendered test
suite on a per-host basis.

Tests Reference
===============

.. autoclass:: nornir_salt.plugins.processors.TestsProcessor.TestsProcessor
.. autofunction:: nornir_salt.plugins.processors.TestsProcessor.ContainsTest
.. autofunction:: nornir_salt.plugins.processors.TestsProcessor.ContainsLinesTest
.. autofunction:: nornir_salt.plugins.processors.TestsProcessor.EqualTest
.. autofunction:: nornir_salt.plugins.processors.TestsProcessor.CerberusTest
.. autofunction:: nornir_salt.plugins.processors.TestsProcessor.EvalTest
.. autofunction:: nornir_salt.plugins.processors.TestsProcessor.CustomFunctionTest
"""
import logging
import re
import traceback
import fnmatch

from nornir.core.inventory import Host
from nornir.core.task import AggregatedResult, MultiResult, Result, Task
from nornir_salt.utils.pydantic_models import (
    modelTestsProcessorSuite,
    modelTestsProcessorTests,
)
from nornir_salt.plugins.functions import FFun, FFun_functions

log = logging.getLogger(__name__)

try:
    from cerberus import Validator

    HAS_CERBERUS = True
except ImportError:
    log.debug("Failed to import Cerberus library, install: pip install cerberus")
    HAS_CERBERUS = False

try:
    import jinja2

    HAS_JINJA2 = True
except ImportError:
    log.debug("Failed to import Jinja2 library, install: pip install Jinja2")
    HAS_JINJA2 = False

try:
    import yaml

    HAS_YAML = True
except ImportError:
    log.debug("Failed to import PyYAML library, install: pip install PyYAML")
    HAS_YAML = False

# return datum template dictionary
test_result_template = {
    "name": "",  # name of the test
    "task": "",  # name of the task
    "result": "PASS",  # test result PASS, FAIL, ERROR
    "success": True,  # success status
    "failed": False,  # failure status
    "exception": None,  # description of failure reason
    "test": None,  # test type to perform .g. contains
    "criteria": "",  # criteria that failed the test e.g. pattern or string
}


def _get_result_by_path(data, path, host):
    """
    Helper generator function to iterate over data and yield
    ``nornir.core.task.Result`` object with result attribute set to data
    at given path.

    :param data: (dict or list) structured data to retrieve data subset from
    :param path: (list) list of path items to get from data
    :param host: (obj)  Nornir host object
        :return result: ``nornir.core.task.Result`` object with data at given path
    """
    if path == []:
        yield Result(host=host, result=data)
    elif isinstance(data, dict):
        for result in _get_result_by_path(data[path[0]], path[1:], host):
            yield result
    elif path[0].isdigit() and isinstance(data, list):
        for result in _get_result_by_path(data[int(path[0])], path[1:], host):
            yield result
    elif path[0] == "*" and isinstance(data, list):
        for item in data:
            for result in _get_result_by_path(item, path[1:], host):
                yield result


def EvalTest(host, result, expr, revert=False, err_msg=None, globs=None, **kwargs):
    """
    Function to check result running python built-in ``Eval`` or ``Exec``
    function against provided python expression.

    This function in its use cases sits in between pre-built test function such as
    ``ContainsTest`` or ``EqualTest`` and running custom Python test function using
    ``CustomFunctionTest`` function. ``Eval`` allows to use any python expressions
    that evaluates to True or False without the need to write custom functions.

    If expression string starts with ``assert``, will use ``Exec`` function,
    uses ``Eval`` for everything else.

    Eval and Exec functions' ``globals`` dictionary populated with ``result`` and
    ``host`` variables, ``result`` contains ``nornir.core.task.Result`` result attribute
    while ``host`` references Nornir host object. This allows to use expressions
    like this::

        "'7.7.7.7' in result"
        "assert '7.7.7.8' in result, 'NTP server 7.7.7.8 not in config'"
        "len(result.splitlines()) == 3"

    Eval and Exec functions' ``globals`` dictionary attribute merged with ``**globs``
    supplied to ``EvalTest`` function call, that allows to use any additional variables
    or functions. For example, below is equivalent to running ``contains_lines`` test::

        tests = [
            {
                "test": "eval",
                "task": "show run | inc logging",
                "name": "Test Syslog config",
                "expr": "all(map(lambda line: line in result, lines))",
                "globs": {
                    "lines": ["logging host 1.1.1.1", "logging host 2.2.2.2"]
                },
                "err_msg": "Syslog config is wrong"
            }
        ]

    ``lines`` variable shared with ``eval`` globals space, allowing to reference it
    as part of expression.

    .. warning: using eval and exec could be dangerous, running tests from untrusted
        sources generally a bad idea as any custom code can be executed on the system.

    :param host: (obj) Nornir host object
    :param result: (obj) ``nornir.core.task.Result`` object
    :param expr: (str) Python expression to evaluate
    :param revert: (bool) if True, changes results to opposite - check for inequality
    :param err_msg: (str) exception message to use on test failure
    :param globs: (dict) dictionary to use as ``eval/exec`` ``globals`` space
    :param kwargs: (dict) any additional ``**kwargs`` keyword arguments to include in return Result object
    :return result: ``nornir.core.task.Result`` object with test results
    """
    globs = globs or {}
    ret = test_result_template.copy()
    ret.update(kwargs)

    try:
        if expr.strip().startswith("assert"):
            check_result = exec(  # nosec
                expr, {"result": result.result, "host": host, **globs}, {}
            )
        else:
            check_result = eval(  # nosec
                expr, {"result": result.result, "host": host, **globs}, {}
            )
        if check_result is False:
            ret.update({"result": "FAIL", "success": False})
            ret["exception"] = err_msg if err_msg else "Expression evaluated to False"
    except AssertionError as e:
        ret.update({"result": "FAIL", "success": False})
        ret["exception"] = err_msg if err_msg else (str(e) or "AssertionError")
    except:
        ret.update({"result": "ERROR", "success": False})
        ret["exception"] = err_msg if err_msg else traceback.format_exc()

    # revert results
    if revert:
        if ret["success"] is False:
            ret.update({"result": "PASS", "success": True})
            ret["exception"] = None
        elif ret["success"] is True:
            ret.update({"result": "FAIL", "success": False})
            ret["exception"] = err_msg if err_msg else "Pattern and output equal"
    return Result(host=host, **ret)


def _cerberus_validate_item(validator_engine, data, schema, ret_data):
    """Helper function to avoid code repetition for Cerberus validation"""
    res = validator_engine.validate(document=data, schema=schema)
    if not res:
        ret_data.update(
            {"result": "FAIL", "success": False, "exception": validator_engine.errors}
        )
    try:
        ret_data["name"] = ret_data["name"].format(**data)
    except KeyError:
        pass
    return ret_data


def CerberusTest(host, result, schema, allow_unknown=True, **kwargs):
    """
    Function to check results using ``Cerberus`` module schema. Results must be a structured
    data - dictionary, list - strings and other types of data not supported.

    :param host: (obj) Nornir host object
    :param result: ``nornir.core.task.Result`` object
    :param schema: (dictionary) Cerberus schema definition to us for validation
    :param allow_uncknown: (bool) Cerberus allow unknown parameter, default is True
    :param kwargs: (dict) any additional ``**kwargs`` keyword arguments to include in return Result object

    .. warning:: Cerberus library only supports validation of dictionary structures,
        while nested elements could be lists, as a result, ``CerberusTest`` function
        was coded to support validation of dictionary or list of dictionaries results.

    .. note:: ``kwargs`` ``name`` key value formatted using python format function supplying
        dictionary being validated as arguments
    """
    # form ret structure
    ret = test_result_template.copy()
    ret.update(kwargs)

    # run check
    if not HAS_CERBERUS:
        ret.update({"result": "ERROR", "success": False})
        ret[
            "exception"
        ] = "Failed to import Cerberus library, install: pip install cerberus"
        return Result(host=host, **ret)
    validator_engine = Validator()
    validator_engine.allow_unknown = allow_unknown

    # validate dictionary results
    if isinstance(result.result, dict):
        ret = _cerberus_validate_item(validator_engine, result.result, schema, ret)
        return Result(host=host, **ret)
    # validate list of dictionaries results
    elif isinstance(result.result, list):
        validation_results = []
        for item in result.result:
            if not isinstance(item, dict):
                continue
            ret_copy = ret.copy()
            ret_copy = _cerberus_validate_item(validator_engine, item, schema, ret_copy)
            validation_results.append(Result(host=host, **ret_copy))
        return validation_results
    else:
        raise TypeError(
            "nornir-salt:CerberusTest unsupported results type '{}', supported - dictionary, list".format(
                type(result.result)
            )
        )


def _load_custom_fun_from_text(function_text, function_name, globals_dictionary=None):
    """
    Helper function to load custom function code from text using
    Python ``exec`` built-in function
    """
    if function_name not in function_text:
        raise RuntimeError(
            "nornir-salt:CustomFunctionTest no '{}' function in function text".format(
                function_name
            )
        )

    globals_dictionary = globals_dictionary or {}
    data = {}
    glob_dict = {
        "__builtins__": __builtins__,
        "False": False,
        "True": True,
        "None": None,
    }
    glob_dict.update(globals_dictionary)

    # load function by running exec
    exec(compile(function_text, "<string>", "exec"), glob_dict, data)  # nosec

    # add extracted functions to globals for recursion to work
    glob_dict.update(data)

    return data[function_name]


def CustomFunctionTest(
    host,
    result,
    function_file=None,
    function_text=None,
    function_call=None,
    function_name="run",
    function_kwargs=None,
    globals_dictionary=None,
    add_host=False,
    **kwargs,
):
    """
    Wrapper around calling custom function to perform results checks.

    :param host: (obj) Nornir host object
    :param result: ``nornir.core.task.Result`` object
    :param function_name: (str) function name, default is ``run``
    :param function_file: (str) OS path to file with ``function_name`` function
    :param function_text: (str) Python code text for ``function_name`` function
    :param function_call: (callable) reference to callable python function
    :param globals_dictionary: (dict) dictionary to merge with global space of the custom function,
      used only if ``function_file`` or ``function_text`` arguments provided.
    :param function_kwargs: (dict) ``**function_kwargs`` to pass on to custom function
    :param add_host: (bool) default is False, if True adds ``host`` argument to ``function_kwargs``
      as a reference to Nornir Host object that this function executing for
    :param kwargs: (dict) any additional key word arguments to include in results

    .. warning:: ``function_file`` and ``function_text`` use ``exec`` function
       to compile python code, using test functions from untrusted sources can
       be dangerous.

    Custom functions should accept one positional argument for results following these rules:

    * if ``task`` is a string result is ``nornir.core.task.Result``
    * if ``task`` is a list of task names result is a list of ``nornir.core.task.Result`` objects
      of corresponding tasks
    * if ``use_all_tasks`` set to True result is ``nornir.core.task.MultiResult`` object

    If ``add_host`` set to True, custom function must accept ``host`` argument as a reference
    to Nornir host object this task results are being tested for.

    Any additional parameters can be passed to custom test function using ``function_kwargs``
    arguments.

    Custom function can return a dictionary or a list of dictionaries to include in
    results. Each dictionary can have any keys, but it is recommended to have at least
    these keys:

    * ``exception`` - error description if any
    * ``result`` - "PASS", "FAIL" or "ERROR" string
    * ``success`` - boolean True or False

    If a list returned by custom function, each list item forms individual result item.

    If custom test function returns empty list, empty dictionary or None or True test considered
    successful and dictionary added to overall results with ``result`` key set to ``PASS``.

    If custom test function returns False test outcome considered unsuccessful and dictionary
    added to overall results with ``result`` key set to ``FAIL``.

    Sample custom test function to accept ``Result`` object when ``use_all_tasks`` set to False and
    ``task`` is a sting representing name of the task::

        def custom_test_function(result):
            # result is nornir.core.task.Result object
            if "7.7.7.8" not in result.result:
                return {
                    "exception": "Server 7.7.7.8 not in config",
                    "result": "FAIL",
                    "success": False
                }

    Sample custom test function to accept ``MultiResult`` object when ``use_all_tasks`` set to True::

        def custom_test_function(result):
            # result is nornir.core.task.MultiResult object - list of nornir.core.task.Result objects
            ret = []
            for item in result:
                if item.result == None: # skip empty results
                    continue
                elif item.name == "show run | inc ntp":
                    if "7.7.7.8" not in item.result:
                        ret.append({
                            "exception": "NTP Server 7.7.7.8 not in config",
                            "result": "FAIL",
                            "success": False
                        })
                elif item.name == "show run | inc logging":
                    if "1.1.1.1" not in item.result:
                        ret.append({
                            "exception": "Logging Server 1.1.1.1 not in config",
                            "result": "FAIL",
                            "success": False
                        })
            return ret
    """
    function_kwargs = function_kwargs or {}
    globals_dictionary = globals_dictionary or {}

    if add_host:
        function_kwargs["host"] = host

    # form ret structure
    ret = test_result_template.copy()
    ret.update(kwargs)

    # load and compile custom function
    try:
        if function_text:
            test_function = _load_custom_fun_from_text(
                function_text, function_name, globals_dictionary
            )
        elif function_file:
            with open(function_file, encoding="utf-8") as f:
                test_function = _load_custom_fun_from_text(
                    f.read(), function_name, globals_dictionary
                )
        elif function_call:
            test_function = function_call
        else:
            raise RuntimeError(
                "nornir-salt:CustomFunctionTest no custom function found."
            )
    except:
        msg = "nornir-salt:CustomFunctionTest function loading error:\n{}".format(
            traceback.format_exc()
        )
        log.error(msg)
        ret.update({"result": "ERROR", "success": False, "exception": msg})
        return Result(host=host, **ret)
    # run custom function
    try:
        test_function_result = test_function(result, **function_kwargs)
    except:
        msg = "nornir-salt:CustomFunctionTest function run error:\n{}".format(
            traceback.format_exc()
        )
        log.error(msg)
        ret.update({"result": "ERROR", "success": False, "exception": msg})
        return Result(host=host, **ret)
    # form and return results
    if (
        test_function_result == []
        or test_function_result == {}
        or test_function_result is None
        or test_function_result is True
    ):
        return Result(host=host, **ret)
    elif test_function_result is False:
        ret.update({"result": "FAIL", "success": False})
        return Result(host=host, **ret)
    elif isinstance(test_function_result, list):
        ret_list = []
        for item in test_function_result:
            ret_copy = ret.copy()
            ret_copy.update(item)
            ret_list.append(Result(host=host, **ret_copy))
        return ret_list
    elif isinstance(test_function_result, dict):
        ret.update(test_function_result)
        return Result(host=host, **ret)
    else:
        raise TypeError(
            "nornir-salt:CustomFunctionTest test function returned unsupported results type: {}".format(
                type(test_function_result)
            )
        )


def EqualTest(host, result, pattern, revert=False, err_msg=None, **kwargs):
    """
    Function to check result is equal to the pattern.

    :param host: (obj) Nornir host object
    :param result: (obj) ``nornir.core.task.Result`` object
    :param pattern: (any) string, dict, list or any other object to check for equality
    :param revert: (bool) if True, changes results to opposite - check for inequality
    :param err_msg: (str) exception message to use on test failure
    :param kwargs: (dict) any additional ``**kwargs`` keyword arguments to include in return Result object
    :return result: ``nornir.core.task.Result`` object with test results
    """
    # form ret structure
    ret = test_result_template.copy()
    ret.update(kwargs)
    if isinstance(pattern, str):
        ret["criteria"] = (
            pattern.replace("\n", "\\n")
            if len(pattern) < 25
            else pattern[0:24].replace("\n", "\\n")
        )

    # run the check
    if pattern != result.result:
        ret.update({"result": "FAIL", "success": False})
        ret["exception"] = err_msg if err_msg else "Pattern and output not equal"
    # revert results
    if revert:
        if ret["success"] is False:
            ret.update({"result": "PASS", "success": True})
            ret["exception"] = None
        elif ret["success"] is True:
            ret.update({"result": "FAIL", "success": False})
            ret["exception"] = err_msg if err_msg else "Pattern and output equal"
    return Result(host=host, **ret)


def ContainsLinesTest(
    host,
    result,
    pattern,
    use_re=False,
    count=None,
    revert=False,
    err_msg=None,
    **kwargs,
):
    """
    Function to check that all lines contained in result output.

    Tests each line one by one, this is the key difference compared to
    ``ContainsTest`` function, where whole pattern checked for presence in
    output from device.

    :param host: (obj) Nornir host object
    :param result: (obj) ``nornir.core.task.Result`` object
    :param pattern: (str or list) multiline string or list of lines to check
    :param use_re: (bool) if True uses re.search to check for line pattern in output
    :param count: (int) check exact number of line pattern occurrences in the output
    :param revert: (bool) if True, changes results to opposite - check lack of lines in output
    :param err_msg: (str) exception message to use on test failure
    :param kwargs: (dict) any additional ``**kwargs`` keyword arguments to include in return Result object
    :return result: ``nornir.core.task.Result`` object with test results
    """
    # form ret structure
    ret = test_result_template.copy()
    ret.update(kwargs)

    # run the check
    lines_list = pattern.splitlines() if isinstance(pattern, str) else pattern
    for line in lines_list:
        check_result = ContainsTest(
            host=host,
            result=result,
            pattern=line,
            use_re=use_re,
            count=count,
            revert=revert,
            err_msg=err_msg,
        )
        if not check_result.success:
            ret.update({"result": "FAIL", "success": False})
            ret["exception"] = check_result.exception
            ret["criteria"] = check_result.criteria
            break
    return Result(host=host, **ret)


def ContainsTest(
    host,
    result,
    pattern,
    use_re=False,
    count=None,
    count_ge=None,
    count_le=None,
    revert=False,
    err_msg=None,
    **kwargs,
):
    """
    Function to check if pattern contained in output of given result.

    :param host: (obj) Nornir host object
    :param result: (obj) ``nornir.core.task.Result`` object
    :param pattern: (str) pattern to check containment for
    :param use_re: (bool) if True uses re.search to check for pattern in output
    :param count: (int) check exact number of pattern occurrences in the output
    :param count_ge: (int) check number of pattern occurrences in the output is greater or equal to given value
    :param count_le: (int) check number of pattern occurrences in the output is lower or equal to given value
    :param revert: (bool) if True, changes results to opposite - check lack of containment
    :param err_msg: (str) exception message to use on test failure
    :param kwargs: (dict) any additional ``**kwargs`` keyword arguments to include in return Result object
    :return result: ``nornir.core.task.Result`` object with test results
    """
    pattern = str(pattern)
    # form ret structure
    ret = test_result_template.copy()
    ret.update(kwargs)
    ret["criteria"] = (
        pattern.replace("\n", "\\n")
        if len(pattern) < 25
        else pattern[0:24].replace("\n", "\\n")
    )

    # add count to return results
    if count:
        ret["count"] = count
    if count_ge:
        ret["count_ge"] = count_ge
    if count_le:
        ret["count_le"] = count_le

    # run the check
    if use_re:
        if not re.search(pattern, result.result):
            ret.update({"result": "FAIL", "success": False})
            ret["exception"] = err_msg if err_msg else "Regex pattern not in output"
    elif count and result.result.count(pattern) != count:
        ret.update({"result": "FAIL", "success": False})
        ret["exception"] = (
            err_msg if err_msg else "Pattern not in output {} times".format(count)
        )
    elif count_ge and result.result.count(pattern) < count_ge:
        ret.update({"result": "FAIL", "success": False})
        ret["exception"] = (
            err_msg
            if err_msg
            else "Pattern not in output greater or equal {} times".format(count_ge)
        )
    elif count_le and result.result.count(pattern) > count_le:
        ret.update({"result": "FAIL", "success": False})
        ret["exception"] = (
            err_msg
            if err_msg
            else "Pattern not in output lower or equal {} times".format(count_le)
        )
    elif pattern not in result.result:
        ret.update({"result": "FAIL", "success": False})
        ret["exception"] = err_msg if err_msg else "Pattern not in output"
    # revert results if requested to do so
    if revert:
        if ret["success"] is False:
            ret.update({"result": "PASS", "success": True})
            ret["exception"] = None
        elif ret["success"] is True:
            ret.update({"result": "FAIL", "success": False})
            if use_re:
                ret["exception"] = err_msg if err_msg else "Regex pattern in output"
            elif count:
                ret["exception"] = (
                    err_msg if err_msg else "Pattern in output {} times".format(count)
                )
            elif count_ge:
                ret["exception"] = (
                    err_msg
                    if err_msg
                    else "Pattern in output greater or equal {} times".format(count_ge)
                )
            elif count_le:
                ret["exception"] = (
                    err_msg
                    if err_msg
                    else "Pattern in output lower or equal {} times".format(count_le)
                )
            else:
                ret["exception"] = err_msg if err_msg else "Pattern in output"
    return Result(host=host, **ret)


test_functions_dispatcher = {
    "contains": {"fun": ContainsTest, "kwargs": {}},
    "ncontains": {"fun": ContainsTest, "kwargs": {"revert": True}},
    "!contains": {"fun": ContainsTest, "kwargs": {"revert": True}},
    "contains_re": {"fun": ContainsTest, "kwargs": {"use_re": True}},
    "!contains_re": {"fun": ContainsTest, "kwargs": {"revert": True, "use_re": True}},
    "ncontains_re": {"fun": ContainsTest, "kwargs": {"revert": True, "use_re": True}},
    "contains_lines": {"fun": ContainsLinesTest, "kwargs": {}},
    "!contains_lines": {"fun": ContainsLinesTest, "kwargs": {"revert": True}},
    "ncontains_lines": {"fun": ContainsLinesTest, "kwargs": {"revert": True}},
    "contains_lines_re": {"fun": ContainsLinesTest, "kwargs": {"use_re": True}},
    "!contains_lines_re": {
        "fun": ContainsLinesTest,
        "kwargs": {"revert": True, "use_re": True},
    },
    "ncontains_lines_re": {
        "fun": ContainsLinesTest,
        "kwargs": {"revert": True, "use_re": True},
    },
    "equal": {"fun": EqualTest, "kwargs": {}},
    "!equal": {"fun": EqualTest, "kwargs": {"revert": True}},
    "nequal": {"fun": EqualTest, "kwargs": {"revert": True}},
    "cerberus": {"fun": CerberusTest, "kwargs": {}},
    "custom": {"fun": CustomFunctionTest, "kwargs": {}},
    "eval": {"fun": EvalTest, "kwargs": {}},
}


class TestsProcessor:
    """
    TestsProcessor designed to run a series of tests for Nornir
    tasks results.

    :param tests: (list of dictionaries) list of tests to run
    :param remove_tasks: (bool) if True (default) removes tasks output from results
    :param kwargs: (any) if provided, ``**kwargs`` will form a single test item
    :param failed_only: (bool) if True, includes only failed tests in results, default is False
    :param build_per_host_tests: (bool) if True, renders and forms per host tests and show commands
    :param render_tests: (bool) if True will use Jinja2 to render tests, rendering skipped otherwise
    :param jinja_kwargs: (dict) Dictionary of arguments for ``jinja2.Template`` object,
        default is ``{"trim_blocks": True, "lstrip_blocks": True}``
    :param subset: (list or str) list or string with comma separated glob patterns to
        match tests' names to execute. Patterns are not case-sensitive. Uses ``fnmatch``
        Python built-in function to do glob patterns matching
    :param tests_data: (dict) dictionary of parameters to supply for test suite templates rendering
    """

    def __init__(
        self,
        tests=None,
        remove_tasks=True,
        failed_only=False,
        jinja_kwargs=None,
        tests_data=None,
        build_per_host_tests=False,
        render_tests=True,
        subset=None,
        **kwargs,
    ):
        self.tests = tests if tests else [kwargs]
        self.remove_tasks = remove_tasks
        self.len_tasks = {}
        self.failed_only = failed_only
        self.jinja_kwargs = jinja_kwargs or {"trim_blocks": True, "lstrip_blocks": True}
        self.tests_data = tests_data or {}
        self.build_per_host_tests = build_per_host_tests
        self.render_tests = render_tests
        self.subset = (
            [i.strip() for i in subset.split(",")]
            if isinstance(subset, str)
            else (subset or [])
        )

        # do preliminary tests suite validation
        if build_per_host_tests:
            _ = modelTestsProcessorTests(tests=self.tests)
        # do full test suite validation
        else:
            _ = modelTestsProcessorSuite(tests=self.tests)

    def _render(self, template, data: dict = None, load: bool = False):
        """
        Helper function to render test items and test tasks

        :param template: string or list of strings to render
        :param load: if True, loads rendered string using YAML module
        :param data: dictionary with data to use for template rendering
        :return: string or list of dictionaries
        """
        data = data or {}
        ret = []

        if self.render_tests:
            # render template string(s)
            if isinstance(template, str):
                template_obj = jinja2.Template(template, **self.jinja_kwargs)
                ret = template_obj.render(data)
            # run recursion if template is a list of strings
            elif isinstance(template, list):
                ret = [self._render(i, data) for i in template]
        else:
            ret = template

        # process rendered string further
        if isinstance(ret, str):
            # check if test rendering produced empty string
            if not ret.strip():
                ret = None
            # load rendered data from YAML string
            elif load is True:
                ret = yaml.safe_load(ret)
                if not isinstance(ret, list):
                    raise ValueError(
                        f"Rendered string did not produce list but '{type(ret)}'"
                    )

        return ret

    def task_started(self, task: Task) -> None:
        """
        This callback called on task start. This method forms per host
        test suits, rendering any of test items if it is a string, extracts
        per host show commands to collect from per-host tests suite items.
        """
        if not self.build_per_host_tests:
            return

        hosts = task.nornir.inventory.hosts

        # form per host tests suite
        for host in hosts.values():
            host.data.setdefault("__task__", {})
            host.data["__task__"]["tests_suite"] = []
            host.data["__task__"]["commands"] = []
            host_data = {
                "host": host,
                "task": task,
                "job_data": host.data.get("job_data", {}),
                "tests_data": self.tests_data,
            }
            #  retrieve tests list
            if isinstance(self.tests, list):
                host_tests = self.tests
            elif isinstance(self.tests, dict):
                host_tests = self.tests.get(host.name, [])
            # iterate over test suite items
            for test in host_tests:
                tests_ = []
                # if test is a string render it using Jinja2 and load using YAML
                if isinstance(test, str):
                    tests_ = self._render(test, host_data, load=True)
                    if tests_ is None:  # skip if not rendered
                        continue
                # if test item is a list, transform it to a dictionary
                elif isinstance(test, list):
                    test_ = {"test": test[1], "pattern": test[2]}
                    test_["name"] = test[3] if len(test) == 4 else None
                    test_["task"] = self._render(test[0], host_data)
                    if test_["task"] is None:  # skip if not rendered
                        continue
                    if test_["test"] in ["eval", "EvalTest"]:
                        test_["expr"] = test_.pop("pattern")
                    tests_ = [test_]
                # use test dict item as is but make a copy of it
                elif isinstance(test, dict):
                    test_ = test.copy()
                    if test_.get("task"):
                        test_["task"] = self._render(test_["task"], host_data)
                        if test_["task"] is None:  # skip if not rendered
                            continue
                    tests_ = [test_]
                else:
                    raise ValueError(f"Unsupported test item type '{type(test)}'")

                # process tests items further
                while tests_:
                    t = tests_.pop()
                    # filter tests by using subset list
                    if self.subset and not any(
                        map(lambda m: fnmatch.fnmatch(t["name"], m), self.subset)
                    ):
                        continue
                    # filter tests by using Fx filters
                    if "cli" in t:
                        filtered_hosts = FFun(task.nornir, **t["cli"])
                        if host.name not in filtered_hosts.inventory.hosts:
                            continue
                    # skip known tasks that are not a cli command
                    if not t.get("task") or t["task"] in ["run_ttp"]:
                        continue
                    # form per-host commands
                    elif isinstance(t["task"], list):
                        for cmd in t["task"]:
                            if cmd not in host.data["__task__"]["commands"]:
                                host.data["__task__"]["commands"].append(cmd)
                    elif isinstance(t["task"], str):
                        if t["task"] not in host.data["__task__"]["commands"]:
                            host.data["__task__"]["commands"].append(t["task"])

                    host.data["__task__"]["tests_suite"].append(t)

            # validate host's tests suite content
            _ = modelTestsProcessorSuite(tests=host.data["__task__"]["tests_suite"])

    def task_instance_started(self, task: Task, host: Host) -> None:
        pass

    def task_instance_completed(
        self, task: Task, host: Host, result: MultiResult
    ) -> None:
        """
        Method to iterate over individual hosts' result after task/sub-tasks completion.
        """
        # check if has failed tasks, do nothing in such case
        if result.failed:
            log.error("nornir_salt:TestsProcessor has failed tasks, do nothing, return")
            return

        test_results = []

        try:
            # decide on tests content
            if self.build_per_host_tests:
                tests_suite = host.data["__task__"]["tests_suite"]
            else:
                tests_suite = self.tests

            # do the tests
            for test in tests_suite:
                # make a copy of test item to not interfere with other hosts' testing
                test = test if self.build_per_host_tests else test.copy()

                # if test item is a list, transform it to a dictionary
                if isinstance(test, list):
                    test = {
                        "task": test[0],
                        "test": test[1],
                        "pattern": test[2],
                        "name": test[3] if len(test) == 4 else None,
                    }
                    if test["test"] in ["eval", "EvalTest"]:
                        test["expr"] = test.pop("pattern")

                # make sure has result item in a test
                test["result"] = None

                # make sure we have test name defined
                if not test.get("name"):
                    test["name"] = "{} {} {}..".format(
                        test.get("task", "Test all tasks")
                        if test.get("use_all_tasks")
                        else test["task"],
                        test["test"],
                        str(test.get("pattern", ""))[:9],
                    )

                # get task results to use; use all results
                if test.get("use_all_tasks") is True:
                    test["result"] = result
                # use subset of task results
                elif isinstance(test["task"], list):
                    test["result"] = []
                    for i in result:
                        # check if need to skip this task
                        if hasattr(i, "skip_results") and i.skip_results is True:
                            continue
                        if i.name in test["task"]:
                            test["result"].append(i)
                # use results for single task only
                else:
                    # try to find task by matching it's name
                    for i in result:
                        # check if need to skip this task
                        if hasattr(i, "skip_results") and i.skip_results is True:
                            continue
                        if i.name == test["task"]:
                            test["result"] = i
                            break
                    else:
                        # use first task if only one test and one task given
                        tasks = [t for t in result if not hasattr(t, "skip_results")]
                        if len(self.tests) == 1 and len(tasks) == 1:
                            test["result"] = tasks[0]

                # check if found no task results for this test item
                if test["result"] is None or test["result"] == []:
                    test[
                        "exception"
                    ] = "Found no results to test - all tasks failed or test name does not match any of task names"
                    test["result"] = "ERROR"
                    test["success"] = False
                    ret = {**test_result_template.copy(), **test}
                    _ = ret.pop("expr", None)
                    test_results.append(Result(host=host, **ret))
                    continue

                # get test function and function kwargs
                if test["test"] in test_functions_dispatcher:
                    test_func = test_functions_dispatcher[test["test"]]["fun"]
                    test.update(test_functions_dispatcher[test["test"]]["kwargs"])
                elif test["test"] in globals() and "Test" in test["test"]:
                    test_func = globals()[test["test"]]
                else:
                    raise NameError(
                        "nornir-salt:TestsProcessor unsupported test function '{}'".format(
                            test["test"]
                        )
                    )

                # run the test
                log.debug(
                    "nornir-salt:TestsProcessor running test '{}'".format(test["name"])
                )
                try:
                    # run test for data at given path
                    if test.get("path"):
                        report_all = test.pop("report_all", False)
                        res = [
                            test_func(host=host, result=item, **test)
                            for item in _get_result_by_path(
                                data=test.pop("result").result,
                                path=test.pop("path").split("."),
                                host=host,
                            )
                        ]
                        # leave only failed results
                        if not report_all:
                            res = [i for i in res if i.success is False]
                            # add single successful test if no tests failed
                            if not res:
                                ret = test_result_template.copy()
                                ret.update(test)
                                _ = ret.pop("expr", None)
                                res = Result(host=host, **ret)
                    else:
                        res = test_func(host=host, **test)
                except:
                    msg = "nornir-salt:TestsProcessor run error:\n{}".format(
                        traceback.format_exc()
                    )
                    log.error(msg)
                    ret = test_result_template.copy()
                    ret.update(test)
                    ret.update({"result": "ERROR", "success": False, "exception": msg})
                    res = Result(host=host, **ret)

                if isinstance(res, list):
                    test_results.extend(res)
                else:
                    test_results.append(res)
        except:
            test_results.append(
                Result(
                    host=host,
                    exception=traceback.format_exc(),
                    result=traceback.format_exc(),
                    success=False,
                    name="nornir-salt:TestsProcessor task_instance_completed error",
                )
            )
        # remove tasks with device's output
        if self.remove_tasks:
            while result:
                _ = result.pop()
        # save test results
        result.extend(test_results)

    def subtask_instance_started(self, task: Task, host: Host) -> None:
        pass

    def subtask_instance_completed(
        self, task: Task, host: Host, result: MultiResult
    ) -> None:
        pass

    def task_completed(self, task: Task, result: AggregatedResult) -> None:

        # remove tests suite from host's data
        for host in task.nornir.inventory.hosts.values():
            _ = host.data.get("__task__", {}).pop("tests_suite", None)
            _ = host.data.get("__task__", {}).pop("commands", None)

        # remove non failed tasks if requested to do so
        if self.failed_only:
            for hostname, results in result.items():
                good_tests = []
                for index, i in enumerate(results):
                    if hasattr(i, "success") and i.success is True:
                        good_tests.append(index)
                # pop starting from last index to preserve lower indexes
                for i in reversed(good_tests):
                    _ = results.pop(i)
