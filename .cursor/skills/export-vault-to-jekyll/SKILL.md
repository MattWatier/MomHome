---
name: export-vault-to-jekyll
description: >-
  Export MomHome vault Markdown to the family Jekyll site under `_output/`.
  Use when refreshing the site from vault, adding pages, or serving locally.
---

# Export vault → Jekyll

## Hard rules

- Site reads **vault Markdown**, never the protected seed CSV under `_data/do not edit/`.
- No PII beyond the Vienna Metro search anchor.
- Cards show all-in; location pages show price breakdown + review snapshot.

## Refresh from vault

```bash
python3 scripts/export_vault_to_jekyll.py
```

Copies `vault/locations/*/index.md` (skipping `example: true`) into `_output/_locations/<slug>.md` with `layout: location`.

## Serve locally

```bash
cd _output
bundle install
bundle exec jekyll serve --host 127.0.0.1 --port 43127 --livereload --livereload-port 43128
```

Open http://127.0.0.1:43127

## Site map (v1)

| Path | Purpose |
|------|---------|
| `/` | Hero + filterable location cards |
| `/care-lens/` | Shared care profile / search anchor |
| `/locations/<slug>/` | Location detail from vault front matter + body |

## Do not

- Publish to GitHub Pages until Matt asks
- Invent inspections/reviews in the export layer
- Mutate `_data/do not edit/`
