"""Admin module."""

import abc
import functools
import re
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, TYPE_CHECKING

from driverlessai import _commons
from driverlessai import _core
from driverlessai import _enums
from driverlessai import _utils

if TYPE_CHECKING:
    import fsspec  # noqa F401


def _requires_admin(func: Callable) -> Callable:
    """Decorates methods that require admin access."""

    @functools.wraps(func)
    def wrapped(self: "Admin", *args: Any, **kwargs: Any) -> Any:
        if not self.is_admin:
            raise Exception("Administrator access is required to access this feature.")
        return func(self, *args, **kwargs)

    return wrapped


class _EntityKind(str, Enum):
    DATASET = "dataset"
    EXPERIMENT = "model_summary"


class Admin:
    """
    Facilitate operations to perform administrative tasks on the Driverless AI server.
    """

    def __init__(self, client: "_core.Client") -> None:
        self._client = client
        self._is_admin: Optional[bool] = None

    @property
    def is_admin(self) -> bool:
        """
        Returns whether the current user is an admin or not.

        Returns:
            `True` if the user is an admin, otherwise `False`.
        """
        if self._is_admin is None:
            try:
                self._client._backend.get_users_insights()
                self._is_admin = True
            except self._client._server_module.protocol.RemoteError:
                self._is_admin = False
        return self._is_admin

    @_requires_admin
    def list_users(self) -> List[str]:
        """
        Lists users in the Driverless AI server.

        Returns:
            Usernames of the users.
        """
        return [
            user_insight.dump()["user"]
            for user_insight in self._client._backend.get_users_insights()
        ]

    @_requires_admin
    @_utils.beta
    @_utils.min_supported_dai_version("1.10.5")
    def list_current_users(self) -> List[str]:
        """
        Lists users who are currently logged-in to the Driverless AI server.

        Returns:
            Usernames of the currently logged-in users.
        """
        return self._client._backend.get_current_users()

    @_requires_admin
    @_utils.beta
    def list_datasets(self, username: str) -> List["DatasetProxy"]:
        """
        Lists datasets created by the specified user.

        Args:
            username: Username of the user.

        Returns:
            Datasets of the user.

        ??? example "Example: Delete all datasets created by a user"
            ```py
            for d in client.admin.list_datasets("alice"):
                print(f"Deleting {d.name} ...")
                d.delete()
            ```
        """
        response = self._client._backend.admin_list_entities(
            username=username, kind=_EntityKind.DATASET
        )
        return [DatasetProxy(self._client, username, item) for item in response.items]

    @_requires_admin
    @_utils.beta
    def list_experiments(self, username: str) -> List["ExperimentProxy"]:
        """
        Lists experiments created by the specified user.

        Args:
            username: Username of the user.

        Returns:
            Experiments of the user.

        ??? example "Example: Find running experiments of a user"
            ```py
            running_experiments = [
                e for e in client.admin.list_experiments("alice") if e.is_running()
            ]
            ```
        """
        response = self._client._backend.admin_list_entities(
            username=username, kind=_EntityKind.EXPERIMENT
        )
        return [
            ExperimentProxy(self._client, username, item) for item in response.items
        ]

    @_requires_admin
    def transfer_data(self, from_user: str, to_user: str) -> None:
        """
        Transfers all data belonging to one user to another user.

        Args:
            from_user: Username of the user that data will be transferred from.
            to_user: Username of the user that data will be transferred to.
        """
        if from_user == to_user:
            raise ValueError("Cannot transfer data between the same user.")
        self._client._backend.admin_transfer_entities(
            username_from=from_user, username_to=to_user
        )

    @_requires_admin
    @_utils.min_supported_dai_version("1.10.5")
    def list_server_logs(self) -> List["DAIServerLog"]:
        """
        Lists the server logs of the Driverless AI server.

        Returns:
            Server logs of the Driverless AI server.
        """
        log_files = self._client._backend.get_server_logs_details()

        return [
            DAIServerLog(
                client=self._client,
                raw_info=log_file,
            )
            for log_file in log_files
        ]


