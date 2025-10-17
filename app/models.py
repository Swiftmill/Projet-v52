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
    is_series = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    episodes = db.relationship(
        "Episode",
        backref="movie",
        cascade="all, delete-orphan",
    )

    def category_list(self) -> list[str]:
        if not self.categories:
            return []
        return [cat.strip() for cat in self.categories.split(",") if cat.strip()]

    @property
    def primary_video_url(self) -> str | None:
        if self.video_url:
            return self.video_url
        if self.episodes:
            first_episode = sorted(
                self.episodes,
                key=lambda ep: (ep.season_number, ep.episode_number),
            )[0]
            return first_episode.video_url
        return None


class Episode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id", ondelete="CASCADE"), nullable=False)
    season_number = db.Column(db.Integer, default=1, nullable=False)
    episode_number = db.Column(db.Integer, default=1, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    synopsis = db.Column(db.Text, nullable=True)
    runtime = db.Column(db.String(50), nullable=True)
    video_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint(
            "movie_id",
            "season_number",
            "episode_number",
            name="uq_episode_movie_season_number",
        ),
    )

    def label(self) -> str:
        return f"S{self.season_number:02d}E{self.episode_number:02d}"


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
        demo_movies: Iterable[dict[str, str | int | None | bool]] = [
            {
                "title": "Money Heist: Part 4",
                "synopsis": (
                    "As the Professor races to save Lisbon, members of the crew "
                    "deal with their own crises."
                ),
                "year": 2020,
                "rating": "8.8/10",
                "maturity_badge": "16+",
                "runtime": "4 Parties",
                "spotlight_title": "La Casa de Papel",
                "spotlight_tagline": "No plan survives first contact with reality.",
                "thumbnail_url": "https://source.unsplash.com/480x720/?heist",
                "hero_url": "https://source.unsplash.com/1280x720/?money,heist",
                "background_url": "https://source.unsplash.com/1980x1080/?dark,heist",
                "trailer_url": "https://www.youtube.com/watch?v=p_PJbmrX4uk",
                "categories": "Action, Thriller",
                "is_series": True,
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
                "is_series": False,
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
                "categories": "Sci-Fi, Mystery",
                "is_series": True,
            },
        ]

        for data in demo_movies:
            episodes_data = []
            if data.get("is_series"):
                if data["title"] == "Money Heist: Part 4":
                    episodes_data = [
                        {
                            "season_number": 4,
                            "episode_number": 1,
                            "title": "Game Over",
                            "runtime": "52 min",
                            "video_url": "https://archive.org/download/sample-video-file/mp4/sample_960x540.mp4",
                        },
                        {
                            "season_number": 4,
                            "episode_number": 2,
                            "title": "La conquête de l'or",
                            "runtime": "48 min",
                            "video_url": "https://archive.org/download/ElephantsDream/ed_1024_512kb.mp4",
                        },
                    ]
                elif data["title"] == "Stranger Things":
                    episodes_data = [
                        {
                            "season_number": 4,
                            "episode_number": 1,
                            "title": "The Hellfire Club",
                            "runtime": "1h 16",
                            "video_url": "https://archive.org/download/BigBuckBunny_328/BigBuckBunny_512kb.mp4",
                        },
                        {
                            "season_number": 4,
                            "episode_number": 2,
                            "title": "Vecna's Curse",
                            "runtime": "1h 18",
                            "video_url": "https://archive.org/download/Sintel/sintel-2048-surround.mp4",
                        },
                    ]

            movie_data = {key: value for key, value in data.items() if key != "is_series"}
            movie = Movie(is_series=bool(data.get("is_series")), **movie_data)
            db.session.add(movie)
            db.session.flush()

            for episode in episodes_data:
                db.session.add(Episode(movie_id=movie.id, **episode))

    db.session.commit()
