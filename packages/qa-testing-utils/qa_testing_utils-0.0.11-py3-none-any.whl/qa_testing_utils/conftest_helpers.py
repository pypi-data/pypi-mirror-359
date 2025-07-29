# SPDX-FileCopyrightText: 2025 Adrian Herscu
#
# SPDX-License-Identifier: Apache-2.0

import inspect
import logging.config
import sys
from pathlib import Path

import pytest


def configure(config: pytest.Config,
              path: Path = Path(__file__).parent / "logging.ini") -> None:
    """
    Configures logging for pytest using a specified INI file, or defaults to internal logging.ini.

    Args:
        config (pytest.Config): The pytest configuration object.
        path (Path, optional): Path to the logging configuration file. Defaults to 'logging.ini' in the current directory.
    """
    caller_module = inspect.getmodule(inspect.stack()[1][0])
    module_name = caller_module.__name__ if caller_module else "unknown"

    if path.is_file():
        logging.config.fileConfig(path)
        logging.info(f"{module_name} loaded logs config from: {path}")
    else:
        sys.stderr.write(f"{module_name} couldn't find logs config file {path}")


def makereport(
        item: pytest.Item, call: pytest.CallInfo[None]) -> pytest.TestReport:
    """
    Creates a pytest test report and appends the test body source code to the report sections.

    Args:
        item (pytest.Item): The pytest test item.
        call (pytest.CallInfo[None]): The call information for the test.
    Returns:
        pytest.TestReport: The generated test report with the test body included.
    """
    report = pytest.TestReport.from_item_and_call(item, call)

    if call.when == "call":
        report.sections.append(('body', get_test_body(item)))

    return report


def get_test_body(item: pytest.Item) -> str:
    """
    Retrieves the source code of the test function for the given pytest item.

    Args:
        item (pytest.Item): The pytest test item.
    Returns:
        str: The source code of the test function, or an error message if unavailable.
    """
    function = getattr(item, 'function', None)
    if function is None:
        return "No function found for this test item."

    try:
        return inspect.getsource(function)
    except Exception as e:
        return f"Could not get source code: {str(e)}"
