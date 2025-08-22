#!/usr/bin/env python3
"""
Get currently active (open) Edge workspaces.

This module uses AppleScript/JXA to query actual open Edge windows
to determine which workspaces are truly active.
"""

import subprocess
import json
from typing import Set


def get_active_workspace_names() -> Set[str]:
    """
    Get names of currently active (open) workspaces.
    
    Returns
    -------
    set of str
        Set of workspace names that are currently open in Edge windows.
    """
    # JXA script to get all Edge window names
    jxa_script = '''
    let edge = Application("Microsoft Edge");
    let names = [];
    try {
        if (edge.running()) {
            names = edge.windows().map(w => w.name());
        }
    } catch(e) {
        // Edge not running or no windows
    }
    JSON.stringify(names);
    '''
    
    try:
        result = subprocess.run(
            ['osascript', '-l', 'JavaScript', '-e', jxa_script],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode == 0 and result.stdout:
            window_names = json.loads(result.stdout.strip())
            # Filter out empty names and return as set
            return {name for name in window_names if name}
        
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
        # If anything fails, return empty set
        pass
    
    return set()


def is_workspace_active(workspace_name: str) -> bool:
    """
    Check if a specific workspace is currently active (has an open window).
    
    Parameters
    ----------
    workspace_name : str
        Name of the workspace to check.
    
    Returns
    -------
    bool
        True if the workspace has an open window, False otherwise.
    """
    active_workspaces = get_active_workspace_names()
    return workspace_name in active_workspaces


if __name__ == "__main__":
    # Test the function
    active = get_active_workspace_names()
    print(f"Active workspaces: {active}")
    
    # Test specific workspaces
    test_names = ["Main", "work 01", "shopping 01", "InvestAI"]
    for name in test_names:
        status = is_workspace_active(name)
        print(f"  {name}: {'Active' if status else 'Not active'}")