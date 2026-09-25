# MomHome family site (`_output/`)

Read-only Jekyll export of the Obsidian vault for family review.

## Run locally

From the repo root:

```bash
python3 scripts/export_vault_to_jekyll.py
cd _output
bundle install
bundle exec jekyll serve --host 127.0.0.1 --port 43127 --livereload
```

Open [http://127.0.0.1:43127](http://127.0.0.1:43127).

## Rules

- Source of truth is `vault/locations/*/index.md` (not the protected seed CSV).
- Re-run the export script after vault edits.
- No PII beyond the Vienna Metro search anchor.
