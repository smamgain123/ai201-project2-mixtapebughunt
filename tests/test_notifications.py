from app import create_app, db
from models import User, Song, Notification
from services.notification_service import rate_song


app = create_app()

def test_rating_creates_notification():
    with app.app_context():
        db.drop_all()
        db.create_all()

        owner = User(
            username="owner",
            email="owner@test.com"
        )

        rater = User(
            username="rater",
            email="rater@test.com"
        )

        db.session.add_all([owner, rater])
        db.session.commit()

        song = Song(
            title="Regression Song",
            artist="Test Artist",
            shared_by=owner.id,
        )

        db.session.add(song)
        db.session.commit()

        rate_song(rater.id, song.id, 5)

        notification = (
            db.session.query(Notification)
            .filter_by(
                user_id=owner.id,
                notification_type="song_rated",
            )
            .first()
        )

        assert notification is not None
        assert "Regression Song" in notification.body
        assert "rater" in notification.body