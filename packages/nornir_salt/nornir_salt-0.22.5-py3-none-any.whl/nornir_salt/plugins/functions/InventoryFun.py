"""
InventoryFun
############

Function to interact with in memory Nornir Inventory data.

InventoryFun Sample Usage
===========================

Sample code to invoke ``InventoryFun`` function to ``create`` new host::

    from nornir_salt.plugins.functions import InventoryFun

    host_data = {
        "name": "IOL3",
        "hostname": "192.168.217.99",
        "platform": "ios",
        "groups": ["lab", "bma"],
        "connection_options": {
            "napalm": {
                "port": 2022,
                "extras": {
                    "foo": "bar"
                }
            }
        }
    }

    res = InventoryFun(nr, call="create_host", **host_data)
    # or res = InventoryFun(nr, "create_host", **host_data)

Sample code to invoke ``InventoryFun`` function to ``update`` existing host::

    from nornir_salt.plugins.functions import InventoryFun

    host_data = {
        "name": "IOL2",
        "hostname": "192.168.217.99",
        "platform": "ios_xe",
        "username": "new_username",
        "password": "new_password",
        "port": 123,
        "groups": ["lab", "bma"],
        "data": {
            "made_by": "humans",
        },
        "connection_options": {
            "napalm": {
                "port": 2022,
                "extras": {
                    "foo": "bar1"
                }
            }
        }
    }

    res = InventoryFun(nr, call="update_host", groups_action="append", **host_data)
    # or res = InventoryFun(nr, "update_host", groups_action="append", **host_data)

Sample code to invoke ``InventoryFun`` function to ``delete`` existing host::

    from nornir_salt.plugins.functions import InventoryFun

    res = InventoryFun(nr, call="delete_host", name="IOL2")
    # or res = InventoryFun(nr, "delete_host", name="IOL2")

Sample code to invoke ``InventoryFun`` function to bulk ``load`` from list::

    from nornir_salt.plugins.functions import InventoryFun

    data = [
        {
            "call": "create_host",
            "name": "IOL3",
            "hostname": "192.168.217.99",
            "platform": "ios",
            "groups": ["lab", "bma"],
        },
        {
            "call": "delete_host",
            "name": "IOL2",
        },
        {
            "call": "update_host",
            "name": "IOL1",
            "hostname": "1.2.3.4",
            "platform": "ios_xe",
            "groups": ["bma"],
            "groups_action": "remove"
        },
        {
            "call": "create",
            "name": "IOL4",
            "hostname": "192.168.217.4",
            "platform": "iosxr",
            "groups": ["lab"],
        },
    ]

    res = InventoryFun(nr, call="load", data=data)
    # or res = InventoryFun(nr, "load", data=data)

InventoryFun Reference
======================

.. autofunction:: nornir_salt.plugins.functions.InventoryFun.InventoryFun

Call Functions Reference
========================

.. autofunction:: nornir_salt.plugins.functions.InventoryFun._create_host
.. autofunction:: nornir_salt.plugins.functions.InventoryFun._read_host
.. autofunction:: nornir_salt.plugins.functions.InventoryFun._read_inventory
.. autofunction:: nornir_salt.plugins.functions.InventoryFun._read_host_data
.. autofunction:: nornir_salt.plugins.functions.InventoryFun._update_host
.. autofunction:: nornir_salt.plugins.functions.InventoryFun._delete_host
.. autofunction:: nornir_salt.plugins.functions.InventoryFun._load
.. autofunction:: nornir_salt.plugins.functions.InventoryFun._list_hosts
.. autofunction:: nornir_salt.plugins.functions.InventoryFun._list_hosts_platforms
.. autofunction:: nornir_salt.plugins.functions.InventoryFun._update_defaults
"""
import logging

from .FFun import FFun
from nornir.core.inventory import Host, ConnectionOptions

log = logging.getLogger(__name__)


def _create_host(nr, name, groups=None, connection_options=None, **kwargs):
    """
    Function to add new host in inventory or replace existing host.

    :param nr: (obj) Nornir object
    :param name: (str) host name
    :param groups: (list) list of host's parent group names
    :param connection_options: (dict) connection options dictionary
    :param kwargs: (dict) host base attributes such as hostname, port,
        username, password, platform, data
    :return: True on success

    If group given in ``groups`` list does not exist, no error raised, it simply skipped.
    """
    groups = groups or []
    connection_options = connection_options or {}

    # add new host or replace existing host completely
    nr.inventory.hosts[name] = Host(
        name=name,
        hostname=kwargs.pop("hostname", name),
        defaults=nr.inventory.defaults,
        connection_options={
            cn: ConnectionOptions(
                hostname=c.get("hostname"),
                port=c.get("port"),
                username=c.get("username"),
                password=c.get("password"),
                platform=c.get("platform"),
                extras=c.get("extras"),
            )
            for cn, c in connection_options.items()
        },
        groups=[
            nr.inventory.groups[group_name]
            for group_name in groups
            if group_name in nr.inventory.groups
        ],
        **kwargs
    )

    return {name: True}


