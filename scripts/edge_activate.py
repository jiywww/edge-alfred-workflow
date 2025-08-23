#!/usr/bin/env python3
"""
Universal Edge window activation module.

This module provides methods to activate Edge windows.

Note: Due to macOS system limitations, activating Edge will bring ALL windows
to the front. This is standard macOS behavior and cannot be avoided.
See WINDOW_ACTIVATION_RESEARCH.md for details on methods tested.
"""

import subprocess


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
        applescript = """
        tell application "Microsoft Edge"
            activate
        end tell
        """
        result = subprocess.run(
            ["osascript", "-e", applescript], capture_output=True, text=True
        )
        return result.returncode == 0
    except Exception:
        return False


def activate_edge_for_profile(profile_dir: str):
    """
    Launch and activate Edge for a specific profile.

    Note: If a window with this profile is already open, it will be activated.
    Otherwise, a new window will be opened. Profile must exist.

    Parameters
    ----------
    profile_dir : str
        Profile directory name (e.g., "Default", "Profile 1").

    Returns
    -------
    bool
        True if successful, False otherwise.
    """
    import sys
    from edge_profile_store import ProfileStore

    # Check if profile exists
    store = ProfileStore()
    profiles = store.load()
    profile_exists = any(p.dir_name == profile_dir for p in profiles)

    if not profile_exists:
        print(f"Profile {profile_dir} does not exist", file=sys.stderr)
        return False

    # For profile activation, we'll use the original method which works well
    edge_bin = "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
    try:
        # Launch with profile
        subprocess.Popen([edge_bin, f"--profile-directory={profile_dir}"])
        return True
    except Exception:
        return False


def activate_edge_for_workspace(workspace_id: str, profile_dir: str):
    """
    Launch and activate Edge for a specific workspace.

    This method creates the workspace window in the background, then uses
    the Swift helper to raise only that specific window, avoiding the issue
    of bringing all Edge windows forward.

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
    import os
    import json
    import time
    
    edge_bin = "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"

    try:
        # Step 1: Launch workspace in background (won't bring window forward)
        subprocess.Popen(
            [
                edge_bin,
                f"--profile-directory={profile_dir}",
                f"--launch-workspace={workspace_id}",
            ]
        )
        
        # Give Edge time to create the window
        time.sleep(1.5)
        
        # Step 2: Get the newly created window information
        script_dir = os.path.dirname(os.path.abspath(__file__))
        list_windows_path = os.path.join(script_dir, "edge_list_windows")
        
        if not os.path.exists(list_windows_path):
            # Fallback: If no window lister, just return (window created but in background)
            return True
            
        result = subprocess.run(
            [list_windows_path], capture_output=True, text=True, timeout=2
        )
        
        if result.returncode != 0:
            return True  # Window created but we can't raise it
            
        try:
            windows = json.loads(result.stdout)
            if not windows:
                return True  # No windows found, but launch succeeded
                
            # Get the most recently created window (should be first in list)
            # The window list is typically ordered with newest/frontmost first
            newest_window = windows[0]
            pid = newest_window["pid"]
            window_number = newest_window["windowNumber"]
            
        except (json.JSONDecodeError, KeyError):
            return True  # Window created but can't parse info
            
        # Step 3: Use the Swift helper to raise only the workspace window
        raise_window_path = os.path.join(script_dir, "edge_raise_window")
        
        if not os.path.exists(raise_window_path):
            return True  # Window created but can't raise it
            
        result = subprocess.run(
            [raise_window_path, str(pid), str(window_number)],
            capture_output=True,
            text=True,
            timeout=3,
        )
        
        return result.returncode == 0
        
    except Exception:
        return False


def activate_edge_for_tab(window_index: int, tab_index: int):
    """
    Activate Edge and switch to a specific tab.

    This uses a custom Swift helper to raise only the specific window,
    avoiding the macOS limitation of bringing all windows forward.

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
    import os
    import json

    # Step 1: Get window information using our Swift window lister
    script_dir = os.path.dirname(os.path.abspath(__file__))
    list_windows_path = os.path.join(script_dir, "edge_list_windows")

    # Try to get window information
    if os.path.exists(list_windows_path):
        result = subprocess.run(
            [list_windows_path], capture_output=True, text=True, timeout=2
        )
        if result.returncode == 0:
            try:
                windows = json.loads(result.stdout)
                if windows and window_index <= len(windows):
                    # Get the window info (window_index is 1-based, array is 0-based)
                    window = windows[window_index - 1]
                    pid = window["pid"]
                    window_number = window["windowNumber"]
                else:
                    return _activate_edge_for_tab_fallback(window_index, tab_index)
            except (json.JSONDecodeError, KeyError):
                return _activate_edge_for_tab_fallback(window_index, tab_index)
        else:
            return _activate_edge_for_tab_fallback(window_index, tab_index)
    else:
        return _activate_edge_for_tab_fallback(window_index, tab_index)

    # Step 2: Use the Swift helper to raise only the specific window
    raise_window_path = os.path.join(script_dir, "edge_raise_window")

    if not os.path.exists(raise_window_path):
        return _activate_edge_for_tab_fallback(window_index, tab_index)

    result = subprocess.run(
        [raise_window_path, str(pid), str(window_number)],
        capture_output=True,
        text=True,
        timeout=3,
    )

    if result.returncode != 0:
        return _activate_edge_for_tab_fallback(window_index, tab_index)

    # Step 3: Switch to the tab after the window is raised
    switch_tab_script = f"""
    (() => {{
        let edge = Application("Microsoft Edge");
        try {{
            let windows = edge.windows();
            if ({window_index - 1} < windows.length) {{
                let window = windows[{window_index - 1}];
                window.activeTabIndex = {tab_index};
                return true;
            }}
            return false;
        }} catch(e) {{
            return false;
        }}
    }})();
    """

    try:
        subprocess.run(
            ["osascript", "-l", "JavaScript", "-e", switch_tab_script],
            capture_output=True,
            text=True,
            timeout=1,
        )
    except Exception:
        pass  # Tab switch is optional, window is already raised

    return True


def _activate_edge_for_tab_fallback(window_index: int, tab_index: int):
    """
    Fallback method for tab activation (brings all windows forward).

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
    # Original implementation
    applescript = f"""
    tell application "Microsoft Edge"
        -- First set the target window as the front window
        set index of window {window_index} to 1
        -- Then switch to the specific tab
        set active tab index of window 1 to {tab_index}
        -- Finally activate the application
        activate
    end tell
    """

    try:
        result = subprocess.run(
            ["osascript", "-e", applescript], capture_output=True, text=True
        )
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
