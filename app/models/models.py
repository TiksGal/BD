from datetime import datetime
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from uuid import uuid4 
from sqlalchemy import Column, Integer, String, ForeignKey
from run import app, db

class User(db.Model, UserMixin):  # Inherit from UserMixin
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    surname = db.Column(db.String(128), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    quizzes = db.relationship('Quiz', backref='creator', lazy='dynamic')  # Use 'dynamic' for large sets
    games = db.relationship('Game', backref='user')
    
    def __repr__(self):
        return f'<User {self.username}>'

class Quiz(db.Model):
    __tablename__ = 'quizzes'

    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    tourney_code = db.Column(db.String(255), unique=True, nullable=False, default=lambda: uuid4().hex[:5])  # Add tourney_code
    questions = db.relationship('Question', backref='quiz', lazy='dynamic', cascade="all, delete-orphan")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Quiz {self.name}>'

class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question_number = db.Column(db.Integer, nullable=False)
    content = db.Column(db.String(256), nullable=False)
    correct_answer = db.Column(db.String(128), nullable=True)
    options = db.relationship('Option', backref='question', lazy='dynamic', cascade="all, delete-orphan")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    qr_code_path = db.Column(db.String(256))
    question_type = db.Column(db.String(100), nullable=False, default='testinis')
    image_url = db.Column(db.String(256))
    external_url = db.Column(db.String(256))
    def __repr__(self):
        return f'<Question {self.id}>'

class Option(db.Model):
    __tablename__ = 'options'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    content = db.Column(db.String(128), nullable=False)
    is_correct = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Option {self.content}> for Question ID {self.question_id}>'

class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Pakeista iš 'user.id' į 'users.id'
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)  # Pakeista iš 'quiz.id' į 'quizzes.id'
    score = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Game {self.id} - User {self.user_id} - Quiz {self.quiz_id} - Score {self.score}>'




