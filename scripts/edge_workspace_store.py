#!/usr/bin/env python3
"""
Edge Workspace Store for Microsoft Edge.

This module provides functionality to read and manage Microsoft Edge workspaces
from the local cache files across all profiles.
"""

import json
from dataclasses import dataclass
from typing import Dict, List, Optional
import re

import edge_paths
from edge_profile_store import ProfileStore, EdgeProfile


@dataclass(frozen=True)
class EdgeWorkspace:
    """
    Represents a Microsoft Edge workspace.

    Attributes
    ----------
    id : str
        Unique identifier for the workspace.
    name : str
        Display name of the workspace.
    profile_dir : str
        Directory name of the profile (e.g., "Default", "Profile 1").
    profile_name : str
        Human-readable name of the profile.
    profile_email : str
        Email associated with the profile.
    active : bool
        Whether the workspace is currently active.
    color : int
        Color index for the workspace.
    tab_count : int
        Number of tabs in the workspace.
    last_active_time : float
        Unix timestamp of last activity.
    is_owner : bool
        Whether the current user owns the workspace.
    shared : bool
        Whether the workspace is shared with others.
    """
    
    id: str
    name: str
    profile_dir: str
    profile_name: str
    profile_email: str
    active: bool
    color: int
    tab_count: int
    last_active_time: float
    is_owner: bool
    shared: bool


class WorkspaceStore:
    """
    Manages Edge workspace data across all profiles.
    
    This class reads workspace cache files from all Edge profiles
    and provides methods to search and retrieve workspace information.
    """
    
    def __init__(self):
        """
        Initialize the WorkspaceStore.
        """
        self.profile_store = ProfileStore()
        self._workspaces_cache: Optional[List[EdgeWorkspace]] = None
    
    def _parse_tab_count(self, menu_subtitle: str) -> int:
        """
        Extract tab count from menu subtitle.
        
        Parameters
        ----------
        menu_subtitle : str
            Subtitle string like "1 tab" or "5 tabs".
        
        Returns
        -------
        int
            Number of tabs, or 0 if parsing fails.
        """
        match = re.match(r'(\d+)\s+tabs?', menu_subtitle)
        if match:
            return int(match.group(1))
        return 0
    
    def _load_workspaces_from_profile(self, profile: EdgeProfile) -> List[EdgeWorkspace]:
        """
        Load workspaces from a specific profile.
        
        Parameters
        ----------
        profile : EdgeProfile
            Profile object from ProfileStore.
        
        Returns
        -------
        list of EdgeWorkspace
            List of workspaces found in the profile.
        """
        workspaces = []
        workspace_cache_path = edge_paths.user_data_dir() / profile.dir_name / "Workspaces" / "WorkspacesCache"
        
        if not workspace_cache_path.exists():
            return workspaces
        
        try:
            with open(workspace_cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            workspace_list = data.get('workspaces', [])
            
            for ws in workspace_list:
                workspace = EdgeWorkspace(
                    id=ws.get('id', ''),
                    name=ws.get('name', 'Unnamed'),
                    profile_dir=profile.dir_name,
                    profile_name=profile.display_name,
                    profile_email=profile.email or '',
                    active=ws.get('active', False),
                    color=ws.get('color', 0),
                    tab_count=self._parse_tab_count(ws.get('menuSubtitle', '')),
                    last_active_time=ws.get('last_active_time', 0),
                    is_owner=ws.get('isOwner', True),
                    shared=ws.get('shared', False)
                )
                workspaces.append(workspace)
        
        except (json.JSONDecodeError, IOError):
            # Silently skip profiles with invalid workspace data
            pass
        
        return workspaces
    
    def load_all_workspaces(self) -> List[EdgeWorkspace]:
        """
        Load all workspaces from all Edge profiles.
        
        Returns
        -------
        list of EdgeWorkspace
            All workspaces sorted by last active time (most recent first).
        """
        if self._workspaces_cache is not None:
            return self._workspaces_cache
        
        all_workspaces = []
        profiles = self.profile_store.load()
        
        for profile in profiles:
            workspaces = self._load_workspaces_from_profile(profile)
            all_workspaces.extend(workspaces)
        
        # Sort by last active time, most recent first
        all_workspaces.sort(key=lambda w: w.last_active_time, reverse=True)
        
        self._workspaces_cache = all_workspaces
        return all_workspaces
    
    def search(self, query: str = "") -> List[EdgeWorkspace]:
        """
        Search for workspaces matching the query.
        
        Parameters
        ----------
        query : str
            Search query to match against workspace names, profile names, etc.
        
        Returns
        -------
        list of EdgeWorkspace
            Matching workspaces sorted by relevance and last active time.
        """
        workspaces = self.load_all_workspaces()
        
        if not query:
            return workspaces
        
        query_lower = query.lower()
        scored_results = []
        
        for workspace in workspaces:
            score = 0
            
            # Exact match on workspace name
            if query_lower == workspace.name.lower():
                score += 100
            # Workspace name starts with query
            elif workspace.name.lower().startswith(query_lower):
                score += 50
            # Query in workspace name
            elif query_lower in workspace.name.lower():
                score += 30
            
            # Profile name matching
            if query_lower in workspace.profile_name.lower():
                score += 20
            
            # Profile email matching
            if query_lower in workspace.profile_email.lower():
                score += 10
            
            # Active workspace bonus
            if workspace.active:
                score += 5
            
            if score > 0:
                scored_results.append((score, workspace))
        
        # Sort by score (descending), then by last active time
        scored_results.sort(key=lambda x: (x[0], x[1].last_active_time), reverse=True)
        
        return [workspace for _, workspace in scored_results]
    
    def get_workspace_by_id(self, workspace_id: str) -> Optional[EdgeWorkspace]:
        """
        Get a specific workspace by its ID.
        
        Parameters
        ----------
        workspace_id : str
            Unique identifier of the workspace.
        
        Returns
        -------
        EdgeWorkspace or None
            The workspace if found, None otherwise.
        """
        workspaces = self.load_all_workspaces()
        for workspace in workspaces:
            if workspace.id == workspace_id:
                return workspace
        return None