from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from . import db
from .models import Episode, Movie

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(func):
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Accès réservé à l'équipe StreamBox.", "error")
            return redirect(url_for("auth.login", next=request.url))
        return func(*args, **kwargs)

    return wrapper


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    movies = Movie.query.order_by(Movie.created_at.desc()).all()
    return render_template("admin/dashboard.html", movies=movies)


def _movie_from_request(movie: Movie | None = None) -> Movie:
    if movie is None:
        movie = Movie()

    movie.title = request.form.get("title", "").strip()
    movie.synopsis = request.form.get("synopsis", "").strip()
    movie.year = int(request.form.get("year", 0) or 0)
    movie.rating = request.form.get("rating")
    movie.maturity_badge = request.form.get("maturity_badge")
    movie.runtime = request.form.get("runtime")
    movie.spotlight_title = request.form.get("spotlight_title")
    movie.spotlight_tagline = request.form.get("spotlight_tagline")
    movie.thumbnail_url = request.form.get("thumbnail_url")
    movie.hero_url = request.form.get("hero_url")
    movie.background_url = request.form.get("background_url")
    movie.trailer_url = request.form.get("trailer_url")
    movie.video_url = request.form.get("video_url")
    movie.categories = request.form.get("categories")
    movie.is_series = request.form.get("is_series") == "1"

    return movie


@admin_bp.route("/movies/new", methods=["GET", "POST"])
@login_required
@admin_required
def create_movie():
    movie: Movie | None = None
    if request.method == "POST":
        movie = _movie_from_request()
        if not movie.title or not movie.synopsis:
            flash("Titre et synopsis sont obligatoires.", "error")
        elif not movie.is_series and not movie.video_url:
            flash("Pour un film, l'URL vidéo principale est obligatoire.", "error")
        else:
            db.session.add(movie)
            db.session.commit()
            if movie.is_series:
                flash(
                    "Série enregistrée. Étape suivante : ajoutez vos épisodes.",
                    "success",
                )
                return redirect(
                    url_for("admin.list_episodes", movie_id=movie.id, setup="1")
                )

            flash("Nouveau film ajouté !", "success")
            return redirect(url_for("admin.dashboard"))
    return render_template(
        "admin/movie_form.html",
        movie=movie if request.method == "POST" else None,
    )


@admin_bp.route("/movies/<int:movie_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_movie(movie_id: int):
    movie = Movie.query.get_or_404(movie_id)
    if request.method == "POST":
        movie = _movie_from_request(movie)
        if not movie.title or not movie.synopsis:
            flash("Titre et synopsis sont obligatoires.", "error")
        elif not movie.is_series and not movie.video_url:
            flash("Pour un film, l'URL vidéo principale est obligatoire.", "error")
        else:
            db.session.commit()
            flash("Programme mis à jour.", "success")
            return redirect(url_for("admin.dashboard"))
    return render_template("admin/movie_form.html", movie=movie)


def _episode_from_request(movie: Movie, episode: Episode | None = None) -> Episode:
    if episode is None:
        episode = Episode(movie=movie)

    episode.title = request.form.get("title", "").strip()
    episode.synopsis = request.form.get("synopsis", "").strip() or None
    episode.runtime = request.form.get("runtime", "").strip() or None
    episode.video_url = request.form.get("video_url", "").strip()
    episode.season_number = int(request.form.get("season_number", 1) or 1)
    episode.episode_number = int(request.form.get("episode_number", 1) or 1)

    return episode


@admin_bp.route("/movies/<int:movie_id>/episodes")
@login_required
@admin_required
def list_episodes(movie_id: int):
    movie = Movie.query.get_or_404(movie_id)
    if not movie.is_series:
        flash("Ce programme est un film, aucun épisode à gérer.", "info")
        return redirect(url_for("admin.edit_movie", movie_id=movie.id))
    episodes = sorted(
        movie.episodes,
        key=lambda ep: (ep.season_number, ep.episode_number),
    )
    return render_template("admin/episode_list.html", movie=movie, episodes=episodes)


@admin_bp.route("/movies/<int:movie_id>/episodes/new", methods=["GET", "POST"])
@login_required
@admin_required
def create_episode(movie_id: int):
    movie = Movie.query.get_or_404(movie_id)
    if not movie.is_series:
        flash("Impossible d'ajouter un épisode à un film.", "error")
        return redirect(url_for("admin.edit_movie", movie_id=movie.id))

    if request.method == "POST":
        episode = _episode_from_request(movie)
        if not episode.title or not episode.video_url:
            flash("Le titre et l'URL vidéo de l'épisode sont obligatoires.", "error")
        else:
            db.session.add(episode)
            db.session.commit()
            flash("Épisode ajouté !", "success")
            return redirect(url_for("admin.list_episodes", movie_id=movie.id))

    return render_template("admin/episode_form.html", movie=movie, episode=None)


@admin_bp.route(
    "/movies/<int:movie_id>/episodes/<int:episode_id>/edit",
    methods=["GET", "POST"],
)
@login_required
@admin_required
def edit_episode(movie_id: int, episode_id: int):
    movie = Movie.query.get_or_404(movie_id)
    episode = Episode.query.get_or_404(episode_id)
    if episode.movie_id != movie.id:
        flash("Épisode introuvable pour ce programme.", "error")
        return redirect(url_for("admin.list_episodes", movie_id=movie.id))

    if request.method == "POST":
        episode = _episode_from_request(movie, episode)
        if not episode.title or not episode.video_url:
            flash("Le titre et l'URL vidéo de l'épisode sont obligatoires.", "error")
        else:
            db.session.commit()
            flash("Épisode mis à jour.", "success")
            return redirect(url_for("admin.list_episodes", movie_id=movie.id))

    return render_template("admin/episode_form.html", movie=movie, episode=episode)


@admin_bp.route(
    "/movies/<int:movie_id>/episodes/<int:episode_id>/delete",
    methods=["POST"],
)
@login_required
@admin_required
def delete_episode(movie_id: int, episode_id: int):
    movie = Movie.query.get_or_404(movie_id)
    episode = Episode.query.get_or_404(episode_id)
    if episode.movie_id != movie.id:
        flash("Épisode introuvable pour ce programme.", "error")
        return redirect(url_for("admin.list_episodes", movie_id=movie.id))

    db.session.delete(episode)
    db.session.commit()
    flash("Épisode supprimé.", "success")
    return redirect(url_for("admin.list_episodes", movie_id=movie.id))


@admin_bp.route("/movies/<int:movie_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_movie(movie_id: int):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash("Programme supprimé.", "success")
    return redirect(url_for("admin.dashboard"))
