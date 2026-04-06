# Music Recommender Simulation

## ℹ️ Project Overview
This project simulates how a basic music recommendation system works by designing a modular architecture in Python that transforms song data and "taste profiles" into personalized suggestions. It demonstrates the difference between collaborative filtering and content-based filtering by implementing a pure content-based approach using song attributes like genre, mood, energy, danceability, and acousticness.

## How The System Works

Real-world recommendation systems at scale (like Spotify or TikTok) often use a mix of collaborative filtering (analyzing what similar users listen to) and content-based filtering (analyzing the audio features of the songs themselves). They process massive amounts of data, including user behavior (skips, likes, playlist additions) and raw audio analysis.

This simulation prioritizes a **content-based approach**. It scores a catalog of songs against a specific "User Profile" to find the closest match. The system will prioritize genre and mood as the strongest indicators of preference, while using numerical features (energy, danceability, acousticness) to fine-tune the ranking.

### Algorithm Recipe
The recommender uses a weighted scoring logic to judge every song in the catalog:
* **+2.0 points** for a direct Genre match.
* **+1.0 point** for a direct Mood match.
* **Up to +1.0 point** based on Energy proximity (calculated as `1.0 - |song_energy - target_energy|`).
* **Up to +0.5 points** based on Danceability proximity.
* **Up to +0.5 points** based on Acousticness proximity.

*Potential Bias Note:* Because genre is weighted so heavily (2.0 points), this system might over-prioritize genre matching, potentially ignoring great songs that perfectly match the user's mood and energy preferences but happen to be classified under a different genre.

## Features Used
* **Song Object:** `title`, `artist`, `genre`, `mood`, `energy`, `tempo_bpm`, `danceability`, `acousticness`.
* **User Profile:** `favorite_genre`, `favorite_mood`, `target_energy`, `target_danceability`, `target_acousticness`.

## Running the Simulation
To run the simulation and see the recommendations for various profiles:
```bash
python -m src.main
```

### Example Output
![CLI Output Screenshot Placeholder](cli_output.txt)
*(Note: A text capture of the CLI output is available in `cli_output.txt`)*
