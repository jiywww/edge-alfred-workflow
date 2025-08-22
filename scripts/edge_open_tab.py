#!/usr/bin/env python3
"""
Open/switch to a specific Edge tab.

This script switches to a specific tab in Microsoft Edge
by window and tab index.
"""

import sys
import subprocess
import os


def switch_to_tab(window_index: int, tab_index: int) -> bool:
    """
    Switch to a specific tab in Edge using JXA.

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
    jxa_script = f'''
    (() => {{
        let edge = Application("Microsoft Edge");
        
        try {{
            if (!edge.running()) {{
                return JSON.stringify({{success: false, error: "Edge is not running"}});
            }}
            
            let windows = edge.windows();
            
            // Check if window exists (convert to 0-based index)
            let windowIdx = {window_index - 1};
            if (windowIdx < 0 || windowIdx >= windows.length) {{
                return JSON.stringify({{
                    success: false, 
                    error: `Window {window_index} not found (only ${{windows.length}} windows open)`
                }});
            }}
            
            let window = windows[windowIdx];
            let tabs = window.tabs();
            
            // Check if tab exists (convert to 0-based index)
            let tabIdx = {tab_index - 1};
            if (tabIdx < 0 || tabIdx >= tabs.length) {{
                return JSON.stringify({{
                    success: false,
                    error: `Tab {tab_index} not found in window {window_index} (only ${{tabs.length}} tabs)`
                }});
            }}
            
            // Activate Edge application
            edge.activate();
            
            // Bring window to front
            window.index = 1;
            
            // Get the tab's URL and title for activation
            let targetTab = tabs[tabIdx];
            let targetUrl = targetTab.url();
            
            // Set active tab by URL matching (workaround)
            window.activeTabIndex = tabIdx + 1;
            
            return JSON.stringify({{success: true}});
            
        }} catch(e) {{
            return JSON.stringify({{success: false, error: e.toString()}});
        }}
    }})();
    '''

    try:
        result = subprocess.run(
            ['osascript', '-l', 'JavaScript', '-e', jxa_script],
            capture_output=True,
            text=True,
            timeout=3
        )

        if result.returncode == 0 and result.stdout:
            import json
            response = json.loads(result.stdout.strip())
            
            if response.get('success'):
                return True
            else:
                error = response.get('error', 'Unknown error')
                print(f"Error: {error}", file=sys.stderr)
                return False
        else:
            print(f"Script failed with return code {result.returncode}", file=sys.stderr)
            if result.stderr:
                print(f"Error: {result.stderr}", file=sys.stderr)
            return False

    except subprocess.TimeoutExpired:
        print("Script timed out", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return False


def copy_url_to_clipboard(url: str) -> bool:
    """
    Copy URL to clipboard.

    Parameters
    ----------
    url : str
        URL to copy.

    Returns
    -------
    bool
        True if successful, False otherwise.
    """
    try:
        subprocess.run(
            ['pbcopy'],
            input=url,
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def close_tab(window_index: int, tab_index: int) -> bool:
    """
    Close a specific tab in Edge using JXA.

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
    jxa_script = f'''
    (() => {{
        let edge = Application("Microsoft Edge");
        
        try {{
            if (!edge.running()) {{
                return JSON.stringify({{success: false, error: "Edge is not running"}});
            }}
            
            let windows = edge.windows();
            let windowIdx = {window_index - 1};
            
            if (windowIdx < 0 || windowIdx >= windows.length) {{
                return JSON.stringify({{success: false, error: "Window not found"}});
            }}
            
            let window = windows[windowIdx];
            let tabs = window.tabs();
            let tabIdx = {tab_index - 1};
            
            if (tabIdx < 0 || tabIdx >= tabs.length) {{
                return JSON.stringify({{success: false, error: "Tab not found"}});
            }}
            
            // Close the tab
            tabs[tabIdx].close();
            
            return JSON.stringify({{success: true}});
            
        }} catch(e) {{
            return JSON.stringify({{success: false, error: e.toString()}});
        }}
    }})();
    '''

    try:
        result = subprocess.run(
            ['osascript', '-l', 'JavaScript', '-e', jxa_script],
            capture_output=True,
            text=True,
            timeout=3
        )

        if result.returncode == 0:
            return True
        else:
            return False

    except Exception:
        return False


def main():
    """
    Main function to handle tab operations.
    """
    if len(sys.argv) < 2:
        print("Usage: edge_open_tab.py <window_index>:<tab_index>", file=sys.stderr)
        print("   or: edge_open_tab.py --copy-url <url>", file=sys.stderr)
        print("   or: edge_open_tab.py --close <window_index>:<tab_index>", file=sys.stderr)
        sys.exit(64)

    # Check for special actions from environment variables (Alfred)
    action = os.environ.get('action', 'switch')

    if action == 'copy_url' and len(sys.argv) >= 2:
        # Copy URL to clipboard
        url = sys.argv[1]
        if copy_url_to_clipboard(url):
            print(f"URL copied to clipboard: {url}")
            sys.exit(0)
        else:
            print("Failed to copy URL to clipboard", file=sys.stderr)
            sys.exit(1)

    elif action == 'close_tab' and len(sys.argv) >= 2:
        # Close tab
        arg = sys.argv[1]
        try:
            window_index, tab_index = map(int, arg.split(':'))
            if close_tab(window_index, tab_index):
                print(f"Closed tab {tab_index} in window {window_index}")
                sys.exit(0)
            else:
                print(f"Failed to close tab {tab_index} in window {window_index}", file=sys.stderr)
                sys.exit(1)
        except ValueError:
            print(f"Invalid argument format: {arg}", file=sys.stderr)
            sys.exit(64)

    else:
        # Default action: switch to tab
        arg = sys.argv[1]
        
        try:
            # Parse window:tab format
            window_index, tab_index = map(int, arg.split(':'))
        except ValueError:
            print(f"Invalid argument format: {arg}", file=sys.stderr)
            print("Expected format: <window_index>:<tab_index>", file=sys.stderr)
            sys.exit(64)

        # Switch to the tab
        if switch_to_tab(window_index, tab_index):
            print(f"Switched to tab {tab_index} in window {window_index}")
            sys.exit(0)
        else:
            print(f"Failed to switch to tab {tab_index} in window {window_index}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()