# Locations overview

Open **`Locations overview.base`** in this vault (`vault/` — the folder that contains `.obsidian/`).

Bases is enabled as a core plugin. Switch views on the toolbar:

- **All locations** — every real `locations/<slug>/index.md` (excludes `example: true`)
- **Under $5k** / **Under $6k** — by `all_in_estimate_monthly`
- **Unknown price** — null estimate or `price_confidence: none`
- **By room type** / **One-bedrooms** / **Studios**
- **Material red flags** — `review_material_red_flags: true`
- **By distance** — `distance_miles_seed`
- **Waitlist notes** — non-empty `waitlist_seed` from Matt’s outreach columns

## If the Base looks empty

1. Confirm the vault root is `/Users/mattwatier/Repo/MomHome/vault` (not the repo root, not `momshome/`).
2. Reload Obsidian (`Reload app without saving`) so it picks up the rewritten `.base`.
3. Use the Dataview fallback note: **`Locations overview.md`** (Dataview community plugin is enabled in this vault).
