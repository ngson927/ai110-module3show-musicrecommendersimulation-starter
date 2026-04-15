# 🎧 Model Card: VibeFinder 1.0

---

## 1. Model Name

**VibeFinder 1.0** — a content-based music recommender simulation built for classroom exploration.

---

## 2. Goal / Task

VibeFinder tries to answer one question: *given what a user says they like, which songs in the catalog are the best match right now?*

It does this by comparing five features of every song against the user's stated preferences and giving each song a score from 0 to 10. The songs with the highest scores are recommended. It does not predict what a user will click on, does not learn from behavior, and does not use data from other users. It just scores and ranks.

---

## 3. Data Used

- **Catalog size:** 18 songs in `data/songs.csv`
- **Features per song:** genre, mood, energy (0–1), tempo (BPM), valence (0–1), danceability (0–1), acousticness (0–1)
- **Genres covered:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, r&b, classical, metal, folk, edm, country, funk (15 total)
- **Moods covered:** happy, chill, intense, relaxed, focused, moody, sad, romantic, peaceful, angry, nostalgic, energized, melancholic, playful (14 total)

**Known limits of the data:**
- The catalog is tiny. 11 of 14 moods have only one song. This means most users will only get one mood match in the entire top 5.
- Feature values (energy, valence, etc.) were assigned by hand, not measured from real audio. They may not reflect how these songs would actually be analyzed by a tool like Spotify.
- Only Western music genres are represented. No African, Latin, K-pop, Bollywood, or regional genres are in the catalog.
- 8 of 18 songs are high-energy (above 0.70). Low-energy users have fewer good matches available.

---

## 4. Algorithm Summary

The system scores each song using five rules, then returns the top results in order.

**Rule 1 — Energy (up to 3.5 points)**
The system checks how close a song's energy level is to what the user asked for. A song at exactly the right energy gets 3.5 points. A song at the opposite extreme gets 0. This rewards "closest match" — not just the loudest or the most energetic song.

**Rule 2 — Mood (up to 2.5 points)**
If the song's mood label matches the user's favorite mood exactly, it gets 2.5 points. If not, it gets zero. There is no partial credit. This is intentional — a wrong mood is a hard mismatch that most listeners would skip.

**Rule 3 — Valence (up to 1.5 points)**
Valence measures whether a song sounds happy/bright or dark/melancholic. The system rewards songs whose emotional tone is closest to the user's target. This rule helps separate songs that have the same energy but feel completely different — for example, an intense-but-triumphant track vs. an intense-but-dark one.

**Rule 4 — Genre (up to 1.5 points)**
If the song's genre matches the user's preferred genre exactly, it gets 1.5 points. Otherwise zero. Genre is weighted below mood because users are more likely to tolerate an unexpected genre than an unexpected vibe.

**Rule 5 — Acoustic texture (up to 1.0 point)**
The system checks whether a song is organic/warm (acoustic) or electronic/produced. If the user prefers acoustic, songs with higher acousticness score higher. If the user prefers electronic, songs with lower acousticness score higher. This separates a warm jazz piano from a synthesized EDM drop even if they have similar energy.

**Final score = sum of all five rules. Maximum = 10.0 points. Sorted highest to lowest. Top 5 returned.**

---

## 5. Observed Behavior / Biases

**What works well:**
When a user's preferences line up with a song that hits all five rules, the result is unambiguous — scores of 9.5–9.8 out of 10, and the recommendation matches intuition immediately. The mood-over-genre weight decision proved correct: in testing, a happy indie pop song correctly ranked above an intense pop song for a happy user, because the mood match (2.5 pts) outweighed the genre match (1.5 pts). Every recommendation comes with a plain-language explanation, so there are no hidden or unexplainable results.

**Bias 1 — Mood singularity (the most impactful)**
Eleven of 14 moods have exactly one song. A user who wants `romantic`, `nostalgic`, `angry`, or `peaceful` music can earn the 2.5-point mood bonus from at most one song in the entire catalog. Users who want `chill`, `happy`, or `intense` have two or three mood-matching songs — a structural advantage that has nothing to do with the weights. This makes the system unequally useful: a romantic music user will always receive four recommendations that don't match their mood no matter what.

