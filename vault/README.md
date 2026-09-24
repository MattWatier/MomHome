# Vault conventions

## Obsidian

**Open this folder as the vault:** `/Users/mattwatier/Repo/MomHome/vault`

That is the folder that contains `.obsidian/` plus `locations/`, `_queues/`, and `_templates/`. Do **not** open the repo root, and do **not** open a nested folder such as `MomHome/` (those were empty decoy vaults).

After opening `vault/`, you should see `locations/` with one folder per facility (`index.md` inside each).

**Filter locations:** open `Locations overview.base` (see `Locations overview README.md`).

## Conventions

1. **Folder per location:** `locations/<slug>/index.md` is primary; optional siblings `reviews.md`, `inspections.md`, `visits.md`.
2. **UID** from seed in front matter; slug = safe name; never rewrite `_data/do not edit`.
3. **Scannable fields in YAML;** long-form only in body (overview, pros/cons, price table, ratings, red flags, inspections/visits rollups).
4. **All-in monthly** on cards (`all_in_estimate_monthly` when known); breakdown in body.
5. **Every review/inspection collection needs a source URL.**
6. **Queues** in `_queues/` — want-to-review / visit / follow-up — sorted **newest date first**.
7. **Care lens:** private room, 3 meals, meds reminder/self-admin with oversight, cane + walk-in shower, Vienna Metro anchor, VA-first.
8. **No invented inspections/reviews** on seed import — stubs only.
9. **No PII** beyond the agreed search anchor (Vienna Metro parking lot). Do not copy home street addresses from seed column headers into vault notes.
10. Export later: vault → `_output/` Jekyll (skill only until ready).
