#!/usr/bin/env python3
from __future__ import annotations
import subprocess
import sys
from edge_paths import find_edge_binary


def open_with_profile(profile_dir: str, url: str | None = None) -> int:
    edge_bin = find_edge_binary()
    if not edge_bin.exists():
        print("Edge binary not found. Is Microsoft Edge installed?", file=sys.stderr)
        return 1
    args = [str(edge_bin), f"--profile-directory={profile_dir}"]
    if url:
        args.append(url)
    try:
        # Launch Edge
        subprocess.Popen(args)
        
        # Bring Edge to front using AppleScript
        applescript = '''
        tell application "Microsoft Edge"
            activate
        end tell
        '''
        subprocess.run(['osascript', '-e', applescript], capture_output=True)
        
        return 0
    except Exception as e:
        print(f"Failed to open Edge: {e}", file=sys.stderr)
        return 2


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: edge_open.py <PROFILE_DIR> [URL]", file=sys.stderr)
        return 64
    return open_with_profile(argv[1], argv[2] if len(argv) >= 3 else None)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
