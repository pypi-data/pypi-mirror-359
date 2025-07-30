# SPDX-FileCopyrightText: 2025 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for :func:`elements_http_upload.upload.resolve_uploads`."""

from pathlib import Path

import pytest

from elements_http_upload.models import FileUpload
from elements_http_upload.upload import resolve_uploads


def test_single_file(test_file: Path) -> None:
    upload = FileUpload(source=test_file, target=Path("/some/remote/path"))
    assert resolve_uploads(upload) == [upload]


def test_missing_root(test_file: Path) -> None:
    upload = FileUpload(source=test_file)
    with pytest.raises(ValueError):
        resolve_uploads(upload)


def test_missing_absolute(test_file: Path) -> None:
    upload = FileUpload(source=test_file, target=Path("some/relative/path"))
    with pytest.raises(ValueError):
        resolve_uploads(upload)


def test_recursive(isolated_test_file: Path, tmp_path) -> None:
    upload = FileUpload(
        source=isolated_test_file.parent, target=Path("/some/remote/path")
    )
    resolved = resolve_uploads(upload, recursive=True)
    assert len(resolved) == 1
    assert resolved[0].source == isolated_test_file
    assert (
        resolved[0].target
        == Path("/some/remote/path/") / isolated_test_file.name
    )


def test_missing_recursive(test_file: Path) -> None:
    upload = FileUpload(
        source=test_file.parent, target=Path("/some/remote/path")
    )
    with pytest.raises(IOError):
        resolve_uploads(upload)