def _read_host(nr, **kwargs):
    """
    Function to return inventory content for host(s) using FFun
    function to filter hosts.

    :param nr: (obj) Nornir object
    :param kwargs: (dict) arguments to use with FFun function to filter hosts
    :return: (dict) host(s) inventory dictionary keyed by host name(s)
    """
    hosts = FFun(nr, kwargs=kwargs)
    return hosts.inventory.dict()["hosts"]


def _read_inventory(nr, **kwargs):
    """
    Function to return inventory content using FFun function to filter hosts.

    :param nr: (obj) Nornir object
    :param kwargs: (dict) arguments to use with FFun function to filter hosts
    :return: (dict) inventory dictionary with groups, defaults and hosts
    """
    hosts = FFun(nr, kwargs=kwargs)
    return hosts.inventory.dict()


def _update_host(
    nr,
    name,
    groups=None,
    connection_options=None,
    data=None,
    groups_action="append",
    **kwargs
):
    """
    Function to update host's inventory.

    :param nr: (obj) Nornir object
    :param name: (str) host name
    :param groups: (list) list of host's parent group names
    :param groups_action: (str) what to do with groups - ``append`` (default),
        ``insert`` (prepend) or ``remove``
    :param connection_options: (dict) connection options dictionary
    :param data: (dict) dictionary with host's data
    :param kwargs: (dict) host base attributes such as hostname, port,
        username, password, platform
    :return: True on success

    ``data`` and ``connection_options`` replace existing values for top keys
    similar to dictionary ``update`` method, no recursive merge performed.

    If group given in ``groups`` list does not exist, no error raised, it simply skipped.
    """
    groups = groups or []
    connection_options = connection_options or {}
    data = data or {}

    # do sanity checks
    if groups_action not in ["append", "insert", "remove"]:
        raise ValueError(
            "nornir-salt:InventoryFun groups_action should be append, insert or remove, not '{}'".format(
                groups_action
            )
        )

    # get host object to update
    try:
        host_obj = nr.inventory.hosts[name]
    except KeyError:
        return False
    existing_groups = [g.name for g in host_obj.groups]

    # update base attributes
    host_obj.hostname = kwargs.get("hostname", host_obj.hostname)
    host_obj.platform = kwargs.get("platform", host_obj.platform)
    host_obj.port = kwargs.get("port", host_obj.port)
    host_obj.username = kwargs.get("username", host_obj.username)
    host_obj.password = kwargs.get("password", host_obj.password)

    # update data
    host_obj.data.update(data)

    # update connection options
    for cn, c in connection_options.items():
        host_obj.connection_options[cn] = ConnectionOptions(
            hostname=c.get("hostname"),
            port=c.get("port"),
            username=c.get("username"),
            password=c.get("password"),
            platform=c.get("platform"),
            extras=c.get("extras"),
        )

    # update groups
    for group_name in groups:
        if group_name not in nr.inventory.groups:
            continue
        if groups_action == "append" and group_name not in existing_groups:
            host_obj.groups.append(nr.inventory.groups[group_name])
        elif groups_action == "insert" and group_name not in existing_groups:
            host_obj.groups.insert(0, nr.inventory.groups[group_name])
        elif groups_action == "remove" and group_name in existing_groups:
            host_obj.groups.remove(nr.inventory.groups[group_name])

    return {host_obj.name: True}


def _delete_host(nr, name):
    """
    Function to delete host from inventory.

    :param nr: (obj) Nornir object
    :param name: (str or list) host name or a list of host names to delete
    :return: True on success
    """
    ret = {}
    names = [name] if isinstance(name, str) else name

    for n in names:
        _ = nr.inventory.hosts.pop(n, None)
        ret[n] = True

    return ret


def _load(nr, data):
    """
    Accept a list of items, where each item executed sequentially
    to perform one of the operations to create, update or delete.

    :param data: (list) list of dictionary items to work with
    :param nr: (obj) Nornir Object

    Each list dictionary item should contain ``call`` key holding the name
    of function to call, rest of the dictionary used as a ``**kwargs`` with
    specidfied call function.
    """
    return [fun_dispatcher[item.pop("call")](nr, **item) for item in data]


def _list_hosts(nr, **kwargs):
    """
    Function to return a list of host names contained in inventory.

    Supports filtering using FFun function.

    :param nr: (obj) Nornir object
    :param kwargs: (dict) FFun function arguments to filter hosts
    :return: (list) list of host names
    """
    hosts = FFun(nr, kwargs=kwargs)
    return list(hosts.inventory.hosts.keys())


def _list_hosts_platforms(nr, **kwargs):
    """
    Function to return a dictionary keyed by host names containing platforms details.

    Supports filtering using FFun function.

    :param nr: (obj) Nornir object
    :param kwargs: (dict) FFun function arguments to filter hosts
    :return: (list) list of host names
    """
    hosts = FFun(nr, kwargs=kwargs)
    return {
        host_name: host.platform for host_name, host in hosts.inventory.hosts.items()
    }


