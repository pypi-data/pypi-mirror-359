# SPDX-FileCopyrightText: 2025 Helmholtz-Zentrum hereon GmbH
#
# SPDX-License-Identifier: Apache-2.0

"""Upload module for elements."""

from __future__ import annotations

import mimetypes
import os
import threading
import time
import warnings
from collections import defaultdict
from pathlib import Path
from queue import Empty, Queue
from typing import Dict, List, Optional, TypeVar, Union
from urllib.parse import urlencode

import progressbar

from .models import FileUpload, UploadSettings

T = TypeVar("T")


def resolve_uploads(
    *uploads: FileUpload,
    recursive: bool = False,
    target_root: Optional[Path] = None,
) -> List[FileUpload]:
    """Resolve files and folders into individual upload files.

    Parameters
    ----------
    *uploads : FileUpload
        The file or directory information for the upload. If a
        :attr:`~FileUpload.source` points to a directory, `recursive` has to
        be true.
    recursive : bool, optional
        Whether folders should be check recursively, by default False. If an
        uploads :attr:`~FileUpload.source` points to a directory and this
        option is ``False``, an error is raised.
    target_root : Optional[Path], optional
        Root folder on the remote system, by default None. If this is set,
        all :attr:`~FileUpload.target` paths in the `uploads` need to be
        relative and will be appended to the `target_root`. If this is not,
        all :attr:`~FileUpload.target` paths in the `uploads` need to be
        absolute paths.

    Returns
    -------
    List[FileUpload]
        _description_
    """
    ret: List[FileUpload] = []
    for upload in uploads:
        if not upload.source.exists():
            raise IOError(f"{upload.source} does not exist")
        elif not upload.target.is_absolute() and target_root is None:
            raise ValueError(
                f"Remote target {upload.target} is relative path and "
                "target_root has not been specified!"
            )
        elif upload.target.is_absolute() and target_root is not None:
            raise ValueError(
                f"Remote target {upload.target} is absolute path and "
                f"target_root has been set to {target_root}! Please use "
                "relative target paths."
            )
        elif upload.source.is_file():
            if target_root is not None:
                target_name: Union[Path, str]
                if str(upload.target) == ".":
                    target_name = upload.source.name
                else:
                    target_name = upload.target
                ret.append(
                    FileUpload(
                        source=upload.source,
                        target=target_root / target_name,
                    )
                )
            else:
                ret.append(upload)
        elif upload.source.is_dir():
            if not recursive:
                raise IOError(
                    f"{upload.source} is a directory and recursive is not set "
                    "to True"
                )
            if target_root:
                upload.target = target_root / upload.target
            children = [
                FileUpload(
                    source=upload.source / fname, target=upload.target / fname
                )
                for fname in os.listdir(str(upload.source))
            ]
            ret.extend(resolve_uploads(*children, recursive=True))
    return ret


def _get_filenames(*paths: str, recursive: bool = False) -> List[Path]:
    """Get all files in the given paths.

    Parameters
    ----------
    *paths : str
        The paths to check for filenames
    recursive: bool
        Whether folders should be check recursively.

    Returns
    -------
    List[Path]
        The files in the given paths.
    """
    ret: List[Path] = []
    for path in map(Path, paths):
        if not path.exists():
            raise IOError(f"{path} does not exist")
        elif path.is_file():
            ret.append(path)
        elif path.is_dir():
            if not recursive:
                raise IOError(
                    f"{path} is a directory and recursive is set to false!"
                )
            elif path.is_symlink():
                warnings.warn(
                    f"Ignoring symbolic link to directory at {path}",
                    stacklevel=2,
                )
            else:
                ret.extend(_get_filenames(*os.listdir(), recursive=recursive))
    return ret


