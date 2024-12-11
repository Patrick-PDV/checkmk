#!/usr/bin/env python3
# Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from typing import Any, Dict, Mapping

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
)
from cmk.plugins.redfish.lib import parse_redfish, redfish_health_state, RedfishAPIData

Section = Dict[str, Mapping[str, Any]]


agent_section_apt = AgentSection(
    name="redfish_system",
    parse_function=parse_redfish,
    parsed_section_name="redfish_system",
)


def discover_redfish_system(section: RedfishAPIData) -> DiscoveryResult:
    if not section:
        return
    if len(section) == 1:
        yield Service(item="state")
    else:
        for element in section:
            # FIXME: If this works, the section must look completely different
            item = f"state {element.get('Id', '0')}"  # type: ignore[attr-defined]
            yield Service(item=item)


def check_redfish_system(item: str, section: RedfishAPIData) -> CheckResult:
    if not section:
        return
    data = None
    if len(section) == 1:
        # FIXME: If this works, the section must look completely different
        data = section[0]  # type: ignore[index]
    else:
        for element in section:
            if f"state {element.get('Id')}" == item:  # type: ignore[attr-defined]
                data = element
                break

    if not data:
        return

    state = data.get("Status", {"Health": "Unknown"})
    result_state, state_text = redfish_health_state(state)
    message = f"System with SerialNr: {data.get('SerialNumber')}, has State: {state_text}"

    yield Result(state=State(result_state), summary=message)


check_plugin_redfish_system = CheckPlugin(
    name="redfish_system",
    service_name="System %s",
    sections=["redfish_system"],
    discovery_function=discover_redfish_system,
    check_function=check_redfish_system,
)
