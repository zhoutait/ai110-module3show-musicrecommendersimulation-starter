"""
recommender.py — Core logic for the Music Recommender Simulation.

Provides functions to load song data from CSV, score individual songs
against a user preference profile, and rank a catalog to produce
top-K recommendations.
"""

import csv
import os


def load_songs(filepath: str) -> list[dict]:
    """Load songs from a CSV file and return a list of song dictionaries with typed values."""
    songs = []
    with open(filepath, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Convert numerical fields to appropriate Python types
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = int(row["tempo_bpm"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
    return songs


def score_song(user_prefs: dict, song: dict) -> tuple[float, list[str]]:
    """
    Score a single song against a user preference profile.

    Scoring Algorithm Recipe:
      +2.0 points  — genre match
      +1.0 point   — mood match
      +1.0 point   — energy proximity  (1 - |song_energy - target_energy|)
      +0.5 points  — danceability proximity (scaled)
      +0.5 points  — acousticness proximity (scaled)

    Returns a tuple of (total_score, reasons) where reasons is a list of
    human-readable strings explaining each contribution to the score.
    """
    score = 0.0
    reasons = []

    # --- Genre match (+2.0) ---
    if song.get("genre", "").lower() == user_prefs.get("favorite_genre", "").lower():
        score += 2.0
        reasons.append("genre match (+2.0)")

    # --- Mood match (+1.0) ---
    if song.get("mood", "").lower() == user_prefs.get("favorite_mood", "").lower():
        score += 1.0
        reasons.append("mood match (+1.0)")

    # --- Energy proximity (+0.0 to +1.0) ---
    target_energy = user_prefs.get("target_energy", 0.5)
    energy_gap = abs(song["energy"] - target_energy)
    energy_score = round(1.0 - energy_gap, 3)
    score += energy_score
    reasons.append(f"energy proximity (+{energy_score:.3f})")

    # --- Danceability proximity (+0.0 to +0.5) ---
    target_dance = user_prefs.get("target_danceability", 0.5)
    dance_gap = abs(song["danceability"] - target_dance)
    dance_score = round((1.0 - dance_gap) * 0.5, 3)
    score += dance_score
    reasons.append(f"danceability proximity (+{dance_score:.3f})")

    # --- Acousticness proximity (+0.0 to +0.5) ---
    target_acoustic = user_prefs.get("target_acousticness", 0.5)
    acoustic_gap = abs(song["acousticness"] - target_acoustic)
    acoustic_score = round((1.0 - acoustic_gap) * 0.5, 3)
    score += acoustic_score
    reasons.append(f"acousticness proximity (+{acoustic_score:.3f})")

    return round(score, 3), reasons


def recommend_songs(user_prefs: dict, songs: list[dict], k: int = 5) -> list[dict]:
    """
    Rank all songs by score and return the top-k recommendations.

    Uses score_song as the judge for every song in the catalog, then
    sorts the results from highest to lowest score using sorted() so
    the original list is not mutated.
    """
    scored = []
    for song in songs:
        total_score, reasons = score_song(user_prefs, song)
        scored.append({
            "title": song["title"],
            "artist": song["artist"],
            "genre": song["genre"],
            "mood": song["mood"],
            "energy": song["energy"],
            "score": total_score,
            "reasons": reasons,
        })

    # sorted() returns a new list; the original catalog is preserved
    ranked = sorted(scored, key=lambda s: s["score"], reverse=True)
    return ranked[:k]
