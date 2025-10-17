from __future__ import annotations

from collections import defaultdict

from flask import Blueprint, abort, render_template, request

from .models import Movie

main_bp = Blueprint("main", __name__)


@main_bp.app_context_processor
def inject_categories():
    categories = defaultdict(list)
    for movie in Movie.query.order_by(Movie.created_at.desc()).all():
        for category in movie.category_list():
            categories[category].append(movie)
    return {
        "category_sections": dict(categories),
    }


@main_bp.route("/")
def home():
    spotlight = Movie.query.order_by(Movie.created_at.desc()).first()
    new_releases = Movie.query.order_by(Movie.created_at.desc()).limit(8).all()
    trending = Movie.query.order_by(Movie.rating.desc()).limit(8).all()
    return render_template(
        "index.html",
        spotlight=spotlight,
        new_releases=new_releases,
        trending=trending,
    )


@main_bp.route("/movie/<int:movie_id>")
def movie_detail(movie_id: int):
    movie = Movie.query.get(movie_id)
    if not movie:
        abort(404)
    related = Movie.query.filter(Movie.id != movie.id).limit(6).all()
    episodes_by_season: dict[int, list] = {}
    if movie.is_series:
        season_map = defaultdict(list)
        for episode in movie.episodes:
            season_map[episode.season_number].append(episode)
        episodes_by_season = dict(sorted(season_map.items()))
        for episodes in episodes_by_season.values():
            episodes.sort(key=lambda ep: ep.episode_number)

    return render_template(
        "movie_detail.html",
        movie=movie,
        related=related,
        primary_video=movie.primary_video_url,
        episodes_by_season=episodes_by_season,
    )


@main_bp.route("/search")
def search():
    query = request.args.get("q", "").strip()
    results = []
    if query:
        like = f"%{query}%"
        results = Movie.query.filter(Movie.title.ilike(like)).order_by(Movie.title).all()
    return render_template("search.html", query=query, results=results)
