import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
import urllib.request as req

from analyzer import app, db, bcrypt, classify,json_data,api_key
from analyzer.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from analyzer.models import User, Post, Movies
from flask_login import login_user, current_user, logout_user, login_required
import json
from sqlalchemy.sql import exists    





@app.route("/")
@app.route("/home")
def home():
    form = PostForm()
    # moviePosts = Movies.query.all()
    # print(json_data)
    return render_template('home.html', json_data=json_data,form=form)





@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
@app.route("/login/<movie_id>", methods=['GET', 'POST'])
def login(movie_id=0):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('post', post_id=movie_id) )
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))
    
@app.route("/toprated")
def toprated():
    
    movieSort = Movies.query.order_by(Movies.rating).all()
    # movieUSort = Movies.query.all()
    movieSort.reverse()
    print(len(movieSort))
    bulk_data = []
    ratings = []
    for i in movieSort:
        base_url = "https://api.themoviedb.org/3/movie/" + str(i.id) + "?api_key=" + api_key + "&language=en-US"
        api_conn = req.urlopen(base_url)
       
        movie_data = json.loads(api_conn.read())
        bulk_data.append(movie_data.copy())
    # print(bulk_data)
    return render_template('toprated.html', bulk_data = bulk_data,movieSort = movieSort)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)





@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def post(post_id):

    base_url = "https://api.themoviedb.org/3/movie/" + str(post_id) + "?api_key=" + api_key + "&language=en-US"
    api_conn = req.urlopen(base_url)
    movie_data = json.loads(api_conn.read())
    form = PostForm(request.form)
    if form.validate_on_submit():
        review = request.form['content']
        y,proba = classify(review)
        postR = 0
        if(y == 'negative'):
            postR = 1 - proba
            print(proba)
        else:
            postR = proba
        

        postO = Post(title=form.title.data, content=form.content.data, author=current_user, movies_id = post_id,postRating=round(postR*10, 2))
        db.session.add(postO)
        db.session.commit()   
        flash('Your post has been created!', 'success') 
        
     
    post = Post.query.filter_by(movies_id=post_id).all()
    postLen = len(post)
    sum = 0
    for p in post:
        sum = sum + p.postRating
    if(postLen != 0):
        rate = sum/postLen
    else:
        rate =  0
    rate = round(rate,2)
    
    exists = db.session.query(db.exists().where(Movies.id == post_id)).scalar()
    if not exists:
        movie = Movies(id=post_id,movieName = movie_data['title'])
        db.session.add(movie)
        db.session.commit()
    
    moviePost = Movies.query.get(post_id)
    moviePost.rating = rate
    db.session.commit()
   
    
    
    return render_template('post.html', title = movie_data["title"], moviePost=movie_data,post=post,rate=round(rate,2),form=form,movieRate = moviePost)