def _read_host_data(nr, keys, default=None, **kwargs):
    """
    Function to return hosts data under certain keys.

    :param nr: (obj) Nornir object
    :param keys: list of strings each string a a dot seprated path to data
    :param default: default value to return if key path item not present in host's data
    :return: dictionary keyed by host name with databeing a dictionary keyed by paths

    For example if host has this data::

        hosts:
          nrp1:
            data:
              config:
                interfaces:
                  Lo0:
                    description: foobar
                 bgp:
                   asn: 1234

    if ``keys=["config.interfaces.Lo0", "config.bgp", "ntp.config"]`` this function
    will return::

        {
            "nrp1": {
                "config.interfaces.Lo0": {"description": "foobar"},
                "config.bgp": {"asn": 1234},
                "ntp.config": None
            }
        }

    .. warning:: This function does not support retrievieng individual list items,
        each item in keys path should refer to a data dictionary key.
    """
    ret = {}
    # filter hosts
    hosts = FFun(nr, kwargs=kwargs)
    # iterate over host objects
    for host_name, host_data in hosts.inventory.hosts.items():
        ret[host_name] = {}
        # iterate over path keys
        for key_path in keys:
            reference = host_data
            # iterate over individual key in the path
            for key in [i.strip() for i in key_path.split(".")]:
                reference = reference.get(key, default)
                # stop if encountered default item
                if reference == default:
                    break
            # reference now points to desired piece of data
            ret[host_name][key_path] = reference

    return ret


def _update_defaults(
    nr,
    connection_options: dict = None,
    data: dict = None,
    password: str = ...,
    platform: str = ...,
    port: int = ...,
    username: str = ...,
    **kwargs
) -> bool:
    """
    Function to update defaults inventory.

    :param nr: (obj) Nornir object
    :param connection_options: (dict) dictionary with defaults's
        connection options data to update. Should be keyed by
        connection name with value being a dictionary of connection
        attributes - hostname, port, username, password, platform
        and extras dictionary
    :param data: (dict) dictionary with defaults's data to update
    :param kwargs: (dict) additional key-value pairs to add into
        defaults data
    :return: True on success

    Replaces existing values for top keys similar to dictionary
    ``update`` method, no recursive merge performed.
    """
    data = data or {}
    data = {**data, **kwargs}

    # update defaults data
    if connection_options:
        for name, opts in connection_options.items():
            nr.inventory.defaults.connection_options[name] = ConnectionOptions(
                hostname=opts.get("hostname"),
                port=opts.get("port"),
                username=opts.get("username"),
                password=opts.get("password"),
                platform=opts.get("platform"),
                extras=opts.get("extras"),
            )
    if data:
        nr.inventory.defaults.data.update(data)
    if password is not ...:
        nr.inventory.defaults.password = password
    if port is not ...:
        nr.inventory.defaults.port = port
    if platform is not ...:
        nr.inventory.defaults.platform = platform
    if username is not ...:
        nr.inventory.defaults.username = username

    return True


fun_dispatcher = {
    "create_host": _create_host,
    "update_host": _update_host,
    "delete_host": _delete_host,
    "read_host": _read_host,
    "create": _create_host,
    "update": _update_host,
    "delete": _delete_host,
    "read": _read_host,
    "read_inventory": _read_inventory,
    "read_host_data": _read_host_data,
    "load": _load,
    "list_hosts": _list_hosts,
    "list_hosts_platforms": _list_hosts_platforms,
    "update_defaults": _update_defaults,
}


def InventoryFun(nr, call, **kwargs):
    """
    Dispatcher function to execute one of ``call`` functions.

    :param nr: (obj) Nornir object
    :param call: (str) name of function to call
    :param kwargs: (dict) arguments to pass on to call function
    :returns: call function results

    Supported ``call`` function values:

    - ``create_host`` or ``create`` - calls ``_create_host``, creates new host or replaces existing host object
    - ``read_host`` or ``read`` - calls ``_read_host``, read host inventory content
    - ``update_host`` or ``update`` - calls ``_update_host``, non recursively update host attributes
    - ``delete_host`` or ``delete`` - calls ``_delete_host``, deletes host object from Nornir Inventory
    - ``load`` - calls ``_load``, to simplify calling multiple functions
    - ``read_inventory`` - calls ``_read_inventory``, read inventory content for groups, default and hosts
    - ``read_host_data`` - calls ``_read_host_data`` to return host's data under provided path keys
    - ``list_hosts`` - calls ``_list_hosts``, return a list of inventory's host names
    - ``list_hosts_platforms`` - calls ``_list_hosts_platforms``, return a dictionary of hosts' platforms
    - ``update_defaults`` - calls ``_update_defaults``, non recursively update defaults attributes
    """
    return fun_dispatcher[call](nr, **kwargs)
