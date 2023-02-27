#!/usr/bin/env python3
# Copyright (C) 2022 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Collection, Sequence
from pathlib import Path
from typing import NamedTuple

import pytest


class ChangedFiles(NamedTuple):
    test_all_files: bool
    file_paths: Collection[Path]

    def is_changed(self, path: Path) -> bool:
        return self.test_all_files or str(path) in self.file_paths


def pytest_addoption(parser):
    parser.addoption("--python-files", nargs="*", default=[], help="python files to check")
    parser.addoption("--changed-files", nargs="*", default=[], help="files to check")
    parser.addoption("--test-all-files", action="store_true", help="test all files")


@pytest.fixture
def python_files(request: pytest.FixtureRequest) -> Sequence[str]:
    if not (files := request.config.getoption("--python-files")):
        pytest.skip()
    return files


@pytest.fixture
def changed_files(request: pytest.FixtureRequest) -> ChangedFiles:
    test_all_files = request.config.getoption("--test-all-files")
    files = request.config.getoption("--changed-files")
    if not test_all_files and not files:
        pytest.skip()
    return ChangedFiles(test_all_files=test_all_files, file_paths={Path(f) for f in files})
