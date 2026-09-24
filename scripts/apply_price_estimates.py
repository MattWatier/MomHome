#!/usr/bin/env python3
"""Apply researched price estimates to vault location stubs. Does not touch _data/do not edit."""
from __future__ import annotations

import re
from pathlib import Path

AS_OF = "2026-09-24"
ROOT = Path(__file__).resolve().parents[1]
LOCS = ROOT / "vault" / "locations"

# Research keyed by slug. Selection rules already applied in these values:
# prefer 1BR <= ~5k; else cheaper qualifying studio/1BR under 5k when possible.
# room_rate = base when separable; all_in = best all-in guess (may equal base when care bundled
# or when care fees unknown — noted in price_notes).
PRICES: dict[str, dict] = {
    "arbor-terrace-sudley-manor": {
        "room_type": "unknown",
        "all_in_estimate_monthly": 4260,
        "room_rate_monthly": 4260,
        "price_source_url": "https://www.arborcompany.com/locations/virginia/manassas-sudley-manor",
        "price_confidence": "medium",
        "price_notes": "Official AL apartments start $4,260. Seniorly lists private from $3,695 and 1BR from $3,995 (secondary). Meals/meds typically via care tier; confirm all-in.",
        "body_extra": (
            "Official site lists assisted living apartments starting at **$4,260**/mo "
            "([Arbor Terrace Sudley Manor](https://www.arborcompany.com/locations/virginia/manassas-sudley-manor)). "
            "Secondary: Seniorly private from $3,695 / 1BR from $3,995 "
            "([Seniorly](https://www.seniorly.com/assisted-living/virginia/manassas/arbor-terrace-sudley-manor)). "
            "Room type not broken out on the official starting figure — confirm studio vs 1BR on tour."
        ),
    },
    "bedford-court": {
        "room_type": "studio",
        "all_in_estimate_monthly": 7418,
        "room_rate_monthly": 3500,
        "price_source_url": "https://www.sunriseseniorliving.com/communities/md/bedford-court",
        "price_confidence": "low",
        "price_notes": "Official CCRC rooms start $3,500 (likely IL). Seed/third-party AL studio ~$7,418+; care fees may add. Prefer AL studio estimate for screening.",
        "body_extra": (
            "Official Bedford Court page: room rates start at **$3,500**/mo "
            "([Bedford Court](https://www.sunriseseniorliving.com/communities/md/bedford-court)) — "
            "likely includes independent living. Seed/third-party AL studio figure ~**$7,418+**/mo used for assisted-living screening; "
            "confirm current AL studio/1BR quote and care fees."
        ),
    },
    "braddock-glen": {
        "room_type": "one_bedroom",
        "all_in_estimate_monthly": 3500,
        "room_rate_monthly": 3500,
        "price_source_url": "https://www.sunriseseniorliving.com/communities/va/braddock-glen",
        "price_confidence": "high",
        "price_notes": "Official: studio $3,300+; 1BR $3,500+. Selected 1BR (under $5k). Meals/housekeeping in room rate; care level + med management priced separately. Income limits may apply (FCRHA).",
        "body_extra": (
            "Sunrise official floor plans (2026): assisted living **studio $3,300+**, **1BR $3,500+** "
            "([Braddock Glen](https://www.sunriseseniorliving.com/communities/va/braddock-glen)). "
            "Selected **1BR** under ~$5k. Room rate includes fresh cuisine, programs, housekeeping; "
            "care level and medication management are additional. Also listed via FCRHA "
            "([FCRHA property page](https://www.fcrha.org/properties/braddock-glen-assisted-living/1))."
        ),
    },
    "bright-hands-assisted-living": {
        "room_type": "unknown",
        "all_in_estimate_monthly": 5000,
        "room_rate_monthly": 5000,
        "price_source_url": "https://brighthandsmd.com/",
        "price_confidence": "medium",
        "price_notes": "From $5,000/mo all-inclusive private room per seed/operator site messaging: 3 meals, med admin, 24/7 care, housekeeping. Studio vs 1BR not published.",
        "body_extra": (
            "Operator/seed messaging: private room from **$5,000**/mo all-inclusive "
            "(3 meals/day, medication administration, 24/7 care, housekeeping) "
            "([Bright Hands](https://brighthandsmd.com/)). Confirm current private-room type and rate."
        ),
    },
    "bright-hands-assisted-living-ii": {
        "room_type": "unknown",
        "all_in_estimate_monthly": 5000,
        "room_rate_monthly": 5000,
        "price_source_url": "https://brighthandsmd.com/",
        "price_confidence": "medium",
        "price_notes": "Same operator rate sheet as Bright Hands I: from $5,000/mo all-inclusive private. Confirm II-specific quote.",
        "body_extra": (
            "Same operator site as Bright Hands I: private room from **$5,000**/mo all-inclusive "
            "([Bright Hands](https://brighthandsmd.com/)). Confirm whether II matches I pricing."
        ),
    },
    "brightview-dulles-corner": {
        "room_type": "unknown",
        "all_in_estimate_monthly": 7395,
        "room_rate_monthly": 7395,
        "price_source_url": "https://www.brightviewseniorliving.com/find-a-community/brightview-dulles-corner/pricing",
        "price_confidence": "medium",
        "price_notes": "Private AL ~$7,395+/mo; includes 5 hrs personal care/week, 3 meals/day, med help. Room type not broken out in seed figure.",
        "body_extra": (
            "Brightview pricing page / seed: private assisted living ~**$7,395+**/mo including 5 hrs personal care/week, "
            "3 meals/day, and help taking medications "
            "([Brightview Dulles Corner pricing](https://www.brightviewseniorliving.com/find-a-community/brightview-dulles-corner/pricing)). "
            "Confirm studio vs 1BR on quote."
        ),
    },
    "brightview-fair-oaks": {
        "room_type": "studio",
        "all_in_estimate_monthly": 5800,
        "room_rate_monthly": 5800,
        "price_source_url": "https://www.seniorly.com/assisted-living/virginia/fairfax/brightview-fair-oaks-fairfax",
        "price_confidence": "medium",
        "price_notes": "No $ on Brightview pricing page. Seniorly: studio ~$5,800; 1BR ~$6,700. Mirador 1BR $7,335+. Selected cheaper studio. Includes ~5 hrs care/week + meals + med help per Brightview AL model.",
        "body_extra": (
            "Official Brightview Fair Oaks pricing page describes AL inclusions (5 hrs care/week, 3 meals, med help) but no dollar amounts "
            "([Brightview pricing](https://www.brightviewseniorliving.com/find-a-community/brightview-fair-oaks/pricing)). "
            "Third-party: Seniorly studio **$5,800** / 1BR **$6,700** "
            "([Seniorly](https://www.seniorly.com/assisted-living/virginia/fairfax/brightview-fair-oaks-fairfax)); "
            "Mirador lists 1BR **$7,335+** "
            "([Mirador](https://www.miradorliving.com/assisted-living/virginia/fairfax/brightview-fair-oaks-fairfax)). "
            "Selected **studio** (cheaper qualifying option; both over ~$5k)."
        ),
    },
    "brightview-west-end": {
        "room_type": "unknown",
        "all_in_estimate_monthly": 5200,
        "room_rate_monthly": 5200,
        "price_source_url": "https://www.brightviewseniorliving.com/find-a-community/brightview-west-end",
        "price_confidence": "low",
        "price_notes": "Suite ~$5,200+/mo from seed/listings; med management and meals listed. Confirm AL private studio/1BR.",
        "body_extra": (
            "Seed/listing estimate: suite ~**$5,200+**/mo with medication management and meals mentioned "
            "([Brightview West End](https://www.brightviewseniorliving.com/find-a-community/brightview-west-end)). "
            "Confirm current assisted-living private-room quote."
        ),
    },
    "brookdale-lake-ridge": {
        "room_type": "unknown",
        "all_in_estimate_monthly": 5445,
        "room_rate_monthly": 5445,
        "price_source_url": "https://www.brookdale.com/en/communities/brookdale-lake-ridge.html",
        "price_confidence": "medium",
        "price_notes": "Private AL apartment $5,445+/mo base; dining included; med management offered; personalized care fees extra — true all-in higher.",
        "body_extra": (
            "Listed private assisted-living apartment **$5,445+**/mo base; dining included; managing medications offered; care fees extra "
            "([Brookdale Lake Ridge](https://www.brookdale.com/en/communities/brookdale-lake-ridge.html)). "
            "Confirm studio vs 1BR and care-level total."
        ),
    },
    "brookdale-potomac": {
        "room_type": "unknown",
        "all_in_estimate_monthly": 5740,
        "room_rate_monthly": 5740,
        "price_source_url": "https://www.brookdale.com/en/communities/brookdale-potomac.html",
        "price_confidence": "medium",
        "price_notes": "Private AL apartment $5,740+/mo base; dining included; care fees extra.",
        "body_extra": (
            "Listed private assisted-living apartment **$5,740+**/mo base; dining included; personalized care fees extra "
            "([Brookdale Potomac](https://www.brookdale.com/en/communities/brookdale-potomac.html))."
        ),
    },
    "celebration-villa-of-martinsburg": {
        "room_type": "studio",
        "all_in_estimate_monthly": 6650,
        "room_rate_monthly": 6650,
        "price_source_url": "https://celebrationvillaofmartinsburg.com/floor-plans-pricing/",
        "price_confidence": "high",
        "price_notes": "Official: small studio $6,650; large studio $7,150; shared suite $8,650 excluded. No private 1BR listed. Meals; med management via care.",
        "body_extra": (
            "Official floor plans: small studio **$6,650**/mo, large studio **$7,150**/mo, shared two-room suite **$8,650** (excluded) "
            "([Celebration Villa floor plans & pricing](https://celebrationvillaofmartinsburg.com/floor-plans-pricing/)). "
            "Selected **small studio** (cheapest private). No private 1BR published."
        ),
    },
    "charter-senior-living-of-fredericksburg": {
        "room_type": "studio",
        "all_in_estimate_monthly": 4995,
        "room_rate_monthly": 4995,
        "price_source_url": "https://www.charterfredericksburg.com/floor-plans/",
        "price_confidence": "high",
        "price_notes": "Official: private studio $4,995; 1BR $7,495 (over $5k — not preferred). Includes 3 meals, utilities, housekeeping. Med/care levels may add.",
        "body_extra": (
            "Official floor plans: assisted living private studios start **$4,995**/mo; one-bedrooms **$7,495**/mo "
            "([Charter Fredericksburg floor plans](https://www.charterfredericksburg.com/floor-plans/)). "
            "Selected **studio** (under ~$5k; 1BR over budget preference). Includes meals, utilities, housekeeping; confirm care-level add-ons."
        ),
    },
    "commonwealth-senior-living-at-front-royal": {
        "room_type": "unknown",
        "all_in_estimate_monthly": 7050,
        "room_rate_monthly": 7050,
        "price_source_url": "https://www.commonwealthsl.com/commonwealth-senior-living-at-front-royal",
        "price_confidence": "medium",
        "price_notes": "Suite $235/day (~$7,050/mo) Level 1; deluxe $248/day; 1BR $264/day (~$7,920). Selected cheapest suite. Higher care may exceed $8k.",
        "body_extra": (
            "Published daily rates (seed/operator): suite **$235/day (~$7,050/mo)**, deluxe **$248/day**, 1BR **$264/day (~$7,920)** including Level 1 care "
            "([Commonwealth Front Royal](https://www.commonwealthsl.com/commonwealth-senior-living-at-front-royal)). "
            "Selected suite (cheapest). Confirm current private studio/1BR."
        ),
    },
    "edenton-retirement-community": {
        "room_type": "studio",
        "all_in_estimate_monthly": 7100,
        "room_rate_monthly": 6050,
        "price_source_url": "https://www.mylivingchoice.com/property/edenton-retirement-community",
        "price_confidence": "low",
        "price_notes": "Studio base ~$6,050–$6,150 + care $1,050–$1,650 → all-in ~$7,100–$7,800. Used low end of all-in range.",
        "body_extra": (
            "Third-party/seed: AL studio base ~**$6,050–$6,150** plus care ~**$1,050–$1,650** → all-in ~**$7,100–$7,800**/mo "
            "([MyLivingChoice / Edenton](https://www.mylivingchoice.com/property/edenton-retirement-community)). "
            "Selected studio all-in low end; confirm with community."
        ),
    },
    "evermore-senior-living": {
        "room_type": "unknown",
        "all_in_estimate_monthly": 6000,
        "room_rate_monthly": 6000,
        "price_source_url": "https://www.miradorliving.com/assisted-living/virginia/woodbridge/evermore-senior-living",
        "price_confidence": "low",
        "price_notes": "Suite ~$6,000+/mo per Mirador/seed; meals and med management listed. Confirm studio/1BR.",
        "body_extra": (
            "Mirador/seed listing: suite ~**$6,000+**/mo; medication management and meals listed "
            "([Evermore on Mirador](https://www.miradorliving.com/assisted-living/virginia/woodbridge/evermore-senior-living))."
        ),
    },
    "harmony-at-martinsburg": {
        "room_type": "unknown",
        "all_in_estimate_monthly": 4520,
        "room_rate_monthly": 4520,
        "price_source_url": "https://www.harmonyseniorservices.com/community/harmony-at-martinsburg/assisted-living/",
        "price_confidence": "medium",
        "price_notes": "AL from $4,520–$4,600/mo base; chef meals included; med management via care level. Room type not specified — confirm studio vs 1BR.",
        "body_extra": (
            "Harmony/seed: assisted living from **$4,520–$4,600**/mo base; chef-prepared meals included; medication management via care level "
            "([Harmony at Martinsburg](https://www.harmonyseniorservices.com/community/harmony-at-martinsburg/assisted-living/)). "
            "Selected low end; confirm whether a 1BR exists under ~$5k."
        ),
    },
    "harmony-at-spring-hill": {
        "room_type": "unknown",
        "all_in_estimate_monthly": 3900,
        "room_rate_monthly": 3900,
        "price_source_url": "https://www.harmonyseniorservices.com/community/harmony-at-spring-hill/",
        "price_confidence": "medium",
        "price_notes": "AL apartments from $3,900/mo; chef meals included; med assistance via AL care. Confirm studio vs 1BR under $5k.",
        "body_extra": (
            "Harmony: Assisted Living apartments start at **$3,900**/mo; chef-prepared meals included "
            "([Harmony at Spring Hill](https://www.harmonyseniorservices.com/community/harmony-at-spring-hill/)). "
            "Confirm room type and assessed care total."
        ),
    },
    "our-father-s-house-christian-home": {
        "room_type": "one_bedroom",
        "all_in_estimate_monthly": 6494,
        "room_rate_monthly": 6494,
        "price_source_url": "https://www.miradorliving.com/assisted-living/virginia/culpeper/our-fathers-house-christian-home",
        "price_confidence": "low",
        "price_notes": "Mirador 1BR ~$6,494+/mo; meals and med management listed.",
        "body_extra": (
            "Mirador listing: 1BR approx. **$6,494+**/mo "
            "([Our Father's House](https://www.miradorliving.com/assisted-living/virginia/culpeper/our-fathers-house-christian-home))."
        ),
    },
    "paul-spring-retirement-community": {
        "room_type": "one_bedroom",
        "all_in_estimate_monthly": 7015,
        "room_rate_monthly": 7015,
        "price_source_url": "https://www.miradorliving.com/assisted-living/virginia/alexandria/paul-spring-retirement-community",
        "price_confidence": "low",
        "price_notes": "Mirador: 1BR ~$7,015+; studio ~$7,599+. Selected cheaper 1BR.",
        "body_extra": (
            "Mirador: 1BR ~**$7,015+**/mo; studio ~**$7,599+**/mo "
            "([Paul Spring](https://www.miradorliving.com/assisted-living/virginia/alexandria/paul-spring-retirement-community)). "
            "Selected **1BR** (cheaper)."
        ),
    },
    "potomac-place-assisted-living-and-memory-care": {
        "room_type": "one_bedroom",
        "all_in_estimate_monthly": 4800,
        "room_rate_monthly": 4800,
        "price_source_url": "https://www.potomacplace.com/",
        "price_confidence": "low",
        "price_notes": "Third-party estimate: 1BR ~$4,800+; studio ~$5,200+. Prefer 1BR under $5k. Confirm with community.",
        "body_extra": (
            "Third-party/seed estimates: 1BR ~**$4,800+**/mo; studio ~**$5,200+**/mo "
            "([Potomac Place](https://www.potomacplace.com/)). Selected **1BR** under ~$5k preference. Confirm current rates."
        ),
    },
    "rembrandt-assisted-living": {
        "room_type": "one_bedroom",
        "all_in_estimate_monthly": 6414,
        "room_rate_monthly": 6414,
        "price_source_url": "https://www.miradorliving.com/assisted-living/virginia/falls-church/rembrandt-assisted-living",
        "price_confidence": "low",
        "price_notes": "Mirador 1BR ~$6,414+/mo; meals and med management listed.",
        "body_extra": (
            "Mirador: 1BR approx. **$6,414+**/mo "
            "([Rembrandt](https://www.miradorliving.com/assisted-living/virginia/falls-church/rembrandt-assisted-living))."
        ),
    },
    "shenandoah-senior-living": {
        "room_type": "one_bedroom",
        "all_in_estimate_monthly": 6067,
        "room_rate_monthly": 6067,
        "price_source_url": "https://www.miradorliving.com/assisted-living/virginia/front-royal/shenandoah-senior-living",
        "price_confidence": "low",
        "price_notes": "Mirador: 1BR ~$6,067+; studio ~$6,572+. Selected cheaper 1BR.",
        "body_extra": (
            "Mirador: 1BR ~**$6,067+**/mo; studio ~**$6,572+**/mo "
            "([Shenandoah Senior Living](https://www.miradorliving.com/assisted-living/virginia/front-royal/shenandoah-senior-living)). "
            "Selected **1BR**."
        ),
    },
    "spring-arbor-of-frederick": {
        "room_type": "studio",
        "all_in_estimate_monthly": 6947,
        "room_rate_monthly": 6947,
        "price_source_url": "https://www.springarborliving.com/md/frederick/spring-arbor-of-frederick/",
        "price_confidence": "medium",
        "price_notes": "Private studio $6,947; 1BR alcove $7,872; standard 1BR $8,121 excluded. Selected studio. Meals + med management offered.",
        "body_extra": (
            "Published: private studio **$6,947**/mo; 1BR alcove **$7,872**; standard 1BR **$8,121** (excluded as over stretch preference) "
            "([Spring Arbor of Frederick](https://www.springarborliving.com/md/frederick/spring-arbor-of-frederick/)). "
            "Selected **studio**."
        ),
    },
    "spring-oak-at-warrenton": {
        "room_type": "unknown",
        "all_in_estimate_monthly": 5875,
        "room_rate_monthly": 5875,
        "price_source_url": "https://www.springoakliving.com/warrenton",
        "price_confidence": "medium",
        "price_notes": "AL from $5,875/mo; studios and 1BRs available; meals included. Confirm which room type at that start and med package.",
        "body_extra": (
            "Spring Oak: assisted living from **$5,875**/mo; studios and 1BRs available; meals included "
            "([Spring Oak at Warrenton](https://www.springoakliving.com/warrenton)). Confirm room type and med-management package."
        ),
    },
    "stern-life-assisted-living-thames-drive": {
        "room_type": "unknown",
        "all_in_estimate_monthly": 5000,
        "room_rate_monthly": 5000,
        "price_source_url": "https://sternlifeassistedliving.com/",
        "price_confidence": "low",
        "price_notes": "Private room ~$5,000–$6,500/mo; higher care +$1,000. Includes med admin + 3 meals. Selected low end.",
        "body_extra": (
            "Operator/seed: private room ~**$5,000–$6,500**/mo; higher care from +$1,000; medication administration and 3 meals/day included "
            "([Stern Life](https://sternlifeassistedliving.com/)). Selected low end; confirm Thames Drive private rate."
        ),
    },
    "stern-life-assisted-living-walnut-street": {
        "room_type": "unknown",
        "all_in_estimate_monthly": 5000,
        "room_rate_monthly": 5000,
        "price_source_url": "https://sternlifeassistedliving.com/",
        "price_confidence": "low",
        "price_notes": "From $5,000/mo includes med admin, 3 meals, 24/7 supervision, personal care. Confirm private-room Walnut rate.",
        "body_extra": (
            "Operator/seed: from **$5,000**/mo including medication administration, 3 meals/day, 24/7 supervision "
            "([Stern Life](https://sternlifeassistedliving.com/)). Confirm Walnut Street private-room quote."
        ),
    },
    "sunrise-at-bluemont-park": {
        "room_type": "studio",
        "all_in_estimate_monthly": 4900,
        "room_rate_monthly": 4900,
        "price_source_url": "https://www.sunriseseniorliving.com/communities/va/sunrise-at-bluemont-park",
        "price_confidence": "medium",
        "price_notes": "Official starting $4,900+. Seed had studio $4,530 / 1BR $5,533 — prefer studio under $5k (1BR over). Care + med fees extra.",
        "body_extra": (
            "Official community starting rate **$4,900+**/mo "
            "([Sunrise at Bluemont Park](https://www.sunriseseniorliving.com/communities/va/sunrise-at-bluemont-park)). "
            "Seed had studio $4,530+ / 1BR $5,533+; selected **studio** under ~$5k (1BR over preference). "
            "Meals in room rate; care level and medication management additional."
        ),
    },
    "sunrise-at-mount-vernon": {
        "room_type": "studio",
        "all_in_estimate_monthly": 4700,
        "room_rate_monthly": 4700,
        "price_source_url": "https://www.sunriseseniorliving.com/communities/va/sunrise-at-mount-vernon",
        "price_confidence": "medium",
        "price_notes": "Official starting $4,700+. Seed studio $4,900+. Care + med fees extra. Room-type dollars not fully broken out on fetch.",
        "body_extra": (
            "Official starting rate **$4,700+**/mo "
            "([Sunrise at Mount Vernon](https://www.sunriseseniorliving.com/communities/va/sunrise-at-mount-vernon)). "
            "Treated as studio-class start; confirm 1BR availability under ~$5k. Care/med fees additional."
        ),
    },
    "sunrise-at-silas-burke-house": {
        "room_type": "studio",
        "all_in_estimate_monthly": 4500,
        "room_rate_monthly": 4500,
        "price_source_url": "https://www.sunriseseniorliving.com/communities/va/sunrise-at-silas-burke-house",
        "price_confidence": "high",
        "price_notes": "Official: studio $4,500+; 1BR $6,300+. Prefer studio under $5k. Meals included; care + med fees extra.",
        "body_extra": (
            "Official: AL **studio $4,500+**, **1BR $6,300+**, 2BR $6,200+ "
            "([Sunrise at Silas Burke House](https://www.sunriseseniorliving.com/communities/va/sunrise-at-silas-burke-house)). "
            "Selected **studio** (1BR over ~$5k). Base includes meals/programs/housekeeping; care and med management extra."
        ),
    },
    "sunrise-of-alexandria": {
        "room_type": "one_bedroom",
        "all_in_estimate_monthly": 3400,
        "room_rate_monthly": 3400,
        "price_source_url": "https://www.sunriseseniorliving.com/communities/va/sunrise-of-alexandria",
        "price_confidence": "medium",
        "price_notes": "Official starting $3,500+. Seed: 1BR $3,400+; studio $3,500+. Prefer 1BR under $5k. Care + med fees extra.",
        "body_extra": (
            "Official community start **$3,500+**/mo "
            "([Sunrise of Alexandria](https://www.sunriseseniorliving.com/communities/va/sunrise-of-alexandria)); "
            "seed room breakdown 1BR **$3,400+** / studio **$3,500+**. Selected **1BR** under ~$5k. Care/med fees additional."
        ),
    },
    "sunrise-of-arlington": {
        "room_type": "studio",
        "all_in_estimate_monthly": 4100,
        "room_rate_monthly": 4100,
        "price_source_url": "https://www.sunriseseniorliving.com/communities/va/sunrise-of-arlington",
        "price_confidence": "high",
        "price_notes": "Official: AL studio $4,100+; 2BR $5,900+ (no 1BR listed). Selected studio. Care + med fees extra.",
        "body_extra": (
            "Official: AL **studio $4,100+**, **2BR $5,900+** (no 1BR on current floor-plan list) "
            "([Sunrise of Arlington](https://www.sunriseseniorliving.com/communities/va/sunrise-of-arlington)). "
            "Selected **studio**. Care level and medication management additional."
        ),
    },
    "sunrise-of-springfield": {
        "room_type": "one_bedroom",
        "all_in_estimate_monthly": 3400,
        "room_rate_monthly": 3400,
        "price_source_url": "https://www.sunriseseniorliving.com/communities/va/sunrise-of-springfield",
        "price_confidence": "high",
        "price_notes": "Official: studio $3,200+; 1BR $3,400+; 2BR $4,200+. Prefer 1BR under $5k. Care + med fees extra.",
        "body_extra": (
            "Official: AL **studio $3,200+**, **1BR $3,400+**, **2BR $4,200+** "
            "([Sunrise of Springfield](https://www.sunriseseniorliving.com/communities/va/sunrise-of-springfield)). "
            "Selected **1BR**. Base includes meals/programs/housekeeping; care and med management extra."
        ),
    },
    "sunrise-of-vienna": {
        "room_type": "studio",
        "all_in_estimate_monthly": 6200,
        "room_rate_monthly": 6200,
        "price_source_url": "https://www.sunriseseniorliving.com/communities/va/sunrise-of-vienna",
        "price_confidence": "high",
        "price_notes": "Official: AL studio-class $6,200+; larger suites $9,000+/$9,700+. 1BR over $8k stretch — selected studio. Care + med fees extra.",
        "body_extra": (
            "Official: assisted living suites from **$6,200+**/mo; larger plans **$9,000+** / **$9,700+** "
            "([Sunrise of Vienna](https://www.sunriseseniorliving.com/communities/va/sunrise-of-vienna)). "
            "Selected studio-class start; 1BR/2BR exceed comfortable budget. Care and medication management additional."
        ),
    },
    "the-kensington-falls-church": {
        "room_type": "one_bedroom",
        "all_in_estimate_monthly": 6967,
        "room_rate_monthly": 6967,
        "price_source_url": "https://www.miradorliving.com/assisted-living/virginia/falls-church/the-kensington-falls-church",
        "price_confidence": "low",
        "price_notes": "Mirador 1BR ~$6,967+/mo; meals and med management listed. Confirm assessed-care total.",
        "body_extra": (
            "Mirador: 1BR approx. **$6,967+**/mo "
            "([The Kensington Falls Church](https://www.miradorliving.com/assisted-living/virginia/falls-church/the-kensington-falls-church))."
        ),
    },
    "the-view-alexandria": {
        "room_type": "unknown",
        "all_in_estimate_monthly": 4586,
        "room_rate_monthly": 4586,
        "price_source_url": "https://theviewalexandria.org/care-options/assisted-living/",
        "price_confidence": "high",
        "price_notes": "Official AL from $4,586/mo includes 3 meals, programs, weekly housekeeping, linen, 1 parking. Personal care + med management via individualized plan (extra). Studios–2BRs offered.",
        "body_extra": (
            "Official: Assisted Living rates start at **$4,586**/mo including three daily meals, programs, weekly housekeeping, linen service, and parking for one vehicle; "
            "personal care and medication management via individualized care plan "
            "([The View Alexandria assisted living](https://theviewalexandria.org/care-options/assisted-living/)). "
            "Confirm which floor plan (studio vs 1BR) at that start — prefer 1BR if available at/under ~$5k."
        ),
    },
    "the-village-at-orchard-ridge": {
        "room_type": "one_bedroom",
        "all_in_estimate_monthly": 5016,
        "room_rate_monthly": 5016,
        "price_source_url": "https://www.thevillageatorchardridge.org/assisted-living-community-winchester-va",
        "price_confidence": "low",
        "price_notes": "AL estimated from ~$5,016/mo; private 1BR-style apartments; meals and med management listed.",
        "body_extra": (
            "Community/seed estimate: assisted living from about **$5,016**/mo for private 1BR-style apartments "
            "([Village at Orchard Ridge](https://www.thevillageatorchardridge.org/assisted-living-community-winchester-va))."
        ),
    },
    "tribute-at-the-glen": {
        "room_type": "one_bedroom",
        "all_in_estimate_monthly": 4500,
        "room_rate_monthly": 4500,
        "price_source_url": "https://www.miradorliving.com/assisted-living/virginia/woodbridge/tribute-at-the-glen",
        "price_confidence": "low",
        "price_notes": "Mirador 1BR ~$4,500+/mo under $5k preference; meals and med management listed.",
        "body_extra": (
            "Mirador: 1BR approx. **$4,500+**/mo "
            "([Tribute at the Glen](https://www.miradorliving.com/assisted-living/virginia/woodbridge/tribute-at-the-glen)). "
            "Selected **1BR** under ~$5k."
        ),
    },
    "viva-senior-living-at-stafford": {
        "room_type": "unknown",
        "all_in_estimate_monthly": 6000,
        "room_rate_monthly": 6000,
        "price_source_url": "https://www.vivaseniorliving.com/stafford",
        "price_confidence": "medium",
        "price_notes": "Private AL suite $6,000+/mo base; dining offered; additional care fees. Confirm studio vs 1BR.",
        "body_extra": (
            "Listed private assisted-living suite **$6,000+**/mo base; medication management and dining offered; care fees extra "
            "([VIVA Stafford](https://www.vivaseniorliving.com/stafford))."
        ),
    },
    "willow-oaks-assisted-living-at-birmingham-green": {
        "room_type": "one_bedroom",
        "all_in_estimate_monthly": 7696,
        "room_rate_monthly": 7696,
        "price_source_url": "https://www.miradorliving.com/assisted-living/virginia/manassas/willow-oaks-assisted-living-at-birmingham-green",
        "price_confidence": "low",
        "price_notes": "Mirador 1BR ~$7,696+; studio ~$8,338 excluded as higher. Selected cheaper 1BR.",
        "body_extra": (
            "Mirador: 1BR ~**$7,696+**/mo; studio ~**$8,338** "
            "([Willow Oaks](https://www.miradorliving.com/assisted-living/virginia/manassas/willow-oaks-assisted-living-at-birmingham-green)). "
            "Selected **1BR** (cheaper)."
        ),
    },
}


