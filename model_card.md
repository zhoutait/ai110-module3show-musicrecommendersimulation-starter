# Model Card: VibeFinder 1.0

## Goal / Task
The goal of this system is to predict and suggest songs that a user might enjoy based on their stated preferences for genre, mood, and specific audio features. It acts as a content-based recommender simulation to understand how basic recommendation logic functions.

## Data Used
The dataset consists of a small, curated CSV catalog of 20 songs (`data/songs.csv`). The data features categorical attributes (`genre`, `mood`) and numerical attributes (`energy`, `tempo_bpm`, `danceability`, `acousticness` on a 0.0–1.0 scale). The dataset is limited in scope and heavily skewed towards pop and rock genres.

## Algorithm Summary
The system scores each song against a user's taste profile using a weighted logic:
* A direct genre match awards 2.0 points.
* A direct mood match awards 1.0 point.
* Numerical features (energy, danceability, acousticness) award up to 1.0 or 0.5 points based on how close the song's value is to the user's target value.
The songs are then ranked from highest to lowest total score to produce the top recommendations.

## Observed Behavior / Biases
The system exhibits a strong "filter bubble" effect due to the heavy weighting of genre. A song that perfectly matches a user's mood and energy but belongs to a different genre will almost always be outranked by a mediocre match within the user's preferred genre. Additionally, the system over-prioritizes pop and rock because they make up a large portion of the dataset.

## Evaluation Process
The system was stress-tested using five distinct user profiles:
* High-Energy Pop Lover
* Chill Lofi Listener
* Deep Intense Rock Fan
* Sad Pop Ballad Seeker
* Electronic Dance Enthusiast

By comparing the outputs for these profiles, it became clear that the scoring logic effectively differentiates between intense, high-energy tracks and chill, acoustic tracks. However, the dominance of the genre weight was evident in edge cases where cross-genre recommendations were blocked.

## Intended Use and Non-Intended Use
**Intended Use:** This system is designed as an educational tool to simulate and understand the basic principles of content-based recommendation algorithms and weighted scoring logic.
**Non-Intended Use:** This system should not be used in a production environment or to make real-world recommendations, as its dataset is too small, its features are overly simplistic, and it lacks collaborative filtering or feedback loops to improve accuracy over time.

## Ideas for Improvement
1. **Dynamic Weighting:** Allow the user to adjust the importance of each feature (e.g., a user who cares more about mood than genre could shift the weights).
2. **Larger Dataset:** Integrate with a real API (like Spotify's) to pull thousands of songs for a more realistic and diverse catalog.
3. **Collaborative Filtering:** Add user history data to recommend songs based on what similar users have liked, moving beyond just audio features.

## Personal Reflection
My biggest learning moment during this project was realizing how simple math can create the illusion of complex "understanding." The system doesn't know what "chill" sounds like; it just knows that a low energy score and a high acousticness score match the numerical target for a "chill" profile.

Using AI tools like Copilot helped me brainstorm the scoring logic and quickly generate the diverse song dataset, but I had to double-check the math to ensure the proximity scores were calculating correctly (e.g., `1.0 - abs(gap)`).

I was surprised by how quickly a "filter bubble" forms. By heavily weighting genre, the algorithm became rigid, refusing to suggest great electronic songs to a rock fan, even if the energy and mood matched perfectly. If I extended this project, I would implement a "surprise me" feature that occasionally ignores genre to introduce variety and break the bubble.
