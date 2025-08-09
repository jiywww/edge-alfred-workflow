#!/usr/bin/env python3
from __future__ import annotations
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
from edge_paths import local_state_path, profile_dir_path

AVATAR_ID_RE = re.compile(r"IDR_PROFILE_AVATAR_(\d+)")


@dataclass(frozen=True)
class EdgeProfile:
    dir_name: str
    display_name: str
    email: Optional[str] = None
    is_omitted_from_ui: Optional[bool] = None
    avatar_icon: Optional[str] = None
    gaia_picture_file_name: Optional[str] = None

    def avatar_id(self) -> Optional[str]:
        if self.avatar_icon:
            m = AVATAR_ID_RE.search(self.avatar_icon)
            if m:
                return m.group(1)
        return None

    def profile_path(self) -> Path:
        return profile_dir_path(self.dir_name)


class ProfileStore:
    def __init__(self, local_state: Path | None = None) -> None:
        self._local_state = local_state or local_state_path()
        self._profiles: List[EdgeProfile] = []

    def load(self) -> List[EdgeProfile]:
        p = self._local_state
        if not p.exists():
            return []
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return []
        info_cache: Dict[str, Dict] = (
            data.get("profile", {}).get("info_cache", {}) or {}
        )
        results: List[EdgeProfile] = []
        for dir_name, meta in info_cache.items():
            name = (
                meta.get("name")
                or meta.get("gaia_given_name")
                or meta.get("gaia_name")
                or dir_name
            )
            email = meta.get("user_name") or meta.get("gaia_email")
            is_omitted = meta.get("is_omitted_from_ui")
            avatar_icon = meta.get("avatar_icon") or meta.get("profile_avatar")
            gaia_picture_file_name = meta.get("gaia_picture_file_name")
            results.append(
                EdgeProfile(
                    dir_name=dir_name,
                    display_name=str(name),
                    email=str(email) if email else None,
                    is_omitted_from_ui=bool(is_omitted)
                    if is_omitted is not None
                    else None,
                    avatar_icon=str(avatar_icon) if avatar_icon else None,
                    gaia_picture_file_name=str(gaia_picture_file_name)
                    if gaia_picture_file_name
                    else None,
                )
            )
        results = [r for r in results if not r.is_omitted_from_ui]
        results.sort(key=lambda r: (r.dir_name != "Default", r.display_name.lower()))
        self._profiles = results
        return results

    def all(self) -> List[EdgeProfile]:
        return list(self._profiles)

    def search(self, q: str) -> List[EdgeProfile]:
        if not q:
            return self.all()
        ql = q.lower()
        out: List[EdgeProfile] = []
        for prof in self._profiles:
            joined = " ".join(
                filter(None, [prof.display_name, prof.dir_name, prof.email or ""])
            ).lower()
            if all(tok in joined for tok in ql.split()):
                out.append(prof)
        return out
