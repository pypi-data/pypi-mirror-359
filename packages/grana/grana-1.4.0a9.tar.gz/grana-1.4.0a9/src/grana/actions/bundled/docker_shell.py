"""Shell action wrapped into a docker container"""

import contextlib
import functools
import tempfile
import typing as t
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import aiodocker
import aiohttp
from aiodocker.containers import DockerContainer
from aiohttp.client import DEFAULT_TIMEOUT

from ..base import StandardStreamsActionBase, ArgsBase, StreamCaptureConfiguration, CaptureStream
from ...config.constants import C

__all__ = [
    "DockerShellArgs",
    "DockerShellAction",
]


class BindMode(Enum):
    """Allowed bind mount modes"""

    READ_ONLY = "ro"
    READ_WRITE = "rw"


class NetworkMode(Enum):
    """Allowed network modes"""

    BRIDGE = "bridge"
    HOST = "host"
    NONE = "none"


@dataclass
class Auth:
    """Docker auth info"""

    username: str
    password: str
    hostname: t.Optional[str] = None


@dataclass
class Network:
    """Container network specification"""

    mode: NetworkMode = NetworkMode.BRIDGE


@dataclass
class FileDockerBind:
    """File-based bind mount specification"""

    src: str
    dest: str
    mode: BindMode = BindMode.READ_WRITE


@dataclass
class ContentDockerBind:
    """Content-based bind mount specification"""

    contents: str
    dest: str
    mode: BindMode = BindMode.READ_ONLY


class DockerShellArgs(ArgsBase):
    """Args for docker shell"""

    command: str
    image: str
    environment: t.Optional[dict[str, str]] = None
    cwd: t.Optional[str] = None
    pull: bool = False
    executable: str = "/bin/sh"
    bind: t.Optional[list[t.Union[FileDockerBind, ContentDockerBind]]] = None
    network: Network = field(default_factory=Network)  # pylint: disable=invalid-field-call
    privileged: bool = False
    auth: t.Optional[Auth] = None
    capture: list[CaptureStream] = field(default_factory=list)  # pylint: disable=invalid-field-call


class DockerShellAction(StandardStreamsActionBase):
    """Runs a shell command in a docker container."""

    args: DockerShellArgs
    _ENTRY_SCRIPT_FILE_NAME: str = "entry.sh"
    _CONTAINER_TMP_DIRECTORY: str = "/tmp-grana"  # nosec

    @contextlib.asynccontextmanager
    async def _make_container(self, client: aiodocker.Docker) -> t.AsyncGenerator[DockerContainer, None]:
        container_name = f"grana-docker-shell-{uuid.uuid4().hex}"
        self.logger.info(f"Starting docker shell container {container_name!r}")
        container_entry_file_path: str = f"{self._CONTAINER_TMP_DIRECTORY}/{self._ENTRY_SCRIPT_FILE_NAME}"
        with tempfile.TemporaryDirectory() as tmp_directory:
            local_tmp_dir_path: Path = Path(tmp_directory)
            local_tmp_dir_path.chmod(0o777)
            self.logger.debug(f"Local temp dir is {local_tmp_dir_path}")
            entry_file_content: str = self.args.command
            if C.SHELL_INJECT_YIELD_FUNCTION:
                entry_file_content = f"{self._SHELL_SERVICE_FUNCTIONS_DEFINITIONS}\n{entry_file_content}"
            bind_configs: list[t.Union[FileDockerBind, ContentDockerBind]] = [
                ContentDockerBind(
                    contents=entry_file_content,
                    dest=container_entry_file_path,
                    mode=BindMode.READ_WRITE,
                )
            ]
            if self.args.bind:
                bind_configs += self.args.bind
            container_binds: list[str] = []
            for bind_config in bind_configs:
                if isinstance(bind_config, FileDockerBind):
                    local_file_full_name: str = bind_config.src
                else:
                    bind_contents_local_file: Path = local_tmp_dir_path / uuid.uuid4().hex
                    bind_contents_local_file.write_text(data=bind_config.contents, encoding="utf-8")
                    bind_contents_local_file.chmod(0o777)
                    local_file_full_name = str(bind_contents_local_file)
                container_binds.append(f"{local_file_full_name}:{bind_config.dest}:{bind_config.mode.value}")
            self.logger.debug(f"Container volumes: {container_binds}")
            container: DockerContainer = await client.containers.run(
                name=container_name,
                config={
                    "Entrypoint": [],
                    "Cmd": [self.args.executable, container_entry_file_path],
                    "Image": self.args.image,
                    "HostConfig": {
                        "Binds": container_binds,
                        "Init": True,
                        "NetworkMode": self.args.network.mode.value,
                    },
                    "Env": [f"{k}={v}" for k, v in (self.args.environment or {}).items()],
                    "WorkingDir": self.args.cwd,
                    "Privileged": self.args.privileged,
                },
                auth=self._make_auth(),
            )
            try:
                yield container
            finally:
                await container.delete(force=True)

    @functools.cache
    def _make_auth(self) -> t.Optional[dict[str, str]]:
        if self.args.auth is None:
            return None
        auth_dict: dict[str, str] = {
            "username": self.args.auth.username,
            "password": self.args.auth.password,
        }
        if self.args.auth.hostname is not None:
            auth_dict["serveraddress"] = self.args.auth.hostname
        return auth_dict

    async def run(self) -> None:
        async with aiodocker.Docker() as client:
            # Enable default timeout for the connect phase only
            # pylint: disable=protected-access
            client.session._timeout = aiohttp.ClientTimeout(
                connect=DEFAULT_TIMEOUT.total,
            )
            if self.args.pull:
                self.logger.info(f"Pulling image: {self.args.image!r}")
                await client.pull(
                    from_image=self.args.image,
                    auth=self._make_auth(),
                )
            async with self._make_container(client) as container:
                streams_transmission = await self._start_streams_transmission(
                    stdout=container.log(stdout=True, follow=True),
                    stderr=container.log(stderr=True, follow=True),
                )
                await streams_transmission
                result: dict = await container.wait()
                self.logger.debug(f"Docker container result: {result}")
                if (code := result.get("StatusCode", -1)) != 0:
                    self.fail(f"Exit code: {code}")

    @functools.cache
    def _get_capture_configration(self) -> StreamCaptureConfiguration:
        return StreamCaptureConfiguration.from_streams_list(self.args.capture)
