from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from contextlib import contextmanager
from flask_migrate import Migrate

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Configure your database URI below
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "game.db")
app.config["SECRET_KEY"] = "7e00696cd12d5df1dea20f5056a5f47e"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
# Initialize Flask-Migrate
migrate = Migrate(app, db)
# Adjust the import paths based on your actual application structure
from app.models.models import Question, Option, Quiz  # Make sure this import matches your project structure

# Context manager for providing a transactional scope
@contextmanager
def transactional_scope():
    """Provide a transactional scope around a series of operations."""
    try:
        yield
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred: {e}")
    finally:
        db.session.remove()  # Use remove() instead of close() for scoped session

def create_question_with_options(quiz_id, question_content, correct_answer, options_list):
    """Create a question with options and save to the database."""
    with transactional_scope():
        question = Question(quiz_id=quiz_id, content=question_content, correct_answer=correct_answer)
        db.session.add(question)
        db.session.flush()  # Get question.id before committing to obtain ID

        for option_data in options_list:
            option = Option(question_id=question.id, **option_data)
            db.session.add(option)

        print(f"Question '{question.content}' with its options added successfully!")


if __name__ == "__main__":
    with app.app_context():
        quiz_id = 1  # Make sure this quiz exists in your database
        question_content = "What is the capital of France?"
        correct_answer = "Paris"  # The correct answer to the question
        options_list = [
            {"content": "Paris", "is_correct": True},
            {"content": "Rome", "is_correct": False},
            {"content": "Berlin", "is_correct": False},
            {"content": "Madrid", "is_correct": False}
        ]

        create_question_with_options(quiz_id, question_content, correct_answer, options_list)


