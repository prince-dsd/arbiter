from datetime import datetime
from analyzer import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movieName = db.Column(db.String(120), nullable=False, default='Provide data')
    runTime = db.Column(db.String(120), nullable=False, default='Provide data')
    Actor = db.Column(db.String(120), nullable=False, default='Provide data')
    director = db.Column(db.String(120), nullable=False, default='Provide data')
    release = db.Column(db.String(120), nullable=False, default='Provide data')
    genre = db.Column(db.String(120), nullable=False, default='Provide data')
    language = db.Column(db.String(120), nullable=False, default='Provide data')
    rating = db.Column(db.Numeric(precision=2, asdecimal=False, decimal_return_scale=None), default=0.0)
    descr = db.Column(db.String(300), nullable=False, default='Provide data')
    
    
    movieImage = db.Column(db.String(120), nullable=False, default='default.jpg')
    movieImage_1 = db.Column(db.String(120), nullable=False, default='default.jpg')
    movieImage_2 = db.Column(db.String(120), nullable=False, default='default.jpg')
    movieImage_3 = db.Column(db.String(120), nullable=False, default='default.jpg')
    movieImage_4 = db.Column(db.String(120), nullable=False, default='default.jpg')
    movie_posts = db.relationship('Post', backref='movie', lazy=True)
    pg = db.Column(db.String(10), nullable=False, default='Provide data')

   
    

    def __repr__(self):
        return f"Movies('{self.movieName}', '{self.runTime}','{self.Actor}','{self.release}','{self.genre}','{self.language}','{self.rating}', '{self.movieImage}', '{self.movieImage_1}, '{self.movieImage_2}, '{self.movieImage_3}, '{self.movieImage_4})"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movies_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    postRating = db.Column(db.Numeric(precision=2, asdecimal=False, decimal_return_scale=None))

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

