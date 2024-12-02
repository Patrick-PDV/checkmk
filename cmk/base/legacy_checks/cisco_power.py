#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


# mypy: disable-error-code="var-annotated"

from cmk.base.check_api import LegacyCheckDefinition
from cmk.base.config import check_info

from cmk.agent_based.v2 import OIDEnd, SNMPTree, StringTable
from cmk.plugins.lib.cisco import DETECT_CISCO

# .1.3.6.1.4.1.9.9.13.1.5.1.2.1 "removed"
# .1.3.6.1.4.1.9.9.13.1.5.1.2.2 "AC Power Supply"
# .1.3.6.1.4.1.9.9.13.1.5.1.3.1 5
# .1.3.6.1.4.1.9.9.13.1.5.1.3.2 1
# .1.3.6.1.4.1.9.9.13.1.5.1.4.1 1
# .1.3.6.1.4.1.9.9.13.1.5.1.4.2 2

cisco_power_states = (
    "",
    "normal",
    "warning",
    "critical",
    "shutdown",
    "not present",
    "not functioning",
)

cisco_power_sources = (
    "",
    "unknown",
    "AC",
    "DC",
    "external power supply",
    "internal redundant",
)


def item_name_from(description: str) -> str:
    """Returns a combination from device description and OID index which can
    be used as service item name.
    >>> item_name_from("")
    'supply'
    >>> item_name_from("removed")
    'removed'
    >>> item_name_from("Switch#1, PowerSupply#1, Status is Normal, RPS Not Present")
    'Switch 1 PowerSupply 1'
    >>> item_name_from("Sw1, PS1 Normal, RPS NotExist")
    'Sw1 PS1'
    >>> item_name_from("Switch 1 - Power Supply A, Normal")
    'Switch 1 - Power Supply A'
    >>> item_name_from("Sw1, PSA Normal")
    'Sw1 PSA'
    >>> item_name_from("Switch#1, PowerSupply 1")
    'Switch 1 PowerSupply 1'
    """
    # The 'description part' of given description string which might
    # contain extra status information (comma separated) or might even be empty
    # description can be, depending on the device model.
    if len(splitted := [x.strip() for x in description.split(",")]) == 1:
        device_description = description
    elif "#" in splitted[-1] or "Power" in splitted[-1]:
        device_description = " ".join(splitted)
    elif splitted[-1].startswith("PS"):
        device_description = " ".join([splitted[0], splitted[-1].split(" ")[0]])
    elif splitted[-2].startswith("PS"):
        device_description = " ".join(splitted[:-2] + splitted[-2].split(" ")[:-1])
    elif splitted[-2].startswith("Status"):
        device_description = " ".join(splitted[:-2])
    else:
        device_description = " ".join(splitted[:-1])

    return device_description.replace("#", " ") or "supply"


def inventory_cisco_power(info):
    # Note: the name of the power supply is not unique. We have seen
    # a Cisco with four entries in the MIB. So we force uniqueness
    # by appending a "/4" for ID 4 if the name is not unique
    discovered = {}
    for sid, textinfo in (head for *head, state, _source in info if state != "5"):
        discovered.setdefault(item_name_from(textinfo), []).append(sid)

    for name, entries in discovered.items():
        if len(entries) == 1:
            yield name, None
        else:
            yield from ((f"{name} {entry}", None) for entry in entries)


def check_cisco_power(item, _no_params, info):
    for sid, textinfo, state, source in info:
        item_name_base = item_name_from(textinfo)
        if item in (item_name_base, f"{item_name_base} {sid}", f"{item_name_base}/{sid}"):
            state_str = cisco_power_states[int(state)]
            source_str = cisco_power_sources[int(source)]
            return (
                0 if state == 1 else 1 if state == 2 else 2,
                f"Status: {state_str}, Source: {source_str}",
            )
    return None


def parse_cisco_power(string_table: StringTable) -> StringTable:
    return string_table


check_info["cisco_power"] = LegacyCheckDefinition(
    parse_function=parse_cisco_power,
    detect=DETECT_CISCO,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.9.9.13.1.5.1",
        oids=[
            OIDEnd(),  # becomes SID
            "2",  # textinfo
            "3",  # state
            "4",  # source
        ],
    ),
    service_name="Power %s",
    discovery_function=inventory_cisco_power,
    check_function=check_cisco_power,
)
