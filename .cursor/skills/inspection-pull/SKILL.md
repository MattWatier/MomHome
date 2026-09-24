---
name: inspection-pull
description: >-
  Pull VA DSS assisted-living and VDH kitchen inspection notes into a location
  vault note with source URLs. Use after a location stub exists.
---

# Inspection pull

## When

Location stub exists under `vault/locations/<slug>/`. Do not invent findings.

## Sources

1. VA DSS ALF search: https://www.dss.virginia.gov/facility/search/alf.cgi  
   Focus post-COVID; health-related / repeated unresolved violations matter more than paperwork nits.
2. VA Dept of Health kitchen inspections by district: https://inspections.myhealthdepartment.com/virginia/districts

## Output

Prefer sibling `inspections.md` from `vault/_templates/inspections.md`, or a clearly headed section on `index.md` for short notes. Every block needs the **source URL**.
