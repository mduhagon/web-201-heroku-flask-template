from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length


class NewLocationForm(FlaskForm):
    description = StringField('Location description',
                           validators=[DataRequired(), Length(min=1, max=80)])
    lookup_address = StringField('Search address')

    coord_latitude = HiddenField('Latitude',validators=[DataRequired()])

    coord_longitude = HiddenField('Longitude', validators=[DataRequired()])                    

    submit = SubmitField('Create Location')