def fmt_num(n):
    if n is None:
        return "null"
    return str(int(n)) if float(n) == int(n) else str(n)


def upsert_fm(fm: str, updates: dict) -> str:
    lines = fm.strip("\n").splitlines()
    keys_done = set()
    out = []
    for line in lines:
        m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
        if not m:
            out.append(line)
            continue
        key = m.group(1)
        if key in updates:
            val = updates[key]
            if val is None:
                out.append(f"{key}: null")
            elif isinstance(val, bool):
                out.append(f"{key}: {'true' if val else 'false'}")
            elif isinstance(val, (int, float)):
                out.append(f"{key}: {fmt_num(val)}")
            else:
                # quote strings that need it
                s = str(val)
                if any(c in s for c in ":#{}[]|&*!?>'@`") or s.startswith((" ", "-")) or "\n" in s:
                    s_esc = s.replace('"', '\\"')
                    out.append(f'{key}: "{s_esc}"')
                else:
                    out.append(f'{key}: "{s}"' if (" " in s or s == "") else f"{key}: {s}")
                    # always quote descriptive strings for safety
                    if key in (
                        "price_notes",
                        "price_source_url",
                        "room_type",
                        "price_confidence",
                        "price_as_of",
                    ) or " " in s or "/" in s or "$" in s or "," in s:
                        s_esc = s.replace('"', '\\"')
                        out[-1] = f'{key}: "{s_esc}"'
            keys_done.add(key)
        else:
            out.append(line)
    # insert new keys before status if present, else append
    insert_at = None
    for i, line in enumerate(out):
        if line.startswith("status:"):
            insert_at = i
            break
    new_keys = [
        ("room_type", updates.get("room_type")),
        ("all_in_estimate_monthly", updates.get("all_in_estimate_monthly")),
        ("room_rate_monthly", updates.get("room_rate_monthly")),
        ("price_source_url", updates.get("price_source_url")),
        ("price_as_of", updates.get("price_as_of")),
        ("price_confidence", updates.get("price_confidence")),
        ("price_notes", updates.get("price_notes")),
    ]
    to_add = []
    for k, v in new_keys:
        if k in keys_done:
            continue
        if v is None and k != "all_in_estimate_monthly" and k != "room_rate_monthly":
            continue
        if v is None:
            to_add.append(f"{k}: null")
        elif isinstance(v, (int, float)):
            to_add.append(f"{k}: {fmt_num(v)}")
        else:
            s_esc = str(v).replace('"', '\\"')
            to_add.append(f'{k}: "{s_esc}"')
    if to_add:
        if insert_at is None:
            out.extend(to_add)
        else:
            out[insert_at:insert_at] = to_add
    return "\n".join(out) + "\n"


