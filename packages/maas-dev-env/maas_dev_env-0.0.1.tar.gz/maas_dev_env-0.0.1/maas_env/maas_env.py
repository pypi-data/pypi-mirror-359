from abc import ABC, abstractmethod
import argparse
from dataclasses import dataclass
from enum import StrEnum
from importlib.resources import files
import logging
from pathlib import Path
import subprocess
import sys
from typing import override, TypeVar

import yaml


class CustomFormatter(logging.Formatter):
    white = "\033[37;40m"
    grey = "\033[90;40m"
    yellow = "\033[1;33;40m"
    red = "\033[1;31;40m"
    reset = "\033[0m"
    msg_format = "%(message)s"
    err_format = "%(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + msg_format + reset,
        logging.INFO: white + msg_format + reset,
        logging.WARNING: yellow + msg_format + reset,
        logging.ERROR: red + err_format + reset,
        logging.CRITICAL: red + err_format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(CustomFormatter())

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

CWD = str(Path.cwd())
REPO_PATH = "/work"


@dataclass
class CmdResult:
    ret_code: int
    stdout: str


def execute_cmd(cmd: list[str], log_level=logging.INFO, silent=False) -> CmdResult:
    """Wrapper to execute a command through subprocess that adds some logging."""
    cmd_as_str = " ".join(cmd)
    if not silent:
        logger.log(level=log_level, msg=cmd_as_str)
    stdout = ""
    with subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    ) as proc:
        for line in proc.stdout:
            line = line.decode("utf-8")
            stdout += line
            if not silent:
                logger.log(level=log_level, msg=f"  {line.strip()}")

    if proc.returncode != 0 and not silent:
        logger.error(f"Command: {cmd_as_str} failed with exit status {proc.returncode}")
        sys.exit(1)
    return CmdResult(proc.returncode, stdout)


class InstallationMethod(StrEnum):
    SNAP = "snap"
    DEB = "deb"


@dataclass
class LXDConfig:
    image: str
    name: str


@dataclass
class Config:
    """Representation of the YAML config."""

    lxd: LXDConfig
    commands: dict[str, list[str]]
    overlayfs_workdir_prefix: str
    files: dict
    dirs: dict


