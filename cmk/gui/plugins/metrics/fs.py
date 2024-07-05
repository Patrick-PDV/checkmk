#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.gui.graphing._utils import graph_info, metric_info
from cmk.gui.i18n import _

# .
#   .--Metrics-------------------------------------------------------------.
#   |                   __  __      _        _                             |
#   |                  |  \/  | ___| |_ _ __(_) ___ ___                    |
#   |                  | |\/| |/ _ \ __| '__| |/ __/ __|                   |
#   |                  | |  | |  __/ |_| |  | | (__\__ \                   |
#   |                  |_|  |_|\___|\__|_|  |_|\___|___/                   |
#   |                                                                      |
#   +----------------------------------------------------------------------+
#   |  Definitions of metrics                                              |
#   '----------------------------------------------------------------------'

# Title are always lower case - except the first character!
# Colors: See indexed_color() in cmk/gui/plugins/metrics/utils.py

metric_info["fs_growth"] = {
    "title": _("Growth"),
    "unit": "bytes/d",
    "color": "#29cfaa",
}

metric_info["fs_trend"] = {
    "title": _("Growth trend"),
    "unit": "bytes/d",
    "color": "#808080",
}

# .
#   .--Graphs--------------------------------------------------------------.
#   |                    ____                 _                            |
#   |                   / ___|_ __ __ _ _ __ | |__  ___                    |
#   |                  | |  _| '__/ _` | '_ \| '_ \/ __|                   |
#   |                  | |_| | | | (_| | |_) | | | \__ \                   |
#   |                   \____|_|  \__,_| .__/|_| |_|___/                   |
#   |                                  |_|                                 |
#   +----------------------------------------------------------------------+
#   |  Definitions of time series graphs                                   |
#   '----------------------------------------------------------------------'

graph_info["growing"] = {
    "title": _("Growing"),
    "metrics": [
        (
            "fs_growth.max,0,MAX",
            "area",
            _("Growth"),
        ),
    ],
}

graph_info["shrinking"] = {
    "title": _("Shrinking"),
    "consolidation_function": "min",
    "metrics": [
        ("fs_growth.min,0,MIN,-1,*#299dcf", "-area", _("Shrinkage")),
    ],
}

graph_info["fs_trend"] = {
    "title": _("Growth trend"),
    "metrics": [
        ("fs_trend", "line"),
    ],
}
