# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder 1.0 suggests up to 5 songs from an 18-song catalog based on a user's stated genre preference, mood, target energy level, emotional tone (valence), and acoustic texture preference. It is designed for classroom exploration of content-based filtering concepts — not for real users or production deployment. The system assumes users can accurately describe their preferences upfront (genre, mood, energy) and that those preferences remain constant throughout a session. It makes no attempt to learn from listening behavior.

---

## 3. How the Model Works

Each song in the catalog is given a score from 0 to 10 by comparing five of its features against the user's stated preferences. Songs that are energetically closest to what the user wants earn the most points (up to 3.5). A mood match awards a fixed 2.5 points — the system treats a wrong mood as a hard mismatch. Emotional tone (valence) and genre each contribute up to 1.5 points, and acoustic texture adds up to 1 point. All 18 songs are scored independently, then sorted from highest to lowest. The top 5 are returned along with a plain-language explanation of exactly which features earned points and how many.

The key design choice is that mood outweighs genre: a jazz song in the right mood is preferred over a pop song in the wrong mood. Energy uses a proximity formula — the closer a song's intensity is to the user's target, the more points it earns — so the system rewards "closest match," not "loudest song."

---

## 4. Data

The catalog contains 18 songs across 15 genres and 14 moods, stored in `data/songs.csv`. The original 10-song starter set was expanded with 8 additional songs to cover genres absent from the original (hip-hop, r&b, classical, metal, folk, edm, country, funk) and moods absent from the original (sad, romantic, peaceful, angry, nostalgic, energized, melancholic, playful).

Despite this expansion, the catalog is heavily skewed: lofi has 3 songs, pop has 2, and every other genre has exactly 1. Eleven of 14 moods are represented by a single song each. The energy distribution leans toward high-energy content (8 of 18 songs have energy above 0.70). The dataset reflects a Western popular music bias — no African, Latin, or South Asian genres are present — and was constructed synthetically, meaning song feature values were assigned by hand rather than measured from real audio.

---

## 5. Strengths

The system works well when the user's preferences align with a song that has matching genre, mood, and energy simultaneously — in these cases the top result is unambiguous (scores of 9.5–9.8/10) and consistent with musical intuition. The proximity-based energy scoring correctly surfaces songs that are "close enough" rather than just the loudest, which means a user wanting moderate energy does not always get extreme results. The explanation output (e.g., "mood match (+2.50), energy proximity (+3.43)") makes every recommendation fully traceable — there are no black-box decisions. The weight sensitivity experiment confirmed the baseline weights are stable: doubling energy or removing genre did not change the top-ranked song in any tested profile.

---

## 6. Limitations and Bias

**Primary weakness: mood singularity creates a two-tier catalog.**
Eleven of 14 moods in the catalog have exactly one song. This means any user whose favorite mood is `sad`, `romantic`, `peaceful`, `angry`, `nostalgic`, `energized`, `melancholic`, or `playful` can earn the 2.5-point mood bonus from at most one song in the entire catalog — and zero songs if that single match also fails on energy. Users preferring `chill`, `happy`, or `intense` have two or three mood-matching options, giving them a structural scoring advantage. In practice, this means the system is not equally useful across all mood preferences: a user who wants `romantic` music will almost always receive four recommendations that don't match their mood at all, regardless of how good their other preferences are specified.

**Secondary weakness: acousticness gap amplifies electronic songs.**
Three songs — Gym Hero (0.05), Iron Surge (0.04), and Drop Zone (0.03) — have near-zero acousticness. For every non-acoustic user (6 of 7 tested profiles), these songs automatically earn 0.95–0.97 acousticness points regardless of whether they match any other preference. This causes them to appear in the top 5 across wildly different user profiles: Gym Hero appeared in 5 of 7 tested top-5 lists, not because it was genuinely relevant but because no song in the mid-range acousticness zone (0.3–0.7) exists to compete.

**Tertiary weakness: energy weight dominates conflicting preferences.**
With 3.5 out of 10 maximum points, energy is 35% of the total score. When a user has preferences that are structurally incompatible in the catalog (e.g., high energy AND acoustic texture), energy always wins. The acoustic + max-energy edge case placed the electronic Drop Zone at #1 over the folk Porch Swing Days — the song the user most likely wanted — because energy + mood together (6.0 pts) overwhelmed the acoustic preference entirely.

