#!/usr/bin/env python3
"""
Alfred script filter for searching Microsoft Edge workspaces.

This script provides an Alfred interface for searching and selecting
Edge workspaces across all profiles.
"""

import sys
import time
from datetime import datetime
from typing import Dict, Any, List

import alfred_json
from edge_workspace_store import WorkspaceStore, EdgeWorkspace


def format_time_ago(timestamp: float) -> str:
    """
    Format a timestamp as a human-readable "time ago" string.

    Parameters
    ----------
    timestamp : float
        Unix timestamp.

    Returns
    -------
    str
        Human-readable time string like "2 hours ago" or "Yesterday".
    """
    if timestamp == 0:
        return "Never"

    now = time.time()
    diff = now - timestamp

    if diff < 0:
        return "Just now"

    if diff < 60:
        return "Just now"
    elif diff < 3600:
        minutes = int(diff / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif diff < 86400:
        hours = int(diff / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff < 172800:
        return "Yesterday"
    elif diff < 604800:
        days = int(diff / 86400)
        return f"{days} days ago"
    elif diff < 2592000:
        weeks = int(diff / 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    else:
        # For older items, show the actual date
        date = datetime.fromtimestamp(timestamp)
        return date.strftime("%B %d, %Y")


def get_workspace_icon(workspace: EdgeWorkspace) -> str:
    """
    Get the appropriate icon for a workspace.

    Parameters
    ----------
    workspace : EdgeWorkspace
        The workspace to get an icon for.

    Returns
    -------
    str
        Path to the icon file.
    """
    # Color mapping for workspace colors (simplified)
    # You could create colored folder icons for each color index
    return "icons/profile.png"


def format_workspace_subtitle(workspace: EdgeWorkspace) -> str:
    """
    Format the subtitle for a workspace item.

    Parameters
    ----------
    workspace : EdgeWorkspace
        The workspace to format.

    Returns
    -------
    str
        Formatted subtitle string.
    """
    parts = []

    # Profile name
    parts.append(f"Profile: {workspace.profile_name}")

    # Tab count
    if workspace.tab_count == 1:
        parts.append("1 tab")
    elif workspace.tab_count > 1:
        parts.append(f"{workspace.tab_count} tabs")

    # Active status or last active time
    if workspace.active:
        parts.append("Active")
    else:
        parts.append(format_time_ago(workspace.last_active_time))

    # Shared status
    if workspace.shared:
        parts.append("Shared")

    return " • ".join(parts)


def create_alfred_item(workspace: EdgeWorkspace) -> Dict[str, Any]:
    """
    Create an Alfred item for a workspace.

    Parameters
    ----------
    workspace : EdgeWorkspace
        The workspace to create an item for.

    Returns
    -------
    dict
        Alfred item representing the workspace.
    """
    # Prepare the argument as a JSON string with workspace ID and profile directory
    arg = f"{workspace.id}|{workspace.profile_dir}"

    # Add emoji for active/shared workspaces
    title = workspace.name
    if workspace.active:
        title = f"🟢 {title}"
    elif workspace.shared:
        title = f"👥 {title}"

    return alfred_json.item(
        title=title,
        subtitle=format_workspace_subtitle(workspace),
        arg=arg,
        uid=workspace.id,
        icon_path=get_workspace_icon(workspace),
        valid=True,
        mods={
            "alt": {
                "subtitle": f"Copy workspace ID: {workspace.id}",
                "arg": workspace.id,
                "valid": True,
            },
            "cmd": {
                "subtitle": f"Owner: {'Yes' if workspace.is_owner else 'No'} • Color: {workspace.color}",
                "valid": False,
            },
        },
    )


def main():
    """
    Main function for the Alfred script filter.
    """
    # Get query from Alfred
    query = sys.argv[1] if len(sys.argv) > 1 else ""

    # Initialize the workspace store
    store = WorkspaceStore()

    items: List[Dict[str, Any]] = []

    try:
        # Search for workspaces
        workspaces = store.search(query)

        if not workspaces:
            # No workspaces found
            if query:
                items.append(
                    alfred_json.item(
                        title="No workspaces found",
                        subtitle=f"No workspaces matching '{query}'",
                        icon_path="icons/edge-alfred.png",
                        valid=False,
                    )
                )
            else:
                items.append(
                    alfred_json.item(
                        title="No workspaces",
                        subtitle="No Edge workspaces found in any profile",
                        icon_path="icons/edge-alfred.png",
                        valid=False,
                    )
                )
        else:
            # Add workspace items
            for workspace in workspaces:
                item = create_alfred_item(workspace)
                items.append(item)

    except Exception as e:
        # Error handling
        items.append(
            alfred_json.item(
                title="Error loading workspaces",
                subtitle=str(e),
                icon_path="icons/edge-alfred.png",
                valid=False,
            )
        )

    # Output the results
    alfred_json.dump(items)


if __name__ == "__main__":
    main()
