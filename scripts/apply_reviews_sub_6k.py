#!/usr/bin/env python3
"""Apply review / red-flag research into vault location stubs.

Reads scripts/data/reviews_sub_6k.json and updates:
  - vault/locations/<slug>/index.md front matter + Ratings/Red flags sections
  - vault/locations/<slug>/reviews.md (create/overwrite)

Never touches _data/do not edit.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "scripts" / "data" / "reviews_sub_6k.json"
LOCATIONS = ROOT / "vault" / "locations"

FM_KEYS = [
    "review_google_rating",
    "review_google_count",
    "review_yelp_rating",
    "review_yelp_count",
    "review_overall_sentiment",
    "review_red_flags",
    "review_pros",
    "review_source_urls",
    "review_as_of",
    "review_confidence",
    "review_material_red_flags",
]


def yaml_scalar(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        if isinstance(v, float) and v == int(v):
            return str(int(v)) if v.is_integer() is False else (str(int(v)) if float(v).is_integer() else str(v))
        # prefer 4.2 style
        if isinstance(v, float):
            return str(v)
        return str(v)
    s = str(v).replace('"', '\\"')
    return f'"{s}"'


def yaml_list(items, indent=0):
    if not items:
        return "[]"
    pad = " " * indent
    lines = []
    for it in items:
        if isinstance(it, str):
            esc = it.replace('"', '\\"')
            lines.append(f'{pad}- "{esc}"')
        else:
            lines.append(f"{pad}- {it}")
    return "\n" + "\n".join(lines)


def format_rating(v):
    if v is None:
        return "null"
    return str(v)


def upsert_front_matter(fm: str, fields: dict) -> str:
    # Remove any existing review_* keys
    lines = fm.splitlines()
    kept = []
    skip_list = False
    for line in lines:
        if skip_list:
            if re.match(r"^\s+-\s+", line) or (line.startswith(" ") and line.strip().startswith("-")):
                continue
            # end of list when a new key at column 0 or empty
            if re.match(r"^[a-zA-Z0-9_]+:", line) or line.strip() == "":
                skip_list = False
            else:
                # indented continuation?
                if line.startswith(" ") and not re.match(r"^[a-zA-Z0-9_]+:", line.lstrip()):
                    continue
                skip_list = False
        m = re.match(r"^([a-zA-Z0-9_]+):", line)
        if m and m.group(1) in FM_KEYS:
            # if value is empty and next lines are list items, skip those
            rest = line.split(":", 1)[1].strip()
            if rest in ("", "|", ">", "[]"):
                skip_list = True
            continue
        kept.append(line)

    # Insert new fields before trailing empty / end — after price_notes or status if present
    insert_at = len(kept)
    for i, line in enumerate(kept):
        if line.startswith("status:"):
            insert_at = i
            break
    else:
        # before last non-empty
        for i in range(len(kept) - 1, -1, -1):
            if kept[i].strip():
                insert_at = i + 1
                break

    block = []
    block.append(f"review_google_rating: {format_rating(fields.get('google_rating'))}")
    block.append(f"review_google_count: {format_rating(fields.get('google_count'))}")
    block.append(f"review_yelp_rating: {format_rating(fields.get('yelp_rating'))}")
    block.append(f"review_yelp_count: {format_rating(fields.get('yelp_count'))}")
    block.append(f"review_overall_sentiment: {yaml_scalar(fields['sentiment'])}")
    block.append("review_red_flags:" + yaml_list(fields.get("red_flags") or [], indent=0))
    block.append("review_pros:" + yaml_list(fields.get("pros") or [], indent=0))
    block.append("review_source_urls:" + yaml_list(fields.get("source_urls") or [], indent=0))
    block.append(f"review_as_of: {yaml_scalar(fields['as_of'])}")
    block.append(f"review_confidence: {yaml_scalar(fields['confidence'])}")
    block.append(f"review_material_red_flags: {yaml_scalar(fields['material_red_flags'])}")

    new_lines = kept[:insert_at] + block + kept[insert_at:]
    return "\n".join(new_lines)


def replace_section(body: str, heading: str, content: str) -> str:
    pattern = rf"(## {re.escape(heading)}\n)(.*?)(?=\n## |\Z)"
    repl = f"## {heading}\n\n{content.rstrip()}\n\n"
    if re.search(pattern, body, flags=re.S):
        return re.sub(pattern, repl, body, count=1, flags=re.S)
    return body.rstrip() + "\n\n" + repl


def reviews_md(name: str, uid: str, d: dict, as_of: str) -> str:
    def fmt_avg(r, c):
        if r is None:
            return "_Not found / not usable_"
        if c is None:
            return f"{r}/5"
        return f"{r}/5 ({c} reviews)"

    flags = d.get("red_flags") or []
    pros = d.get("pros") or []
    urls = d.get("source_urls") or []

    flag_txt = "\n".join(f"  - {f}" for f in flags) if flags else "  - None recurring at research time."
    pros_txt = "\n".join(f"  - {p}" for p in pros) if pros else "  - (thin)"
    src_txt = "\n".join(f"- {u}" for u in urls)
    yelp_thin = d.get("yelp_count") in (None, 0) or (
        d.get("yelp_count") is not None and d.get("yelp_count") < 5
    )

    return f"""---
