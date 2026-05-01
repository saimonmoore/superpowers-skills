#!/usr/bin/env python3
"""Find Tolaria notes whose `URL` frontmatter matches a given URL.

Usage:
    find_duplicate_url.py <vault-dir> <url>

Output:
    Prints one matching filename (relative to vault) per line. Empty output
    means no duplicate. Exits 0 on success (with or without matches),
    non-zero only on bad arguments.

Matching is on a normalized form of the URL:
- lowercased scheme and host
- default ports stripped
- common tracking query params dropped (utm_*, gclid, fbclid, mc_cid,
  mc_eid, igshid, ref, ref_src, _hsenc, _hsmi)
- fragment dropped
- trailing slash stripped from non-root paths

Frontmatter URL values are extracted with a tolerant parser that handles:
- quoted scalars (single or double)
- markdown-link form like `URL: "[https://x.com/y](https://x.com/y)"`
- bare values
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

TRACKING_PREFIXES = ("utm_",)
TRACKING_EXACT = {
    "gclid", "fbclid", "mc_cid", "mc_eid", "igshid",
    "ref", "ref_src", "_hsenc", "_hsmi",
}
DEFAULT_PORTS = {"http": 80, "https": 443}


def normalize(url: str) -> str:
    url = url.strip()
    if not url:
        return ""
    parts = urlsplit(url)
    scheme = parts.scheme.lower()
    host = parts.hostname or ""
    host = host.lower()

    netloc = host
    if parts.port and parts.port != DEFAULT_PORTS.get(scheme):
        netloc = f"{host}:{parts.port}"
    if parts.username:
        userinfo = parts.username + (f":{parts.password}" if parts.password else "")
        netloc = f"{userinfo}@{netloc}"

    path = parts.path or ""
    if len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/")

    kept = [
        (k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if k not in TRACKING_EXACT and not any(k.startswith(p) for p in TRACKING_PREFIXES)
    ]
    query = urlencode(kept)

    return urlunsplit((scheme, netloc, path, query, ""))


_FM_FENCE = re.compile(r"^---\s*$")
_URL_LINE = re.compile(r"^URL\s*:\s*(.*)$", re.IGNORECASE)
_MD_LINK = re.compile(r"^\[(?P<text>[^\]]+)\]\((?P<href>[^)]+)\)$")


def extract_urls(md_path: Path) -> list[str]:
    """Return all URL candidates from a note's frontmatter URL field.

    For a markdown-link value `[text](href)` both `text` and `href` are
    returned, so duplicate detection catches notes where the user typed
    different schemes/hosts in the two halves.
    """
    try:
        with md_path.open("r", encoding="utf-8") as fh:
            first = fh.readline()
            if not _FM_FENCE.match(first):
                return []
            for line in fh:
                if _FM_FENCE.match(line):
                    return []
                m = _URL_LINE.match(line)
                if not m:
                    continue
                raw = m.group(1).strip()
                if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ('"', "'"):
                    raw = raw[1:-1].strip()
                ml = _MD_LINK.match(raw)
                if ml:
                    return [ml.group("text").strip(), ml.group("href").strip()]
                return [raw]
    except OSError:
        return []
    return []


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: find_duplicate_url.py <vault-dir> <url>", file=sys.stderr)
        return 2
    vault = Path(argv[1])
    if not vault.is_dir():
        print(f"not a directory: {vault}", file=sys.stderr)
        return 2
    target = normalize(argv[2])
    if not target:
        print("empty url after normalization", file=sys.stderr)
        return 2

    matches: list[str] = []
    for md in sorted(vault.glob("*.md")):
        for existing in extract_urls(md):
            if existing and normalize(existing) == target:
                matches.append(md.name)
                break

    for name in matches:
        print(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
