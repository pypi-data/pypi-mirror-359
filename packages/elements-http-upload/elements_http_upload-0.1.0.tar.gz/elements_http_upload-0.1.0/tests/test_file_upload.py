# SPDX-FileCopyrightText: 2025 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: Apache-2.0

"""Test for the upload process."""

from elements_http_upload.models import FileUpload, UploadSettings
from elements_http_upload.upload import UploadProcess


def test_upload(
    test_upload: FileUpload, upload_settings: UploadSettings
) -> None:
    """Test uploading a single file."""
    upload_process = UploadProcess(upload_settings, test_upload)
    upload_process.start()
