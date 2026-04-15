"""
Command line runner for the Music Recommender Simulation.

Runs all user profiles — standard and adversarial — in a single pass
and prints ranked recommendations with per-rule score explanations.
"""

from src.recommender import load_songs, recommend_songs


# ---------------------------------------------------------------------------
# User Profiles
# ---------------------------------------------------------------------------

PROFILES = [
    # --- Standard profiles ---
    {
        "_label": "High-Energy Pop",
        "_note": "Standard: upbeat pop fan",
        "favorite_genre": "pop",
        "favorite_mood":  "happy",
        "target_energy":  0.80,
        "target_valence": 0.80,
        "likes_acoustic": False,
    },
    {
        "_label": "Chill Lofi Study",
        "_note": "Standard: low-energy focus session",
        "favorite_genre": "lofi",
        "favorite_mood":  "focused",
        "target_energy":  0.40,
        "target_valence": 0.60,
        "likes_acoustic": True,
    },
    {
        "_label": "Deep Intense Rock",
        "_note": "Standard: high-energy workout listener",
        "favorite_genre": "rock",
        "favorite_mood":  "intense",
        "target_energy":  0.92,
        "target_valence": 0.40,
        "likes_acoustic": False,
    },

    # --- Adversarial / edge-case profiles ---
    {
        "_label": "EDGE: Sad but High Energy",
        "_note": "Conflict — sad mood normally pairs with low energy (0.2-0.4). "
                 "Does the system surface sad songs with wrong energy, or "
                 "energetic songs with wrong mood?",
        "favorite_genre": "hip-hop",
        "favorite_mood":  "sad",
        "target_energy":  0.92,
        "target_valence": 0.20,
        "likes_acoustic": False,
    },
    {
        "_label": "EDGE: Genre Not in Catalog",
        "_note": "Favorite genre 'k-pop' does not exist in songs.csv. "
                 "No song can ever earn the 1.5 genre points. "
                 "Does the system still return useful results on the other 4 rules?",
        "favorite_genre": "k-pop",
        "favorite_mood":  "happy",
        "target_energy":  0.75,
        "target_valence": 0.80,
        "likes_acoustic": False,
    },
    {
        "_label": "EDGE: Perfectly Neutral",
        "_note": "All numerical targets at 0.5 — the exact midpoint. "
                 "Every song is equally 'close'. Does the system produce "
                 "a meaningful ranking or near-tied scores?",
        "favorite_genre": "ambient",
        "favorite_mood":  "chill",
        "target_energy":  0.50,
        "target_valence": 0.50,
        "likes_acoustic": False,
    },
    {
        "_label": "EDGE: Acoustic but Max Energy",
        "_note": "Conflict — acoustic songs in the catalog are low energy (0.18-0.42). "
                 "High energy songs are electronic. Both preferences cannot be "
                 "satisfied at once. Which trade-off does the system make?",
        "favorite_genre": "folk",
        "favorite_mood":  "energized",
        "target_energy":  0.95,
        "target_valence": 0.70,
        "likes_acoustic": True,
    },
]


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

WIDTH = 56
DIVIDER = "-" * WIDTH


def print_profile_results(label, note, user_prefs, recommendations) -> None:
    """Print a formatted block of results for one user profile."""
    print()
    print("=" * WIDTH)
    print(f"  {label}")
    print(f"  {note}")
    print("=" * WIDTH)
    print(f"  Genre   : {user_prefs['favorite_genre']}")
    print(f"  Mood    : {user_prefs['favorite_mood']}")
    print(f"  Energy  : {user_prefs['target_energy']}")
    print(f"  Valence : {user_prefs['target_valence']}")
    print(f"  Acoustic: {'yes' if user_prefs['likes_acoustic'] else 'no'}")
    print("-" * WIDTH)
    print()

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"  #{rank}  {song['title']}  —  {song['artist']}")
        print(f"       Score : {score:.2f} / 10.00")
        print(f"       Genre : {song['genre']}  |  Mood: {song['mood']}")
        print(f"       Why   : {explanation}")
        print(f"  {DIVIDER}")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    songs = load_songs("data/songs.csv")

    for profile in PROFILES:
        label = profile.pop("_label")
        note  = profile.pop("_note")
        recs  = recommend_songs(profile, songs, k=5)
        print_profile_results(label, note, profile, recs)
        profile["_label"] = label
        profile["_note"]  = note


if __name__ == "__main__":
    main()
