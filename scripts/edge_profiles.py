#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path

from alfred_json import dump, item
from edge_profile_store import ProfileStore

THIS_DIR = Path(__file__).resolve().parent

DEFAULT_ICON = THIS_DIR.parent / "icon.png"

def build_items(q: str):
    """
    Build Alfred items for profile search.
    
    Parameters
    ----------
    q : str
        Search query string.
    
    Yields
    ------
    dict
        Alfred item dictionary for each matching profile.
    """
    store = ProfileStore()
    store.load()
    for p in store.search(q):
        subtitle_bits = [f"dir: {p.dir_name}"]
        if p.email:
            subtitle_bits.append(p.email)
        yield item(
            title=p.display_name,
            subtitle="  •  ".join(subtitle_bits),
            arg=p.dir_name,
            uid=f"edge-profile-{p.dir_name}",
            icon_path=str(DEFAULT_ICON) if DEFAULT_ICON.exists() else None,
            mods={
                "alt": {
                    "arg": p.dir_name,
                    "subtitle": f"Copy profile directory: {p.dir_name}",
                }
            },
        )


def main(argv: list[str]) -> int:
    q = " ".join(argv[1:]).strip()
    dump(build_items(q))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
