# Project 5: Mixtape Bug Hunt Submission

## AI Usage

I used ChatGPT during codebase orientation and debugging. I shared the service files and asked it to explain each module's responsibility, identify relevant call chains, and clarify suspicious Python behavior such as list slicing and weekday values.

I did not rely only on AI output to decide whether a change was correct. I verified the bugs by running the provided tests, inspected the relevant routes and service functions, applied targeted fixes, and reran the tests after each change. For the notification issue, I compared the working playlist notification path with the rating path to confirm the missing architectural step.

---

# Codebase Map

## Main files and responsibilities

### `app.py`

Creates the Flask application, configures SQLAlchemy, initializes the database, and registers the route blueprints.

### `models.py`

Defines the database entities and relationships:

- `User` stores profile information, listening streak, friendships, playlists, ratings, and notifications.
- `Song` stores song metadata, sharing information, tags, ratings, and listening events.
- `ListeningEvent` records when a user listened to a song.
- `Rating` stores a user's score for a song and prevents duplicate ratings through a unique constraint.
- `Playlist` stores playlist metadata.
- `playlist_entries` connects playlists and songs while storing song position, who added it, and when it was added.
- `Notification` stores user notifications and read status.

### `routes/`

The route files parse HTTP requests, call service functions, and format responses.

- `routes/songs.py` handles sharing, searching, retrieving, and rating songs.
- `routes/playlists.py` handles playlist creation and playlist song retrieval.
- `routes/users.py` handles user information, streaks, and notifications.
- `routes/feed.py` handles listening and activity feeds.

### `services/`

The service layer contains the application's business logic.

- `streak_service.py` creates listening events and updates listening streaks.
- `playlist_service.py` creates playlists and returns playlist songs in position order.
- `notification_service.py` saves ratings and creates notifications for song interactions.
- `search_service.py` searches songs by title or artist.
- `feed_service.py` returns recent listening activity from friends.

### `seed_data.py`

Creates sample users, songs, friendships, playlists, ratings, and listening events for local testing.

### `tests/`

Contains automated tests for streak behavior, playlist retrieval, and search behavior.

## Data flow example: rating a song

1. A user sends a request to `POST /songs/<song_id>/rate`.
2. `routes/songs.py` reads the user ID and score from the request.
3. The route calls `notification_service.rate_song()`.
4. `rate_song()` validates that the score is between 1 and 5.
5. It retrieves the song and rating user from the database.
6. It checks whether the user already rated the song.
7. It either creates a new `Rating` or updates the existing rating.
8. If the rater is not the original song sharer, the service creates a `song_rated` notification for the sharer.
9. The service returns the saved rating to the route.

## Architectural patterns noticed

Routes are thin and delegate business logic to service modules. Models define persistence and relationships, while services perform validation, querying, updates, and notification behavior. The bugs were therefore investigated by starting at the relevant route and tracing the call into the corresponding service.

---

# Issue #1 — Listening streak resets on Sunday

## How I reproduced it

I ran:

```bash
pytest tests/test_streaks.py