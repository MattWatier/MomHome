---
name: export-vault-to-jekyll
description: >-
  Kickoff-only notes for exporting MomHome vault Markdown to a Jekyll site under
  `_output/`. Do not build the site until asked.
---

# Export vault → Jekyll (kickoff only)

## Status

**Do not build** `_output/` or a Jekyll UI until Matt asks. This skill documents the intended inputs only.

## Intended inputs

- `vault/locations/*/index.md` (+ optional child notes)
- Front matter: uid, name, address, website, ratings (with sources), all-in estimate, status, queue dates
- Queues in `vault/_queues/`

## Constraints

- Site reads **vault Markdown**, not CSV
- No PII beyond search anchor
- Cards show all-in; location pages show price breakdown
- Family-only; publish later when Matt is ready