@dataclass
class Mountable(ABC):
    @abstractmethod
    def mount_cmd(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def unmount_cmd(self) -> str:
        raise NotImplementedError()


@dataclass
class MountableDir(Mountable):
    """A directory to be mounted as an OverlayFS.

    Attributes:
        - lower: the lower dir in the overlay. It corresponds to the one
            already present in deb/snap MAAS.
        - upper: the upper dir in the overlay. It corresponds to the source
            files in our local repo.
        - work: the workdir in the overlay. Must be on the same FS of the upper
            dir.
    """

    lower: str
    upper: str
    work: str

    @override
    def mount_cmd(self) -> str:
        return f"sudo mount -t overlay overlay -o lowerdir={self.lower},upperdir={self.upper},workdir={self.work} {self.lower}"

    @override
    def unmount_cmd(self) -> str:
        return f"sudo umount {self.lower}"


@dataclass
class MountableFile(Mountable):
    """A file to be mounted as a read-only bind mount.

    Attributes:
        - source: the source file in our local repo.
        - dest: the file that has to be replaced in the deb/snap.
    """

    source: str
    dest: str

    @override
    def mount_cmd(self) -> str:
        return f"sudo mount -o bind,ro {self.source} {self.dest}"

    @override
    def unmount_cmd(self) -> str:
        return f"sudo umount {self.dest}"


@dataclass
class Executor(ABC):
    @abstractmethod
    def construct_command(self, command: str) -> list[str]:
        raise NotImplementedError()

    def exec(self, command: str, log_level=logging.INFO, silent=False) -> CmdResult:
        full_cmd = self.construct_command(command)
        return execute_cmd(full_cmd, log_level, silent)


@dataclass
class LocalExecutor(Executor):
    def construct_command(self, command: str) -> list[str]:
        full_cmd = ["bash", "-c", command]
        return full_cmd


@dataclass
class LXDContainerExecutor(Executor):
    """Execute commands in a container."""

    container_name: str

    def construct_command(self, command: str) -> list[str]:
        full_cmd = [
            "lxc",
            "exec",
            self.container_name,
            "--",
            "bash",
            "-c",
            command,
        ]
        return full_cmd


@dataclass
class LXDManager:
    """Manage LXD containers."""

    config: LXDConfig

    def container_exists(self):
        result = execute_cmd(["lxc", "info", self.config.name], silent=True)
        return result.ret_code == 0

    def get_or_create_container(self, action: str) -> LXDContainerExecutor:
        if not self.container_exists():
            if action == "destroy":
                logger.warning(
                    f"Container {self.config.name} doesn't exist. Skipping deletion."
                )
                sys.exit(0)
            execute_cmd(
                [
                    "lxc",
                    "launch",
                    self.config.image,
                    self.config.name,
                    "--config",
                    "security.nesting=true",  # Needed for OverlayFS
                    "--config",
                    "raw.idmap=both 1000 1000",
                ],
            )
            execute_cmd(
                [
                    "lxc",
                    "config",
                    "device",
                    "add",
                    self.config.name,
                    "workdir",
                    "disk",
                    f"source={CWD}",
                    f"path={REPO_PATH}",
                ],
            )
            execute_cmd(
                [
                    "lxc",
                    "exec",
                    self.config.name,
                    "--",
                    "cloud-init",
                    "status",
                    "--wait",
                ]
            )
            logger.info(f"Container {self.config.name} created and configured.")
        return LXDContainerExecutor(self.config.name)

    def remove_container(self):
        if self.container_exists():
            execute_cmd(["lxc", "delete", "--force", self.config.name])
            logger.info(f"Container {self.config.name} removed.")
        else:
            logger.warning(
                f"Container {self.config.name} doesn't exist. Skipping deletion."
            )


@dataclass
class MAASManager:
    """Manage a MAAS installation."""

    executor: Executor
    config: Config

    def get_repo_path(self) -> str:
        if isinstance(self.executor, LXDContainerExecutor):
            return REPO_PATH
        return CWD

    def verify_installed(self) -> bool:
        res = []
        for cmd in self.config.commands["verify"]:
            res.append(self.executor.exec(cmd, silent=True).ret_code == 0)
        return all(res)

    def ensure_installed(self):
        if not self.verify_installed():
            logger.error("MAAS is not installed. Run the `init` command first.")
            sys.exit(1)

    def get_dirs_mappings(self) -> list[MountableDir]:
        repo_path = self.get_repo_path()
        overlayfs_workdir = f"{repo_path}/{self.config.overlayfs_workdir_prefix}"

        dirs_mappings = [
            MountableDir(
                lower=lower,
                upper=f"{repo_path}/{upper}",
                work=f"{overlayfs_workdir}/{upper}",
            )
            for upper, lower in self.config.dirs.items()
        ]
        return dirs_mappings

    def get_files_mappings(self) -> list[MountableFile]:
        repo_path = self.get_repo_path()
        file_mappings = [
            MountableFile(source=f"{repo_path}/{source}", dest=dest)
            for source, dest in self.config.files.items()
        ]
        return file_mappings

    def post_install(self):
        if not self.verify_installed():
            logger.error("Failed to install maas")
            sys.exit(1)
        for cmd in self.config.commands["post_install"]:
            self.executor.exec(cmd)

    def install(self):
        for cmd in self.config.commands["install"]:
            self.executor.exec(cmd)
        self.post_install()

    def start(self):
        for cmd in self.config.commands["start"]:
            self.executor.exec(cmd)

    def stop(self):
        for cmd in self.config.commands["stop"]:
            self.executor.exec(cmd)

    def build_artifacts(self):
        for cmd in self.config.commands["build"]:
            self.executor.exec(cmd)


@dataclass
class DebMAAS(MAASManager):
    pass


@dataclass
class SnapMAAS(MAASManager):
    @override
    def get_dirs_mappings(self) -> list[MountableDir]:
        mappings = super().get_dirs_mappings()
        # replace /snap/maas/current with /snap/maas/00000
        revision = self.get_revision()
        for m in mappings:
            m.lower = m.lower.replace("/snap/maas/current", f"/snap/maas/{revision}")
        return mappings

    @override
    def get_files_mappings(self) -> list[MountableFile]:
        mappings = super().get_files_mappings()
        # replace /snap/maas/current with /snap/maas/00000
        revision = self.get_revision()
        for m in mappings:
            m.dest = m.dest.replace("/snap/maas/current", f"/snap/maas/{revision}")
        return mappings

    def get_revision(self):
        path = self.executor.exec("realpath /snap/maas/current", silent=True).stdout
        revision = path.removeprefix("/snap/maas/").strip()
        return revision


T = TypeVar("T", bound=Mountable)


@dataclass
class MountManager[T](ABC):
    executor: Executor
    mountables: list[T]

    def mount_all(self):
        mounts = self.read_proc_mounts()
        for m in self.mountables:
            self._mount_one(m, mounts)

    def unmount_all(self):
        mounts = self.read_proc_mounts()
        for m in self.mountables:
            self._unmount_one(m, mounts)

    def read_proc_mounts(self):
        return self.executor.exec(
            "awk '{print $2}' /proc/mounts", silent=True
        ).stdout.split("\n")

    @abstractmethod
    def _mount_one(self, m: T, mounts: list[str]):
        raise NotImplementedError()

    @abstractmethod
    def _unmount_one(self, m: T, mounts: list[str]):
        raise NotImplementedError()


@dataclass
class DirsManager(MountManager[MountableDir]):
    @override
    def _mount_one(self, m: MountableDir, mounts: list[str]):
        self._create_workdir(m)
        if m.lower not in mounts:
            self.executor.exec(m.mount_cmd(), log_level=logging.DEBUG)

    @override
    def _unmount_one(self, m: MountableDir, mounts: list[str]):
        if m.lower in mounts:
            self.executor.exec(m.unmount_cmd(), log_level=logging.DEBUG)

    def _create_workdir(self, m: MountableDir):
        self.executor.exec(f"mkdir -p {m.work}", silent=True)

    def _delete_workdir(self, m: MountableDir):
        self.executor.exec(f"rm -rf {m.work}", silent=True)


@dataclass
class FilesManager(MountManager[MountableFile]):
    @override
    def _mount_one(self, m: MountableFile, mounts: list[str]):
        if m.dest not in mounts:
            self.executor.exec(m.mount_cmd(), log_level=logging.DEBUG)

    @override
    def _unmount_one(self, m: MountableFile, mounts: list[str]):
        if m.dest in mounts:
            self.executor.exec(m.unmount_cmd(), log_level=logging.DEBUG)


@dataclass
class SyncManager:
    mount_managers: list[MountManager]

    @classmethod
    def create(cls, maas: MAASManager):
        return cls(
            mount_managers=[
                DirsManager(maas.executor, maas.get_dirs_mappings()),
                FilesManager(maas.executor, maas.get_files_mappings()),
            ],
        )

    def sync(self):
        self.unsync()
        logger.info("Mounting files and directories...")
        for manager in self.mount_managers:
            manager.mount_all()

    def unsync(self):
        logger.info("Unmounting files and directories...")
        for manager in self.mount_managers:
            manager.unmount_all()


def load_yaml_config(path: str, method: InstallationMethod) -> Config:
    with open(path, "r") as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            logger.error("Failed to parse the YAML config file")
            logger.error(f"Error: {str(exc)}")
            sys.exit(1)

    config = config[method]

    try:
        lxd_config = LXDConfig(**config.pop("lxd"))
        return Config(lxd=lxd_config, **config)
    except TypeError as exc:
        logger.error("Unknown attribute in YAML config file")
        logger.error(f"Error: {str(exc)}")
        sys.exit(1)


def add_common_arguments(p: argparse.ArgumentParser):
    p.add_argument(
        "--config",
        default=files("maas_env").joinpath("config.yaml"),
        help="Path to config file",
        type=Path,
    )
    method_group = p.add_mutually_exclusive_group(required=True)
    method_group.add_argument(
        "--snap", action="store_true", help="Snap MAAS environment"
    )
    method_group.add_argument("--deb", action="store_true", help="Deb MAAS environment")
    p.add_argument("-v", action="store_true", help="Verbose output")


def main():
    parser = argparse.ArgumentParser(description="MAAS Testing Environment Script")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser(
        "init", help="Initialize the LXD container and install MAAS on it."
    )
    add_common_arguments(init_parser)

    sync_parser = subparsers.add_parser("sync", help="Sync and test environment")
    add_common_arguments(sync_parser)

    clear_parser = subparsers.add_parser("unsync", help="Unmount and reset environment")
    add_common_arguments(clear_parser)

    destroy_parser = subparsers.add_parser("destroy", help="Destroy the LXD container")
    add_common_arguments(destroy_parser)

    args = parser.parse_args()

    if args.v:
        logger.setLevel(logging.DEBUG)

    method = InstallationMethod.SNAP if args.snap else InstallationMethod.DEB
    config = load_yaml_config(args.config, method)

    inside_container = (
        execute_cmd(["hostname"], silent=True).stdout.strip() == config.lxd.name
    )

    lxd = LXDManager(config.lxd)
    if inside_container:
        executor = LocalExecutor()
    else:
        executor = lxd.get_or_create_container(args.command)

    match method:
        case InstallationMethod.SNAP:
            maas = SnapMAAS(executor, config)
        case InstallationMethod.DEB:
            maas = DebMAAS(executor, config)

    match args.command:
        case "init":
            maas.install()

        case "sync":
            sync_manager = SyncManager.create(maas)
            maas.ensure_installed()
            maas.stop()
            maas.build_artifacts()
            sync_manager.sync()
            maas.start()

        case "unsync":
            sync_manager = SyncManager.create(maas)
            maas.ensure_installed()
            maas.stop()
            sync_manager.unsync()
            maas.start()

        case "destroy":
            if inside_container:
                logger.error("'destroy' command cannot be run inside LXD container.")
                sys.exit(1)
            sync_manager = SyncManager.create(maas)
            sync_manager.unsync()
            lxd.remove_container()


if __name__ == "__main__":
    main()
