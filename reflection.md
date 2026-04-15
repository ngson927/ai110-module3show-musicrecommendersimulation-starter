# Reflection: Profile Comparisons and What They Reveal

This file documents observations from running seven user profiles through the recommender.
Each section compares two profiles side by side and explains — in plain language — why the
outputs differ and what that reveals about how the scoring logic actually works.

---

## Pair 1: High-Energy Pop vs. Chill Lofi Study

**Pop profile wants:** upbeat pop, happy mood, high energy (0.80), bright tone, no acoustic  
**Lofi profile wants:** lofi, focused mood, low energy (0.40), calm tone, acoustic

These two are opposites in almost every dimension, so their top results share zero songs.

The pop profile gets *Sunrise City* at #1 — fast, produced, cheerful. The lofi profile gets
*Focus Flow* at #1 — slow, acoustic, understated. Both score nearly 9.7/10 because in each
case the catalog has one song that matches all five rules simultaneously.

The interesting observation is what happens at #4 and #5 for the lofi profile: *Coffee Shop
Stories* (jazz) and *Porch Swing Days* (folk) sneak in despite being the wrong genre. They
earn those spots purely through acoustic texture and low energy — no genre or mood points.
This shows the acousticness rule doing useful cross-genre work: the system found "sounds like
what you want" even when the label didn't match. That is a genuine win for content-based logic.

---

## Pair 2: Deep Intense Rock vs. Sad + High Energy

**Rock profile wants:** rock, intense mood, very high energy (0.92), dark tone, not acoustic  
**Sad profile wants:** hip-hop, sad mood, very high energy (0.92), very dark tone (valence 0.20), not acoustic

Both profiles want nearly identical energy. The difference is mood and emotional tone (valence).

The rock profile gets *Storm Runner* at #1 — the only rock/intense song in the catalog.
The sad profile gets *Lost in Translation* at #1 — the only hip-hop/sad song.

But notice what happens below #1. For the rock profile, *Gym Hero* (pop/intense) comes in
at #2 because it matches the "intense" mood. For the sad profile, *Iron Surge* (metal/angry)
comes in at #2 — it has no mood match, but its very dark valence (0.22) is close to the
user's dark target (0.20), and its energy matches perfectly.

The takeaway: same energy target, completely different #2 results. Mood and valence together
act as a "vibe filter" that separates songs even when their intensity is identical.

---

## Pair 3: Missing Genre (k-pop) vs. Perfectly Neutral

**k-pop profile wants:** k-pop (not in catalog), happy mood, moderate energy (0.75), bright tone  
**Neutral profile wants:** ambient, chill mood, middle energy (0.50), middle tone, not acoustic

Both profiles are in some way "handicapped" — k-pop has a genre that doesn't exist in the
catalog, and neutral has all its numeric targets at the exact midpoint where no song is
particularly close or far.

For the k-pop profile, the missing genre just means no song can ever earn the 1.5 genre
points. The system still works — it returns *Rooftop Lights* and *Sunrise City* as #1 and #2,
both happy and upbeat, both sensible picks. The maximum achievable score is 8.5 instead of
10.0, but the ranking is still useful. Missing a preference doesn't break the system; it just
lowers the ceiling.

For the neutral profile, everything is equally "okay" — no song is much closer or further
than any other on energy or valence. What decides the ranking is the two binary rules: mood
match (2.5 pts) and genre match (1.5 pts). *Spacewalk Thoughts* wins because it earns both.
*Midnight Coding* and *Library Rain* come in #2 and #3 because they match the chill mood
even though their genre is lofi, not ambient. When numbers blur together, labels take over.

---

## Pair 4: Deep Intense Rock vs. Acoustic + Max Energy

**Rock profile wants:** rock, intense mood, energy 0.92, dark, not acoustic  
**Acoustic+MaxEnergy profile wants:** folk, energized mood, energy 0.95, acoustic

These two profiles both want maximum energy, but one wants electronic texture and the other
wants acoustic warmth. This is where the system breaks.

The rock profile works perfectly. Storm Runner (rock/intense/0.91 energy/not acoustic) hits
on all five dimensions and scores 9.74/10. There is a song in the catalog built exactly for
this user.

The acoustic+max energy profile fails. The user wants something like a fast, energetic
acoustic guitar track — think live folk-punk or driving bluegrass. That song doesn't exist
in the catalog. The closest acoustic song (*Porch Swing Days*, folk) only has 0.32 energy.
The closest high-energy song (*Drop Zone*, EDM) is completely electronic.

The system picks Drop Zone at #1. Why? Because energy (3.5 pts) + mood match (2.5 pts)
together = 6.0 points, which beats everything else even after Drop Zone earns almost zero
for acousticness (it scores 0.03 out of a possible 1.0 for an acoustic user). Porch Swing
Days — the song the user probably wanted — only scores 5.21/10 because its energy (0.32)
is so far from the target (0.95) that it loses 2.35 points on that rule alone.

This is the clearest demonstration of what high weights actually mean: a 3.5-point feature
can override a 1.0-point feature even when the 1.0-point feature is perfectly matched.

---

## The Gym Hero Problem — Plain Language Explanation

*Why does Gym Hero keep showing up for people who just want happy pop?*

Gym Hero is a very produced, electronic-sounding pop track. In audio terms, it has almost
no acoustic texture — its acousticness score is 0.05 out of 1.0. That means it sounds like
it was made entirely in a studio with synthesizers and drum machines, with no organic
instruments at all.

Here is the problem: the scoring system awards up to 1.0 point for acoustic texture match.
For any user who says "I don't want acoustic music," the system calculates:

```
acoustic points = 1.0 × (1 - song.acousticness)
               = 1.0 × (1 - 0.05)
               = 0.95 points
```

That is near-perfect texture points — automatically, for every single non-acoustic user,
regardless of what else they want. Gym Hero doesn't need to match your genre, mood, or
emotional tone to earn those 0.95 points. It earns them just by being extremely electronic.

Imagine judging a job applicant by saying "we don't want someone who works from home" and
then the same candidate keeps making the shortlist at every company because they happen to
live next to every office. Their commute is not the reason you want to hire them, but it
keeps boosting their score.

The real fix is not to lower the acousticness weight — it is to add more songs with
mid-range acousticness (0.3–0.7) to the catalog, so that electronic songs have actual
competitors for those texture points rather than winning by default.

---

## Summary: What These Comparisons Show

| Comparison | Key insight |
|---|---|
| Pop vs. Lofi | Acousticness creates useful cross-genre recommendations when genre labels don't match |
| Rock vs. Sad+High Energy | Same energy target, different mood/valence → completely different results below #1 |
| Missing Genre vs. Neutral | Binary rules (mood, genre) act as tiebreakers when numeric features converge |
| Rock vs. Acoustic+MaxEnergy | High-weight features override low-weight features even when perfectly satisfied |
| Gym Hero problem | Catalog gaps (no mid-acousticness songs) let extreme values dominate by default |
