"""
ToFileProcessor Plugin
######################

Processor plugin to save task execution results to file.

ToFileProcessor Sample Usage
============================

Code to demonstrate how to use ``ToFileProcessor`` plugin::

    from nornir import InitNornir
    from nornir_netmiko import netmiko_send_command
    from nornir_salt.plugins.processors import ToFileProcessor

    nr = InitNornir(config_file="config.yaml")

    nr_with_processor = nr.with_processors([
        ToFileProcessor(tf="config", base_url="./Output/")
    ])

    nr_with_processor.run(
        task=netmiko_send_command,
        command_string="show run"
    )

ToFileProcessor reference
=========================

.. autofunction:: nornir_salt.plugins.processors.ToFileProcessor.ToFileProcessor
"""
import logging
import time
import os
import json
import traceback
import random

from nornir.core.inventory import Host
from nornir.core.task import AggregatedResult, MultiResult, Task
from multiprocessing import Lock

log = logging.getLogger(__name__)


class ToFileProcessor:
    """
    ToFileProcessor can save task execution results to file on a per host basis.
    If multiple tasks present, results of all of them saved in same file.

    :param tf: (str) name of the file groups content
    :param base_url: (str) OS path to folder where to save files, default "/var/nornir-salt/"
    :param max_files: (int) default is 5, maximum number of file for given ``tf`` file group
    :param index: (str) index filename to read and store files data into
    :param skip_failed: (bool) if True, do not save failed task results, default is False
    :param tf_index_lock: Lock object to safely access and update files index to make files
        saving operation thread and/or multiprocessing safe

    Files saved under ``base_url`` location, where individual filename formed using string::

        {tf}__{timestamp}__{rand}__{hostname}.txt

    Where:

    * tf - value of ``tf`` attribute
    * timestamp - ``%d_%B_%Y_%H_%M_%S`` time formatted string, e.g. "12_June_2021_21_48_11"
    * rand - random integer in range from 10 to 1000
    * hostname - ``name`` attribute of host

    In addition, ``tf_index_{index}.json`` file created under ``base_url`` to track files created
    using dictionary structure::

        {
            "facts": {
                "ceos1": [
                    {
                        "filename": "/var/salt-nornir/nrp1/files/facts__10_June_2022_13_42_36__683__ceos1.txt",
                        "tasks": {
                            "run_ttp": {
                                "content_type": "json",
                                "span": [0, 139]
                            }
                        },
                        "timestamp": "10 Jun 2022 13:42:36 UTC"
                    }
                ]
            },
            "show_clock_output": {
                "ceos1": [
                    {
                        "filename": "/var/salt-nornir/nrp1/files/show_clock_output__10_June_2022_14_34_20__1__ceos1.txt",
                        "tasks": {
                            "show clock": {
                                "content_type": "str",
                                "span": [0, 59]
                            }
                        },
                        "timestamp": "10 Jun 2022 14:34:20 UTC"
                    },
                ]
            }
        }

    Where ``config`` is ``tf`` attribute value, ``"show run | inc ntp": [0, 48]`` -
    ``show run | inc ntp`` task results span indexes inside
    ``./tofile_outputs/config__22_August_2021_14_08_33__IOL1.txt`` text file.

    ``tf_index_{index}.json`` used by other plugins to retrieve previous results for the task,
    it could be considered as a simplified index database.
    """

    def __init__(
        self,
        tf,
        base_url="/var/nornir-salt/",
        max_files=5,
        index=None,
        skip_failed=False,
        tf_index_lock=None,
    ):
        self.tf = tf
        self.base_url = base_url
        self.max_files = max(1, max_files)
        self.index = index or "common"
        self.skip_failed = skip_failed
        self.tf_index_lock = tf_index_lock or Lock()

        self.aliases_file = os.path.join(
            base_url, "tf_index_{}.json".format(self.index)
        )
        self.aliases_data = {}  # dictionary to store tf_index_{index}.json content

    def _load_aliases(self):
        # create aliases file if does not exist
        if not os.path.exists(self.aliases_file):
            os.makedirs(os.path.dirname(self.aliases_file), exist_ok=True)
            with open(self.aliases_file, mode="w", encoding="utf-8") as f:
                f.write(json.dumps({}))

        # load aliases data
        with open(self.aliases_file, mode="r", encoding="utf-8") as f:
            self.aliases_data = json.loads(f.read())

    def _dump_aliases(self):
        with open(self.aliases_file, mode="w", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    self.aliases_data, sort_keys=True, indent=4, separators=(",", ": ")
                )
            )

    def task_started(self, task: Task) -> None:
        pass  # ignore

    def task_instance_started(self, task: Task, host: Host) -> None:
        pass  # ignore

    def task_instance_completed(
        self, task: Task, host: Host, result: MultiResult
    ) -> None:
        """save to file on a per-host basis"""
        if result.failed and self.skip_failed:
            log.warning(
                "nornir_salt:ToFileProcessor '{}' has failed tasks and skip_failed is True, do nothing, return".format(
                    host.name
                )
            )
            return

        # lock the index from overwrite
        self.tf_index_lock.acquire()

        try:
            # load filegroups data into memory
            self._load_aliases()

            host_filename = "{tf}__{timestamp}__{rand}__{hostname}.txt".format(
                timestamp=time.strftime("%d_%B_%Y_%H_%M_%S"),
                rand=random.randint(0, 1000),  # nosec
                hostname=host.name,
                tf=self.tf,
            )
            host_filename = os.path.join(self.base_url, host_filename)

            # add aliases data
            self.aliases_data.setdefault(self.tf, {})
            self.aliases_data[self.tf].setdefault(host.name, [])

            # save data to file and populate alias details for tasks
            os.makedirs(os.path.dirname(host_filename), exist_ok=True)
            with open(host_filename, mode="w", encoding="utf-8") as f:
                self.aliases_data[self.tf][host.name].insert(
                    0,
                    {
                        "filename": host_filename,
                        "tasks": {},
                        "timestamp": time.strftime("%d %b %Y %H:%M:%S %Z"),
                    },
                )
                span_start = 0

                for i in result:
                    # skip if has skip_results and no exception
                    if (
                        hasattr(i, "skip_results")
                        and i.skip_results is True
                        and not i.exception
                    ):
                        continue
                    # skip if has exception but skip_failed is True
                    if i.exception and self.skip_failed:
                        continue

                    # save results to file
                    if isinstance(i.result, (str, int, float, bool)):
                        result_to_save = str(i.result)
                        self.aliases_data[self.tf][host.name][0]["tasks"][i.name] = {
                            "content_type": "str"
                        }
                    # convert structured data to json
                    else:
                        result_to_save = json.dumps(
                            i.result, sort_keys=True, indent=4, separators=(",", ": ")
                        )
                        self.aliases_data[self.tf][host.name][0]["tasks"][i.name] = {
                            "content_type": "json"
                        }
                    f.write(result_to_save + "\n")

                    # add aliases data
                    span = (span_start, span_start + len(result_to_save) + 1)
                    self.aliases_data[self.tf][host.name][0]["tasks"][i.name][
                        "span"
                    ] = span
                    span_start += len(result_to_save) + 1  # f.write appends \n hence +1

            # check if need to delete old files
            if len(self.aliases_data[self.tf][host.name]) > self.max_files:
                file_to_rm = self.aliases_data[self.tf][host.name].pop(-1)
                try:
                    os.remove(file_to_rm["filename"])
                except:
                    log.error(
                        "nornir-salt:ToFileProcessor failed to remove file '{}':\n{}".format(
                            file_to_rm, traceback.format_exc()
                        )
                    )

            # save data to index file
            self._dump_aliases()
        except Exception as e:
            raise e
        finally:
            self.tf_index_lock.release()

    def subtask_instance_started(self, task: Task, host: Host) -> None:
        pass  # ignore subtasks

    def subtask_instance_completed(
        self, task: Task, host: Host, result: MultiResult
    ) -> None:
        pass  # ignore subtasks

    def task_completed(self, task: Task, result: AggregatedResult) -> None:
        pass
