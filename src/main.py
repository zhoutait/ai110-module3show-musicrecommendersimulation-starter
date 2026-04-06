"""
main.py — CLI entry point for the Music Recommender Simulation.

Loads song data, defines multiple user preference profiles, and
outputs ranked recommendations with scores and explanations.
"""

import os
from src.recommender import load_songs, recommend_songs


def main():
    # Load the song catalog
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")
    songs = load_songs(data_path)
    print(f"✅ Loaded {len(songs)} songs from catalog.\n")
    print("=" * 80)

    # Define multiple user preference profiles
    profiles = [
        {
            "name": "High-Energy Pop Lover",
            "favorite_genre": "pop",
            "favorite_mood": "happy",
            "target_energy": 0.85,
            "target_danceability": 0.85,
            "target_acousticness": 0.10,
        },
        {
            "name": "Chill Lofi Listener",
            "favorite_genre": "lofi",
            "favorite_mood": "chill",
            "target_energy": 0.25,
            "target_danceability": 0.60,
            "target_acousticness": 0.90,
        },
        {
            "name": "Deep Intense Rock Fan",
            "favorite_genre": "rock",
            "favorite_mood": "intense",
            "target_energy": 0.95,
            "target_danceability": 0.50,
            "target_acousticness": 0.05,
        },
        {
            "name": "Sad Pop Ballad Seeker",
            "favorite_genre": "pop",
            "favorite_mood": "sad",
            "target_energy": 0.35,
            "target_danceability": 0.40,
            "target_acousticness": 0.80,
        },
        {
            "name": "Electronic Dance Enthusiast",
            "favorite_genre": "electronic",
            "favorite_mood": "intense",
            "target_energy": 0.90,
            "target_danceability": 0.80,
            "target_acousticness": 0.05,
        },
    ]

    # Generate recommendations for each profile
    for profile in profiles:
        print(f"\n🎵 Profile: {profile['name']}")
        print(f"   Genre: {profile['favorite_genre']} | Mood: {profile['favorite_mood']} | Energy: {profile['target_energy']}")
        print("-" * 80)

        recommendations = recommend_songs(profile, songs, k=5)

        for i, rec in enumerate(recommendations, start=1):
            print(f"{i}. {rec['title']} — {rec['artist']}")
            print(f"   Genre: {rec['genre']} | Mood: {rec['mood']} | Energy: {rec['energy']}")
            print(f"   Score: {rec['score']:.3f}")
            print(f"   Reasons: {', '.join(rec['reasons'])}")
            print()

        print("=" * 80)


if __name__ == "__main__":
    main()
