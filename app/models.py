from __future__ import annotations

from datetime import datetime
from typing import Iterable

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from . import db, login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    synopsis = db.Column(db.Text, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.String(20), nullable=True)
    maturity_badge = db.Column(db.String(10), nullable=True)
    runtime = db.Column(db.String(50), nullable=True)
    spotlight_title = db.Column(db.String(120), nullable=True)
    spotlight_tagline = db.Column(db.String(255), nullable=True)
    thumbnail_url = db.Column(db.String(255), nullable=True)
    hero_url = db.Column(db.String(255), nullable=True)
    background_url = db.Column(db.String(255), nullable=True)
    trailer_url = db.Column(db.String(255), nullable=True)
    video_url = db.Column(db.String(255), nullable=True)
    categories = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def category_list(self) -> list[str]:
        if not self.categories:
            return []
        return [cat.strip() for cat in self.categories.split(",") if cat.strip()]


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    if user_id and user_id.isdigit():
        return User.query.get(int(user_id))
    return None


def seed_data() -> None:
    """Create a default admin and demo content when the database is empty."""
    if User.query.count() == 0:
        admin = User(username="admin", email="admin@example.com", is_admin=True)
        admin.set_password("admin123")
        db.session.add(admin)

    if Movie.query.count() == 0:
        demo_movies: Iterable[dict[str, str | int | None]] = [
            {
                "title": "Money Heist: Part 4",
                "synopsis": (
                    "As the Professor races to save Lisbon, members of the crew "
                    "deal with their own crises."
                ),
                "year": 2020,
                "rating": "8.8/10",
                "maturity_badge": "16+",
                "runtime": "4 Parts",
                "spotlight_title": "La Casa de Papel",
                "spotlight_tagline": "No plan survives first contact with reality.",
                "thumbnail_url": "https://source.unsplash.com/480x720/?heist",
                "hero_url": "https://source.unsplash.com/1280x720/?money,heist",
                "background_url": "https://source.unsplash.com/1980x1080/?dark,heist",
                "trailer_url": "https://www.youtube.com/watch?v=p_PJbmrX4uk",
                "video_url": "https://archive.org/download/sample-video-file/mp4/sample_960x540.mp4",
                "categories": "Action, Thriller",
            },
            {
                "title": "The Witcher",
                "synopsis": (
                    "Geralt of Rivia, a solitary monster hunter, struggles to find his "
                    "place in a world."
                ),
                "year": 2019,
                "rating": "8.2/10",
                "maturity_badge": "18+",
                "runtime": "3 Seasons",
                "spotlight_title": "Destiny is a beast.",
                "spotlight_tagline": "Destinies collide in the Continent.",
                "thumbnail_url": "https://source.unsplash.com/480x720/?witcher",
                "hero_url": "https://source.unsplash.com/1280x720/?fantasy,warrior",
                "background_url": "https://source.unsplash.com/1980x1080/?fantasy,dark",
                "trailer_url": "https://www.youtube.com/watch?v=ndl1W4ltcmg",
                "video_url": "https://archive.org/download/BigBuckBunny_328/BigBuckBunny_512kb.mp4",
                "categories": "Fantasy, Drama",
            },
            {
                "title": "Stranger Things",
                "synopsis": (
                    "When a young boy vanishes, a small town uncovers a mystery involving "
                    "secret experiments."
                ),
                "year": 2016,
                "rating": "8.7/10",
                "maturity_badge": "16+",
                "runtime": "4 Seasons",
                "spotlight_title": "The Upside Down awaits.",
                "spotlight_tagline": "Friends don't lie.",
                "thumbnail_url": "https://source.unsplash.com/480x720/?stranger-things",
                "hero_url": "https://source.unsplash.com/1280x720/?neon,forest",
                "background_url": "https://source.unsplash.com/1980x1080/?mystery,neon",
                "trailer_url": "https://www.youtube.com/watch?v=mnd7sFt5c3A",
                "video_url": "https://archive.org/download/ElephantsDream/ed_1024_512kb.mp4",
                "categories": "Sci-Fi, Mystery",
            },
        ]

        for data in demo_movies:
            db.session.add(Movie(**data))

    db.session.commit()
