#!/usr/bin/env python3
"""Export vault location Markdown into the Jekyll site under `_output/`.

Reads vault Markdown only (never the protected seed CSV).
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VAULT_LOCATIONS = ROOT / "vault" / "locations"
OUT_LOCATIONS = ROOT / "_output" / "_locations"

FM_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n(.*)$", re.S)


def parse_fm(text: str) -> tuple[dict[str, str], str, str]:
    m = FM_RE.match(text)
    if not m:
        return {}, "", text
    fm_raw, body = m.group(1), m.group(2)
    data: dict[str, str] = {}
    for line in fm_raw.splitlines():
        if not line.strip() or line.startswith(" ") or line.startswith("-") or line.startswith("\t"):
            continue
        if ":" not in line:
            continue
        key, _, rest = line.partition(":")
        data[key.strip()] = rest.strip()
    return data, fm_raw, body


def is_example(data: dict[str, str]) -> bool:
    return data.get("example", "").lower() in {"true", '"true"', "'true'"}


def ensure_layout(fm_raw: str) -> str:
    lines = fm_raw.splitlines()
    out: list[str] = []
    saw_layout = False
    for line in lines:
        if line.startswith("layout:"):
            out.append("layout: location")
            saw_layout = True
        else:
            out.append(line)
    if not saw_layout:
        out.insert(0, "layout: location")
    return "\n".join(out)


def main() -> int:
    if not VAULT_LOCATIONS.is_dir():
        raise SystemExit(f"Missing vault locations: {VAULT_LOCATIONS}")

    if OUT_LOCATIONS.exists():
        shutil.rmtree(OUT_LOCATIONS)
    OUT_LOCATIONS.mkdir(parents=True)

    written = 0
    skipped = 0
    for index in sorted(VAULT_LOCATIONS.glob("*/index.md")):
        text = index.read_text(encoding="utf-8")
        data, fm_raw, body = parse_fm(text)
        if not data or is_example(data):
            skipped += 1
            continue
        slug = (data.get("slug") or "").strip().strip("\"'") or index.parent.name
        slug = slug.strip("\"'")
        fm = ensure_layout(fm_raw)
        out = f"---\n{fm}\n---\n{body}"
        (OUT_LOCATIONS / f"{slug}.md").write_text(out, encoding="utf-8")
        written += 1

    print(f"exported: {written}")
    print(f"skipped: {skipped}")
    print(f"dest: {OUT_LOCATIONS.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
