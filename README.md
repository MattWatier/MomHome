# MomHome

Family-only planning vault for evaluating assisted living options near the Vienna Metro search anchor (Virginia-first).

## Layout

- `_data/do not edit/` — protected seed CSVs (**agents: read-only**)
- `vault/` — source of truth (Markdown + front matter) **and** the Obsidian vault root
- `vault/locations/<slug>/` — one folder per facility; `index.md` is the primary note
- `_output/` — family Jekyll site (read-only export of vault Markdown)
- `.cursor/skills/` — agent workflows (seed import, inspections, reviews, tour debrief, Jekyll export)

## Obsidian

Open **`/Users/mattwatier/Repo/MomHome/vault`** in Obsidian (Open folder as vault).

That folder already contains `.obsidian/` and the location stubs under `locations/`. Do not open the repo root or a nested subfolder.

## Family site (Jekyll)

```bash
python3 scripts/export_vault_to_jekyll.py
cd _output && bundle install
bundle exec jekyll serve --host 127.0.0.1 --port 43127 --livereload --livereload-port 43128
```

Then open http://127.0.0.1:43127

## Seed → vault

```bash
python3 scripts/import_seed_locations.py
```

Reads `_data/do not edit/*.csv` and writes stubs under `vault/locations/`. Never mutates the seed.
