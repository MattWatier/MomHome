# MomHome

Family-only planning vault for evaluating assisted living options near the Vienna Metro search anchor (Virginia-first).

## Layout

- `_data/do not edit/` — protected seed CSVs (**agents: read-only**)
- `vault/` — source of truth (Markdown + front matter)
- `vault/locations/<slug>/` — one folder per facility; `index.md` is the primary note
- `.cursor/skills/` — agent workflows (seed import, inspections, reviews, tour debrief, later Jekyll export)
- No Jekyll / `_output/` site yet

## Seed → vault

```bash
python3 scripts/import_seed_locations.py
```

Reads `_data/do not edit/*.csv` and writes stubs under `vault/locations/`. Never mutates the seed.

## Obsidian

An Obsidian vault may live under `vault/MomHome/` for local editing. Location stubs are under `vault/locations/` (sibling), not inside the Obsidian folder.
