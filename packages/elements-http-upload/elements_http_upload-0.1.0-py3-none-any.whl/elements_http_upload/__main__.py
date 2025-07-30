# SPDX-FileCopyrightText: 2025 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: Apache-2.0

"""Command-line interface for elements-http-upload"""

import argparse
import textwrap
from pathlib import Path


def get_parser() -> argparse.ArgumentParser:
    from pydantic import HttpUrl, SecretStr
    from pydantic_settings import SettingsConfigDict

    from .models import FileUpload, UploadSettings

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.epilog = textwrap.dedent(
        """
        **Environment variables**

        Instead of specifying the connection and upload settings
        (Host, API token) via the command line, you can also set
        environment variables prefixed with ``elements_upload_``,
        i.e. ``elements_upload_host``, ``elements_upload_api_token``,
        etc. Upper and lowercase variable names are possible. The
        following environment variables are available:

        - elements_http_upload_host
        - elements_http_upload_api_token
        - elements_http_upload_skip_certificate_validation
        - elements_http_upload_chunk_size
        - elements_http_upload_concurrent_uploads
        - elements_http_upload_silent
        - elements_http_upload_verbose


        **Examples**

        For examples, please visit
        <https://elements-http-upload.readthedocs.io/en/latest/usage.html>
        """
    )

    connection_group = parser.add_argument_group("Connection Settings")

    _dummy_url = HttpUrl("https://example.com")

    class DummySettings(UploadSettings):
        model_config = SettingsConfigDict(env_prefix="elements_upload_")

        host: HttpUrl = _dummy_url
        api_token: SecretStr = SecretStr("")

    default_settings = DummySettings()

    host_set = default_settings.host != _dummy_url

    connection_group.add_argument(
        "-H",
        "--host",
        help=(
            "The url of the elements instance in the form of "
            "`https://sub.domain`"
        ),
        default=default_settings.host if host_set else None,
        required=not host_set,
    )

    connection_group.add_argument(
        "-t",
        "--api-token",
        help="The API token to use for the requests",
        default=default_settings.api_token,
        required=not default_settings.api_token,
    )

    connection_group.add_argument(
        "--no-verify",
        action="store_true",
        dest="skip_certificate_validation",
        help="Skip the verification of SSL certificates in HTTPS requests.",
    )

    upload_group = parser.add_argument_group("Upload settings")

    upload_group.add_argument(
        "-c",
        "--chunk-size",
        default=default_settings.chunk_size,
        help="The chunk size to use within one single request.",
    )

    upload_group.add_argument(
        "-n",
        "--concurrent-uploads",
        default=default_settings.concurrent_uploads,
        help="The number of parallel upload threads.",
    )

    output_group = parser.add_argument_group("Verbosity options")

    output_group.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug mode and be more verbose",
    )

    output_group.add_argument(
        "-s",
        "--silent",
        action="store_true",
        help="Do not provide progress information.",
    )

    file_group = parser.add_argument_group("File options")

    file_group.add_argument(
        "uploads",
        help=textwrap.dedent(
            """
            The files or directories to upload. ``LOCAL-SRC`` is the local file
            (or directory if ``--recursive`` is set), ``REMOTE-DEST`` is the
            destination on the remote system. If ``REMOTE-DEST`` is not set,
            ``--target-root`` must be specified. If ``REMOTE-DEST`` is set,
            it needs to be a relative path to the given ``--target-root``, or
            and absolute path if ``--target-root`` is not specified.
            """
        ),
        metavar="LOCAL-SRC[:REMOTE-DEST]",
        nargs="+",
        type=FileUpload.from_str,
    )

    file_group.add_argument(
        "-d",
        "--target-root",
        help=(
            "Root folder on the remote system, by default None. If this is "
            "set, all target paths in the `uploads` need to be "
            "relative and will be appended to the `target_root`. If this is "
            "not set, all destination paths in the `uploads` need to be "
            "absolute paths."
        ),
        type=Path,
    )

    file_group.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help=(
            "If true, upload all files in a directory "
            "(symbolic links are ignored for directories, but not for files)"
        ),
    )

    return parser


def main():
    from .models import UploadSettings
    from .upload import UploadProcess, resolve_uploads

    parser = get_parser()
    args = parser.parse_args()  # noqa: F841

    settings = UploadSettings.model_validate(vars(args))
    all_uploads = resolve_uploads(
        *args.uploads,
        recursive=args.recursive,
        target_root=args.target_root,
    )

    process = UploadProcess(
        settings,
        *all_uploads,
    )
    process.start()


if __name__ == "__main__":
    main()
