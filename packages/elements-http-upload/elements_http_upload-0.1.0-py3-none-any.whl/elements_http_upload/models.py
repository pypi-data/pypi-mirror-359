# SPDX-FileCopyrightText: 2025 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import datetime as dt
import hashlib
import random
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import requests
from pydantic import BaseModel, Field, HttpUrl, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

if TYPE_CHECKING:
    from requests import Response


class FileUpload(BaseModel):
    """A model for a file to upload."""

    source: Path = Field(description="The local resource to upload")

    target: Path = Field(
        default_factory=Path,
        description="The target resource on the remote system.",
    )

    @computed_field  # type:ignore[misc]
    @cached_property
    def upload_id(self) -> str:
        timestamp = dt.datetime.now().strftime("%Y%m%d%H%M%S")
        random_identifier = random.randint(10000, 99999)
        text = "%s:%s" % (self.source, self.target)
        md5_sum = hashlib.md5(text.encode()).hexdigest()
        return "%s-%s-%s" % (random_identifier, md5_sum, timestamp)

    @computed_field  # type:ignore[misc]
    @cached_property
    def file_size(self) -> int:
        return self.source.stat().st_size

    @classmethod
    def from_str(cls, text: str):
        """Generate a file upload from a colon-delimited string

        Parameters
        ----------
        text : str
            A colon-delimited string, where the part before the colon
            corresponds to the source, and the (optional) part after the colon
            corresponds to the target

        Returns
        -------
        FileUpload
            A new :class:`FileUpload`
        """
        splitted = text.split(":")
        source = Path(splitted[0])
        target = splitted[1] if len(splitted) > 1 else "."
        if target.endswith("/") and source.is_file():
            target = target + source.name
        return cls(source=source, target=Path(target))


class ConnectionSettings(BaseSettings):
    """Settings for connecting to an elements instance."""

    model_config = SettingsConfigDict(
        env_prefix="elements_upload_", extra="ignore"
    )

    host: HttpUrl = Field(description="The url of the elements installation")

    api_token: SecretStr = Field(description="The token for the upload.")

    skip_certificate_validation: bool = Field(
        default=False, description="Skip the verification of SSL certificates."
    )

    def request(
        self,
        path: str,
        method: Literal["GET", "POST"] = "GET",
        *args,
        headers=None,
        **kwargs,
    ) -> Response:
        """Make a request to the host."""
        combined_headers = {
            "Authorization": "Bearer " + self.api_token.get_secret_value()
        }
        if headers:
            combined_headers.update(headers)
        rest_url = str(self.host)
        if not rest_url.endswith("/"):
            rest_url += "/"
        if path.startswith("/"):
            path = path[1:]
        rest_url += path
        if self.skip_certificate_validation:
            kwargs["verify"] = False
        if method == "GET":
            return requests.get(
                rest_url, *args, headers=combined_headers, **kwargs
            )
        else:
            return requests.post(
                rest_url, *args, headers=combined_headers, **kwargs
            )


class UploadSettings(ConnectionSettings):
    """Settings for uploading data to a base folder."""

    model_config = SettingsConfigDict(
        env_prefix="elements_upload_", extra="ignore"
    )

    chunk_size: int = Field(
        default=10485760, description="The chunksize for the individual upload"
    )

    concurrent_uploads: int = Field(
        default=5, description="The number of parallel threads for the upload"
    )

    silent: bool = Field(
        default=False, description="Be silent during the upload."
    )

    verbose: bool = Field(
        default=False, description="Be (much) more verbose during the upload."
    )
