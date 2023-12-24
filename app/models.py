from . import db
from werkzeug.security import (generate_password_hash,
                               check_password_hash)
from flask_login import UserMixin
from . import login_manager
from datetime import datetime
from flask_login import current_user

@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(int(user_id))

from . import db

class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    overview = db.Column(db.Text)
    poster = db.Column(db.String)
    vote_average = db.Column(db.Float)
    vote_count = db.Column(db.Integer)
    video = db.Column(db.String)
    type = db.Column(db.String(255))
    reviews = db.relationship('Review', backref='movie', lazy='dynamic')

    def __init__(self, id, title, overview, poster, vote_average, vote_count):
        self.id = id
        self.title = title
        self.overview = overview
        self.poster = 'https://image.tmdb.org/t/p/w500/' + poster
        self.vote_average = vote_average
        self.vote_count = vote_count

    @classmethod
    def get_movies(cls):
        return cls.query.all()

    @classmethod
    def get_movie_by_id(cls, movie_id):
        return cls.query.filter_by(id=movie_id).first()
    
    @classmethod 
    def get_trending_movies(cls):
        return cls.query.order_by(cls.vote_count.desc()).all()[:5]
    
    @classmethod
    def get_top_rated_movies(cls):
        return cls.query.order_by(cls.vote_average.desc()).all()[:5]
    
    @classmethod
    def get_upcoming_movies(cls):
        # Return movie that don't have a video yet
        return cls.query.filter_by(video=None).all()[:5]
    
    @classmethod
    def get_movies_by_type(cls, movie_type):
        return cls.query.filter_by(type=movie_type).all()

    @classmethod
    def search_movies(cls, search_term):
        return cls.query.filter(cls.title.ilike(f"%{search_term}%")).all()

    @classmethod
    def add_movie(cls):
        new_movie = Movie(
            title='Your Movie Title',
            overview='Your movie overview...',
            poster='path/to/poster.jpg',
            vote_average=8.5,
            vote_count=1000,
            type='Action'
        )

        db.session.add(new_movie)
        db.session.commit()
    
class User(UserMixin, db.Model):
    # Ovewriting a the table name geneerated by SQLAlchemy
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(255))
    email = db.Column(db.String(255), unique = True, index = True)
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
    bio = db.Column(db.String(255))
    profile_pic_path = db.Column(db.String())
    password_hash = db.Column(db.String(255))
    reviews = db.relationship('Review',backref = 'user',lazy = "dynamic")

    @property
    def password(self):
        raise AttributeError("You cannot read the password attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @classmethod
    def update_profile_pic(self, new_pic_path):
        self.profile_pic_path = new_pic_path
        db.session.commit()
    
    @classmethod
    def update_password(self, new_password):
        self.password = generate_password_hash(new_password)
    
    @classmethod
    def get_current_user_details(cls):
        """
        Class method to get details of the current user in the session.
        Returns a dictionary with user details or None if no user is logged in.
        """
        if current_user.is_authenticated:
            return current_user
        return None
    
    def __repr__(self):
        return f'User {self.username}'

class Review(db.Model):

    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'))  # Add the foreign key
    movie_title = db.Column(db.String)
    image_path = db.Column(db.String)
    review_title = db.Column(db.String)
    movie_review = db.Column(db.String)
    posted = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    
    def save_review(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_reviews(cls,id):
        reviews = Review.query.filter_by(movie_id = id).all()
        return reviews

class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(255))
    users = db.relationship("User", backref = "role", lazy = "dynamic")

    def __repr__(self):
        return f"User {self.name}"