**Bias 2 — Acousticness floor exploit (the most surprising)**
Three songs — Gym Hero (0.05), Iron Surge (0.04), and Drop Zone (0.03) — are extremely electronic. For every user who says "I don't want acoustic music," those songs automatically earn 0.95–0.97 texture points just for being electronic, with no requirement to match mood, genre, or energy. Gym Hero appeared in 5 out of 7 tested top-5 lists not because it was a good fit, but because the catalog has no mid-range acoustic songs (0.3–0.7) to compete with it. The fix is more songs in that range, not different weights.

**Bias 3 — Energy dominates incompatible preferences**
Energy is worth 3.5 out of 10 points — 35% of the total. When two preferences conflict (like wanting high energy AND acoustic texture), energy always wins. In testing, an EDM track ranked #1 for a user who explicitly asked for acoustic folk music, simply because the EDM song's energy and mood matched better than any acoustic song could. This is a real flaw: the system cannot gracefully handle preferences that are structurally impossible to satisfy together in a small catalog.

---

## 6. Evaluation Process

Seven user profiles were tested: three standard profiles and four adversarial edge cases designed to expose weaknesses.

**Standard profiles tested:**
- *High-Energy Pop* (genre: pop, mood: happy, energy: 0.80) — baseline happy listener
- *Chill Lofi Study* (genre: lofi, mood: focused, energy: 0.40, acoustic: yes) — low-energy background music
- *Deep Intense Rock* (genre: rock, mood: intense, energy: 0.92) — workout listener

**Adversarial profiles tested:**
- *Sad + High Energy* — conflicting preferences (sad mood but high energy target)
- *Missing Genre (k-pop)* — favorite genre not in catalog
- *Perfectly Neutral* — all numeric targets at the midpoint (0.5)
- *Acoustic + Max Energy* — two preferences that cannot both be satisfied

**Results summary:**

| Profile | Top result | Felt right? |
|---|---|---|
| High-Energy Pop | Sunrise City (9.69/10) | Yes |
| Chill Lofi Study | Focus Flow (9.76/10) | Yes |
| Deep Intense Rock | Storm Runner (9.74/10) | Yes |
| Sad + High Energy | Lost in Translation (8.78/10) | Yes — emotional fit won over energy |
| Missing Genre | Rooftop Lights (8.09/10) | Yes — graceful degradation |
| Perfectly Neutral | Spacewalk Thoughts (8.08/10) | Yes — categorical rules broke the tie |
| Acoustic + Max Energy | Drop Zone (7.41/10) | **No** — EDM beat folk |

A weight sensitivity experiment was also run. Doubling the energy weight produced no rank changes — it only inflated scores proportionally. Removing the mood weight caused one rank swap (Gym Hero overtook Rooftop Lights for second place in the pop profile), which confirmed that mood is the most structurally important weight in the recipe.

---

## 7. Intended Use and Non-Intended Use

**Intended use:**
- Classroom demonstration of how content-based filtering works
- Learning how weighted scoring, proximity formulas, and categorical matching combine to produce ranked results
- Exploring how small changes to weights or catalog composition change recommendations
- Understanding what "bias" means in a recommendation system through hands-on experimentation

**Not intended for:**
- Real music discovery for actual users — the catalog is too small and the feature values are synthetic
- Any deployment in a product or app — there is no personalization, no behavioral learning, and no diversity enforcement
- Representing any real user population — the catalog reflects one person's genre choices and hand-assigned values
- Making decisions about music preferences at scale — a system with 18 songs and 14 mood labels is not a substitute for systems trained on millions of tracks with measured audio features

---

## 8. Ideas for Improvement

**1. Add 2–3 songs per mood**
Right now 11 moods have only one song. A user who wants "romantic" music gets one mood match in the entire catalog. Adding more songs per mood would make the mood weight actually useful for most users, not just the ones who happen to want chill, happy, or intense music.

