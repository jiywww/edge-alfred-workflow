#!/usr/bin/env python3
"""
Edge Tabs Store for Microsoft Edge.

This module provides functionality to get all open tabs from Microsoft Edge
using JXA (JavaScript for Automation) and correlates them with profile and
workspace information.
"""

import subprocess
import json
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import sys

from edge_workspace_store import WorkspaceStore, EdgeWorkspace
from edge_profile_store import ProfileStore, EdgeProfile


@dataclass(frozen=True)
class EdgeTab:
    """
    Represents an open Microsoft Edge tab.

    Attributes
    ----------
    title : str
        Tab title.
    url : str
        Tab URL.
    window_index : int
        Window index (1-based).
    window_id : int
        Window ID from JXA.
    window_name : str
        Window name (often workspace name).
    tab_index : int
        Tab index within window (1-based).
    active : bool
        Whether this is the active tab in its window.
    profile_name : str
        Name of the profile.
    profile_email : str
        Email associated with the profile.
    profile_dir : str
        Profile directory name.
    workspace_name : Optional[str]
        Workspace name if in a workspace.
    workspace_id : Optional[str]
        Workspace ID if in a workspace.
    workspace_shared : bool
        Whether the workspace is shared.
    """

    title: str
    url: str
    window_index: int
    window_id: int
    window_name: str
    tab_index: int
    active: bool
    profile_name: str
    profile_email: str
    profile_dir: str
    workspace_name: Optional[str] = None
    workspace_id: Optional[str] = None
    workspace_shared: bool = False


