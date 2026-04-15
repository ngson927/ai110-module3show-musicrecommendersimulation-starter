from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    # Challenge 1 — advanced features (optional, default to neutral values)
    popularity: int = 50
    decade: str = "unknown"
    mood_tag: str = ""
    speechiness: float = 0.0
    liveness: float = 0.0


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    target_valence: float = 0.5


# ---------------------------------------------------------------------------
# Challenge 2 — Scoring Modes
# Named weight presets a user can switch between in main.py.
# ---------------------------------------------------------------------------

DEFAULT_WEIGHTS = {
    "energy":       3.5,   # strongest continuous signal — physical intensity
    "mood":         2.5,   # binary match — wrong mood = instant skip
    "valence":      1.5,   # separates happy-intense from dark-intense
    "genre":        1.5,   # useful anchor, but below mood
    "acousticness": 1.0,   # texture — organic vs. electronic
}

SCORING_MODES = {
    # Balanced default recipe
    "default":        DEFAULT_WEIGHTS,

    # Genre-First: for users who strongly identify with one genre
    "genre_first":    {"energy": 1.5, "mood": 1.5, "valence": 1.0,
                       "genre": 5.0, "acousticness": 1.0},

    # Mood-First: for users who prioritize emotional feel above all
    "mood_first":     {"energy": 2.0, "mood": 5.5, "valence": 1.5,
                       "genre": 0.5, "acousticness": 0.5},

    # Energy-Focused: for activity-based listening (gym, running, studying)
    "energy_focused": {"energy": 7.0, "mood": 1.0, "valence": 1.0,
                       "genre": 0.5, "acousticness": 0.5},

    # Vibe-Match: emotional tone over genre or raw intensity
    "vibe_match":     {"energy": 2.5, "mood": 2.5, "valence": 3.5,
                       "genre": 0.5, "acousticness": 1.0},
}


