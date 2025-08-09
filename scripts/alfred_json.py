#!/usr/bin/env python3
"""Very small helper to emit Alfred Script Filter JSON."""

from __future__ import annotations
import json
from typing import Any, Dict, Iterable


def item(
    *,
    title: str,
    subtitle: str = "",
    arg: str | None = None,
    uid: str | None = None,
    icon_path: str | None = None,
    variables: Dict[str, str] | None = None,
    valid: bool = True,
    mods: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    d: Dict[str, Any] = {"title": title, "subtitle": subtitle, "valid": valid}
    if arg is not None:
        d["arg"] = arg
    if uid is not None:
        d["uid"] = uid
    if icon_path:
        d["icon"] = {"path": icon_path}
    if variables:
        d["variables"] = variables
    if mods:
        d["mods"] = mods
    return d


def dump(items: Iterable[Dict[str, Any]]) -> None:
    print(json.dumps({"items": list(items)}, ensure_ascii=False))
