from flask import (render_template, request, redirect, 
                   url_for, abort, jsonify)
from . import main
from ..request import get_movies, get_movie, search_movie
from .forms import ReviewForm, UpdateProfile
from ..models import Review, User, Movie
from flask_login import login_required, current_user
from .. import db, photos
import markdown2

# Views
@main.route('/')
def index():
    popular_movies = get_movies("popular")
    upcoming_movie = get_movies("upcoming")
    now_showing_movie = get_movies("now_playing")
    title = 'Home - Welcome to The best Movie Review Website Online'

    search_movie = request.args.get('movie_query')
    if search_movie:
        return redirect(url_for('.search',movie_name=search_movie))
    else:      
        return render_template('index.html',
                                title = title, 
                                popular = popular_movies,
                                upcoming = upcoming_movie,
                                now_showing = now_showing_movie)


@main.route('/movies/trending')
def get_trending_movies():
    trending_movies = Movie.get_trending_movies()
    
    # Convert the list of movies to a JSON response
    trending_movies_json = [
        {
            'id': movie.id,
            'title': movie.title,
            'overview': movie.overview,
            'poster': movie.poster,
            'vote_average': movie.vote_average,
            'vote_count': movie.vote_count,
            'video': movie.video,
            'type': movie.type,
            # Include other properties as needed
        } 
        for movie in trending_movies
    ]
    
    return jsonify(trending_movies_json)

@main.route('/movies/top_rated')
def get_top_rated_movies():
    top_rated_movies = Movie.get_top_rated_movies()
    
    # Convert the list of movies to a JSON response
    top_rated_movies_json = [
        {
            'id': movie.id,
            'title': movie.title,
            'overview': movie.overview,
            'poster': movie.poster,
            'vote_average': movie.vote_average,
            'vote_count': movie.vote_count,
            'video': movie.video,
            'type': movie.type,
            # Include other properties as needed
        } 
        for movie in top_rated_movies
    ]
    
    return jsonify(top_rated_movies_json)

@main.route('/movies/upcoming')
def get_upcoming_movies():
    upcoming_movies = Movie.get_upcoming_movies()
    
    # Convert the list of movies to a JSON response
    upcoming_movies_json = [
        {
            'id': movie.id,
            'title': movie.title,
            'overview': movie.overview,
            'poster': movie.poster,
            'vote_average': movie.vote_average,
            'vote_count': movie.vote_count,
            'video': movie.video,
            'type': movie.type,
            # Include other properties as needed
        } 
        for movie in upcoming_movies
    ]
    
    return jsonify(upcoming_movies_json)

@main.route("/movies/<int:id>")
def movie(id):
    movie_detail = Movie.get_movie_by_id(id)
    
    # Get movie details
    return jsonify({
        'id': movie_detail.id,
        'title': movie_detail.title,
        'overview': movie_detail.overview,
        'poster': movie_detail.poster,
        'vote_average': movie_detail.vote_average,
        'vote_count': movie_detail.vote_count,
        'video': movie_detail.video,
        'type': movie_detail.type,
        # Include other properties as needed
    })
                            
@main.route('/search/<movie_name>')
def search(movie_name):
    # Get movie details by name
    searched_movies = Movie.search_movies(movie_name)
    
    # Convert the list of movies to a JSON response
    searched_movies_json = [
        {
            'id': movie.id,
            'title': movie.title,
            'overview': movie.overview,
            'poster': movie.poster,
            'vote_average': movie.vote_average,
            'vote_count': movie.vote_count,
            'video': movie.video,
            'type': movie.type,
            # Include other properties as needed
        } 
        for movie in searched_movies
    ]
    
    return jsonify(searched_movies_json)

@main.route('/user/detail')
def get_current_user_detail():
    user = User.get_current_user_details()
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role_id': user.role_id,
        'profile_pic_path': user.profile_pic_path,
        # Include other properties as needed
    })
    
@login_required

@main.route('/movie/review/new/<int:id>', methods = ['GET','POST'])
@login_required
def new_review(id):
    form = ReviewForm()
    movie = get_movie(id)

    if form.validate_on_submit():
        title = form.title.data
        review = form.review.data
        new_review = Review(movie_id = movie.id,
                            movie_title = movie.title,
                            image_path = movie.poster,
                            review_title = title,
                            movie_review = review,
                            user = current_user)
        new_review.save_review()
        return redirect(url_for('main.movie',id = movie.id ))

    title = f'{movie.title} review'
    return render_template('new_review.html',
                            title = title, 
                            review_form = form, 
                            movie = movie)

@main.route("/review/<int:id>")
def single_review(id):
    review = Review.query.get(id)

    if review is None:
        abort(404)
    format_review_title = markdown2.markdown(review.review_title,
                                            extras = ["code-friendly", "fenced-code-blocks"])
    format_review = markdown2.markdown(review.movie_review,
                                        extras = ["code-friendly", "fenced-code-blocks"])
    
    return render_template("review.html", 
                            review = review,
                            format_review_title = format_review_title,
                            format_review = format_review)

@main.route("/user/<uname>")
def profile(uname):
    user = User.query.filter_by(username = uname).first()

    if user is None:
        abort(404)

    title = user.username

    return render_template("profile/profile.html",
                            user = user,
                            title = title)

@main.route("/user/<uname>/update", methods = ["GET", "POST"])
@login_required
def update_profile(uname):
    user = User.query.filter_by(username = uname).first()
    if user is None:
        abort(404)

    form = UpdateProfile()

    if form.validate_on_submit():
        user.bio = form.bio.data
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("main.profile", 
                                uname = user.username))

    return render_template("profile/update.html",
                            form = form)

@main.route("/user/<uname>/update/pic", methods = ["POST"])
@login_required
def update_pic(uname):
    user = User.query.filter_by(username = uname).first()
    if "photo" in request.files:
        filename = photos.save(request.files["photo"])
        path = f"photos/{filename}"
        user.profile_pic_path = path
        db.session.commit()
    return redirect(url_for("main.profile",
                             uname = uname))