class DAIServerLog(_commons.ServerLog):
    """A server log file in the Driverless AI server."""

    def __init__(self, client: "_core.Client", raw_info: Any):
        path = re.sub(
            "^.*?/files/",
            "",
            re.sub("^.*?/log_files/", "", raw_info.resource_url),
        )
        super().__init__(client=client, file_path=path)
        self._raw_info = raw_info

    def download(
        self,
        dst_dir: str = ".",
        dst_file: Optional[str] = None,
        file_system: Optional["fsspec.spec.AbstractFileSystem"] = None,
        overwrite: bool = False,
        timeout: float = 30,
    ) -> str:
        """
        Downloads the log file.

        Args:
            dst_dir: The path where the log file will be saved.
            dst_file: The name of the log file (overrides the default file name).
            file_system: FSSPEC-based file system to download to
                instead of the local file system.
            overwrite: Whether to overwrite or not if a file already exists.
            timeout: Connection timeout in seconds.
        Returns:
            Path to the downloaded log file.
        """
        return super()._download(
            dst_dir=dst_dir,
            dst_file=dst_file,
            file_system=file_system,
            overwrite=overwrite,
            timeout=timeout,
            download_type=_enums.DownloadType.LOGS,
        )

    @property
    def size(self) -> int:
        """Size of the log file in bytes."""
        return self._raw_info.size

    @property
    def created(self) -> str:
        """Time of creation."""
        return self._raw_info.ctime_str

    @property
    def last_modified(self) -> str:
        """Time of last modification."""
        return self._raw_info.mtime_str


class ServerObjectProxy(abc.ABC):
    def __init__(self, client: "_core.Client", owner: str, key: str, name: str = None):
        self._client = client
        self._owner = owner
        self._key = key
        self._name = name

    @property
    def key(self) -> str:
        """Universally unique identifier of the entity."""
        return self._key

    @property
    def name(self) -> str:
        """Name of the entity."""
        return self._name

    @property
    def owner(self) -> str:
        """Owner of the entity."""
        return self._owner

    @property
    @abc.abstractmethod
    def _kind(self) -> _EntityKind:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_raw_info(self) -> dict:
        raise NotImplementedError

    def delete(self) -> None:
        """Permanently deletes the entity from the Driverless AI server."""
        self._client._backend.admin_delete_entity(
            username=self.owner, kind=self._kind, key=self.key
        )


class DatasetProxy(ServerObjectProxy):
    """A Proxy for admin access for a dataset in the Driverless AI server."""

    def __init__(self, client: "_core.Client", owner: str, raw_info: dict) -> None:
        super().__init__(
            client=client,
            owner=owner,
            key=raw_info["entity"]["key"],
            name=raw_info["entity"]["name"],
        )
        self._raw_info = raw_info

    @property
    def _kind(self) -> _EntityKind:
        return _EntityKind.DATASET

    @property
    def columns(self) -> List[str]:
        """Column names of the dataset."""
        return [c["name"] for c in self._get_raw_info()["entity"]["columns"]]

    @property
    def creation_timestamp(self) -> float:
        """
        Creation timestamp of the dataset in seconds since the epoch (POSIX timestamp).
        """
        return self._get_raw_info()["created"]

    @property
    def data_source(self) -> str:
        """Original data source of the dataset."""
        return self._get_raw_info()["entity"]["data_source"]

    @property
    def description(self) -> Optional[str]:
        """Description of the dataset."""
        return self._get_raw_info()["entity"].get("notes")

    @property
    def file_path(self) -> str:
        """Path to the dataset bin file in the Driverless AI server."""
        return self._get_raw_info()["entity"]["bin_file_path"]

    @property
    def file_size(self) -> int:
        """Size in bytes of the dataset bin file in the Driverless AI server."""
        return self._get_raw_info()["entity"]["file_size"]

    @property
    def shape(self) -> Tuple[int, int]:
        """Dimensions of the dataset in (rows, cols) format."""
        return (
            self._get_raw_info()["entity"]["row_count"],
            self._get_raw_info()["entity"]["column_count"],
        )

    def _get_raw_info(self) -> dict:
        return self._raw_info


