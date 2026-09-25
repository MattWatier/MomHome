---
name: review-red-flag-scan
description: >-
  Collect Google/Yelp/Glassdoor/LinkedIn signals for a MomHome location with
  ratings, red flags, sentiment, and required source URLs. Use before tours
  or when refreshing family-experience notes.
---

# Review / red-flag scan

## When

After a location stub exists under `vault/locations/<slug>/`. Run before or alongside tour scheduling. Do **not** invent ratings or invent review quotes.

## Hard rules

- Never mutate `_data/do not edit` (or any protected seed).
- **Every** review collection must cite source URL(s).
- Prefer repeated themes over one-off rants; escalate one-offs only if severe (abuse, neglect, safety).
- Be honest when volume is thin or sources conflict.
- Leave `## RAW OCR`-style protected content alone (N/A here); do not rewrite seed price text.

## Sources

1. **Google Reviews** — average rating, review count, recurring themes  
2. **Yelp** — same; note when volume is tiny (<5)  
3. **Glassdoor / LinkedIn** (optional) — public staff tenure / turnover signal only; no login scraping  

Also acceptable as secondary corroboration (cite clearly): Caring.com, SeniorAdvisor / A Place for Mom, Seniorly, Mirador, U.S. News — never invent their numbers.

## Front matter (on `index.md`)

Add or update:

| Key | Type | Notes |
|-----|------|--------|
| `review_google_rating` | number or null | e.g. `4.2` |
| `review_yelp_rating` | number or null | |
| `review_overall_sentiment` | string | `positive` / `mixed` / `negative` / `thin` |
| `review_red_flags` | list or short string | Repeated worries only |
| `review_source_urls` | list | All URLs used |
| `review_as_of` | `YYYY-MM-DD` | Research date |
| `review_confidence` | `high` / `medium` / `low` / `none` | Volume + agreement |

Optional: `review_google_count`, `review_yelp_count`, `review_pros` (short recurring pros).

## Body / child note

Prefer sibling `reviews.md` from `vault/_templates/reviews.md`. Also fill `## Ratings & sentiment` and `## Red flags` on `index.md` with a short summary that points to `reviews.md`.

### Red-flag themes to watch

Staffing shortages, neglect / missed care, billing surprise / fee opacity, food quality, cleanliness / pests, management turnover, safety / wandering / med errors.

### Confidence guide

- **high** — Google and/or Yelp with solid volume (≥20) and consistent themes  
- **medium** — moderate volume or one strong platform + thin other  
- **low** — <10 reviews total, directories only, or conflicting signals  
- **none** — no usable public reviews found  

## Output checklist

1. Update front matter on `index.md`  
2. Write/update `reviews.md` with sourced Google + Yelp (+ optional staff) blocks  
3. Shorten `## Ratings & sentiment` / `## Red flags` on index to match  
4. If batching (e.g. budget band), also write an internal summary under the project store  
