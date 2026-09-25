#!/usr/bin/env python3
"""Reconcile protected seed CSV into vault locations by UID.

HARD RULE: never write to `_data/do not edit/`. Read-only on seed.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "_data" / "do not edit" / "vienna_assisted_living_expanded_with_uid.csv"
LOCATIONS = ROOT / "vault" / "locations"
REPORT = ROOT / "scripts" / "data" / "seed_reconcile_report.json"

STUB_MARKER = "_Stub from seed. Research and visits fill this in._"

# Seed column → vault front-matter key (seed mirrors / flood-fill targets)
SEED_MIRROR = {
    "Location name": "name",
    "Google address": "address",
    "Web link": "website",
    "Average star rating": "google_rating_seed",
    "Price range (single occupancy)": "price_range_seed",
    "Est. driving distance from 9500 Lagersfield Cir (mi)": "distance_miles_seed",
    "Sub-$5k private starting rate?": "sub_5k_private_start",
    "Contact person": "contact_person_seed",
    "Phone": "phone_seed",
    "Email": "email_seed",
    "Contact source": "contact_source_seed",
    "Web form link": "web_form_link_seed",
    "Quoted monthly price": "quoted_monthly_price_seed",
    "Medication fee": "medication_fee_seed",
    "Waitlist": "waitlist_seed",
    "Notes": "notes_seed",
    "Published info source": "published_info_source_seed",
}

# Identity / researched-sensitive: never overwrite existing vault value on conflict
IDENTITY_KEYS = {"name", "address", "website"}
# Always sync from seed when seed has data (mirrors of seed)
ALWAYS_SYNC = {
    "google_rating_seed",
    "price_range_seed",
    "distance_miles_seed",
    "sub_5k_private_start",
    "contact_person_seed",
    "phone_seed",
    "email_seed",
    "contact_source_seed",
    "web_form_link_seed",
    "quoted_monthly_price_seed",
    "medication_fee_seed",
    "waitlist_seed",
    "notes_seed",
    "published_info_source_seed",
}


def slugify(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "location"


def yaml_str(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    text = str(value)
    if any(
        c in text
        for c in (
            ":",
            "#",
            "{",
            "}",
            "[",
            "]",
            ",",
            "&",
            "*",
            "?",
            "|",
            "-",
            ">",
            "'",
            '"',
            "%",
            "@",
            "`",
            "\n",
        )
    ) or text != text.strip() or text == "" or text.lower() in {
        "yes",
        "no",
        "true",
        "false",
        "null",
    }:
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return text


def parse_rating(raw: str):
    raw = (raw or "").strip()
    if not raw or raw.upper() == "N/A":
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


def seed_value(col: str, raw: str):
    if col == "Average star rating":
        return parse_rating(raw)
    if col == "Est. driving distance from 9500 Lagersfield Cir (mi)":
        return parse_distance(raw)
    if col == "Sub-$5k private starting rate?":
        return parse_sub5k(raw)
    return (raw or "").strip() or None


def values_equal(a, b) -> bool:
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return float(a) == float(b)
    if isinstance(a, bool) or isinstance(b, bool):
        return bool(a) is bool(b) and a == b
    return str(a).strip() == str(b).strip()


def is_empty(v) -> bool:
    if v is None:
        return True
    if isinstance(v, str) and not v.strip():
        return True
    return False


FM_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.S)


def parse_front_matter(text: str) -> tuple[dict, str, str]:
    m = FM_RE.match(text)
    if not m:
        return {}, "", text
    fm_raw = m.group(1)
    body = text[m.end() :]
    data: dict = {}
    # Simple line YAML for scalar keys we care about (no nested lists needed for sync)
    for line in fm_raw.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if line.startswith(" ") or line.startswith("\t") or line.startswith("-"):
            continue
        if ":" not in line:
            continue
        key, _, rest = line.partition(":")
        key = key.strip()
        val = rest.strip()
        if val in ("", "null", "~"):
            data[key] = None
        elif val.lower() == "true":
            data[key] = True
        elif val.lower() == "false":
            data[key] = False
        elif (val.startswith('"') and val.endswith('"')) or (
            val.startswith("'") and val.endswith("'")
        ):
            data[key] = val[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        else:
            try:
                if "." in val:
                    data[key] = float(val)
                else:
                    data[key] = int(val)
            except ValueError:
                data[key] = val
    return data, fm_raw, body


def set_fm_key(fm_raw: str, key: str, value) -> str:
    """Insert or replace a scalar front-matter key, preserving other lines."""
    lines = fm_raw.splitlines()
    rendered = f"{key}: {yaml_str(value)}"
    key_re = re.compile(rf"^{re.escape(key)}:\s*")
    for i, line in enumerate(lines):
        if key_re.match(line):
            lines[i] = rendered
            return "\n".join(lines)
    # Insert after sub_5k / contact block / before status if possible
    insert_after = [
        "published_info_source_seed",
        "notes_seed",
        "waitlist_seed",
        "medication_fee_seed",
        "quoted_monthly_price_seed",
        "web_form_link_seed",
        "contact_source_seed",
        "email_seed",
        "phone_seed",
        "contact_person_seed",
        "price_notes",
        "price_confidence",
        "price_as_of",
        "price_source_url",
        "room_rate_monthly",
        "room_type",
        "all_in_estimate_monthly",
        "sub_5k_private_start",
        "distance_miles_seed",
        "price_range_seed",
        "google_rating_seed",
        "website",
        "address",
        "slug",
        "name",
        "uid",
    ]
    idxs = {ln.split(":", 1)[0].strip(): i for i, ln in enumerate(lines) if ":" in ln and not ln.startswith(" ")}
    pos = None
    for anchor in insert_after:
        if anchor in idxs:
            pos = idxs[anchor] + 1
            break
    if pos is None:
        # before status
        for i, ln in enumerate(lines):
            if ln.startswith("status:"):
                pos = i
                break
    if pos is None:
        lines.append(rendered)
    else:
        lines.insert(pos, rendered)
    return "\n".join(lines)


def append_price_note(fm_raw: str, note: str) -> str:
    data, _, _ = parse_front_matter("---\n" + fm_raw + "\n---\n")
    existing = data.get("price_notes")
    if existing and note in str(existing):
        return fm_raw
    if is_empty(existing):
        return set_fm_key(fm_raw, "price_notes", note)
    combined = f"{existing} | {note}"
    return set_fm_key(fm_raw, "price_notes", combined)


def render_stub(fields: dict) -> str:
    lines = [
        "---",
        f"uid: {yaml_str(fields['uid'])}",
        f"name: {yaml_str(fields['name'])}",
        f"slug: {yaml_str(fields['slug'])}",
        f"address: {yaml_str(fields['address'])}",
        f"website: {yaml_str(fields['website'])}",
        f"google_rating_seed: {yaml_str(fields['google_rating_seed'])}",
        f"price_range_seed: {yaml_str(fields['price_range_seed'])}",
        f"distance_miles_seed: {yaml_str(fields['distance_miles_seed'])}",
        f"sub_5k_private_start: {yaml_str(fields['sub_5k_private_start'])}",
        "all_in_estimate_monthly: null",
        "room_type: null",
        "room_rate_monthly: null",
        "price_source_url: null",
        "price_as_of: null",
        "price_confidence: null",
        "price_notes: null",
        f"contact_person_seed: {yaml_str(fields.get('contact_person_seed'))}",
        f"phone_seed: {yaml_str(fields.get('phone_seed'))}",
        f"email_seed: {yaml_str(fields.get('email_seed'))}",
        f"contact_source_seed: {yaml_str(fields.get('contact_source_seed'))}",
        f"web_form_link_seed: {yaml_str(fields.get('web_form_link_seed'))}",
        f"quoted_monthly_price_seed: {yaml_str(fields.get('quoted_monthly_price_seed'))}",
        f"medication_fee_seed: {yaml_str(fields.get('medication_fee_seed'))}",
        f"waitlist_seed: {yaml_str(fields.get('waitlist_seed'))}",
        f"notes_seed: {yaml_str(fields.get('notes_seed'))}",
        f"published_info_source_seed: {yaml_str(fields.get('published_info_source_seed'))}",
        "status: stub",
        "want_to_review_date: null",
        "visit_date: null",
        "follow_up_date: null",
        "example: false",
        "---",
        "",
        f"# {fields['name']}",
        "",
        "## Overview",
        "",
        STUB_MARKER,
        "",
        "## Pros / cons",
        "",
        "-",
        "",
        "## Price breakdown",
        "",
        "_Seed price notes are in front matter (`price_range_seed`). Refine all-in after quotes/visits._",
        "",
        "## Ratings & sentiment",
        "",
        "_Do not invent. Pull with review skill; cite source URLs._",
        "",
        "## Red flags",
        "",
        "-",
        "",
        "## Inspections",
        "",
        "_Do not invent. Use inspection-pull skill (DSS + VDH)._",
        "",
        "## Visits",
        "",
        "-",
        "",
    ]
    return "\n".join(lines)


def load_seed() -> tuple[list[dict], str]:
    digest = hashlib.sha256(SEED.read_bytes()).hexdigest()
    with SEED.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    out = []
    for row in rows:
        uid = (row.get("UID") or "").strip()
        if not uid:
            continue
        mapped = {"uid": uid}
        for col, key in SEED_MIRROR.items():
            mapped[key] = seed_value(col, row.get(col) or "")
        out.append(mapped)
    return out, digest


def load_vault() -> dict[str, dict]:
    by_uid: dict[str, dict] = {}
    for path in sorted(LOCATIONS.glob("*/index.md")):
        text = path.read_text(encoding="utf-8")
        data, fm_raw, body = parse_front_matter(text)
        if data.get("example") is True:
            continue
        uid = data.get("uid")
        if not uid:
            continue
        by_uid[str(uid).strip()] = {
            "path": path,
            "data": data,
            "fm_raw": fm_raw,
            "body": body,
            "text": text,
            "slug": path.parent.name,
        }
    return by_uid


def soft_price_conflict(seed_row: dict, vault: dict) -> str | None:
    """Flag researched all-in vs seed sub-$5k / quoted notes without clobbering."""
    all_in = vault.get("all_in_estimate_monthly")
    sub = seed_row.get("sub_5k_private_start")
    if all_in is None:
        return None
    try:
        all_in_n = float(all_in)
    except (TypeError, ValueError):
        return None
    notes = []
    if sub is False and all_in_n <= 5000:
        notes.append(
            f"seed conflict 2026-09-24: Sub-$5k private starting rate?=No while researched all_in_estimate_monthly={all_in_n:g} (kept researched)"
        )
    if sub is True and all_in_n > 5000:
        notes.append(
            f"seed conflict 2026-09-24: Sub-$5k private starting rate?=Yes while researched all_in_estimate_monthly={all_in_n:g} (kept researched)"
        )
    quoted = seed_row.get("quoted_monthly_price_seed") or ""
    # Skip daily rates ($N/day) — not comparable to monthly all-in.
    if re.search(r"/\s*day", quoted, re.I):
        quoted_for_cmp = ""
    else:
        quoted_for_cmp = quoted
    m = re.search(r"\$\s*([\d,]+)", quoted_for_cmp)
    if m and all_in is not None:
        try:
            q = float(m.group(1).replace(",", ""))
            # Ignore tiny figures that are clearly not monthly room rates
            if q >= 1000 and abs(q - all_in_n) >= 500:
                notes.append(
                    f"seed conflict 2026-09-24: quoted_monthly_price_seed starts near ${q:g} vs researched all_in={all_in_n:g} (kept researched; seed quote noted)"
                )
        except ValueError:
            pass
    return " | ".join(notes) if notes else None


def main() -> int:
    seed_rows, digest = load_seed()
    vault = load_vault()
    seed_by_uid = {r["uid"]: r for r in seed_rows}

    new_stubs = []
    flood_fills = []  # (uid, key, value)
    syncs = []  # seed mirror updates
    conflicts = []
    vault_only = sorted(set(vault) - set(seed_by_uid))
    new_uids = sorted(set(seed_by_uid) - set(vault))

    used_slugs = {v["slug"]: uid for uid, v in vault.items()}

    for uid in new_uids:
        row = seed_by_uid[uid]
        base = slugify(row["name"])
        slug = base
        if slug in used_slugs and used_slugs[slug] != uid:
            slug = f"{base}-{uid.lower()}"
        dest = LOCATIONS / slug
        index = dest / "index.md"
        if index.exists():
            conflicts.append(
                {
                    "uid": uid,
                    "type": "stub_path_exists",
                    "path": str(index.relative_to(ROOT)),
                }
            )
            continue
        fields = {
            "uid": uid,
            "name": row["name"],
            "slug": slug,
            "address": row["address"] or "",
            "website": row["website"] or "",
            "google_rating_seed": row["google_rating_seed"],
            "price_range_seed": row["price_range_seed"] or "",
            "distance_miles_seed": row["distance_miles_seed"],
            "sub_5k_private_start": row["sub_5k_private_start"],
            "contact_person_seed": row.get("contact_person_seed"),
            "phone_seed": row.get("phone_seed"),
            "email_seed": row.get("email_seed"),
            "contact_source_seed": row.get("contact_source_seed"),
            "web_form_link_seed": row.get("web_form_link_seed"),
            "quoted_monthly_price_seed": row.get("quoted_monthly_price_seed"),
            "medication_fee_seed": row.get("medication_fee_seed"),
            "waitlist_seed": row.get("waitlist_seed"),
            "notes_seed": row.get("notes_seed"),
            "published_info_source_seed": row.get("published_info_source_seed"),
        }
        dest.mkdir(parents=True, exist_ok=True)
        index.write_text(render_stub(fields), encoding="utf-8")
        used_slugs[slug] = uid
        new_stubs.append({"uid": uid, "slug": slug, "path": str(index.relative_to(ROOT))})

    # Refresh vault map after stubs
    vault = load_vault()

    for uid, row in seed_by_uid.items():
        if uid not in vault:
            continue
        entry = vault[uid]
        data = entry["data"]
        fm_raw = entry["fm_raw"]
        changed = False
        loc_floods = []
        loc_syncs = []
        loc_conflicts = []

        for key in SEED_MIRROR.values():
            seed_val = row.get(key)
            if is_empty(seed_val):
                continue
            vault_val = data.get(key)

            if key in IDENTITY_KEYS:
                if is_empty(vault_val):
                    fm_raw = set_fm_key(fm_raw, key, seed_val)
                    data[key] = seed_val
                    changed = True
                    loc_floods.append(key)
                elif not values_equal(vault_val, seed_val):
                    loc_conflicts.append(
                        {
                            "uid": uid,
                            "field": key,
                            "vault": vault_val,
                            "seed": seed_val,
                            "action": "kept_vault",
                        }
                    )
                continue

            if key in ALWAYS_SYNC:
                if is_empty(vault_val):
                    fm_raw = set_fm_key(fm_raw, key, seed_val)
                    data[key] = seed_val
                    changed = True
                    loc_floods.append(key)
                elif not values_equal(vault_val, seed_val):
                    fm_raw = set_fm_key(fm_raw, key, seed_val)
                    data[key] = seed_val
                    changed = True
                    loc_syncs.append({"field": key, "old": vault_val, "new": seed_val})
                continue

        note = soft_price_conflict(row, data)
        if note:
            before = fm_raw
            fm_raw = append_price_note(fm_raw, note)
            if fm_raw != before:
                changed = True
            loc_conflicts.append(
                {
                    "uid": uid,
                    "field": "price_research_vs_seed",
                    "detail": note,
                    "action": "kept_researched_all_in",
                }
            )

        if changed:
            new_text = f"---\n{fm_raw}\n---\n{entry['body']}"
            entry["path"].write_text(new_text, encoding="utf-8")

        for k in loc_floods:
            flood_fills.append({"uid": uid, "field": k, "value": data.get(k)})
        for s in loc_syncs:
            syncs.append({"uid": uid, **s})
        conflicts.extend(loc_conflicts)

    report = {
        "seed_file": str(SEED.relative_to(ROOT)),
        "sha256": digest,
        "seed_uids": len(seed_by_uid),
        "vault_uids": len(vault),
        "new_stubs": new_stubs,
        "flood_fills": flood_fills,
        "seed_mirror_syncs": syncs,
        "conflicts": conflicts,
        "vault_only_uids": vault_only,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8")

    print(f"seed_sha256: {digest}")
    print(f"seed_uids: {len(seed_by_uid)}")
    print(f"vault_uids: {len(vault)}")
    print(f"new_stubs: {len(new_stubs)}")
    for s in new_stubs:
        print(f"  stub: {s['uid']} -> {s['path']}")
    print(f"flood_fill_writes: {len(flood_fills)}")
    from collections import Counter

    print("  by_field:", dict(Counter(f["field"] for f in flood_fills)))
    print(f"seed_mirror_syncs: {len(syncs)}")
    print("  by_field:", dict(Counter(s["field"] for s in syncs)))
    print(f"conflicts: {len(conflicts)}")
    print(f"vault_only: {vault_only}")
    print(f"report: {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
