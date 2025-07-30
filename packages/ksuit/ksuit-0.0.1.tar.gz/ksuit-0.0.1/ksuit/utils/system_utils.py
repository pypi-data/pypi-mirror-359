import logging
import os
import platform
from pathlib import Path

_logger = logging.getLogger(__name__)

def get_installed_cuda_version() -> str | None:
    nvidia_smi_lines = os.popen("nvidia-smi").read().strip().split("\n")
    for line in nvidia_smi_lines:
        if "CUDA Version:" in line:
            return line[line.index("CUDA Version: ") + len("CUDA Version: "):-1].strip()
    return None

def log_system_info() -> None:
    _logger.info("------------------")
    _logger.info("SYSTEM INFO")
    _logger.info(f"host name: {platform.uname().node}")
    _logger.info(f"OS: {platform.platform()}")
    _logger.info(f"OS version: {platform.version()}")
    cuda_version = get_installed_cuda_version()
    if cuda_version is not None:
        _logger.info(f"CUDA version: {cuda_version}")

    # print hash of latest git commit (git describe or similar stuff is a bit ugly because it would require the
    # git.exe path to be added in path as conda/python do something with the path and don't use the system
    # PATH variable by default)
    git_hash_file = Path(".git") / "FETCH_HEAD"
    if git_hash_file.exists():
        with open(git_hash_file) as f:
            lines = f.readlines()
            if len(lines) == 0:
                # this happened when I didn't have internet
                _logger.warning(".git/FETCH_HEAD has no content")
            else:
                git_hash = lines[0][:40]
                _logger.info(f"current commit hash: {git_hash}")
    else:
        _logger.warning("could not retrieve current git commit hash from ./.git/FETCH_HEAD")