# ---------------------------------------------------------------------------
# Recommender class (OOP path — used by tests)
# ---------------------------------------------------------------------------

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(
        self,
        user: UserProfile,
        k: int = 5,
        weights: Optional[Dict[str, float]] = None,
    ) -> List[Song]:
        """Score all songs against the user profile and return the top k sorted by score."""
        user_dict = asdict(user)
        scored = sorted(
            self.songs,
            key=lambda s: score_song(user_dict, asdict(s), weights=weights)[0],
            reverse=True,
        )
        return scored[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable string describing why a song was recommended."""
        _, reasons = score_song(asdict(user), asdict(song))
        return ", ".join(reasons)


# ---------------------------------------------------------------------------
# CSV loader
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    import csv

    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            song = {
                "id":           int(row["id"]),
                "title":        row["title"],
                "artist":       row["artist"],
                "genre":        row["genre"],
                "mood":         row["mood"],
                "energy":       float(row["energy"]),
                "tempo_bpm":    float(row["tempo_bpm"]),
                "valence":      float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
                # Challenge 1 — new fields (graceful fallback if column absent)
                "popularity":   int(row.get("popularity", 50)),
                "decade":       row.get("decade", "unknown"),
                "mood_tag":     row.get("mood_tag", ""),
                "speechiness":  float(row.get("speechiness", 0.0)),
                "liveness":     float(row.get("liveness", 0.0)),
            }
            songs.append(song)
    print(f"Loaded songs: {len(songs)}")
    return songs


# ---------------------------------------------------------------------------
# Core scoring function
# ---------------------------------------------------------------------------

def score_song(
    user_prefs: Dict,
    song: Dict,
    weights: Optional[Dict[str, float]] = None,
) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences using the Algorithm Recipe.

    Core rules (always applied):
        energy, mood, valence, genre, acousticness

    Challenge 1 bonus rules (applied only when user_prefs contains the key):
        prefer_popular   → popularity rule    (max 1.0 pt)
        preferred_decade → decade rule        (max 1.0 pt)
        preferred_mood_tag → mood_tag rule    (max 1.0 pt)
        prefer_live      → liveness rule      (max 0.5 pt)
        avoid_speech     → speechiness rule   (max 0.5 pt)

    Returns:
        (score, reasons) — score is a float, reasons is a list of strings.
    """
    w = {**DEFAULT_WEIGHTS, **(weights or {})}
    score = 0.0
    reasons = []

    # --- Core rules ---

    # Rule 1 — Energy proximity (max w["energy"] pts)
    energy_pts = round(w["energy"] * (1 - abs(song["energy"] - user_prefs["target_energy"])), 2)
    score += energy_pts
    reasons.append(f"energy ({energy_pts:+.2f}/{w['energy']})")

    # Rule 2 — Mood match (binary)
    if song["mood"] == user_prefs["favorite_mood"]:
        score += w["mood"]
        reasons.append(f"mood match (+{w['mood']:.2f})")

    # Rule 3 — Valence proximity
    target_valence = user_prefs.get("target_valence", 0.5)
    valence_pts = round(w["valence"] * (1 - abs(song["valence"] - target_valence)), 2)
    score += valence_pts
    reasons.append(f"valence ({valence_pts:+.2f}/{w['valence']})")

    # Rule 4 — Genre match (binary)
    if song["genre"] == user_prefs["favorite_genre"]:
        score += w["genre"]
        reasons.append(f"genre match (+{w['genre']:.2f})")

    # Rule 5 — Acousticness match
    if user_prefs.get("likes_acoustic", False):
        acoustic_pts = round(w["acousticness"] * song["acousticness"], 2)
    else:
        acoustic_pts = round(w["acousticness"] * (1 - song["acousticness"]), 2)
    score += acoustic_pts
    reasons.append(f"acousticness ({acoustic_pts:+.2f}/{w['acousticness']})")

    # --- Challenge 1: Bonus rules (optional — only applied when user opts in) ---

    # Rule 6 — Popularity (max 1.0 pt)
    # prefer_popular=True → rewards well-known songs; False → rewards niche/underground
    if "prefer_popular" in user_prefs:
        pop_ratio = song.get("popularity", 50) / 100
        pop_pts = round(pop_ratio if user_prefs["prefer_popular"] else (1 - pop_ratio), 2)
        score += pop_pts
        label = "popular" if user_prefs["prefer_popular"] else "underground"
        reasons.append(f"{label} ({pop_pts:+.2f}/1.0)")

    # Rule 7 — Decade match (max 1.0 pt, binary)
    if "preferred_decade" in user_prefs and song.get("decade"):
        if song["decade"] == user_prefs["preferred_decade"]:
            score += 1.0
            reasons.append(f"decade match {song['decade']} (+1.00)")

    # Rule 8 — Mood tag match (max 1.0 pt, binary)
    # More granular than the broad mood category
    if "preferred_mood_tag" in user_prefs and song.get("mood_tag"):
        if song["mood_tag"] == user_prefs["preferred_mood_tag"]:
            score += 1.0
            reasons.append(f"mood tag '{song['mood_tag']}' (+1.00)")

    # Rule 9 — Liveness preference (max 0.5 pt)
    # prefer_live=True → rewards live recordings; False → rewards studio-polished
    if "prefer_live" in user_prefs:
        live_pts = round(0.5 * (song.get("liveness", 0) if user_prefs["prefer_live"]
                                else 1 - song.get("liveness", 0)), 2)
        score += live_pts
        reasons.append(f"liveness ({live_pts:+.2f}/0.5)")

    # Rule 10 — Speechiness preference (max 0.5 pt)
    # avoid_speech=True → rewards instrumental/low-speech songs
    if "avoid_speech" in user_prefs:
        sp = song.get("speechiness", 0)
        speech_pts = round(0.5 * (1 - sp) if user_prefs["avoid_speech"] else 0.5 * sp, 2)
        score += speech_pts
        reasons.append(f"speechiness ({speech_pts:+.2f}/0.5)")

    return round(score, 2), reasons


# ---------------------------------------------------------------------------
# Challenge 3 — Diversity penalty
# Prevents the same artist dominating the top-k results.
# ---------------------------------------------------------------------------

def diversify(
    scored: List[Tuple[Dict, float, str]],
    artist_penalty: float = 1.5,
    genre_penalty: float = 0.5,
) -> List[Tuple[Dict, float, str]]:
    """
    Re-ranks a scored list to reduce artist and genre clustering.

    For each song beyond the first from the same artist, subtracts artist_penalty
    from its score before sorting. Genre penalty is lighter — applied when 3+
    songs from the same genre would appear consecutively.

    Original scores are preserved in the returned tuples (display unchanged).
    The reordering is the only visible effect.
    """
    # Count how many times each artist/genre has appeared so far in the output
    seen_artists: Dict[str, int] = {}
    seen_genres:  Dict[str, int] = {}

    adjusted = []
    for song, score, explanation in scored:
        artist = song["artist"]
        genre  = song["genre"]

        penalty = 0.0
        if seen_artists.get(artist, 0) >= 1:
            penalty += artist_penalty
        if seen_genres.get(genre, 0) >= 2:
            penalty += genre_penalty

        adjusted.append((song, score - penalty, score, explanation))

        seen_artists[artist] = seen_artists.get(artist, 0) + 1
        seen_genres[genre]   = seen_genres.get(genre, 0) + 1

    adjusted.sort(key=lambda x: x[1], reverse=True)
    # Return original scores so the displayed score is always honest
    return [(song, orig_score, explanation) for song, _, orig_score, explanation in adjusted]


# ---------------------------------------------------------------------------
# Main recommendation entry point
# ---------------------------------------------------------------------------

def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    weights: Optional[Dict[str, float]] = None,
    mode: str = "default",
    diversity: bool = False,
    artist_penalty: float = 1.5,
) -> List[Tuple[Dict, float, str]]:
    """
    Score every song, optionally apply diversity re-ranking, return top k.

    Args:
        user_prefs:     user profile dict
        songs:          list of song dicts from load_songs()
        k:              number of results to return
        weights:        explicit weight overrides (takes precedence over mode)
        mode:           named scoring mode from SCORING_MODES (default: "default")
        diversity:      if True, apply artist/genre diversity penalty before top-k
        artist_penalty: score deduction for repeat artists (used when diversity=True)
    """
    resolved_weights = weights or SCORING_MODES.get(mode, DEFAULT_WEIGHTS)

    scored = []
    for song in songs:
        song_score, reasons = score_song(user_prefs, song, weights=resolved_weights)
        scored.append((song, song_score, ", ".join(reasons)))

    scored.sort(key=lambda x: x[1], reverse=True)

    if diversity:
        scored = diversify(scored, artist_penalty=artist_penalty)

    return scored[:k]
