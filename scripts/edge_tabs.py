#!/usr/bin/env python3
"""
Edge tabs search for Alfred workflow.

This script provides search functionality for open Edge tabs
and outputs results in Alfred's JSON format.
"""

import sys
from typing import List, Dict, Any
import os

import alfred_json
from edge_tabs_store import TabStore, EdgeTab


def format_tab_for_alfred(tab: EdgeTab) -> Dict[str, Any]:
    """
    Format an EdgeTab for Alfred output.

    Parameters
    ----------
    tab : EdgeTab
        The tab to format.

    Returns
    -------
    dict
        Alfred item dictionary.
    """
    # Create title with visual indicators
    title_parts = [tab.title]
    if tab.active:
        title_parts.append("⭐")
    
    title = " ".join(title_parts)
    
    # Create subtitle with profile and workspace info
    subtitle_parts = []
    
    # Add profile info (without email)
    subtitle_parts.append(tab.profile_name)
    
    # Add workspace info
    if tab.workspace_name:
        workspace_info = tab.workspace_name
        if tab.workspace_shared:
            workspace_info += " 👥"
        subtitle_parts.append(f"📂 {workspace_info}")
    
    # Add truncated URL
    url_display = tab.url
    if len(url_display) > 50:
        url_display = url_display[:47] + "..."
    subtitle_parts.append(url_display)
    
    subtitle = " | ".join(subtitle_parts)
    
    # Create argument for opening the tab
    # Format: window_index:tab_index
    arg = f"{tab.window_index}:{tab.tab_index}"
    
    # Create unique ID
    uid = f"tab_{tab.window_id}_{tab.tab_index}"
    
    # Icon path - use Edge icon or profile icon if available
    icon_path = os.path.join(os.path.dirname(__file__), "..", "icons", "edge-alfred.png")
    
    # Add modifiers for additional actions
    mods = {
        "cmd": {
            "subtitle": f"Copy URL: {tab.url}",
            "arg": tab.url,
            "variables": {"action": "copy_url"}
        },
        "alt": {
            "subtitle": "Close this tab",
            "arg": arg,
            "variables": {"action": "close_tab"}
        }
    }
    
    return alfred_json.item(
        title=title,
        subtitle=subtitle,
        arg=arg,
        uid=uid,
        icon_path=icon_path,
        mods=mods,
        variables={
            "window_index": str(tab.window_index),
            "tab_index": str(tab.tab_index),
            "profile_dir": tab.profile_dir,
            "workspace_id": tab.workspace_id or ""
        }
    )


def main():
    """
    Main function for Alfred script filter.
    """
    # Get query from Alfred (if any)
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    
    # Initialize tab store
    store = TabStore()
    
    # Search tabs
    if query:
        tabs = store.search_tabs(query)
    else:
        # Show all tabs if no query
        tabs = store.load_all_tabs()
    
    # Format results for Alfred
    items = []
    
    if not tabs:
        # No tabs found
        if query:
            message = f"No tabs matching '{query}'"
        else:
            message = "No open Edge tabs found"
        
        items.append(
            alfred_json.item(
                title=message,
                subtitle="Make sure Microsoft Edge is running with open tabs",
                valid=False,
                icon_path=os.path.join(os.path.dirname(__file__), "..", "icons", "edge-alfred.png")
            )
        )
    else:
        # Add all matching tabs
        for tab in tabs[:50]:  # Limit to 50 results for performance
            items.append(format_tab_for_alfred(tab))
        
        # If there are more results, add a note
        if len(tabs) > 50:
            items.append(
                alfred_json.item(
                    title=f"... and {len(tabs) - 50} more tabs",
                    subtitle="Refine your search to see more specific results",
                    valid=False,
                    icon_path=os.path.join(os.path.dirname(__file__), "..", "icons", "edge-alfred.png")
                )
            )
    
    # Output JSON for Alfred
    alfred_json.dump(items)


if __name__ == "__main__":
    main()