# Reflection: Evaluation Comparisons

## System Evaluation Process

During the evaluation phase, I tested the recommender against five distinct user profiles:
1. High-Energy Pop Lover
2. Chill Lofi Listener
3. Deep Intense Rock Fan
4. Sad Pop Ballad Seeker
5. Electronic Dance Enthusiast

By comparing the recommendations for these profiles, I gained insight into how the scoring logic interprets the dataset and how the features interact.

### High-Energy Pop Lover vs. Chill Lofi Listener
* **What changed:** The pop profile prioritized high energy and high danceability tracks like "Blinding Lights" and "Levitating". The lofi profile shifted completely towards low energy, high acousticness tracks like "lofi hip hop radio" and "Weightless".
* **Why it makes sense:** The scoring logic correctly penalized the energy gap for the lofi profile, ensuring that intense pop songs scored poorly. The high acousticness target (0.90) for the lofi profile also helped elevate ambient tracks, demonstrating that the numerical proximity scores are working as intended to differentiate the "vibe" of the songs.

### Deep Intense Rock Fan vs. Electronic Dance Enthusiast
* **What changed:** Both profiles prefer high energy and intense moods, but the genre targets differ (rock vs. electronic). The rock fan was recommended "Enter Sandman" and "Smells Like Teen Spirit", while the electronic fan was recommended "Sandstorm" and "Midnight City".
* **Why it makes sense:** This pair highlights the dominance of the +2.0 genre weight. Because the energy and mood targets were similar (both high energy, intense), the primary differentiator was the genre match. This confirms that the system is functioning as a strict content-based filter, heavily favoring the specified genre even when cross-genre tracks might have similar audio features.

### Sad Pop Ballad Seeker vs. High-Energy Pop Lover
* **What changed:** Both profiles prefer pop music, but their mood and energy targets are opposite. The ballad seeker received recommendations for "Someone Like You" and "Lovely", while the high-energy lover received "Blinding Lights" and "Levitating".
* **Why it makes sense:** Since the genre match (+2.0) applied equally to both profiles for all pop songs, the ranking was entirely determined by the mood match (+1.0) and the numerical proximity scores. This shows that the secondary features (mood, energy, danceability, acousticness) are effectively breaking ties within a single genre, allowing the system to distinguish between a sad, acoustic pop song and a happy, energetic pop song.

## Final Thoughts
The evaluation process confirmed that the "Algorithm Recipe" is fundamentally sound for a simple content-based recommender. The +2.0 weight for genre acts as a strong primary filter, while the mood and numerical features provide the necessary nuance to rank songs within that genre accurately.

However, the system's reliance on the genre weight also creates a rigid "filter bubble." If a user wants high-energy music, the system will rarely recommend an electronic song to a rock fan, even if the track perfectly matches their energy preference. This highlights a key limitation of simple content-based systems: they struggle to surprise users with cross-genre discoveries.
