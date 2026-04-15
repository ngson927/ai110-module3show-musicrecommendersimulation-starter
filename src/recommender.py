from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

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

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5, weights: Optional[Dict[str, float]] = None) -> List[Song]:
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
            songs.append({
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
            })
    print(f"Loaded songs: {len(songs)}")
    return songs

# ---------------------------------------------------------------------------
# Default weights — edit here to adjust the algorithm recipe globally.
# Max possible score = sum of all weights.
# ---------------------------------------------------------------------------
DEFAULT_WEIGHTS = {
    "energy":       3.5,   # strongest continuous signal — physical intensity
    "mood":         2.5,   # binary match — wrong mood causes instant skip
    "valence":      1.5,   # separates happy-intense from dark-intense
    "genre":        1.5,   # useful anchor, but below mood
    "acousticness": 1.0,   # texture preference — organic vs. electronic
}


def score_song(
    user_prefs: Dict,
    song: Dict,
    weights: Optional[Dict[str, float]] = None,
) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences using the Algorithm Recipe.

    Args:
        user_prefs: user profile dict with keys favorite_genre, favorite_mood,
                    target_energy, target_valence, likes_acoustic.
        song:       song dict from load_songs().
        weights:    optional weight overrides — defaults to DEFAULT_WEIGHTS.
                    Pass a partial dict to override only specific rules.

    Returns:
        (score, reasons)
        score   — float, 0.0 up to sum(weights.values())
        reasons — list of human-readable strings, one per rule that contributed
    """
    w = {**DEFAULT_WEIGHTS, **(weights or {})}
    score = 0.0
    reasons = []

    # Rule 1 — Energy proximity
    # Rewards songs whose energy is closest to the user's target, not just the loudest.
    energy_pts = round(w["energy"] * (1 - abs(song["energy"] - user_prefs["target_energy"])), 2)
    score += energy_pts
    reasons.append(f"energy ({energy_pts:+.2f}/{w['energy']})")

    # Rule 2 — Mood match (binary)
    if song["mood"] == user_prefs["favorite_mood"]:
        score += w["mood"]
        reasons.append(f"mood match (+{w['mood']:.2f})")

    # Rule 3 — Valence proximity
    # Separates songs with identical energy but different emotional tone.
    target_valence = user_prefs.get("target_valence", 0.5)
    valence_pts = round(w["valence"] * (1 - abs(song["valence"] - target_valence)), 2)
    score += valence_pts
    reasons.append(f"valence ({valence_pts:+.2f}/{w['valence']})")

    # Rule 4 — Genre match (binary)
    if song["genre"] == user_prefs["favorite_genre"]:
        score += w["genre"]
        reasons.append(f"genre match (+{w['genre']:.2f})")

    # Rule 5 — Acousticness match
    # Rewards organic/warm texture if likes_acoustic is True, electronic if False.
    if user_prefs.get("likes_acoustic", False):
        acoustic_pts = round(w["acousticness"] * song["acousticness"], 2)
    else:
        acoustic_pts = round(w["acousticness"] * (1 - song["acousticness"]), 2)
    score += acoustic_pts
    reasons.append(f"acousticness ({acoustic_pts:+.2f}/{w['acousticness']})")

    return round(score, 2), reasons


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    weights: Optional[Dict[str, float]] = None,
) -> List[Tuple[Dict, float, str]]:
    """Score every song, sort descending, return top k as (song, score, explanation)."""
    scored = []
    for song in songs:
        song_score, reasons = score_song(user_prefs, song, weights=weights)
        scored.append((song, song_score, ", ".join(reasons)))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