uid: "{uid}"
type: reviews
name: "{name}"
review_as_of: "{as_of}"
---

# Reviews — {name}

Research date: {as_of}. Every block cites source URLs below. Do not treat directory aggregators as a substitute for reading Google/Yelp directly before a tour.

## Summary

- **Overall sentiment:** {d['sentiment']}
- **Confidence:** {d['confidence']}
- **Material red flags:** {"yes" if d['material_red_flags'] else "no"}

{d.get('notes', '')}

## Google

- Average: {fmt_avg(d.get('google_rating'), d.get('google_count'))}
- Sentiment: {d['sentiment']}
- Red flags / repeated worries:
{flag_txt}
- Recurring pros:
{pros_txt}

## Yelp

- Average: {fmt_avg(d.get('yelp_rating'), d.get('yelp_count'))}
- Notes: {"Thin or no Yelp presence — do not overweight." if yelp_thin else "See sources; weigh against Google themes."}

## Staff picture (Glassdoor / LinkedIn)

- Tenure / turnover notes: _Not systematically collected this pass; probe on tour / LinkedIn if shortlisted._
- Source: n/a

## Source URLs

{src_txt}
"""


def process_one(slug: str, d: dict, as_of: str) -> None:
    idx = LOCATIONS / slug / "index.md"
    text = idx.read_text()
    if not text.startswith("---"):
        raise SystemExit(f"No front matter: {idx}")
    parts = text.split("---", 2)
    fm, body = parts[1], parts[2]

    uid_m = re.search(r'^uid:\s*[\"\']?([^\"\']+)[\"\']?\s*$', fm, re.M)
    name_m = re.search(r'^name:\s*[\"\']?(.+?)[\"\']?\s*$', fm, re.M)
    uid = uid_m.group(1) if uid_m else ""
    name = name_m.group(1) if name_m else slug

    fields = dict(d)
    fields["as_of"] = as_of
    new_fm = upsert_front_matter(fm.strip("\n"), fields)

    g = d.get("google_rating")
    gc = d.get("google_count")
    y = d.get("yelp_rating")
    yc = d.get("yelp_count")
    g_txt = f"{g}/5" + (f" (~{gc})" if gc else "") if g is not None else "n/a"
    y_txt = f"{y}/5" + (f" ({yc})" if yc else "") if y is not None else "n/a / thin"

    ratings = (
        f"- **Google:** {g_txt}\n"
        f"- **Yelp:** {y_txt}\n"
        f"- **Overall sentiment:** {d['sentiment']} (confidence: {d['confidence']})\n"
        f"- **As of:** {as_of}\n"
        f"- Detail: see [reviews.md](reviews.md). All sources cited there.\n"
    )
    if d.get("red_flags"):
        red = "\n".join(f"- {f}" for f in d["red_flags"])
        if d["material_red_flags"]:
            red = "**Material / repeated themes:**\n" + red
    else:
        red = "- None recurring at research time (or review volume too thin to judge)."

    body = replace_section(body, "Ratings & sentiment", ratings)
    body = replace_section(body, "Red flags", red)

    idx.write_text("---\n" + new_fm.strip() + "\n---" + body)
    (LOCATIONS / slug / "reviews.md").write_text(reviews_md(name, uid, d, as_of))
    print(f"updated {slug} material={d['material_red_flags']}")


def main():
    payload = json.loads(DATA.read_text())
    as_of = payload["as_of"]
    for slug, d in payload["locations"].items():
        process_one(slug, d, as_of)
    material = sum(1 for d in payload["locations"].values() if d["material_red_flags"])
    thin = sum(1 for d in payload["locations"].values() if d["sentiment"] == "thin" or d["confidence"] in ("none", "low") and not d["material_red_flags"])
    print(f"done: {len(payload['locations'])} locations; material_red_flags={material}")


if __name__ == "__main__":
    main()
