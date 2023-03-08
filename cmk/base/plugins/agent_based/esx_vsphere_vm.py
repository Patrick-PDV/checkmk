#!/usr/bin/env python3
# Copyright (C) 2022 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from typing import Dict, List, Mapping, Sequence

from .agent_based_api.v1 import HostLabel, register
from .agent_based_api.v1.type_defs import HostLabelGenerator, StringTable
from .utils.esx_vsphere import (
    ESXCpu,
    ESXDataStore,
    ESXMemory,
    ESXStatus,
    ESXVm,
    HeartBeat,
    HeartBeatStatus,
    SectionVM,
)


def parse_esx_vsphere_vm(string_table: StringTable) -> SectionVM:
    grouped_values: Dict[str, List[str]] = {}
    for line in string_table:
        # Do not monitor VM templates
        if line[0] == "config.template" and line[1] == "true":
            return None
        grouped_values[line[0]] = line[1:]

    return ESXVm(
        mounted_devices=grouped_values.get("config.hardware.device", []),
        snapshots=grouped_values.get("snapshot.rootSnapshotList", []),
        status=_parse_vm_status(grouped_values),
        heartbeat=_parse_esx_vm_heartbeat_status(grouped_values),
        power_state=_parse_esx_power_state(grouped_values),
        memory=_parse_esx_memory_section(grouped_values),
        cpu=_parse_esx_cpu_section(grouped_values),
        datastores=_parse_esx_datastore_section(grouped_values),
        host=_parse_esx_vm_running_on_host(grouped_values),
        name=_parse_esx_vm_name(grouped_values),
    )


def _parse_vm_status(vm_values: Mapping[str, Sequence[str]]) -> ESXStatus | None:
    if "guest.toolsVersionStatus" not in vm_values:
        return None
    return ESXStatus(vm_values["guest.toolsVersionStatus"][0])


def _parse_esx_vm_name(vm_values: Mapping[str, Sequence]) -> str | None:
    if "name" not in vm_values:
        return None

    return " ".join(vm_values["name"])


def _parse_esx_vm_heartbeat_status(vm_values: Mapping[str, Sequence[str]]) -> HeartBeat | None:
    if "guestHeartbeatStatus" not in vm_values:
        return None

    value = vm_values["guestHeartbeatStatus"][0]
    try:
        vm_status = HeartBeatStatus(value.upper())
    except ValueError:
        vm_status = HeartBeatStatus.UNKNOWN

    return HeartBeat(status=vm_status, value=value)


def _parse_esx_vm_running_on_host(vm_values: Mapping[str, Sequence[str]]) -> str | None:
    if (running_on := vm_values.get("runtime.host")) is None:
        return None

    return running_on[0]


def _parse_esx_power_state(vm_values: Mapping[str, Sequence[str]]) -> str | None:
    if "runtime.powerState" not in vm_values:
        return None
    return vm_values["runtime.powerState"][0]


def _parse_esx_memory_section(vm_values: Mapping[str, Sequence[str]]) -> ESXMemory | None:
    """Parse memory specific values from ESX VSphere VM agent output"""
    memory_mapping = {
        "hostMemoryUsage": "host_usage",
        "guestMemoryUsage": "guest_usage",
        "balloonedMemory": "ballooned",
        "sharedMemory": "shared",
        "privateMemory": "private",
    }

    memory_values = {}
    for memory_type in memory_mapping:
        try:
            value = float(vm_values[f"summary.quickStats.{memory_type}"][0])
        except (KeyError, TypeError, ValueError):
            return None

        memory_values[memory_mapping[memory_type]] = value * 1024**2
    return ESXMemory(**memory_values)


def _parse_esx_cpu_section(vm_values: Mapping[str, Sequence[str]]) -> ESXCpu | None:
    """Parse cpu specific values from ESX VSphere VM agent output"""
    try:
        return ESXCpu(
            overall_usage=int(vm_values["summary.quickStats.overallCpuUsage"][0]),
            cpus_count=int(vm_values["config.hardware.numCPU"][0]),
            cores_per_socket=int(vm_values["config.hardware.numCoresPerSocket"][0]),
        )
    except (KeyError, IndexError):
        return None


def _parse_esx_datastore_section(
    vm_values: Mapping[str, Sequence[str]]
) -> List[ESXDataStore] | None:
    """Parse datastores specific values

    # datastore_entries looks like:
        ['url /vmfs/volumes/513df1e9-12fd7366-ac5a-e41f13e69eaa',
        'uncommitted 51973812224',
        'name zmucvm99-lds',
        'type VMFS',
        'accessible true',
        'capacity 578478407680',
        'freeSpace 68779245568']
    """
    if (datastore_urls := vm_values.get("config.datastoreUrl")) is None:
        return None

    stores = []
    for datastore_url in " ".join(datastore_urls).split("@@"):
        datastore_entries = datastore_url.split("|")
        datastore_details = dict(x.split(" ", 1) for x in datastore_entries)
        free_space = float(datastore_details.get("freeSpace", 0))
        stores.append(
            ESXDataStore(
                name=datastore_details["name"],
                capacity=float(datastore_details.get("capacity", 0)),
                free_space=free_space,
            )
        )
    return stores


def host_label_esx_vshpere_vm(section: SectionVM) -> HostLabelGenerator:
    """Host label function

    Labels:

        cmk/vsphere_object:
            This label is set to "vcenter" if the corresponding host is a
            VMware vCenter, to "server" if the host is an ESXi hostsystem
            and to "vm" if the host is a virtual machine.

    """
    if section and section.host is not None:
        yield HostLabel("cmk/vsphere_object", "vm")


register.agent_section(
    name="esx_vsphere_vm",
    parse_function=parse_esx_vsphere_vm,
    host_label_function=host_label_esx_vshpere_vm,
)
