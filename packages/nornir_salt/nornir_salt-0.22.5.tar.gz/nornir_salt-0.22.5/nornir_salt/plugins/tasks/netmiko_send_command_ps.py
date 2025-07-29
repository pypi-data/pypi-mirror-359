"""
netmiko_send_command_ps
#######################

Send command string to device using promptless (ps) approach. Can be used for any
command, including commands that change device prompt. Multiple commands can be sent
separated by '\n' newline.

.. image:: ../_images/promptless_mode_v0.1.png

Promptless mode allows to detect end of output from device without relying on timers or
correct prompt matching (hence the name - promptless). This mode still uses pattern to
decide if device finished emitting data, but that pattern is not dependent on device's prompt
regex matching.

Each reading cycle, data from device read as fast as possible until device either finishes or
pose to prepare more data. Latter case detected and handled using read timeout timer and checking
if new data received. To detect when device finishes producing output, algorithm sends two space
character to device and checks in next read cycle if last line contains two additional spaces,
concluding that end of output detected if so and continue cycling otherwise.

Overall its similar to how Humans interact with device prompt to verify that its still operational
- try hitting space or type something in terminal to see if its appears on the screen.

Dependencies:

* `nornir-netmiko module <https://pypi.org/project/nornir-netmiko/>`_ required

netmiko_send_command_ps sample usage
=====================================

Code to invoke ``netmiko_send_command_ps`` task::

    from nornir import InitNornir
    from nornir_salt.plugins.tasks import netmiko_send_command_ps

    nr = InitNornir(config_file="config.yaml")

    commands = '''
    show ip int brief
    conf t
    interface loopback 100
    ip address 1.1.1.100 255.255.255.255
    end
    show ip int brief
    write
    '''

    output = nr.run(
        task=netmiko_send_command_ps,
        commands="show run",
        netmiko_kwargs={}
    )

    output_multiline = nr.run(
        task=netmiko_send_command_ps,
        commands=commands,
        netmiko_kwargs={}
    )

netmiko_send_command_ps returns
================================

Returns Nornir results object with individual tasks names set
equal to commands sent to device.

netmiko_send_command_ps reference
==================================

.. autofunction:: nornir_salt.plugins.tasks.netmiko_send_command_ps.netmiko_send_command_ps
.. autofunction:: nornir_salt.plugins.tasks.netmiko_send_command_ps.send_command_ps
"""

import time
import logging
from typing import Any
from nornir.core.task import Result, Task
from difflib import get_close_matches

try:
    from nornir_netmiko.connections import CONNECTION_NAME

    HAS_NETMIKO = True
except ImportError:
    HAS_NETMIKO = False

log = logging.getLogger(__name__)


