"""Load the project configuration and resolve paths relative to the repository root."""
from __future__ import annotations

import hashlib
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = REPO_ROOT / "config" / "config.toml"


def load_config(path: str | Path = DEFAULT_CONFIG) -> dict:
    with open(path, "rb") as fh:
        return tomllib.load(fh)


def repo_path(relative: str) -> Path:
    """Absolute path of a file given relative to the repository root."""
    return REPO_ROOT / relative


def sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_checksum(path: str | Path, expected: str) -> None:
    """Fail loudly if a raw file is not the version recorded in the configuration."""
    if not expected:
        raise ValueError(f"No SHA-256 recorded in config for {path}; add it before running.")
    actual = sha256(path)
    if actual != expected:
        raise ValueError(
            f"Checksum mismatch for {path}:\n  expected {expected}\n  found    {actual}\n"
            "The raw file is not the version recorded in config/config.toml."
        )
