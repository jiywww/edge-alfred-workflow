#!/usr/bin/env python3
from __future__ import annotations
import os
import subprocess
from pathlib import Path

_DEFAULT_EDGE_APP = "/Applications/Microsoft Edge.app"
_DEFAULT_BUNDLE_ID = "com.microsoft.edgemac"


def _edge_binary_from_app(app_path: Path) -> Path:
    return app_path / "Contents/MacOS/Microsoft Edge"


def find_edge_binary() -> Path:
    env_bin = os.environ.get("EDGE_BIN")
    if env_bin and Path(env_bin).exists():
        return Path(env_bin)
    env_app = os.environ.get("EDGE_APP")
    if env_app:
        p = _edge_binary_from_app(Path(env_app))
        if p.exists():
            return p
    p = _edge_binary_from_app(Path(_DEFAULT_EDGE_APP))
    if p.exists():
        return p
    bid = os.environ.get("EDGE_BUNDLE_ID", _DEFAULT_BUNDLE_ID)
    try:
        out = subprocess.check_output(
            [
                "mdfind",
                f"kMDItemCFBundleIdentifier == '{bid}' && kMDItemKind == 'Application'",
            ],
            text=True,
        ).strip()
        for line in out.splitlines():
            cand = Path(line)
            if cand.name.endswith("Microsoft Edge.app"):
                p = _edge_binary_from_app(cand)
                if p.exists():
                    return p
    except Exception:
        pass
    return p  # may not exist


def user_data_dir() -> Path:
    return Path(
        os.environ.get("EDGE_USER_DATA_DIR")
        or (Path.home() / "Library/Application Support/Microsoft Edge")
    )


def local_state_path() -> Path:
    return user_data_dir() / "Local State"


def profile_dir_path(dir_name: str) -> Path:
    return user_data_dir() / dir_name