def replace_or_insert_price_section(body: str, price_md: str) -> str:
    # Replace "## Price breakdown" section or insert "## Price" after Overview
    price_section = f"## Price\n\n{price_md.strip()}\n"
    if re.search(r"^## Price\b", body, re.M):
        body = re.sub(
            r"^## Price\b.*?(?=^## |\Z)",
            price_section + "\n",
            body,
            count=1,
            flags=re.M | re.S,
        )
        # remove old Price breakdown if both exist
        body = re.sub(r"^## Price breakdown\b.*?(?=^## |\Z)", "", body, count=1, flags=re.M | re.S)
        return body
    if re.search(r"^## Price breakdown\b", body, re.M):
        body = re.sub(
            r"^## Price breakdown\b.*?(?=^## |\Z)",
            price_section + "\n",
            body,
            count=1,
            flags=re.M | re.S,
        )
        return body
    # insert after Overview section
    m = re.search(r"^## Overview\b.*?(?=^## |\Z)", body, re.M | re.S)
    if m:
        return body[: m.end()] + "\n" + price_section + "\n" + body[m.end() :]
    return body.rstrip() + "\n\n" + price_section + "\n"


def main():
    updated = 0
    missing = []
    for d in sorted(LOCS.iterdir()):
        if not d.is_dir():
            continue
        slug = d.name
        path = d / "index.md"
        if not path.exists():
            continue
        if slug.startswith("_example"):
            text = path.read_text()
            if "example: true" not in text and "example: false" not in text:
                pass
            # ensure example marked; add note in Price if missing
            parts = text.split("---", 2)
            if len(parts) >= 3:
                fm, body = parts[1], parts[2]
                if "price_confidence" not in fm:
                    fm = upsert_fm(
                        fm,
                        {
                            "room_type": "unknown",
                            "all_in_estimate_monthly": None,
                            "room_rate_monthly": None,
                            "price_source_url": "",
                            "price_as_of": AS_OF,
                            "price_confidence": "none",
                            "price_notes": "Example stub — skipped for real pricing research.",
                        },
                    )
                    body = replace_or_insert_price_section(
                        body,
                        "_Example location — not researched. Not part of the seed shortlist._",
                    )
                    path.write_text("---\n" + fm + "---" + body)
                    print(f"marked example: {slug}")
            continue
        if slug not in PRICES:
            missing.append(slug)
            continue
        p = PRICES[slug]
        text = path.read_text()
        parts = text.split("---", 2)
        if len(parts) < 3:
            raise SystemExit(f"bad front matter: {path}")
        fm, body = parts[1], parts[2]
        updates = {
            "room_type": p["room_type"],
            "all_in_estimate_monthly": p["all_in_estimate_monthly"],
            "room_rate_monthly": p["room_rate_monthly"],
            "price_source_url": p["price_source_url"],
            "price_as_of": AS_OF,
            "price_confidence": p["price_confidence"],
            "price_notes": p["price_notes"],
        }
        fm2 = upsert_fm(fm, updates)
        # ensure all_in key updated even if was null already present
        conf = p["price_confidence"]
        all_in = p["all_in_estimate_monthly"]
        room = p["room_rate_monthly"]
        rtype = p["room_type"]
        summary = (
            f"- **Selected room type:** `{rtype}`\n"
            f"- **All-in estimate:** ${all_in:,}/mo" if all_in is not None else f"- **All-in estimate:** unknown\n"
        )
        if all_in is not None:
            summary = (
                f"- **Selected room type:** `{rtype}`\n"
                f"- **All-in estimate:** ${all_in:,}/mo\n"
                f"- **Base room rate (if separable):** ${room:,}/mo\n"
                f"- **Confidence:** {conf}\n"
                f"- **As of:** {AS_OF}\n\n"
                f"{p['body_extra']}\n\n"
                f"_Seed price text kept in front matter (`price_range_seed`)._"
            )
        else:
            summary = (
                f"- **Selected room type:** `{rtype}`\n"
                f"- **All-in estimate:** unknown\n"
                f"- **Confidence:** {conf}\n\n"
                f"{p['body_extra']}"
            )
        body2 = replace_or_insert_price_section(body, summary)
        path.write_text("---\n" + fm2 + "---" + body2)
        updated += 1
        print(f"updated: {slug} ({rtype}, {all_in})")
    print(f"\nUpdated {updated} real stubs")
    if missing:
        print("MISSING research:", missing)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
