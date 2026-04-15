"""
Music Recommender Simulation — Extended Demo
Showcases all four optional extension challenges in a single run.
"""

from src.recommender import load_songs, recommend_songs, SCORING_MODES

# ---------------------------------------------------------------------------
# Challenge 4 — Visual summary table
# Uses tabulate when available, falls back to clean ASCII.
# ---------------------------------------------------------------------------

try:
    from tabulate import tabulate
    _HAS_TABULATE = True
except ImportError:
    _HAS_TABULATE = False


def _ascii_table(rows: list, headers: list) -> str:
    """Minimal ASCII table fallback when tabulate is not installed."""
    widths = [max(len(str(r[i])) for r in ([headers] + rows)) for i in range(len(headers))]
    sep  = "+-" + "-+-".join("-" * w for w in widths) + "-+"
    def fmt(row):
        return "| " + " | ".join(str(row[i]).ljust(widths[i]) for i in range(len(row))) + " |"
    lines = [sep, fmt(headers), sep] + [fmt(r) for r in rows] + [sep]
    return "\n".join(lines)


def print_results_table(
    label: str,
    note: str,
    user_prefs: dict,
    recommendations: list,
    mode: str = "default",
    diversity: bool = False,
) -> None:
    """Challenge 4 — print recommendations as a formatted table with reasons."""
    W = 64
    print()
    print("=" * W)
    print(f"  {label}")
    if note:
        print(f"  {note}")
    print("-" * W)
    print(f"  Mode     : {mode}  |  Diversity: {'on' if diversity else 'off'}")
    prefs_line = (
        f"  Genre={user_prefs['favorite_genre']}  Mood={user_prefs['favorite_mood']}  "
        f"Energy={user_prefs['target_energy']}  "
        f"Acoustic={'yes' if user_prefs.get('likes_acoustic') else 'no'}"
    )
    print(prefs_line)
    print("=" * W)

    rows = []
    for rank, (song, score, explanation) in enumerate(recommendations, 1):
        rows.append([
            f"#{rank}",
            song["title"],
            f"{score:.2f}",
            f"{song['genre']}/{song['mood']}",
            song.get("mood_tag", ""),
            str(song.get("popularity", "?")),
            song.get("decade", "?"),
        ])

    headers = ["#", "Title", "Score", "Genre/Mood", "Tag", "Pop", "Era"]

    if _HAS_TABULATE:
        print(tabulate(rows, headers=headers, tablefmt="rounded_outline"))
    else:
        print(_ascii_table(rows, headers))

    print()
    print("  Reasons:")
    for rank, (song, score, explanation) in enumerate(recommendations, 1):
        print(f"    #{rank} {song['title'][:22]:<22}  {explanation}")
    print()


# ---------------------------------------------------------------------------
# User profiles
# ---------------------------------------------------------------------------

STANDARD_PROFILES = [
    {
        "_label": "High-Energy Pop",
        "_note":  "Baseline happy pop listener",
        "_mode":  "default",
        "favorite_genre": "pop",
        "favorite_mood":  "happy",
        "target_energy":  0.80,
        "target_valence": 0.80,
        "likes_acoustic": False,
    },
    {
        "_label": "Chill Lofi Study",
        "_note":  "Low-energy acoustic focus session",
        "_mode":  "default",
        "favorite_genre": "lofi",
        "favorite_mood":  "focused",
        "target_energy":  0.40,
        "target_valence": 0.60,
        "likes_acoustic": True,
    },
]

