"""
recommender.py — Core logic for the Music Recommender Simulation.

Provides functions to load song data from CSV, score individual songs
against a user preference profile, and rank a catalog to produce
top-K recommendations.

Supports three scoring modes (Strategy pattern):
  - "genre_first"  : Heavily weights genre + mood match
  - "mood_first"   : Heavily weights mood tag + valence match
  - "energy_first" : Heavily weights energy, tempo, and danceability
"""

import csv


# ---------------------------------------------------------------------------
# New feature: mood tag groups for fuzzy matching
# ---------------------------------------------------------------------------
MOOD_TAG_GROUPS = {
    "euphoric":    {"euphoric", "uplifting"},
    "uplifting":   {"uplifting", "euphoric"},
    "melancholic": {"melancholic"},
    "aggressive":  {"aggressive"},
    "nostalgic":   {"nostalgic"},
    "serene":      {"serene"},
}


def load_songs(filepath: str) -> list[dict]:
    """Load songs from a CSV file and return a list of song dictionaries with typed values."""
    songs = []
    with open(filepath, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = int(row["tempo_bpm"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            # New fields (Challenge 1)
            row["popularity"] = int(row["popularity"])
            row["valence"] = float(row["valence"])
            row["instrumentalness"] = float(row["instrumentalness"])
            # release_decade and mood_tag stay as strings
            songs.append(row)
    return songs


# ---------------------------------------------------------------------------
# Challenge 1 helper: score the five new features
# ---------------------------------------------------------------------------
def _score_advanced_features(user_prefs: dict, song: dict) -> tuple[float, list[str]]:
    """
    Score the five new song attributes added in Challenge 1.

    New scoring rules:
      popularity      — +0.5 if song popularity >= user's min_popularity (default 70)
                        Bonus +0.3 if popularity >= 90 (reward chart-toppers)
      release_decade  — +0.5 if song decade matches user's preferred_decade
      mood_tag        — +1.0 if song mood_tag is in the user's desired mood_tag group
                        +0.5 if it's a related tag (partial match)
      valence         — +0.5 * (1 - |song_valence - target_valence|) proximity score
      instrumentalness— +0.5 if user wants_instrumental and song instrumentalness >= 0.5
                        -0.3 penalty if user wants_instrumental=False and song >= 0.5
    """
    score = 0.0
    reasons = []

    # --- Popularity (+0.0 to +0.8) ---
    min_pop = user_prefs.get("min_popularity", 70)
    if song["popularity"] >= min_pop:
        score += 0.5
        reasons.append(f"popularity ok ({song['popularity']} >= {min_pop}, +0.5)")
        if song["popularity"] >= 90:
            score += 0.3
            reasons.append(f"chart-topper bonus (pop={song['popularity']}, +0.3)")

    # --- Release decade (+0.5) ---
    preferred_decade = user_prefs.get("preferred_decade")
    if preferred_decade and song.get("release_decade") == preferred_decade:
        score += 0.5
        reasons.append(f"era match ({song['release_decade']}, +0.5)")

    # --- Mood tag (+0.5 to +1.0) ---
    desired_tag = user_prefs.get("desired_mood_tag")
    if desired_tag:
        song_tag = song.get("mood_tag", "")
        group = MOOD_TAG_GROUPS.get(desired_tag, {desired_tag})
        if song_tag == desired_tag:
            score += 1.0
            reasons.append(f"mood tag exact match ({song_tag}, +1.0)")
        elif song_tag in group:
            score += 0.5
            reasons.append(f"mood tag related ({song_tag}~{desired_tag}, +0.5)")

    # --- Valence proximity (+0.0 to +0.5) ---
    target_valence = user_prefs.get("target_valence")
    if target_valence is not None:
        valence_gap = abs(song["valence"] - target_valence)
        valence_score = round((1.0 - valence_gap) * 0.5, 3)
        score += valence_score
        reasons.append(f"valence proximity (+{valence_score:.3f})")

    # --- Instrumentalness (+0.5 or -0.3) ---
    wants_instrumental = user_prefs.get("wants_instrumental")
    if wants_instrumental is not None:
        is_instrumental = song["instrumentalness"] >= 0.5
        if wants_instrumental and is_instrumental:
            score += 0.5
            reasons.append(f"instrumental match (+0.5)")
        elif not wants_instrumental and is_instrumental:
            score -= 0.3
            reasons.append(f"instrumental penalty (-0.3)")

    return round(score, 3), reasons


# ---------------------------------------------------------------------------
# Challenge 2: Scoring mode strategies
# ---------------------------------------------------------------------------
def _score_genre_first(user_prefs: dict, song: dict) -> tuple[float, list[str]]:
    """
    Genre-First mode: genre and mood dominate; energy/dance/acoustic are secondary.

    Weights:
      genre match       +3.0  (boosted)
      mood match        +1.5  (boosted)
      energy proximity  +0.5  (reduced)
      danceability      +0.25 (reduced)
      acousticness      +0.25 (reduced)
    """
    score = 0.0
    reasons = []

    if song.get("genre", "").lower() == user_prefs.get("favorite_genre", "").lower():
        score += 3.0
        reasons.append("genre match (+3.0)")

    if song.get("mood", "").lower() == user_prefs.get("favorite_mood", "").lower():
        score += 1.5
        reasons.append("mood match (+1.5)")

    target_energy = user_prefs.get("target_energy", 0.5)
    energy_score = round((1.0 - abs(song["energy"] - target_energy)) * 0.5, 3)
    score += energy_score
    reasons.append(f"energy proximity (+{energy_score:.3f})")

    target_dance = user_prefs.get("target_danceability", 0.5)
    dance_score = round((1.0 - abs(song["danceability"] - target_dance)) * 0.25, 3)
    score += dance_score
    reasons.append(f"danceability proximity (+{dance_score:.3f})")

    target_acoustic = user_prefs.get("target_acousticness", 0.5)
    acoustic_score = round((1.0 - abs(song["acousticness"] - target_acoustic)) * 0.25, 3)
    score += acoustic_score
    reasons.append(f"acousticness proximity (+{acoustic_score:.3f})")

    return round(score, 3), reasons


def _score_mood_first(user_prefs: dict, song: dict) -> tuple[float, list[str]]:
    """
    Mood-First mode: mood tag and valence dominate; genre is secondary.

    Weights:
      mood tag match    +3.0  (new feature, heavily weighted)
      valence proximity +1.5  (new feature, heavily weighted)
      mood match        +1.0
      genre match       +1.0  (reduced)
      energy proximity  +0.5
    """
    score = 0.0
    reasons = []

    desired_tag = user_prefs.get("desired_mood_tag")
    if desired_tag:
        song_tag = song.get("mood_tag", "")
        group = MOOD_TAG_GROUPS.get(desired_tag, {desired_tag})
        if song_tag == desired_tag:
            score += 3.0
            reasons.append(f"mood tag exact match ({song_tag}, +3.0)")
        elif song_tag in group:
            score += 1.5
            reasons.append(f"mood tag related ({song_tag}, +1.5)")

    target_valence = user_prefs.get("target_valence")
    if target_valence is not None:
        valence_score = round((1.0 - abs(song["valence"] - target_valence)) * 1.5, 3)
        score += valence_score
        reasons.append(f"valence proximity (+{valence_score:.3f})")

    if song.get("mood", "").lower() == user_prefs.get("favorite_mood", "").lower():
        score += 1.0
        reasons.append("mood match (+1.0)")

    if song.get("genre", "").lower() == user_prefs.get("favorite_genre", "").lower():
        score += 1.0
        reasons.append("genre match (+1.0)")

    target_energy = user_prefs.get("target_energy", 0.5)
    energy_score = round(1.0 - abs(song["energy"] - target_energy), 3)
    score += energy_score
    reasons.append(f"energy proximity (+{energy_score:.3f})")

    return round(score, 3), reasons


def _score_energy_first(user_prefs: dict, song: dict) -> tuple[float, list[str]]:
    """
    Energy-First mode: energy, tempo, and danceability dominate.

    Weights:
      energy proximity  +2.0  (heavily boosted)
      danceability      +1.5  (heavily boosted)
      tempo proximity   +1.0  (new: rewards BPM closeness)
      genre match       +0.5  (reduced)
      mood match        +0.5  (reduced)
    """
    score = 0.0
    reasons = []

    target_energy = user_prefs.get("target_energy", 0.5)
    energy_score = round((1.0 - abs(song["energy"] - target_energy)) * 2.0, 3)
    score += energy_score
    reasons.append(f"energy proximity (+{energy_score:.3f})")

    target_dance = user_prefs.get("target_danceability", 0.5)
    dance_score = round((1.0 - abs(song["danceability"] - target_dance)) * 1.5, 3)
    score += dance_score
    reasons.append(f"danceability proximity (+{dance_score:.3f})")

    target_bpm = user_prefs.get("target_tempo_bpm", 120)
    bpm_gap_normalized = min(abs(song["tempo_bpm"] - target_bpm) / 100.0, 1.0)
    tempo_score = round((1.0 - bpm_gap_normalized) * 1.0, 3)
    score += tempo_score
    reasons.append(f"tempo proximity (+{tempo_score:.3f})")

    if song.get("genre", "").lower() == user_prefs.get("favorite_genre", "").lower():
        score += 0.5
        reasons.append("genre match (+0.5)")

    if song.get("mood", "").lower() == user_prefs.get("favorite_mood", "").lower():
        score += 0.5
        reasons.append("mood match (+0.5)")

    return round(score, 3), reasons


# Scoring mode registry (Strategy pattern)
SCORING_MODES = {
    "genre_first":  _score_genre_first,
    "mood_first":   _score_mood_first,
    "energy_first": _score_energy_first,
}


def score_song(user_prefs: dict, song: dict, mode: str = "genre_first") -> tuple[float, list[str]]:
    """
    Score a single song against a user preference profile.

    Uses the scoring strategy selected by `mode`:
      "genre_first"  — prioritizes genre and mood match
      "mood_first"   — prioritizes mood tag and valence
      "energy_first" — prioritizes energy, tempo, and danceability

    Always adds advanced feature scores (Challenge 1) on top of the base mode score.
    Returns (total_score, reasons).
    """
    strategy = SCORING_MODES.get(mode, _score_genre_first)
    base_score, base_reasons = strategy(user_prefs, song)
    adv_score, adv_reasons = _score_advanced_features(user_prefs, song)
    return round(base_score + adv_score, 3), base_reasons + adv_reasons


# ---------------------------------------------------------------------------
# Challenge 3: Diversity penalty
# ---------------------------------------------------------------------------
def _apply_diversity_penalty(ranked: list[dict], max_per_artist: int = 2,
                              max_per_genre: int = 3) -> list[dict]:
    """
    Re-rank results by applying a diversity penalty that prevents too many
    songs from the same artist or genre appearing in the top results.

    Rules:
      - An artist already seen >= max_per_artist times gets a -1.0 penalty per extra song.
      - A genre already seen >= max_per_genre times gets a -0.5 penalty per extra song.

    The list is re-sorted after penalties are applied so the final order
    reflects the adjusted scores.
    """
    artist_counts: dict[str, int] = {}
    genre_counts: dict[str, int] = {}

    for rec in ranked:
        artist = rec["artist"]
        genre = rec["genre"]
        penalty = 0.0

        artist_count = artist_counts.get(artist, 0)
        if artist_count >= max_per_artist:
            penalty += 1.0 * (artist_count - max_per_artist + 1)
            rec["reasons"].append(f"artist diversity penalty (-{1.0 * (artist_count - max_per_artist + 1):.1f})")

        genre_count = genre_counts.get(genre, 0)
        if genre_count >= max_per_genre:
            penalty += 0.5 * (genre_count - max_per_genre + 1)
            rec["reasons"].append(f"genre diversity penalty (-{0.5 * (genre_count - max_per_genre + 1):.1f})")

        rec["score"] = round(rec["score"] - penalty, 3)
        artist_counts[artist] = artist_count + 1
        genre_counts[genre] = genre_count + 1

    return sorted(ranked, key=lambda s: s["score"], reverse=True)


def recommend_songs(user_prefs: dict, songs: list[dict], k: int = 5,
                    mode: str = "genre_first", diversity: bool = True) -> list[dict]:
    """
    Rank all songs by score and return the top-k recommendations.

    Args:
        user_prefs: user preference dictionary
        songs:      full song catalog
        k:          number of recommendations to return
        mode:       scoring strategy — "genre_first", "mood_first", or "energy_first"
        diversity:  if True, apply artist/genre diversity penalty (Challenge 3)
    """
    scored = []
    for song in songs:
        total_score, reasons = score_song(user_prefs, song, mode=mode)
        scored.append({
            "title": song["title"],
            "artist": song["artist"],
            "genre": song["genre"],
            "mood": song["mood"],
            "energy": song["energy"],
            "popularity": song["popularity"],
            "release_decade": song["release_decade"],
            "mood_tag": song["mood_tag"],
            "score": total_score,
            "reasons": reasons,
        })

    ranked = sorted(scored, key=lambda s: s["score"], reverse=True)

    if diversity:
        ranked = _apply_diversity_penalty(ranked)

    return ranked[:k]
