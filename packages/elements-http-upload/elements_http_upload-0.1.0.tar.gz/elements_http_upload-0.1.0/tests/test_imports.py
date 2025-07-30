# SPDX-FileCopyrightText: 2025 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: Apache-2.0

"""Test file for imports."""


def test_package_import():
    """Test the import of the main package."""
    import elements_http_upload  # noqa: F401
    import elements_http_upload.models  # noqa: F401
    import elements_http_upload.upload  # noqa: F401