class UploadProcess:
    """A process to upload multiple files."""

    def __init__(
        self,
        settings: UploadSettings,
        *uploads: FileUpload,
    ):
        self.settings = settings
        self.uploads: List[FileUpload] = list(uploads)
        self.nchunks: Dict[str, int] = {
            upload.upload_id: upload.source.stat().st_size
            // settings.chunk_size
            + 1
            for upload in uploads
        }
        self.exit_event = threading.Event()

        self.file_upload_queue: Queue[FileUpload] = Queue(
            maxsize=settings.concurrent_uploads * 2
        )
        self.chunk_upload_queue: Queue[Optional[Dict]] = Queue(
            maxsize=settings.concurrent_uploads * 2
        )
        self.chunk_finish_queue: Queue[str] = Queue()

    def register_upload_worker(self) -> None:
        """Register the upload for the individual file uploads"""
        for upload in self.uploads:
            register_upload_endpoint_request = dict(
                upload_id=upload.upload_id,
                path=str(upload.target),
            )
            retries = 0
            while True:
                if self.exit_event.is_set():
                    return

                response = self.settings.request(
                    "api/2/uploads/register",
                    "POST",
                    json=register_upload_endpoint_request,
                )
                if response.status_code == 200:
                    break
                else:
                    if retries == 5:
                        self.exit_event.set()
                        raise ValueError(
                            "Failed to register upload for %s (%r). Reason: %r - %r"
                            % (
                                upload.target,
                                upload.upload_id,
                                response.status_code,
                                response.content,
                            )
                        )
                    retries += 1
                    time.sleep(retries)
            self.file_upload_queue.put(upload)
        self.file_upload_queue.join()
        for _ in range(self.settings.concurrent_uploads):
            # tell the upload threads to finish
            self.chunk_upload_queue.put(None)

    def split_files_worker(self) -> None:
        """Worker to split files input smaller chunks for upload."""
        uploaded = 0
        total_uploads = sum(self.nchunks.values())
        while uploaded < total_uploads:
            upload = self._safe_get(self.file_upload_queue)
            if upload is None:
                return
            if not self.settings.silent:
                print(upload.source)
            total_chunks = self.nchunks[upload.upload_id]
            chunk_size = self.settings.chunk_size
            mimetype = mimetypes.guess_type(upload.source)[0]
            with upload.source.open("rb") as f:
                for chunk in range(1, total_chunks + 1):
                    current_size = (
                        chunk_size
                        if chunk < total_chunks
                        else (upload.file_size % chunk_size)
                    )
                    query = urlencode(
                        {
                            "flowChunkNumber": chunk,
                            "flowChunkSize": chunk_size,
                            "flowCurrentChunkSize": current_size,
                            "flowTotalSize": upload.file_size,
                            "flowIdentifier": upload.upload_id,
                            "flowFilename": upload.target.name,
                            "flowRelativePath": upload.target.name,
                            "flowTotalChunks": total_chunks,
                        }
                    )
                    data = f.read(chunk_size)
                    self.chunk_upload_queue.put(
                        {
                            "data": data,
                            "url": "api/2/uploads/chunk" + "?" + query,
                            "mimetype": mimetype,
                            "upload_id": upload.upload_id,
                        }
                    )
            uploaded += 1
            self.file_upload_queue.task_done()

    def upload_chunk_worker(self) -> None:
        """A worker function to upload chunks"""
        while True:
            chunk_data = self._safe_get(self.chunk_upload_queue)
            if not chunk_data:
                # queue ended
                self.chunk_upload_queue.task_done()
                return
            else:
                retries = 0
                while True:
                    response = self.settings.request(chunk_data["url"])
                    if response.status_code == 204:
                        break
                    elif retries == 5:
                        self.exit_event.set()
                        raise ValueError(
                            "Could perform pre-upload request for %r. Reason: %r - %r"
                            % (
                                chunk_data["url"],
                                response.status_code,
                                response.content,
                            )
                        )
                    else:
                        retries += 1
                        time.sleep(retries)
                retries = 0
                while True:
                    response = self.settings.request(
                        chunk_data["url"],
                        "POST",
                        data=chunk_data["data"],
                        headers={"Content-Type": chunk_data["mimetype"]},
                    )
                    if response.status_code == 200:
                        break
                    elif retries == 5:
                        self.exit_event.set()
                        raise ValueError(
                            "Could upload chunk for %r. Reason: %r - %r"
                            % (
                                chunk_data["url"],
                                response.status_code,
                                response.content,
                            )
                        )
                    else:
                        retries += 1
                        time.sleep(retries)

                self.chunk_finish_queue.put(chunk_data["upload_id"])
                self.chunk_upload_queue.task_done()

    def _safe_get(self, queue: Queue[T]) -> Optional[T]:
        while True:
            try:
                return queue.get(timeout=1)
            except Empty:
                if self.exit_event.is_set():
                    return None

    def finish_uploads_worker(self) -> None:
        """A worker to finish uploads"""
        chunks = self.nchunks.copy()
        counts: Dict[str, int] = defaultdict(int)
        widgets: List[progressbar.widgets.WidgetBase | str] = [
            progressbar.Percentage(),
            " ",
            progressbar.MultiProgressBar("jobs", fill_left=True),
            " ",
            progressbar.ETA(),
            " ",
            progressbar.FileTransferSpeed(),
        ]
        max_value = sum(chunks.values()) * self.settings.chunk_size
        upload_ids: List[str] = list(chunks)
        jobs = [
            [0, chunks[upload_id] * self.settings.chunk_size]
            for upload_id in upload_ids
        ]
        with progressbar.ProgressBar(
            widgets=widgets, max_value=max_value, redirect_stdout=True
        ) as bar:
            if not self.settings.silent:
                bar.update(0, jobs=jobs, force=True)
            while chunks:
                upload_id = self._safe_get(self.chunk_finish_queue)
                if upload_id is None:
                    return
                jobs[upload_ids.index(upload_id)][
                    0
                ] += self.settings.chunk_size
                progress = sum([progress for progress, total in jobs])
                if not self.settings.silent:
                    bar.update(progress, jobs=jobs, force=True)
                counts[upload_id] += 1
                if counts[upload_id] == chunks[upload_id]:
                    del chunks[upload_id]
                    retries = 0
                    finish_upload_endpoint_request = dict(
                        upload_id=upload_id,
                    )
                    while True:
                        response = self.settings.request(
                            "/api/2/uploads/finish",
                            "POST",
                            json=finish_upload_endpoint_request,
                        )
                        if response.status_code == 200:
                            break
                        else:
                            if retries == 5:
                                raise ValueError(
                                    "Failed to finish upload for %r. Reason: %r - %r"
                                    % (
                                        upload_id,
                                        response.status_code,
                                        response.content,
                                    )
                                )
                            retries += 1
                            time.sleep(retries)
                self.chunk_finish_queue.task_done()

    def start(self):
        """Start the upload process."""

        registration_thread = threading.Thread(
            target=self.register_upload_worker, daemon=True
        )
        chunking_thread = threading.Thread(
            target=self.split_files_worker, daemon=True
        )
        upload_threads = [
            threading.Thread(target=self.upload_chunk_worker, daemon=True)
            for _ in range(
                min(
                    sum(self.nchunks.values()),
                    self.settings.concurrent_uploads,
                )
            )
        ]
        finishing_thread = threading.Thread(
            target=self.finish_uploads_worker, daemon=True
        )

        registration_thread.start()
        chunking_thread.start()
        for thread in upload_threads:
            thread.start()
        finishing_thread.start()
        finishing_thread.join()
