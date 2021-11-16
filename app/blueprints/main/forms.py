from os import name
from flask_wtf import FlaskForm
from app.models import User,Item
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired

class CreateItemsForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    img = StringField('Image Link')
    description = StringField('Description')
    submit = SubmitField('Create Item')
    
class EditItemsForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    img = StringField('Image Link')
    description = StringField('Description')
    submit = SubmitField('Submit')