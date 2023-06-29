from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import DataRequired, Length, Email, Optional
from extensions import db
from flask_wtf.file import FileField, FileAllowed, FileRequired


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(128))
    phone = db.Column(db.String(20), unique=True)
    profile_pic = db.Column(db.String(120), default='default.jpg')  # assuming you will have a default picture for every user
    bio = db.Column(db.String(500))
    location = db.Column(db.String(100))
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    role = db.Column(db.String(64), default='user')
    verified = db.Column(db.Boolean, default=False)
    joined_at = db.Column(db.DateTime(), default=datetime.utcnow)
    
    

    # Relations
    media = db.relationship('Media', back_populates='user', lazy='dynamic')
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship('User', secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'), 
                               lazy='dynamic')
    
    comments = db.relationship('Comment', back_populates='author', lazy='dynamic')
    likes = db.relationship('Like', backref='user', lazy='dynamic')
    dislikes = db.relationship('Dislike', backref='user', lazy='dynamic')
    
    messages_sent = db.relationship('Message',
                                    foreign_keys='Message.sender_id',
                                    backref='author', lazy='dynamic')
    messages_received = db.relationship('Message',
                                        foreign_keys='Message.recipient_id',
                                        backref='recipient', lazy='dynamic')
    

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    bio = StringField('Bio', validators=[Length(0, 500)])
    location = StringField('Location', validators=[Length(0, 100)])
    phone = StringField('Phone Number', validators=[Optional(), Length(0, 20)])
    profile_pic = FileField('Upload Profile Picture', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Submit')
    
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    media_id = db.Column(db.Integer, db.ForeignKey('media.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    user = db.relationship('User', back_populates='comments') 
    post = db.relationship('Post', back_populates='comments')
    media = db.relationship('Media', back_populates='comments')
    author = db.relationship('User', back_populates='comments')


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    media_id = db.Column(db.Integer, db.ForeignKey('media.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    
    # Relationships
    # user = db.relationship('User', back_populates='likes')
    post = db.relationship('Post', back_populates='likes')
    media = db.relationship('Media', back_populates='likes')


class Dislike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    media_id = db.Column(db.Integer, db.ForeignKey('media.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    
     # Relationships
    post = db.relationship('Post', back_populates='dislikes')
    media = db.relationship('Media', back_populates='dislikes')


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# Let's also update Post model to backref the relationships
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    dislikes = db.relationship('Dislike', back_populates='post', lazy='dynamic')
    comments = db.relationship('Comment', back_populates='post', lazy='dynamic')
    likes = db.relationship('Like', back_populates='post', lazy='dynamic')

class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), unique=True)
    upload_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    media_type = db.Column(db.String(20))  # "image" or "video"
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # if you want to associate media with a user
    description = db.Column(db.String(1000))

    user = db.relationship('User', back_populates='media')
    likes = db.relationship('Like', back_populates='media', lazy='dynamic')
    dislikes = db.relationship('Dislike', back_populates='media', lazy='dynamic')
    comments = db.relationship('Comment', back_populates='media', lazy='dynamic')

