from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed

from wtforms import ValidationError
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired

class FileAllowedExtension(object):
    def __init__(self, upload_set, message=None):
        self.upload_set = upload_set
        self.message = message

    def __call__(self, form, field):
        filename = field.data.filename
        if filename and not self.upload_set.file_allowed(field.data, filename):
            message = self.message
            if message is None:
                message = 'File does not have an approved extension: {0}'.format(
                    self.upload_set.get_allowed_extensions()
                )

            field.errors[:] = []
            raise ValidationError(message)


# class PhotoForm(FlaskForm):
#     photo = FileField('Photo', validators=[
#         FileRequired(),
#         FileAllowedExtension('photos', 'Images only!')
#     ])
#     submit = SubmitField('Upload')

# class VideoForm(FlaskForm):
#     video = FileField('Video', validators=[
#         FileRequired(),
#         FileAllowedExtension('videos', 'Videos only!')
#     ])
#     submit = SubmitField('Upload')