class ServerJobProxy(ServerObjectProxy):
    @abc.abstractmethod
    def _get_raw_info(self) -> dict:
        raise NotImplementedError

    @abc.abstractmethod
    def _status(self) -> _enums.JobStatus:
        raise NotImplementedError

    def is_complete(self) -> bool:
        """
        Returns whether the job has been completed successfully or not.

        Returns:
            `True` if the job finished successfully, otherwise `False`.
        """
        return _commons.is_server_job_complete(self._status())

    def is_running(self) -> bool:
        """
        Returns whether the job is currently running or not.

        Returns:
            `True` if the job has been scheduled or is running, finishing, or syncing.
                Otherwise, `False`.
        """
        return _commons.is_server_job_running(self._status())

    def status(self, verbose: int = 0) -> str:
        """
        Returns the status of the job.

        Args:
            verbose:
                - 0: A short description.
                - 1: A short description with a progress percentage.
                - 2: A detailed description with a progress percentage.

        Returns:
            Current status of the job.
        """

        status = self._status()
        # server doesn't always show 100% complete
        progress = 1 if self.is_complete() else self._get_raw_info()["progress"]
        if verbose == 1:
            return f"{status.message} {progress:.2%}"
        elif verbose == 2:
            if status == _enums.JobStatus.FAILED:
                message = self._get_raw_info()["error"]
            elif "message" in self._get_raw_info():
                message = self._get_raw_info()["message"].split("\n")[0]
            else:
                message = ""
            return f"{status.message} {progress:.2%} - {message}"

        return status.message


class ExperimentProxy(ServerJobProxy):
    """A Proxy for admin access for an experiment in the Driverless AI server."""

    def __init__(self, client: "_core.Client", owner: str, raw_info: dict) -> None:
        super().__init__(
            client=client,
            owner=owner,
            key=raw_info["key"],
            name=raw_info["description"],
        )
        self._all_datasets: Optional[List["DatasetProxy"]] = None
        self._datasets: Optional[Dict[str, Optional["DatasetProxy"]]] = None
        self._raw_info = raw_info
        self._settings: Optional[Dict[str, Any]] = None

    def _get_dataset(self, key: str) -> Optional["DatasetProxy"]:
        if self._all_datasets is None:
            self._all_datasets = self._client.admin.list_datasets(self.owner)
        for dataset in self._all_datasets:
            if dataset.key == key:
                return dataset
        return None

    def _get_raw_info(self) -> dict:
        return self._raw_info

    @property
    def _kind(self) -> _EntityKind:
        return _EntityKind.EXPERIMENT

    def _status(self) -> _enums.JobStatus:
        return _enums.JobStatus(self._get_raw_info()["status"])

    @property
    def creation_timestamp(self) -> float:
        """
        Creation timestamp of the experiment in seconds since the epoch
        (POSIX timestamp).
        """
        return self._get_raw_info()["created"]

    @property
    def datasets(self) -> Dict[str, Optional["DatasetProxy"]]:
        """
         Datasets used for the experiment.

        Returns:
            Dictionary of `train_dataset`,`validation_dataset`, and `test_dataset`.
        """
        if not self._datasets:
            train_dataset = self._get_dataset(
                self._get_raw_info()["parameters"]["dataset"]["key"]
            )
            validation_dataset = None
            test_dataset = None
            if self._get_raw_info()["parameters"]["validset"]["key"]:
                validation_dataset = self._get_dataset(
                    self._get_raw_info()["parameters"]["validset"]["key"]
                )
            if self._get_raw_info()["parameters"]["testset"]["key"]:
                test_dataset = self._get_dataset(
                    self._get_raw_info()["parameters"]["testset"]["key"]
                )
            self._datasets = {
                "train_dataset": train_dataset,
                "validation_dataset": validation_dataset,
                "test_dataset": test_dataset,
            }

        return self._datasets

    @property
    def run_duration(self) -> Optional[float]:
        """Run duration of the experiment in seconds."""
        return self._get_raw_info()["training_duration"]

    @property
    def settings(self) -> Dict[str, Any]:
        """Experiment settings."""
        if not self._settings:
            self._settings = self._client.experiments._parse_server_settings(
                self._get_raw_info()["parameters"]
            )
        return self._settings

    @property
    def size(self) -> int:
        """Size in bytes of all the experiment files on the Driverless AI server."""
        return self._get_raw_info()["model_file_size"]
