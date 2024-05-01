from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FieldList, FormField, SelectField, FileField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Optional
from app.models.models import User

class LoginForm(FlaskForm):
    username = StringField("Username", [DataRequired()])
    password = PasswordField("Password", [DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Login")


class RegistrationForm(FlaskForm):
    username = StringField("Username", [DataRequired()])
    name = StringField("Name", [DataRequired()])
    surname = StringField("Surname", [DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", [DataRequired()])
    confirm_password = PasswordField("Repeat password", [EqualTo("password", "Passwords must match")])
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username already in use")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email already in use")


class OptionForm(FlaskForm):
    option_text = StringField('Variantas', validators=[DataRequired()])
    is_correct = BooleanField('Teisingas pasirinkimas')


class QuestionForm(FlaskForm):
    question_type = SelectField('Klausimo tipas', choices=[('testinis', 'Testinis klausimas'), ('atviras', 'Atviras klausimas')], validators=[DataRequired()])
    question_text = TextAreaField('Įveskite klausimą', validators=[DataRequired()])
    options = FieldList(FormField(OptionForm), min_entries=0, max_entries=10)  # Dinamiškai keičiamas variantų skaičius
    image = FileField('Įkelti paveikslėlį', validators=[Optional()])
    external_url = StringField('Nuoroda', validators=[Optional()])
    submit = SubmitField('Pridėti klausimą')


class QuizForm(FlaskForm):
    title = StringField('Pavadinimas', validators=[DataRequired()])
    description = StringField('Aprašymas', validators=[DataRequired()])
    submit = SubmitField('Sukurti')