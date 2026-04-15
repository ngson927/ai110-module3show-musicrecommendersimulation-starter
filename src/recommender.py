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

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Score all songs against the user profile and return the top k sorted by score."""
        user_dict = asdict(user)
        scored = sorted(
            self.songs,
            key=lambda s: score_song(user_dict, asdict(s))[0],
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

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences using the Algorithm Recipe.

    Returns:
        (score, reasons)
        score   — float from 0.0 to 10.0
        reasons — list of human-readable strings explaining each point contribution
    """
    score = 0.0
    reasons = []

    # Rule 1 — Energy proximity (max 3.5 pts)
    # Rewards songs whose energy is closest to the user's target, not just the loudest.
    energy_pts = round(3.5 * (1 - abs(song["energy"] - user_prefs["target_energy"])), 2)
    score += energy_pts
    reasons.append(f"energy proximity ({energy_pts:+.2f})")

    # Rule 2 — Mood match (max 2.5 pts)
    # Binary: full points for an exact match, zero otherwise.
    if song["mood"] == user_prefs["favorite_mood"]:
        score += 2.5
        reasons.append("mood match (+2.50)")

    # Rule 3 — Valence proximity (max 1.5 pts)
    # Separates songs with identical energy but different emotional tone.
    target_valence = user_prefs.get("target_valence", 0.5)
    valence_pts = round(1.5 * (1 - abs(song["valence"] - target_valence)), 2)
    score += valence_pts
    reasons.append(f"valence proximity ({valence_pts:+.2f})")

    # Rule 4 — Genre match (max 1.5 pts)
    # Binary: useful anchor, but weighted below mood.
    if song["genre"] == user_prefs["favorite_genre"]:
        score += 1.5
        reasons.append("genre match (+1.50)")

    # Rule 5 — Acousticness match (max 1.0 pt)
    # Rewards organic/warm texture if likes_acoustic is True, electronic if False.
    if user_prefs.get("likes_acoustic", False):
        acoustic_pts = round(song["acousticness"], 2)
    else:
        acoustic_pts = round(1.0 - song["acousticness"], 2)
    score += acoustic_pts
    reasons.append(f"acousticness match ({acoustic_pts:+.2f})")

    return round(score, 2), reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = []
    for song in songs:
        song_score, reasons = score_song(user_prefs, song)
        explanation = ", ".join(reasons)
        scored.append((song, song_score, explanation))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