# Challenge 1 — profiles using advanced features
ADVANCED_PROFILES = [
    {
        "_label": "CH1 — Nostalgic 2000s Listener",
        "_note":  "Preferred decade + mood tag bonus rules active",
        "_mode":  "default",
        "favorite_genre":   "folk",
        "favorite_mood":    "nostalgic",
        "target_energy":    0.35,
        "target_valence":   0.65,
        "likes_acoustic":   True,
        "preferred_decade": "2000s",        # Rule 7 — decade match bonus
        "preferred_mood_tag": "nostalgic",  # Rule 8 — mood tag bonus
        "prefer_live":      True,           # Rule 9 — liveness bonus
    },
    {
        "_label": "CH1 — Underground Hip-Hop Seeker",
        "_note":  "Low-popularity + high-speech preference active",
        "_mode":  "mood_first",
        "favorite_genre":   "hip-hop",
        "favorite_mood":    "sad",
        "target_energy":    0.60,
        "target_valence":   0.30,
        "likes_acoustic":   False,
        "prefer_popular":   False,    # Rule 6 — rewards niche/underground songs
        "avoid_speech":     False,    # Rule 10 — rewards high speechiness (rap)
    },
]

# Challenge 2 — same profile, four different scoring modes
MODE_DEMO_PROFILE = {
    "favorite_genre": "pop",
    "favorite_mood":  "happy",
    "target_energy":  0.80,
    "target_valence": 0.75,
    "likes_acoustic": False,
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    songs = load_songs("data/songs.csv")

    # ---- Standard profiles ----
    for p in STANDARD_PROFILES:
        label = p.pop("_label"); note = p.pop("_note"); mode = p.pop("_mode")
        recs = recommend_songs(p, songs, k=5, mode=mode)
        print_results_table(label, note, p, recs, mode=mode)
        p["_label"] = label; p["_note"] = note; p["_mode"] = mode

    # ---- Challenge 1 — Advanced features ----
    print("\n" + "━" * 64)
    print("  CHALLENGE 1 — Advanced Song Features (decade, mood tag, liveness)")
    print("━" * 64)
    for p in ADVANCED_PROFILES:
        label = p.pop("_label"); note = p.pop("_note"); mode = p.pop("_mode")
        recs = recommend_songs(p, songs, k=5, mode=mode)
        print_results_table(label, note, p, recs, mode=mode)
        p["_label"] = label; p["_note"] = note; p["_mode"] = mode

    # ---- Challenge 2 — Scoring Modes ----
    print("\n" + "━" * 64)
    print("  CHALLENGE 2 — Scoring Modes (same profile, 4 different modes)")
    print("━" * 64)
    for mode_name in ["default", "genre_first", "mood_first", "energy_focused"]:
        recs = recommend_songs(MODE_DEMO_PROFILE, songs, k=3, mode=mode_name)
        print_results_table(
            f"Mode: {mode_name.upper()}",
            str(SCORING_MODES[mode_name]),
            MODE_DEMO_PROFILE, recs, mode=mode_name,
        )

    # ---- Challenge 3 — Diversity Penalty ----
    print("\n" + "━" * 64)
    print("  CHALLENGE 3 — Diversity Penalty (same profile, diversity on vs. off)")
    print("━" * 64)

    # LoRoom has two songs in the catalog: Focus Flow and Midnight Coding.
    # A lofi/focused user scores both highly — without diversity they both
    # appear in the top 5. With diversity, the second LoRoom song is pushed
    # down to make room for a different artist.
    diversity_profile = {
        "favorite_genre": "lofi",
        "favorite_mood":  "focused",
        "target_energy":  0.40,
        "target_valence": 0.60,
        "likes_acoustic": True,
    }
    recs_no_div = recommend_songs(diversity_profile, songs, k=5, diversity=False)
    recs_div    = recommend_songs(diversity_profile, songs, k=5, diversity=True, artist_penalty=1.5)

    print_results_table("Diversity OFF", "LoRoom appears twice (Focus Flow + Midnight Coding)", diversity_profile, recs_no_div, diversity=False)
    print_results_table("Diversity ON  (artist_penalty=1.5)", "second LoRoom song penalised — new artist enters top 5", diversity_profile, recs_div, diversity=True)


if __name__ == "__main__":
    main()
