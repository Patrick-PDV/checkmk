#!/usr/bin/env python3
# Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
"""server side component to create the special agent call"""

from collections.abc import Iterator, Mapping
from typing import Literal

from pydantic import BaseModel

from cmk.server_side_calls.v1 import (
    HostConfig,
    Secret,
    SpecialAgentCommand,
    SpecialAgentConfig,
)


class ParamsRedfish(BaseModel):
    user: str
    password: Secret
    fetching: Mapping[
        str,
        tuple[Literal["always", "cached", "never"], float],
    ]
    port: int
    proto: Literal["http", "https"]
    retries: int
    timeout: float
    debug: bool


class ParamsRedfishPower(BaseModel):
    user: str
    password: Secret
    port: int
    proto: Literal["http", "https"]
    retries: int
    timeout: float


def _agent_redfish_arguments(
    params: ParamsRedfish, host_config: HostConfig
) -> Iterator[SpecialAgentCommand]:
    enabled_sections = (s for s, (mode, _) in params.fetching.items() if mode != "never")
    disabled_sections = (s for s, (mode, _) in params.fetching.items() if mode == "never")
    cached_sections = (
        f"{name}-{int(interval)}"
        for name, (mode, interval) in params.fetching.items()
        if mode == "cached"
    )

    yield SpecialAgentCommand(
        command_arguments=[
            "-u",
            params.user,
            "--password-id",
            params.password,
            "-p",
            str(params.port),
            "-P",
            params.proto,
            "-m",
            ",".join(enabled_sections),
            "-n",
            ",".join(disabled_sections),
            "-c",
            ",".join(cached_sections),
            "--timeout",
            str(params.timeout),
            "--retries",
            str(params.retries),
            *(("--debug",) if params.debug else ()),
            host_config.primary_ip_config.address or host_config.name,
        ]
    )


special_agent_redfish = SpecialAgentConfig(
    name="redfish",
    parameter_parser=ParamsRedfish.model_validate,
    commands_function=_agent_redfish_arguments,
)


def _agent_redfish_power_arguments(
    params: ParamsRedfishPower, host_config: HostConfig
) -> Iterator[SpecialAgentCommand]:
    yield SpecialAgentCommand(
        command_arguments=[
            "-u",
            params.user,
            "--password-id",
            params.password,
            "-p",
            str(params.port),
            "-P",
            params.proto,
            "--timeout",
            str(params.timeout),
            "--retries",
            str(params.retries),
            host_config.primary_ip_config.address or host_config.name,
        ]
    )


special_agent_redfish_power = SpecialAgentConfig(
    name="redfish_power",
    parameter_parser=ParamsRedfishPower.model_validate,
    commands_function=_agent_redfish_power_arguments,
)
