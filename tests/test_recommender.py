import os
import pytest
from src.recommender import load_songs, score_song, recommend_songs, _apply_diversity_penalty

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_SONGS = [
    {
        "title": "Test Pop Track",
        "artist": "Artist A",
        "genre": "pop",
        "mood": "happy",
        "energy": 0.80,
        "tempo_bpm": 120,
        "danceability": 0.80,
        "acousticness": 0.10,
        "popularity": 88,
        "release_decade": "2020s",
        "mood_tag": "euphoric",
        "valence": 0.90,
        "instrumentalness": 0.00,
    },
    {
        "title": "Chill Lofi Loop",
        "artist": "Artist B",
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.25,
        "tempo_bpm": 85,
        "danceability": 0.60,
        "acousticness": 0.90,
        "popularity": 70,
        "release_decade": "2010s",
        "mood_tag": "serene",
        "valence": 0.35,
        "instrumentalness": 0.85,
    },
    {
        "title": "Rock Anthem",
        "artist": "Artist C",
        "genre": "rock",
        "mood": "intense",
        "energy": 0.95,
        "tempo_bpm": 130,
        "danceability": 0.50,
        "acousticness": 0.02,
        "popularity": 85,
        "release_decade": "1990s",
        "mood_tag": "aggressive",
        "valence": 0.40,
        "instrumentalness": 0.00,
    },
]

POP_USER = {
    "favorite_genre": "pop",
    "favorite_mood": "happy",
    "target_energy": 0.85,
    "target_danceability": 0.85,
    "target_acousticness": 0.10,
    "min_popularity": 80,
    "preferred_decade": "2020s",
    "desired_mood_tag": "euphoric",
    "target_valence": 0.90,
    "wants_instrumental": False,
}


# ---------------------------------------------------------------------------
# Challenge 1: Advanced feature scoring
# ---------------------------------------------------------------------------

def test_score_song_genre_match_increases_score():
    score, reasons = score_song(POP_USER, SAMPLE_SONGS[0], mode="genre_first")
    reason_text = " ".join(reasons)
    assert score > 0
    assert "genre match" in reason_text


def test_score_song_popularity_bonus():
    score, reasons = score_song(POP_USER, SAMPLE_SONGS[0], mode="genre_first")
    reason_text = " ".join(reasons)
    assert "popularity ok" in reason_text


def test_score_song_chart_topper_bonus():
    song = dict(SAMPLE_SONGS[0], popularity=92)
    score, reasons = score_song(POP_USER, song, mode="genre_first")
    reason_text = " ".join(reasons)
    assert "chart-topper bonus" in reason_text


def test_score_song_era_match():
    score, reasons = score_song(POP_USER, SAMPLE_SONGS[0], mode="genre_first")
    reason_text = " ".join(reasons)
    assert "era match" in reason_text


def test_score_song_mood_tag_exact_match():
    score, reasons = score_song(POP_USER, SAMPLE_SONGS[0], mode="genre_first")
    reason_text = " ".join(reasons)
    assert "mood tag exact match" in reason_text


def test_score_song_instrumental_penalty():
    # Chill lofi song has instrumentalness=0.85 but user wants_instrumental=False
    user = dict(POP_USER, wants_instrumental=False)
    score, reasons = score_song(user, SAMPLE_SONGS[1], mode="genre_first")
    reason_text = " ".join(reasons)
    assert "instrumental penalty" in reason_text


def test_score_song_instrumental_reward():
    user = dict(POP_USER, favorite_genre="lofi", wants_instrumental=True)
    score, reasons = score_song(user, SAMPLE_SONGS[1], mode="genre_first")
    reason_text = " ".join(reasons)
    assert "instrumental match" in reason_text


# ---------------------------------------------------------------------------
# Challenge 2: Scoring modes
# ---------------------------------------------------------------------------

def test_recommend_returns_k_results():
    results = recommend_songs(POP_USER, SAMPLE_SONGS, k=2, mode="genre_first", diversity=False)
    assert len(results) == 2


def test_genre_first_mode_prefers_genre_match():
    results = recommend_songs(POP_USER, SAMPLE_SONGS, k=3, mode="genre_first", diversity=False)
    assert results[0]["genre"] == "pop"


def test_mood_first_mode_uses_mood_tag():
    results = recommend_songs(POP_USER, SAMPLE_SONGS, k=3, mode="mood_first", diversity=False)
    # Top result should have euphoric mood_tag since user desires it
    assert results[0]["mood_tag"] == "euphoric"


def test_energy_first_mode_ranks_by_energy():
    # Use a neutral user with no decade/mood-tag/popularity prefs to isolate energy ranking
    energy_user = {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.95,
        "target_danceability": 0.50,
        "target_acousticness": 0.02,
        "target_tempo_bpm": 130,
    }
    results = recommend_songs(energy_user, SAMPLE_SONGS, k=3, mode="energy_first", diversity=False)
    # Rock anthem (energy=0.95) matches target_energy exactly and gets genre+mood bonus
    assert results[0]["title"] == "Rock Anthem"


def test_all_modes_return_valid_results():
    for mode in ["genre_first", "mood_first", "energy_first"]:
        results = recommend_songs(POP_USER, SAMPLE_SONGS, k=2, mode=mode, diversity=False)
        assert len(results) == 2
        assert all("score" in r for r in results)
        assert all("reasons" in r for r in results)


def test_results_sorted_descending_by_score():
    results = recommend_songs(POP_USER, SAMPLE_SONGS, k=3, mode="genre_first", diversity=False)
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


# ---------------------------------------------------------------------------
# Challenge 3: Diversity penalty
# ---------------------------------------------------------------------------

def test_diversity_penalty_applied_for_repeated_artist():
    # Build a list where Artist A appears 3 times
    songs = [
        dict(SAMPLE_SONGS[0], title=f"Song {i}", score=5.0 - i * 0.1,
             reasons=[], artist="Artist A")
        for i in range(3)
    ]
    penalized = _apply_diversity_penalty(songs, max_per_artist=2)
    # Third song from Artist A should have a lower score than original
    artist_a_songs = [s for s in penalized if s["artist"] == "Artist A"]
    assert any("artist diversity penalty" in " ".join(s["reasons"]) for s in artist_a_songs)


def test_diversity_recommend_limits_same_artist():
    # All songs same artist — diversity should penalize 3rd+
    same_artist_songs = [dict(s, artist="Same Guy") for s in SAMPLE_SONGS]
    results = recommend_songs(POP_USER, same_artist_songs, k=3, mode="genre_first", diversity=True)
    assert len(results) == 3  # still returns k results


def test_explain_recommendation_returns_non_empty_string():
    results = recommend_songs(POP_USER, SAMPLE_SONGS, k=1, mode="genre_first", diversity=False)
    explanation = ", ".join(results[0]["reasons"])
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# ---------------------------------------------------------------------------
# Challenge 4: load_songs reads new columns
# ---------------------------------------------------------------------------

def test_load_songs_includes_new_columns():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")
    songs = load_songs(data_path)
    assert len(songs) > 0
    first = songs[0]
    assert "popularity" in first
    assert "release_decade" in first
    assert "mood_tag" in first
    assert "valence" in first
    assert "instrumentalness" in first
    assert isinstance(first["popularity"], int)
    assert isinstance(first["valence"], float)
