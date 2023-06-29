from flask import Flask, render_template, redirect, url_for, abort, request, current_app, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask import flash
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_dropzone import Dropzone
from werkzeug.utils import secure_filename
import os

# Blueprint files
from auth import auth
#from content import content

from config import Config
from extensions import db, login_manager
from models import User, Media, Like, Comment, Dislike, Post
#from forms import PhotoForm, VideoForm


app = Flask(__name__)
app.config.from_object(Config)

dropzone = Dropzone(app)

app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'image'  
app.config['DROPZONE_MAX_FILE_SIZE'] = 3  
app.config['DROPZONE_INPUT_NAME'] = 'photo'
app.config['DROPZONE_MAX_FILES'] = 30  
app.config['DROPZONE_REDIRECT_VIEW'] = 'content.display_photo' 
app.config['DROPZONE_UPLOAD_MULTIPLE'] = True  
app.config['DROPZONE_PARALLEL_UPLOADS'] = 3  

app.config['UPLOADED_PHOTOS_DEST'] = 'static/img'
app.config['UPLOADED_VIDEOS_DEST'] = 'static/videos'
app.config['UPLOAD_PROFILE_PICTURE'] = 'static/profile'

@app.route('/upload_media', methods=['GET', 'POST'])
@login_required
def upload_media():
    if request.method == 'POST':
        file = request.files.get('file')
        description = request.form.get('description') 
        if file:
            print(f"Received file with filename {file.filename}")
            filename = secure_filename(file.filename)
            media_type = 'image' if filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png', 'gif'} else 'video'
            save_path = os.path.join(
                app.config['UPLOADED_PHOTOS_DEST'] if media_type == 'image' else app.config['UPLOADED_VIDEOS_DEST'],
                filename
            )
            file.save(save_path)
            print(f"Saved file to {save_path}")
            new_media = Media(filename=filename, media_type=media_type, user_id=current_user.id, description=description)
            db.session.add(new_media)
            db.session.commit()
            print(f"Added new media with filename {filename} to database and description {description} to database")
            return redirect(url_for('feed'))
    return render_template('upload_media.html')


# Initialize SQLAlchemy and LoginManager with our app
db.init_app(app)
login_manager.init_app(app)

# Register the blueprint
app.register_blueprint(auth, url_prefix='/auth')
# app.register_blueprint(content)

@app.route('/')
@login_required
def home():
    return 'Hello, World!'

@app.route('/like/<int:media_id>', methods=['POST'])
@login_required
def like(media_id):
    existing_like = Like.query.filter_by(user_id=current_user.id, media_id=media_id).first()
    existing_dislike = Dislike.query.filter_by(user_id=current_user.id, media_id=media_id).first()

    if existing_like:
        flash('You already liked this media.')
        return redirect(url_for('feed'))
    
    if existing_dislike:
        db.session.delete(existing_dislike)

    new_like = Like(user_id=current_user.id, media_id=media_id)
    db.session.add(new_like)
    db.session.commit()
    return redirect(url_for('feed'))

@app.route('/dislike/<int:media_id>', methods=['POST'])
@login_required
def dislike(media_id):
    existing_dislike = Dislike.query.filter_by(user_id=current_user.id, media_id=media_id).first()
    existing_like = Like.query.filter_by(user_id=current_user.id, media_id=media_id).first()

    if existing_dislike:
        flash('You already disliked this media.')
        return redirect(url_for('feed'))
    
    if existing_like:
        db.session.delete(existing_like)

    dislike = Dislike(user_id=current_user.id, media_id=media_id)
    db.session.add(dislike)
    db.session.commit()
    return redirect(url_for('feed'))

@app.route('/comment', methods=['POST'])
@login_required
def comment():
    content = request.form['content']
    media_id = request.form['media_id']
    new_comment = Comment(body=content, user_id=current_user.id, media_id=media_id)
    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for('feed'))



@app.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        flash('User not found.')
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=user.username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(user.username))
    return redirect(url_for('user', username=user.username))


@app.route('/unfollow/<int:user_id>', methods=['POST'])
@login_required
def unfollow(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        flash('User not found.')
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=user.username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(user.username))
    return redirect(url_for('user', username=user.username))

@app.route('/user/<string:username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    media = user.media.order_by(Media.upload_time.desc()).all()

    #follower_counts = {follower.username: len(follower.followers.all()) for follower in user.followers}
    follower_counts = len(user.followers.all())
    followee_counts = len(user.followed.all())

    return render_template('user_profile.html', user=user, posts=posts, media=media, follower_counts=follower_counts, followee_counts= followee_counts)


@app.route('/feed')
def feed():
    media_files = Media.query.order_by(Media.upload_time.desc()).all()
    return render_template('feed.html', media_files=media_files)

@app.route('/static/<path:filename>') 
def staticfiles(filename):
    return send_from_directory(app.config['UPLOAD_PROFILE_PICTURE'], filename)



ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    print(current_user)  # Debugging line
    user = User.query.filter_by(id=current_user.id).first()
    print(f'Username: {user.username}, Email: {user.email}, Phone: {user.phone}, bio: {user.bio}')  # Debugging line

    if request.method == 'POST':
        # check if the post request has the file part
        if 'profile_picture' in request.files:
            profile_picture = request.files['profile_picture']
            # if user does not select file, browser submits an empty part without filename
            if profile_picture.filename != '' and profile_picture and allowed_file(profile_picture.filename):
                filename = secure_filename(profile_picture.filename)
                profile_picture.save(os.path.join(app.config['UPLOAD_PROFILE_PICTURE'], filename))
                user.profile_pic = filename  # Add this line to update the profile picture filename

        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.phone = request.form.get('phone')
        user.bio = request.form.get('bio')
        db.session.commit()  # This commit will now also save the updated profile picture filename
        return redirect(url_for('edit_profile'))

    return render_template('edit_profile.html', user=user)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

if __name__ == '__main__':
    with app.app_context():  # create an application context
        db.create_all()  # now we're in a context, so this will work
    app.run(debug=True)