---

## 7. Evaluation

Seven user profiles were tested: three standard (pop/happy, lofi/focused, rock/intense) and four adversarial edge cases (sad+high energy, missing genre, perfectly neutral, acoustic+max energy). For each profile the top 5 results were reviewed against musical intuition, and a cross-profile frequency count was run to surface catalog-level biases.

**Profile results at a glance:**

| Profile | Top result | Correct? | Key observation |
|---|---|---|---|
| High-Energy Pop | Sunrise City (9.69/10) | Yes | All 5 rules matched — unambiguous winner |
| Chill Lofi Study | Focus Flow (9.76/10) | Yes | Jazz and folk surfaced at #4–5 via acousticness despite genre miss |
| Deep Intense Rock | Storm Runner (9.74/10) | Yes | Genre + mood + energy all aligned |
| Sad + High Energy | Lost in Translation (8.78/10) | Yes | Emotional fit (genre+mood+valence = 5.38 pts) beat the energy mismatch |
| Missing Genre (k-pop) | Rooftop Lights (8.09/10) | Yes | Graceful degradation — sensible results, just lower ceiling |
| Perfectly Neutral | Spacewalk Thoughts (8.08/10) | Yes | Categorical matches acted as tiebreakers when proximity scores converged |
| Acoustic + Max Energy | Drop Zone (7.41/10) | **No** | Energy (3.5) + mood (2.5) overwhelmed acoustic preference — EDM beat folk |

**What surprised me:**

The cross-profile frequency count was the most revealing test. Gym Hero appeared in 5 of 7 top-5 lists — not because it was musically relevant, but because its near-zero acousticness (0.05) automatically earned 0.95 texture points from every non-acoustic user. The system was being gamed by a catalog gap, not a weight problem. Doubling the energy weight changed nothing (proportional inflation), but removing mood caused one rank swap — confirming mood is the weight that actually controls ordering between similar songs.

A weight sensitivity experiment confirmed the baseline is stable: doubling energy weight produced no rank changes, while removing mood caused one rank swap (Gym Hero overtook Rooftop Lights for #2 in the pop profile), proving mood is the most structurally important weight.

---

## 8. Future Work

- **Expand mood coverage**: Add 2–3 songs per mood so every mood preference has at least a few candidates. The current single-song moods make the mood weight nearly useless for most users.
- **Fill the acousticness gap**: Add 4–6 songs with mid-range acousticness (0.3–0.6) to break the electronic floor bias that inflates Gym Hero and Drop Zone.
- **Soft genre matching**: Replace binary genre equality with a similarity lookup (e.g., `lofi` ≈ `ambient` ≈ `jazz` for calm, acoustic users) so genre misses don't always score zero.
- **Diversity constraint in ranking**: After scoring, enforce that no more than 2 songs from the same artist or genre appear in the top 5, so the output feels varied.
- **Context-aware profiles**: Allow a user to specify a context (studying, working out, commuting) that automatically adjusts weights — e.g., energy weight rises for workout context, valence weight rises for mood-sensitive contexts.

---

## 9. Personal Reflection

Building this simulation made the mechanics of content-based filtering concrete in a way that reading about it does not. The scoring recipe looks simple on paper, but running adversarial profiles revealed that small catalog imbalances — a handful of songs with extreme acousticness values, eleven moods with only one representative each — can quietly dominate the output in ways that would be invisible without systematic testing. The most surprising discovery was that doubling the energy weight changed nothing: when I expected the rankings to shift dramatically, they stayed identical, which showed that relative distances between songs matter more than absolute weight values.

This changed how I think about Spotify's Discover Weekly. What feels like the app "knowing" your taste is really a much larger version of the same scoring loop — but with millions of songs diluting the catalog biases, behavioral data (skips, replays) replacing static profiles, and collaborative signals from users with similar taste filling in the gaps that pure content-matching misses. The filter bubble problem I observed here — users of rare moods getting worse recommendations — is a real and documented issue in production recommender systems, typically addressed by deliberately injecting diverse or serendipitous results into the ranking.
