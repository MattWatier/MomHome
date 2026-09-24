---
name: review-red-flag-scan
description: >-
  Collect Google/Yelp/Glassdoor/LinkedIn signals for a MomHome location with
  ratings, red flags, sentiment, and required source URLs.
---

# Review / red-flag scan

## When

After stub exists; before or alongside tour scheduling.

## Sources

- Google + Yelp (family experience): average rating, repeated worries, overall sentiment
- Glassdoor + LinkedIn (public): tenure / turnover sense — no account required for public pages

## Output

Use `vault/_templates/reviews.md` or headed sections on `index.md`. **Every collection must include the source link.** Do not invent ratings.
