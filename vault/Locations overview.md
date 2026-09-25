# Locations overview (Dataview fallback)

Same filters as `Locations overview.base`. Use this if the Base view is blank after a reload.

Requires the **Dataview** community plugin (already listed under `.obsidian/community-plugins.json`).

## All locations

```dataview
TABLE WITHOUT ID
  file.link AS Location,
  name AS Name,
  uid AS UID,
  all_in_estimate_monthly AS "All-in $/mo",
  room_type AS "Room type",
  distance_miles_seed AS Miles,
  google_rating_seed AS "Google ★",
  review_material_red_flags AS "Material red flags",
  status AS Status
FROM "locations"
WHERE file.name = "index" AND example != true
SORT all_in_estimate_monthly ASC
```

## Under $5k

```dataview
TABLE WITHOUT ID
  file.link AS Location,
  name AS Name,
  all_in_estimate_monthly AS "All-in $/mo",
  room_type AS "Room type",
  distance_miles_seed AS Miles,
  review_material_red_flags AS "Material red flags",
  uid AS UID
FROM "locations"
WHERE file.name = "index" AND example != true
  AND all_in_estimate_monthly != null
  AND all_in_estimate_monthly <= 5000
SORT all_in_estimate_monthly ASC
```

## Under $6k

```dataview
TABLE WITHOUT ID
  file.link AS Location,
  name AS Name,
  all_in_estimate_monthly AS "All-in $/mo",
  room_type AS "Room type",
  distance_miles_seed AS Miles,
  review_material_red_flags AS "Material red flags",
  uid AS UID
FROM "locations"
WHERE file.name = "index" AND example != true
  AND all_in_estimate_monthly != null
  AND all_in_estimate_monthly <= 6000
SORT all_in_estimate_monthly ASC
```

## Unknown price

```dataview
TABLE WITHOUT ID
  file.link AS Location,
  name AS Name,
  uid AS UID,
  price_range_seed AS "Price range seed",
  price_confidence AS "Price confidence",
  status AS Status,
  distance_miles_seed AS Miles
FROM "locations"
WHERE file.name = "index" AND example != true
  AND (all_in_estimate_monthly = null OR price_confidence = "none")
SORT name ASC
```

## By room type

```dataview
TABLE WITHOUT ID
  file.link AS Location,
  name AS Name,
  all_in_estimate_monthly AS "All-in $/mo",
  distance_miles_seed AS Miles,
  uid AS UID
FROM "locations"
WHERE file.name = "index" AND example != true
GROUP BY room_type
SORT all_in_estimate_monthly ASC
```

## Material red flags

```dataview
TABLE WITHOUT ID
  file.link AS Location,
  name AS Name,
  all_in_estimate_monthly AS "All-in $/mo",
  room_type AS "Room type",
  review_overall_sentiment AS Sentiment,
  review_google_rating AS "Review Google ★",
  distance_miles_seed AS Miles,
  uid AS UID
FROM "locations"
WHERE file.name = "index" AND example != true
  AND review_material_red_flags = true
SORT all_in_estimate_monthly ASC
```