class TabStore:
    """
    Manages Edge tab data by querying open windows and tabs.

    This class uses JXA to get all open tabs and correlates them
    with profile and workspace information.
    """

    def __init__(self):
        """
        Initialize the TabStore.
        """
        self.workspace_store = WorkspaceStore()
        self.profile_store = ProfileStore()
        self._tabs_cache: Optional[List[EdgeTab]] = None

    def _get_tabs_jxa(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get all Edge tabs using JXA (JavaScript for Automation).

        Returns
        -------
        list of dict or None
            List of raw tab information from JXA.
        """
        jxa_script = '''
        (() => {
            let edge = Application("Microsoft Edge");
            let se = Application("System Events");
            let tabs = [];
            
            try {
                if (edge.running()) {
                    let windows = edge.windows();
                    let edgeProcess = se.processes.byName("Microsoft Edge");
                    let seWindows = edgeProcess.windows();
                    
                    for (let i = 0; i < windows.length; i++) {
                        let window = windows[i];
                        let windowName = window.name();
                        let windowIndex = i + 1;
                        let windowId = window.id();
                        
                        // Get profile name from System Events window title
                        let profileName = null;
                        try {
                            if (i < seWindows.length) {
                                let seTitle = seWindows[i].title();
                                // Parse pattern: "... - Microsoft Edge - ProfileName"
                                let match = seTitle.match(/ - Microsoft Edge - ([^-]+)$/);
                                if (match) {
                                    profileName = match[1].trim();
                                }
                            }
                        } catch(e) {
                            // Ignore System Events errors
                        }
                        
                        // Try to get tabs from this window
                        let windowTabs = window.tabs();
                        
                        for (let j = 0; j < windowTabs.length; j++) {
                            let tab = windowTabs[j];
                            let tabInfo = {
                                title: tab.title(),
                                url: tab.url(),
                                windowIndex: windowIndex,
                                windowId: windowId,
                                windowName: windowName,
                                tabIndex: j + 1,
                                active: tab === window.activeTab(),
                                profileName: profileName
                            };
                            tabs.push(tabInfo);
                        }
                    }
                }
            } catch(e) {
                // Return error info
                return JSON.stringify({error: e.toString()});
            }
            
            return JSON.stringify({tabs: tabs});
        })();
        '''

        try:
            result = subprocess.run(
                ['osascript', '-l', 'JavaScript', '-e', jxa_script],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0 and result.stdout:
                data = json.loads(result.stdout.strip())

                if 'error' in data:
                    print(f"JXA Error: {data['error']}", file=sys.stderr)
                    return None

                return data.get('tabs', [])

        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
            return None

    def _correlate_workspace(
        self, window_name: str, workspaces: List[EdgeWorkspace]
    ) -> Optional[EdgeWorkspace]:
        """
        Find matching workspace for a window name.

        Parameters
        ----------
        window_name : str
            The window name from JXA.
        workspaces : list of EdgeWorkspace
            All available workspaces.

        Returns
        -------
        EdgeWorkspace or None
            Matching workspace if found.
        """
        # Direct name match
        for workspace in workspaces:
            if workspace.name == window_name:
                return workspace

        # Check if window name contains workspace name
        for workspace in workspaces:
            if workspace.name in window_name:
                return workspace

        return None

    def load_all_tabs(self) -> List[EdgeTab]:
        """
        Load all open tabs from Microsoft Edge.

        Returns
        -------
        list of EdgeTab
            All open tabs with profile and workspace information.
        """
        if self._tabs_cache is not None:
            return self._tabs_cache

        # Get raw tab data from JXA
        raw_tabs = self._get_tabs_jxa()
        if not raw_tabs:
            return []

        # Load workspace and profile data
        workspaces = self.workspace_store.load_all_workspaces()
        profiles = self.profile_store.load()

        # Create profile lookup by directory
        profile_by_dir = {p.dir_name: p for p in profiles}

        # Default profile for unknown tabs
        default_profile = EdgeProfile(
            dir_name="Default",
            display_name="Default Profile",
            email=None,
            is_omitted_from_ui=False,
            avatar_icon=None,
            gaia_picture_file_name=None
        )

        # Create profile lookup by name
        profile_by_name = {p.display_name: p for p in profiles}

        tabs = []
        for raw_tab in raw_tabs:
            # Try to find matching workspace
            workspace = self._correlate_workspace(raw_tab['windowName'], workspaces)

            # Determine profile
            profile = None
            
            # First try to use the profile name from System Events
            if raw_tab.get('profileName'):
                profile = profile_by_name.get(raw_tab['profileName'])
            
            # If workspace exists, use its profile
            if not profile and workspace:
                profile = profile_by_dir.get(workspace.profile_dir)
            
            # Fallback to default profile
            if not profile:
                profile = default_profile

            # Create EdgeTab object
            tab = EdgeTab(
                title=raw_tab.get('title', 'Untitled'),
                url=raw_tab.get('url', 'about:blank'),
                window_index=raw_tab.get('windowIndex', 0),
                window_id=raw_tab.get('windowId', 0),
                window_name=raw_tab.get('windowName', ''),
                tab_index=raw_tab.get('tabIndex', 0),
                active=raw_tab.get('active', False),
                profile_name=profile.display_name,
                profile_email=profile.email or '',
                profile_dir=profile.dir_name,
                workspace_name=workspace.name if workspace else None,
                workspace_id=workspace.id if workspace else None,
                workspace_shared=workspace.shared if workspace else False
            )
            tabs.append(tab)

        self._tabs_cache = tabs
        return tabs

    def search_tabs(self, query: str) -> List[EdgeTab]:
        """
        Search tabs by title or URL.

        Parameters
        ----------
        query : str
            Search query string.

        Returns
        -------
        list of EdgeTab
            Matching tabs sorted by relevance.
        """
        tabs = self.load_all_tabs()
        
        if not query:
            return tabs

        query_lower = query.lower()
        scored_tabs = []

        for tab in tabs:
            score = 0
            title_lower = tab.title.lower()
            url_lower = tab.url.lower()

            # Exact matches get highest score
            if query_lower == title_lower:
                score = 1000
            elif query_lower == url_lower:
                score = 900
            # Title contains query
            elif query_lower in title_lower:
                score = 500
                # Bonus if query is at the beginning
                if title_lower.startswith(query_lower):
                    score += 100
            # URL contains query  
            elif query_lower in url_lower:
                score = 300
                # Bonus for domain match
                if f"://{query_lower}" in url_lower or f".{query_lower}." in url_lower:
                    score += 100
            # Workspace or profile name match
            elif tab.workspace_name and query_lower in tab.workspace_name.lower():
                score = 200
            elif query_lower in tab.profile_name.lower():
                score = 150
            
            # Bonus for active tab
            if tab.active:
                score += 50

            if score > 0:
                scored_tabs.append((score, tab))

        # Sort by score (descending) and return tabs
        scored_tabs.sort(key=lambda x: x[0], reverse=True)
        return [tab for _, tab in scored_tabs]

    def get_tab_by_indices(
        self, window_index: int, tab_index: int
    ) -> Optional[EdgeTab]:
        """
        Get a specific tab by window and tab indices.

        Parameters
        ----------
        window_index : int
            Window index (1-based).
        tab_index : int
            Tab index within window (1-based).

        Returns
        -------
        EdgeTab or None
            The tab if found.
        """
        tabs = self.load_all_tabs()
        
        for tab in tabs:
            if tab.window_index == window_index and tab.tab_index == tab_index:
                return tab
        
        return None

    def clear_cache(self):
        """Clear the tabs cache to force reload on next access."""
        self._tabs_cache = None


if __name__ == "__main__":
    # Test the TabStore
    store = TabStore()
    tabs = store.load_all_tabs()
    
    print(f"Found {len(tabs)} open tabs\n")
    
    # Show first 5 tabs
    for i, tab in enumerate(tabs[:5], 1):
        print(f"{i}. {tab.title}")
        print(f"   URL: {tab.url}")
        print(f"   Profile: {tab.profile_name} ({tab.profile_email})")
        if tab.workspace_name:
            print(f"   Workspace: {tab.workspace_name}")
        print()
    
    # Test search
    query = "github"
    results = store.search_tabs(query)
    print(f"\nSearch results for '{query}': {len(results)} tabs")
    for tab in results[:3]:
        print(f"  - {tab.title}")