#!/usr/bin/env python3
# Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.graphing.v1 import metrics, perfometers, Title

UNIT_PER_SECOND = metrics.Unit(metrics.DecimalNotation("/s"))

metric_disk_ios = metrics.Metric(
    name="disk_ios",
    title=Title("Disk I/O operations"),
    unit=UNIT_PER_SECOND,
    color=metrics.Color.BLUE,
)

perfometer_disk_ios = perfometers.Perfometer(
    name="disk_ios",
    focus_range=perfometers.FocusRange(
        perfometers.Closed(0),
        perfometers.Open(60),
    ),
    segments=["disk_ios"],
)