def send_command_ps(
    self,
    command_string: str,
    read_timeout: int = 30,
    timeout: int = 120,
    inter_loop_sleep: float = 0.1,
    initial_sleep: float = 0.1,
    strip_prompt: bool = True,
    strip_command: bool = True,
    normalize: bool = True,
    cutoff: float = 0.6,
    nowait: bool = False,
):
    """
    Execute command_string_ps on the SSH channel using promptless (ps) approach. Can be used
    for any commands, including commands that change prompt. Multiple commands can be sent
    separated by '\\n' newline.

    :param command_string: (str) The command(s) to be executed on the remote device.
    :param read_timeout: (int) Timeout in seconds to wait for data from devices, default 30s, if
        set to -1 will wait indefinitely
    :param timeout: (int) Absolute timeout in seconds of overall wait, default 120s, if
        set to -1 will wait indefinitely
    :param inter_loop_sleep: (int) Interval in seconds to sleep between reading loops, default 0.1s
    :param initial_sleep: (int) time to sleep after sending command, default 0.1s
    :param strip_prompt: (bool) Remove the trailing router prompt from the output (default: True).
    :param strip_command: (bool) Remove the echo of the command from the output (default: True).
    :param normalize: (bool) Ensure the proper enter is sent at end of command (default: True).
    :param cutoff: (int) used as difflib get_close_matches cutoff argument to check if last line
        looks similar to any previously seen prompts, default is 0.6
    :param nowait: (bool) Default is False, if True sends command and returns immediately without
        waiting for prompt right after ``initial_sleep`` timer elapsed.
    """
    data_received = ""
    previous_last_line = ""
    no_data_elapsed = 0
    start_time = time.time()

    # add a list of previously matched last lines
    if not hasattr(self, "prompts_seen"):
        self.prompts_seen = set([self.find_prompt().strip()])
        time.sleep(
            3
        )  # need to wait for device to emit find_prompt() output so that self.clear_buffer() can catch it
        log.debug(
            "send_command_ps formed prompts_seen set: {}".format(self.prompts_seen)
        )

    if normalize:
        command_string = self.normalize_cmd(command_string)

    self.clear_buffer()
    self.write_channel(command_string)

    # initial sleep
    time.sleep(initial_sleep)

    # check if need to return immediately after sending commands
    if nowait:
        return "DONE"

    # Main loop to get output from device
    while True:
        if read_timeout != -1 and no_data_elapsed > read_timeout:
            raise TimeoutError(
                "send_command_ps {}s read_timeout expired".format(read_timeout)
            )
        if timeout != -1 and (time.time() - start_time) > timeout:
            raise TimeoutError("send_command_ps {}s timeout expired".format(timeout))

        time.sleep(inter_loop_sleep)
        no_data_elapsed += inter_loop_sleep

        # read data from channel for netmiko 3
        if hasattr(self, "_read_channel"):
            chunk = self._read_channel()
        # read data from channel for netmiko 4
        else:
            chunk = self.read_channel()
        if chunk:
            no_data_elapsed = 0
            data_received += chunk
            new_last_line = data_received.splitlines()[-1]
        else:
            continue

        # junos returns \x07 instead of space, replace it with spaces
        if "\x07" in new_last_line:
            new_last_line = new_last_line.replace("\x07", " ")

        # check if new_last_line looks similar to any of the previous device prompts
        matched = get_close_matches(
            new_last_line.strip(), list(self.prompts_seen), 1, cutoff
        )
        log.debug(
            "send_command_ps: last line '{}' similar prompt - '{}'".format(
                new_last_line.strip(), matched
            )
        )
        if matched:
            # Detect end of output by sending two space chars and checking if received it back in next cycle
            is_end = "{}  ".format(previous_last_line) == new_last_line
            log.debug(
                "send_command_ps: EOF detection - new_last_line: '{}'; previous_last_line: {}; is_end: {}".format(
                    [new_last_line], [previous_last_line], is_end
                )
            )
            if is_end:
                self.prompts_seen.add(new_last_line.strip())
                break
            previous_last_line = new_last_line
            self.write_channel("  ")
    output = self._sanitize_output(
        data_received,
        strip_command=strip_command,
        command_string=command_string,
        strip_prompt=strip_prompt,
    )
    return output


def netmiko_send_command_ps(
    task: Task, command_string: str, enable: bool = False, **kwargs: Any
) -> Result:
    """
    Patch netmiko connection object with send_command_ps method and
    execute it.

    :param command_string: (str) Command to execute on the remote network device.
    :param enable: (bool) Set to True to force Netmiko .enable() call.
    :param kwargs: (dict) Additional arguments to pass to send_command_ps method.
    :return result object: with result of the show command
    """
    net_connect = task.host.get_connection(CONNECTION_NAME, task.nornir.config)
    if enable:
        net_connect.enable()

    if "send_command_ps" not in dir(net_connect):
        setattr(net_connect, "send_command_ps", send_command_ps)

    result = net_connect.send_command_ps(net_connect, command_string, **kwargs)
    return Result(host=task.host, result=result)
