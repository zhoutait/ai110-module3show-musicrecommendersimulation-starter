"""
main.py — CLI entry point for the Music Recommender Simulation.

Loads song data, defines multiple user preference profiles, and
outputs ranked recommendations using all three scoring modes with
a formatted ASCII summary table (Challenge 4).
"""

import os

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False

from src.recommender import load_songs, recommend_songs


def _truncate(text: str, width: int) -> str:
    return text if len(text) <= width else text[:width - 1] + "…"


def print_recommendations_table(profile_name: str, mode: str, recommendations: list[dict]) -> None:
    """
    Challenge 4: Print recommendations as a formatted table.
    Uses tabulate if available, otherwise falls back to clean ASCII formatting.
    Each row includes the score and the top reasons explaining it.
    """
    headers = ["#", "Title", "Artist", "Genre", "Mood Tag", "Pop", "Era", "Score", "Top Reasons"]
    rows = []
    for i, rec in enumerate(recommendations, start=1):
        top_reasons = "; ".join(rec["reasons"][:3])  # show top 3 reasons
        rows.append([
            i,
            _truncate(rec["title"], 22),
            _truncate(rec["artist"], 16),
            rec["genre"],
            rec.get("mood_tag", ""),
            rec.get("popularity", ""),
            rec.get("release_decade", ""),
            f"{rec['score']:.3f}",
            _truncate(top_reasons, 55),
        ])

    mode_label = {"genre_first": "Genre-First", "mood_first": "Mood-First",
                  "energy_first": "Energy-Focused"}.get(mode, mode)
    print(f"\n  Profile : {profile_name}")
    print(f"  Mode    : {mode_label}")
    print()

    if HAS_TABULATE:
        print(tabulate(rows, headers=headers, tablefmt="rounded_outline"))
    else:
        # ASCII fallback
        col_widths = [max(len(str(r[i])) for r in [headers] + rows) for i in range(len(headers))]
        sep = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
        def fmt_row(row):
            return "| " + " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)) + " |"
        print(sep)
        print(fmt_row(headers))
        print(sep)
        for row in rows:
            print(fmt_row(row))
        print(sep)
    print()


def main():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")
    songs = load_songs(data_path)
    print(f"\n✅ Loaded {len(songs)} songs from catalog.")
    if not HAS_TABULATE:
        print("   (Install 'tabulate' for prettier tables: pip install tabulate)")

    # -----------------------------------------------------------------------
    # User profiles — each specifies base prefs + new Challenge 1 fields
    # -----------------------------------------------------------------------
    profiles = [
        {
            "name": "High-Energy Pop Lover",
            "favorite_genre": "pop",
            "favorite_mood": "happy",
            "target_energy": 0.85,
            "target_danceability": 0.85,
            "target_acousticness": 0.10,
            # Challenge 1 new fields
            "min_popularity": 85,
            "preferred_decade": "2020s",
            "desired_mood_tag": "euphoric",
            "target_valence": 0.90,
            "wants_instrumental": False,
        },
        {
            "name": "Chill Lofi Listener",
            "favorite_genre": "lofi",
            "favorite_mood": "chill",
            "target_energy": 0.25,
            "target_danceability": 0.60,
            "target_acousticness": 0.90,
            "min_popularity": 60,
            "preferred_decade": "2010s",
            "desired_mood_tag": "serene",
            "target_valence": 0.30,
            "wants_instrumental": True,
        },
        {
            "name": "Deep Intense Rock Fan",
            "favorite_genre": "rock",
            "favorite_mood": "intense",
            "target_energy": 0.95,
            "target_danceability": 0.50,
            "target_acousticness": 0.05,
            "min_popularity": 80,
            "preferred_decade": "1990s",
            "desired_mood_tag": "aggressive",
            "target_valence": 0.40,
            "wants_instrumental": False,
        },
        {
            "name": "Sad Pop Ballad Seeker",
            "favorite_genre": "pop",
            "favorite_mood": "sad",
            "target_energy": 0.35,
            "target_danceability": 0.40,
            "target_acousticness": 0.80,
            "min_popularity": 80,
            "preferred_decade": "2010s",
            "desired_mood_tag": "melancholic",
            "target_valence": 0.20,
            "wants_instrumental": False,
        },
        {
            "name": "Electronic Dance Enthusiast",
            "favorite_genre": "electronic",
            "favorite_mood": "intense",
            "target_energy": 0.90,
            "target_danceability": 0.80,
            "target_acousticness": 0.05,
            "target_tempo_bpm": 130,
            "min_popularity": 75,
            "preferred_decade": "2000s",
            "desired_mood_tag": "aggressive",
            "target_valence": 0.60,
            "wants_instrumental": False,
        },
    ]

    # Challenge 2: run each profile through all three scoring modes
    scoring_modes = ["genre_first", "mood_first", "energy_first"]

    for profile in profiles:
        print("\n" + "=" * 80)
        for mode in scoring_modes:
            recs = recommend_songs(profile, songs, k=5, mode=mode, diversity=True)
            print_recommendations_table(profile["name"], mode, recs)


if __name__ == "__main__":
    main()
