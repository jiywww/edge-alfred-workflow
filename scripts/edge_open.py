#!/usr/bin/env python3
from __future__ import annotations
import sys
from edge_paths import find_edge_binary
from edge_activate import activate_edge_for_profile


def open_with_profile(profile_dir: str, url: str | None = None) -> int:
    edge_bin = find_edge_binary()
    if not edge_bin.exists():
        print("Edge binary not found. Is Microsoft Edge installed?", file=sys.stderr)
        return 1
    
    # Use the new activation method that only brings one window forward
    if activate_edge_for_profile(profile_dir):
        return 0
    else:
        print("Failed to activate Edge profile", file=sys.stderr)
        return 2


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: edge_open.py <PROFILE_DIR> [URL]", file=sys.stderr)
        return 64
    return open_with_profile(argv[1], argv[2] if len(argv) >= 3 else None)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
