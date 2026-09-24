#!/usr/bin/env python3
"""Import MomHome location stubs from protected seed CSVs.

HARD RULE: never write to `_data/do not edit/`. Read-only.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "_data" / "do not edit"
LOCATIONS = ROOT / "vault" / "locations"

COL_UID = "UID"
COL_NAME = "Location name"
COL_ADDRESS = "Google address"
COL_RATING = "Average star rating"
COL_WEB = "Web link"
COL_PRICE = "Price range (single occupancy)"
COL_DIST = "Est. driving distance from 9500 Lagersfield Cir (mi)"
COL_SUB5K = "Sub-$5k private starting rate?"

STUB_MARKER = "_Stub from seed. Research and visits fill this in._"


def slugify(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "location"


def yaml_str(value: str) -> str:
    if value is None:
        return '""'
    text = str(value)
    if any(c in text for c in (":", "#", "{", "}", "[", "]", ",", "&", "*", "?", "|", "-", ">", "'", '"', "%", "@", "`")) or text != text.strip() or text == "" or text.lower() in {"yes", "no", "true", "false", "null"}:
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return text


def parse_rating(raw: str):
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return raw


def parse_distance(raw: str):
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        return float(raw) if "." in raw else int(raw)
    except ValueError:
        return raw


def parse_sub5k(raw: str):
    v = (raw or "").strip().lower()
    if v == "yes":
        return True
    if v == "no":
        return False
    return None


def render_stub(fields: dict) -> str:
    rating = fields["google_rating_seed"]
    rating_yaml = "null" if rating is None else rating
    dist = fields["distance_miles_seed"]
    dist_yaml = "null" if dist is None else dist
    sub = fields["sub_5k_private_start"]
    if sub is True:
        sub_yaml = "true"
    elif sub is False:
        sub_yaml = "false"
    else:
        sub_yaml = "null"

    return f"""---
uid: {yaml_str(fields['uid'])}
name: {yaml_str(fields['name'])}
slug: {yaml_str(fields['slug'])}
address: {yaml_str(fields['address'])}
website: {yaml_str(fields['website'])}
google_rating_seed: {rating_yaml}
price_range_seed: {yaml_str(fields['price_range_seed'])}
distance_miles_seed: {dist_yaml}
sub_5k_private_start: {sub_yaml}
all_in_estimate_monthly: null
status: stub
want_to_review_date: null
visit_date: null
follow_up_date: null
example: false
---

# {fields['name']}

## Overview

{STUB_MARKER}

## Pros / cons

-

## Price breakdown

_Seed price notes are in front matter (`price_range_seed`). Refine all-in after quotes/visits._

## Ratings & sentiment

_Do not invent. Pull with review skill; cite source URLs._

## Red flags

-

## Inspections

_Do not invent. Use inspection-pull skill (DSS + VDH)._

## Visits

-
"""


def is_safe_to_overwrite(path: Path) -> bool:
    if not path.exists():
        return True
    text = path.read_text(encoding="utf-8")
    if "example: true" in text:
        return False
    if "status: stub" in text and STUB_MARKER in text:
        return True
    return False


def load_seed_rows() -> tuple[list[dict], list[Path]]:
    if not SEED_DIR.is_dir():
        raise SystemExit(f"Seed directory missing: {SEED_DIR}")
    csvs = sorted(p for p in SEED_DIR.iterdir() if p.suffix.lower() == ".csv" and p.is_file())
    if not csvs:
        raise SystemExit(f"No CSV seed files in {SEED_DIR}")
    rows: list[dict] = []
    for path in csvs:
        with path.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["_seed_file"] = path.name
                rows.append(row)
    return rows, csvs


def main() -> int:
    rows, csvs = load_seed_rows()
    LOCATIONS.mkdir(parents=True, exist_ok=True)

    written = []
    skipped = []
    used_slugs: dict[str, str] = {}

    for row in rows:
        uid = (row.get(COL_UID) or "").strip()
        name = (row.get(COL_NAME) or "").strip()
        if not uid or not name:
            skipped.append({"reason": "blank uid or name", "uid": uid, "name": name, "seed": row.get("_seed_file")})
            continue

        base = slugify(name)
        slug = base
        if slug in used_slugs and used_slugs[slug] != uid:
            slug = f"{base}-{uid.lower()}"
        # also check existing folder collision with different uid
        dest_dir = LOCATIONS / slug
        index_path = dest_dir / "index.md"
        if index_path.exists() and not is_safe_to_overwrite(index_path):
            existing = index_path.read_text(encoding="utf-8")
            m = re.search(r"^uid:\s*[\"']?([^\"'\n]+)", existing, re.M)
            existing_uid = (m.group(1).strip() if m else "")
            if existing_uid and existing_uid != uid:
                slug = f"{base}-{uid.lower()}"
                dest_dir = LOCATIONS / slug
                index_path = dest_dir / "index.md"

        used_slugs[slug] = uid

        fields = {
            "uid": uid,
            "name": name,
            "slug": slug,
            "address": (row.get(COL_ADDRESS) or "").strip(),
            "website": (row.get(COL_WEB) or "").strip(),
            "google_rating_seed": parse_rating(row.get(COL_RATING) or ""),
            "price_range_seed": (row.get(COL_PRICE) or "").strip(),
            "distance_miles_seed": parse_distance(row.get(COL_DIST) or ""),
            "sub_5k_private_start": parse_sub5k(row.get(COL_SUB5K) or ""),
        }

        if index_path.exists() and not is_safe_to_overwrite(index_path):
            skipped.append({"reason": "existing non-stub content", "uid": uid, "slug": slug, "path": str(index_path.relative_to(ROOT))})
            continue

        dest_dir.mkdir(parents=True, exist_ok=True)
        index_path.write_text(render_stub(fields), encoding="utf-8")
        written.append({"uid": uid, "slug": slug, "path": str(index_path.relative_to(ROOT)), "seed": row.get("_seed_file")})

    print(f"seed_files: {[p.name for p in csvs]}")
    print(f"rows_read: {len(rows)}")
    print(f"stubs_written: {len(written)}")
    print(f"skipped: {len(skipped)}")
    for item in written[:5]:
        print(f"  sample: {item['path']} ({item['uid']})")
    for item in skipped:
        print(f"  skip: {item}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
