---
name: new-location-from-seed
description: >-
  Create vault location stubs from MomHome seed CSV rows (UID + mapped fields).
  Use when importing or refreshing locations from `_data/do not edit`. Never
  mutates the protected seed.
---

# New location from seed

## Hard rules

- **Read-only** on `_data/do not edit/` (and any file inside it). Never mutate, overwrite, rename, or delete seed files.
- Write only under `vault/locations/<slug>/`.
- **Stubs only** — do not invent inspections, reviews, visit notes, or all-in prices beyond what the seed row states.
- One primary file: `vault/locations/<slug>/index.md`. Do not create empty `reviews.md` / `inspections.md` / `visits.md` unless asked.
- Skip rows with blank `UID` or blank `Location name`.
- Do not overwrite an existing stub that already has research body content unless the user asks to refresh seed fields only.

## Seed file (current)

Path: `_data/do not edit/vienna_assisted_living_expanded_with_uid.csv`

### Column map

| Seed column | Vault front matter |
|-------------|--------------------|
| `UID` | `uid` |
| `Location name` | `name` |
| (derived from name) | `slug` |
| `Google address` | `address` |
| `Web link` | `website` |
| `Average star rating` | `google_rating_seed` |
| `Price range (single occupancy)` | `price_range_seed` |
| `Est. driving distance from 9500 Lagersfield Cir (mi)` | `distance_miles_seed` |
| `Sub-$5k private starting rate?` | `sub_5k_private_start` (`true`/`false` from Yes/No) |

Do **not** copy the home street address from the distance column header into vault notes. Search anchor remains Vienna Metro (see project context).

Always set: `status: stub`, `example: false`. Leave research fields null/empty (`all_in_estimate_monthly`, queue dates).

## Slug

Lowercase the location name; replace non-alphanumeric runs with `-`; trim hyphens. If two rows collide on slug, append `-<uid-lower>` (e.g. `bright-hands-assisted-living-al-0018`).

## Stub body

Use `vault/_templates/location.md` structure. Keep section headings; leave placeholders. Put seed-derived values in front matter, not invented narrative.

## Batch import

Preferred: run the repo script (read-only on seed):

```bash
python3 scripts/import_seed_locations.py
```

Idempotent for stubs: refreshes mapped front-matter fields when `status: stub` and body is still the seed placeholder pattern; never deletes folders.

## After import

Report: rows read, stubs written, skipped (reason), sample paths. Update agent-store `internal/seed-import.md` when running as a Project agent.