**2. Add songs with mid-range acousticness**
Only 2 of 18 songs have acousticness between 0.3 and 0.7. This gap means extremely electronic songs (Gym Hero, Drop Zone, Iron Surge) dominate the texture scoring for all non-acoustic users. Adding 4–6 songs with medium texture would break this exploit and make acousticness a more meaningful differentiator.

**3. Soft genre matching**
Right now genre is binary — lofi and ambient score the same as lofi and heavy metal on the genre rule (both get zero). In reality, lofi and ambient are nearly the same vibe. A similarity table (e.g., lofi ≈ ambient ≈ jazz for calm texture) would let the genre rule do more nuanced work without a complete overhaul of the scoring logic.

---

## 9. Personal Reflection

### Biggest learning moment

The biggest learning moment came from the weight sensitivity experiment — specifically from what *didn't* happen. I expected that doubling the energy weight from 3.5 to 7.0 would visibly shake up the rankings. It changed nothing. Every song that was #1 stayed #1, every #2 stayed #2. That forced me to understand something that isn't obvious from reading about recommender systems: weights control *how much* a feature matters in close contests, but when one song already outscores everything else across multiple features simultaneously, no single weight adjustment can change who wins. The math is stable by design. What actually moves rankings is removing a feature entirely — which is what happened when I set mood to zero and watched Gym Hero jump over Rooftop Lights. That showed me that the *presence or absence* of a signal is often more powerful than how heavily you weight it.

### How AI tools helped — and when I had to double-check

AI tools were genuinely useful for three things in this project: generating the initial algorithm recipe structure, explaining the difference between `.sort()` and `sorted()` when I asked about it, and suggesting the adversarial edge-case profiles (the "missing genre" and "conflicting preferences" ideas both came from prompting for edge cases). Those contributions saved real time and pointed me toward things I might have missed.

Where I had to slow down and verify: the AI's first instinct on weight design was to give genre more points than mood (the starter recipe suggested `+2.0 for genre, +1.0 for mood`). That felt wrong based on how I actually experience music — a wrong mood is more jarring than a wrong genre — so I questioned it, thought it through, and reversed the weights. The AI was generating a plausible-sounding recipe, not reasoning from lived experience. The experiment with the "intense rock user getting a chill lofi song" confirmed my intuition was right. This was a useful reminder: AI tools reflect patterns in training data, not personal judgment. The judgment still has to come from the person building the system.

### What surprised me about simple algorithms "feeling" like recommendations

The most surprising thing was how much the *explanation output* changed the experience of getting a recommendation. When the terminal just prints a song title, it feels arbitrary. When it prints:

```
Sunrise City — Score: 9.69
Why: energy proximity (+3.43), mood match (+2.50), valence proximity (+1.44),
     genre match (+1.50), acousticness match (+0.82)
```

...it suddenly feels like the system *understood* the request. The math underneath is five multiplications and two equality checks — nothing sophisticated — but seeing the reasoning spelled out makes it feel reasoned. That is exactly what Spotify's "Because you listened to..." cards do. They are not showing you a complex neural network's decision. They are showing you a human-readable justification that makes an automated process feel personal. Building the explanation layer made me realize that transparency and perceived intelligence are closely linked in recommender UX — sometimes more so than the actual algorithm quality.

### What I would try next

**Behavioral feedback loop.** The biggest gap between this simulation and a real system is that this one never learns. Every run starts from scratch. Even a minimal version — tracking which top-5 songs the user skips vs. keeps, and nudging weights slightly after each session — would make the system feel alive in a way that static profiles never can.

**Mood detection from context instead of user input.** Asking users to declare their mood upfront is unrealistic. Real systems infer it: time of day, recent listening history, even weather API data. I would experiment with a simple rule-based context layer — if it is after 10pm, automatically lower the energy target and shift valence toward darker values — to see if inferred context produces better results than explicit input.

**Testing against real users.** Every evaluation in this project was me judging whether the output "felt right" based on my own musical taste. That is a sample size of one. Even asking five classmates with different music preferences to run their own profiles and rate the top 5 results would reveal biases in the catalog and weights that I simply cannot see from my own perspective.
