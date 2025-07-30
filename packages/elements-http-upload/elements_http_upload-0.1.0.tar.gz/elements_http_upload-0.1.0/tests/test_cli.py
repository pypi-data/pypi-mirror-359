# SPDX-FileCopyrightText: 2025 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: Apache-2.0

"""Test module for the command-line interface."""

import subprocess as spr
import sys
from pathlib import Path


def test_cli_upload(
    isolated_test_file: Path, remote_test_folder: Path, upload_settings
) -> None:
    """Test upload a file to a folder."""
    spr.check_call(
        [
            sys.executable,
            "-m",
            "elements_http_upload",
            f"{isolated_test_file}:{remote_test_folder}/",
        ]
    )


def test_cli_upload_skip_certs(
    isolated_test_file: Path, remote_test_folder: Path, upload_settings
) -> None:
    """Test upload a file to a folder."""
    spr.check_call(
        [
            sys.executable,
            "-m",
            "elements_http_upload",
            "--no-verify",
            f"{isolated_test_file}:{remote_test_folder}/",
        ]
    )


def test_cli_upload_explicit_name(
    isolated_test_file: Path, remote_test_folder: Path, upload_settings
) -> None:
    """Test upload with explicit name."""
    spr.check_call(
        [
            sys.executable,
            "-m",
            "elements_http_upload",
            f"{isolated_test_file}:{remote_test_folder}/{isolated_test_file.name}",
        ]
    )


def test_cli_upload_recursive(
    isolated_test_file: Path, remote_test_folder: Path, upload_settings
) -> None:
    """Test recursive upload."""
    spr.check_call(
        [
            sys.executable,
            "-m",
            "elements_http_upload",
            "-r",
            f"{isolated_test_file.parent}:{remote_test_folder}",
        ]
    )
