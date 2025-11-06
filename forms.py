from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class ReportForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Length(max=1000)])
    category = SelectField('Category', choices=[('lost','Lost'),('found','Found')], validators=[DataRequired()])
    status = SelectField('Status', choices=[('open','Open'),('claimed','Claimed')], validators=[DataRequired()])
    submit = SubmitField('Report Item')
