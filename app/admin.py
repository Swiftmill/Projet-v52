from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from . import db
from .models import Movie

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

    return movie


@admin_bp.route("/movies/new", methods=["GET", "POST"])
@login_required
@admin_required
def create_movie():
    if request.method == "POST":
        movie = _movie_from_request()
        if not movie.title or not movie.synopsis or not movie.video_url:
            flash("Titre, synopsis et URL vidéo sont obligatoires.", "error")
        else:
            db.session.add(movie)
            db.session.commit()
            flash("Nouveau programme ajouté !", "success")
            return redirect(url_for("admin.dashboard"))
    return render_template("admin/movie_form.html", movie=None)


@admin_bp.route("/movies/<int:movie_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_movie(movie_id: int):
    movie = Movie.query.get_or_404(movie_id)
    if request.method == "POST":
        movie = _movie_from_request(movie)
        db.session.commit()
        flash("Programme mis à jour.", "success")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/movie_form.html", movie=movie)


@admin_bp.route("/movies/<int:movie_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_movie(movie_id: int):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash("Programme supprimé.", "success")
    return redirect(url_for("admin.dashboard"))
