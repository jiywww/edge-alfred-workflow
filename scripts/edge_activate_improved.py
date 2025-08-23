#!/usr/bin/env python3
"""
Improved Edge workspace activation that minimizes window activation.
"""

import subprocess
import time
import json
import os
from typing import Optional, Tuple


def is_workspace_already_open(workspace_id: str) -> Tuple[bool, Optional[int], Optional[int]]:
    """
    Check if a workspace is already open using JXA.
    
    Parameters
    ----------
    workspace_id : str
        The workspace ID to check.
    
    Returns
    -------
    tuple
        (is_open, window_index, tab_index) - indices are 1-based if found
    """
    jxa_script = f"""
    (() => {{
        let edge = Application("Microsoft Edge");
        try {{
            let windows = edge.windows();
            
            for (let i = 0; i < windows.length; i++) {{
                let tabs = windows[i].tabs();
                for (let j = 0; j < tabs.length; j++) {{
                    let url = tabs[j].url();
                    // Check if this is a workspace tab
                    if (url && (url.includes("edge://workspaces/{workspace_id}") || 
                               url.includes("edge://workspaces/") && url.includes("{workspace_id}"))) {{
                        return JSON.stringify({{
                            found: true,
                            windowIndex: i + 1,
                            tabIndex: j + 1
                        }});
                    }}
                }}
            }}
            
            return JSON.stringify({{found: false}});
        }} catch(e) {{
            return JSON.stringify({{found: false, error: e.toString()}});
        }}
    }})();
    """
    
    try:
        result = subprocess.run(
            ["osascript", "-l", "JavaScript", "-e", jxa_script],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout.strip())
            if data.get("found"):
                return True, data.get("windowIndex"), data.get("tabIndex")
    except Exception:
        pass
    
    return False, None, None


def switch_to_existing_workspace(window_index: int, tab_index: int) -> bool:
    """
    Switch to an already open workspace tab without full activation.
    
    Parameters
    ----------
    window_index : int
        Window index (1-based).
    tab_index : int
        Tab index (1-based).
    
    Returns
    -------
    bool
        True if successful.
    """
    # Use the existing tab activation logic from edge_activate.py
    # This uses the Swift helper to raise only the specific window
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    list_windows_path = os.path.join(script_dir, "edge_list_windows")
    raise_window_path = os.path.join(script_dir, "edge_raise_window")
    
    # Get window information
    if os.path.exists(list_windows_path):
        result = subprocess.run(
            [list_windows_path], capture_output=True, text=True, timeout=2
        )
        if result.returncode == 0:
            try:
                windows = json.loads(result.stdout)
                if windows and window_index <= len(windows):
                    window = windows[window_index - 1]
                    pid = window["pid"]
                    window_number = window["windowNumber"]
                    
                    # Raise only this window
                    if os.path.exists(raise_window_path):
                        result = subprocess.run(
                            [raise_window_path, str(pid), str(window_number)],
                            capture_output=True,
                            text=True,
                            timeout=3
                        )
                        
                        if result.returncode == 0:
                            # Switch to the tab
                            switch_script = f"""
                            (() => {{
                                let edge = Application("Microsoft Edge");
                                try {{
                                    edge.windows[{window_index - 1}].activeTabIndex = {tab_index};
                                    return true;
                                }} catch(e) {{
                                    return false;
                                }}
                            }})();
                            """
                            subprocess.run(
                                ["osascript", "-l", "JavaScript", "-e", switch_script],
                                capture_output=True,
                                text=True,
                                timeout=1
                            )
                            return True
            except (json.JSONDecodeError, KeyError):
                pass
    
    return False


def activate_edge_for_workspace_improved(workspace_id: str, profile_dir: str) -> bool:
    """
    Improved workspace activation that checks if already open first.
    
    Parameters
    ----------
    workspace_id : str
        Workspace ID to open.
    profile_dir : str
        Profile directory for the workspace.
    
    Returns
    -------
    bool
        True if successful.
    """
    # Step 1: Check if workspace is already open
    is_open, window_idx, tab_idx = is_workspace_already_open(workspace_id)
    
    if is_open and window_idx and tab_idx:
        # Workspace is already open, just switch to it
        print(f"Workspace already open in window {window_idx}, tab {tab_idx}")
        return switch_to_existing_workspace(window_idx, tab_idx)
    
    # Step 2: Workspace not open, need to launch it
    # Try to launch in background first
    edge_bin = "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
    
    # Get current window count to detect new window
    script_dir = os.path.dirname(os.path.abspath(__file__))
    list_windows_path = os.path.join(script_dir, "edge_list_windows")
    
    windows_before = []
    window_numbers_before = set()
    if os.path.exists(list_windows_path):
        result = subprocess.run(
            [list_windows_path], capture_output=True, text=True, timeout=2
        )
        if result.returncode == 0:
            try:
                windows_before = json.loads(result.stdout)
                window_numbers_before = {w["windowNumber"] for w in windows_before}
            except (json.JSONDecodeError, KeyError):
                pass
    
    # Launch workspace
    # Try without activation first
    cmd = [
        edge_bin,
        f"--profile-directory={profile_dir}",
        f"--launch-workspace={workspace_id}",
        "--silent-launch",
        "--disable-features=AutofillShowTypePredictions",  # Reduces UI updates
        "--disable-features=MediaRouter",  # Reduces background activity
    ]
    
    # Use subprocess with specific flags to minimize activation
    env = os.environ.copy()
    env["NSUnbufferedIO"] = "YES"  # Prevent buffering issues
    
    try:
        # Launch without shell and with minimal connection
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            env=env,
            start_new_session=True,
            preexec_fn=os.setsid if hasattr(os, 'setsid') else None
        )
    except Exception:
        return False
    
    # Step 3: Wait for new window but don't activate it unless needed
    new_window = None
    max_attempts = 15  # 3 seconds
    
    for attempt in range(max_attempts):
        time.sleep(0.2)
        
        # Check if workspace opened
        is_open, window_idx, tab_idx = is_workspace_already_open(workspace_id)
        if is_open and window_idx and tab_idx:
            # Workspace opened successfully
            # Only raise window if user expects it
            # For now, we'll raise it but using single-window method
            return switch_to_existing_workspace(window_idx, tab_idx)
        
        # Also check for new window (fallback)
        if os.path.exists(list_windows_path):
            result = subprocess.run(
                [list_windows_path], capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                try:
                    windows_after = json.loads(result.stdout)
                    for w in windows_after:
                        if w["windowNumber"] not in window_numbers_before:
                            new_window = w
                            break
                except (json.JSONDecodeError, KeyError):
                    continue
    
    # If we detected a new window but couldn't find the workspace
    # It might still be loading
    if new_window:
        time.sleep(0.5)  # Give it time to load
        return True  # Report success even if we can't verify
    
    return False


if __name__ == "__main__":
    # Test the improved activation
    import sys
    
    if len(sys.argv) >= 3:
        workspace_id = sys.argv[1]
        profile_dir = sys.argv[2]
        
        print(f"Testing improved workspace activation...")
        print(f"Workspace: {workspace_id}")
        print(f"Profile: {profile_dir}")
        
        success = activate_edge_for_workspace_improved(workspace_id, profile_dir)
        print(f"Result: {'Success' if success else 'Failed'}")
    else:
        print("Usage: python edge_activate_improved.py <workspace_id> <profile_dir>")