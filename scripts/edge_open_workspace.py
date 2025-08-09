#!/usr/bin/env python3
"""
Open Microsoft Edge with a specific workspace.

This script launches Edge with a specified workspace and profile.
"""

import subprocess
import sys

import edge_paths
from edge_workspace_store import WorkspaceStore


def open_workspace(workspace_id: str, profile_dir: str):
    """
    Open Edge with a specific workspace.
    
    Parameters
    ----------
    workspace_id : str
        The workspace ID to open.
    profile_dir : str
        The profile directory (e.g., "Default", "Profile 1").
    
    Returns
    -------
    int
        Exit code (0 for success, non-zero for error).
    """
    # Check if Edge is installed
    edge_binary = edge_paths.find_edge_binary()
    if not edge_binary.exists():
        print("Error: Microsoft Edge is not installed", file=sys.stderr)
        return 1
    
    # Build the command
    cmd = [str(edge_binary)]
    
    # Add profile directory argument if not Default
    if profile_dir and profile_dir != "Default":
        cmd.extend(["--profile-directory", profile_dir])
    
    # Add workspace launch argument
    cmd.append(f"--launch-workspace={workspace_id}")
    
    try:
        # Launch Edge with the workspace
        subprocess.run(cmd, check=False)
        return 0
    except Exception as e:
        print(f"Error launching Edge: {e}", file=sys.stderr)
        return 2


def main():
    """
    Main function for the script.
    """
    if len(sys.argv) < 2:
        print("Usage: edge_open_workspace.py <workspace_id>|<profile_dir>", file=sys.stderr)
        return 64
    
    # Parse the argument (format: "workspace_id|profile_dir")
    arg = sys.argv[1]
    parts = arg.split("|")
    
    if len(parts) != 2:
        print("Error: Invalid argument format. Expected: workspace_id|profile_dir", file=sys.stderr)
        return 64
    
    workspace_id = parts[0]
    profile_dir = parts[1]
    
    # Validate the workspace exists
    store = WorkspaceStore()
    workspace = store.get_workspace_by_id(workspace_id)
    
    if not workspace:
        print(f"Error: Workspace '{workspace_id}' not found", file=sys.stderr)
        return 2
    
    # Open the workspace
    return open_workspace(workspace_id, profile_dir)


if __name__ == "__main__":
    sys.exit(main())