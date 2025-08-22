#!/usr/bin/env python3
"""
Universal Edge window activation module.

This module provides methods to activate Edge windows.

Note: Due to macOS system limitations, activating Edge will bring ALL windows
to the front. This is standard macOS behavior and cannot be avoided.
See WINDOW_ACTIVATION_RESEARCH.md for details on methods tested.
"""

import subprocess
import time
from typing import Optional


def activate_edge():
    """
    Activate Microsoft Edge application.
    
    Note: This will bring ALL Edge windows to the front due to macOS
    system design. This is the expected behavior on macOS.
    
    Returns
    -------
    bool
        True if successful, False otherwise.
    """
    try:
        # Use standard activation via AppleScript
        applescript = '''
        tell application "Microsoft Edge"
            activate
        end tell
        '''
        result = subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False


def activate_edge_for_profile(profile_dir: str):
    """
    Launch and activate Edge for a specific profile.
    
    This method only brings ONE window to the front (the new profile window)
    by using the 'open' command with a URL.
    
    Parameters
    ----------
    profile_dir : str
        Profile directory name (e.g., "Default", "Profile 1").
    
    Returns
    -------
    bool
        True if successful, False otherwise.
    """
    import os
    
    # First launch the profile window
    edge_bin = "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
    try:
        subprocess.Popen([edge_bin, f"--profile-directory={profile_dir}"])
        # Small delay to let window open
        time.sleep(0.3)
        
        # Get the URL to open from Alfred workflow configuration
        # Users can set this in Alfred Preferences > Workflows > Edge Control > [x] Configure
        activation_url = os.environ.get('EDGE_PROFILE_START_URL', 'edge://newtab')
        
        # Then use 'open' with the configured URL to activate only the new window
        result = subprocess.run(['open', '-a', 'Microsoft Edge', activation_url], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False


def activate_edge_for_workspace(workspace_id: str, profile_dir: str):
    """
    Launch and activate Edge for a specific workspace.
    
    Parameters
    ----------
    workspace_id : str
        Workspace ID to open.
    profile_dir : str
        Profile directory for the workspace.
    
    Returns
    -------
    bool
        True if successful, False otherwise.
    """
    # First launch the workspace window
    edge_bin = "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
    try:
        subprocess.Popen([
            edge_bin,
            f"--profile-directory={profile_dir}",
            f"--launch-workspace={workspace_id}"
        ])
        # Small delay to let window open
        time.sleep(0.3)
    except Exception:
        return False
    
    # Then activate Edge (will bring all windows forward)
    return activate_edge()


def activate_edge_for_tab(window_index: int, tab_index: int):
    """
    Activate Edge and switch to a specific tab.
    
    Parameters
    ----------
    window_index : int
        Window index (1-based).
    tab_index : int
        Tab index within window (1-based).
    
    Returns
    -------
    bool
        True if successful, False otherwise.
    """
    # Switch to the tab and bring the window to front
    applescript = f'''
    tell application "Microsoft Edge"
        -- First set the target window as the front window
        set index of window {window_index} to 1
        -- Then switch to the specific tab
        set active tab index of window 1 to {tab_index}
        -- Finally activate the application
        activate
    end tell
    '''
    
    try:
        result = subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False


if __name__ == "__main__":
    # Test the activation
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "profile" and len(sys.argv) > 2:
            success = activate_edge_for_profile(sys.argv[2])
            print(f"Profile activation: {'Success' if success else 'Failed'}")
        elif sys.argv[1] == "workspace" and len(sys.argv) > 3:
            success = activate_edge_for_workspace(sys.argv[2], sys.argv[3])
            print(f"Workspace activation: {'Success' if success else 'Failed'}")
        elif sys.argv[1] == "tab" and len(sys.argv) > 3:
            success = activate_edge_for_tab(int(sys.argv[2]), int(sys.argv[3]))
            print(f"Tab activation: {'Success' if success else 'Failed'}")
        else:
            success = activate_edge()
            print(f"Default activation: {'Success' if success else 'Failed'}")
    else:
        success = activate_edge()
        print(f"Default activation: {'Success' if success else 'Failed'}")