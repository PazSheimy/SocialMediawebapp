# from flask import Blueprint, render_template, redirect, url_for, request,  current_app
# from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# from flask_login import login_required
# #from forms import PhotoForm, VideoForm
# #from models import photos, videos
# from werkzeug.utils import secure_filename
# import os
# from models import Media

# content = Blueprint('content', __name__)

# @content.route('/upload_photo', methods=['GET', 'POST'])
# @login_required
# def upload_photo():
#     if request.method == 'POST':
#         file = request.files.get('photo')
#         filename = secure_filename(file.filename)
#         file.save(os.path.join(current_app.config['UPLOADED_PHOTOS_DEST'], filename))
#         return redirect(url_for('content.display_photo', filename=filename))
#     return render_template('upload_photo.html')

# @content.route('/upload_video', methods=['GET', 'POST'])
# @login_required
# def upload_video():
#     if request.method == 'POST':
#         file = request.files.get('photo')
#         filename = secure_filename(file.filename)
#         file.save(os.path.join(current_app.config['UPLOADED_VIDEOS_DEST'], filename))
#         return redirect(url_for('content.display_video', filename=filename))
#     return render_template('upload_video.html')



# @app.route('/upload_photo', methods=['GET', 'POST'])
# def upload_photo():
#     if request.method == 'POST':
#         file = request.files.get('photo')
#         filename = secure_filename(file.filename)
#         file.save(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename))
#         new_media = Media(filename=filename, media_type='image', user_id=current_user.id)
#         db.session.add(new_media)
#         db.session.commit()
#         return redirect(url_for('content.display_photo', filename=filename))
#     return render_template('upload_photo.html')

# @app.route('/upload_video', methods=['GET', 'POST'])
# def upload_video():
#     if request.method == 'POST':
#         file = request.files.get('photo')
#         filename = secure_filename(file.filename)
#         file.save(os.path.join(app.config['UPLOADED_VIDEOS_DEST'], filename))
#         new_media = Media(filename=filename, media_type='video', user_id=current_user.id)
#         db.session.add(new_media)
#         db.session.commit()
#         return redirect(url_for('content.display_video', filename=filename))
#     return render_template('upload_video.html')