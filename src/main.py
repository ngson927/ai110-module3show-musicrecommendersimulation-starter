"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

    # --- User Profiles ---
    # Switch between these to test different recommendation scenarios.

    # Profile A: Pop/Happy — upbeat pop, high energy, not acoustic (DEFAULT)
    user_prefs = {
        "favorite_genre": "pop",
        "favorite_mood":  "happy",
        "target_energy":  0.80,
        "target_valence": 0.80,
        "likes_acoustic": False,
    }

    # Profile B: Workout — high energy, intense rock, no acoustic
    # user_prefs = {
    #     "favorite_genre": "rock",
    #     "favorite_mood":  "intense",
    #     "target_energy":  0.90,
    #     "target_valence": 0.50,
    #     "likes_acoustic": False,
    # }

    # Profile C: Study session — low energy, focused lofi, acoustic
    # user_prefs = {
    #     "favorite_genre": "lofi",
    #     "favorite_mood":  "focused",
    #     "target_energy":  0.40,
    #     "target_valence": 0.60,
    #     "likes_acoustic": True,
    # }

    # Profile D: Late night drive — mid energy, moody synthwave, electronic
    # user_prefs = {
    #     "favorite_genre": "synthwave",
    #     "favorite_mood":  "moody",
    #     "target_energy":  0.75,
    #     "target_valence": 0.45,
    #     "likes_acoustic": False,
    # }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    # --- Output formatting ---
    divider = "-" * 52

    print()
    print("=" * 52)
    print("  MUSIC RECOMMENDER — TOP 5 PICKS")
    print("=" * 52)
    print(f"  Genre   : {user_prefs['favorite_genre']}")
    print(f"  Mood    : {user_prefs['favorite_mood']}")
    print(f"  Energy  : {user_prefs['target_energy']}")
    print(f"  Valence : {user_prefs['target_valence']}")
    print(f"  Acoustic: {'yes' if user_prefs['likes_acoustic'] else 'no'}")
    print("=" * 52)
    print()

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"  #{rank}  {song['title']}  —  {song['artist']}")
        print(f"       Score : {score:.2f} / 10.00")
        print(f"       Genre : {song['genre']}  |  Mood: {song['mood']}")
        print(f"       Why   : {explanation}")
        print(f"  {divider}")
    print()


if __name__ == "__main__":
    main()
