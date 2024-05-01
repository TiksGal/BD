import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db_crud import DbCrud
from app.models.models import User, Quiz, Question, Game

# Initialize the Flask application for testing
app = Flask(__name__)
app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set up the Flask-SQLAlchemy extension
db = SQLAlchemy(app)

# Bind the app with the db
with app.app_context():
    db.create_all()

# Define the test suite using unittest
class TestDbCrud(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set up a Flask application context before running the tests.
        cls.app = app
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
    
    @classmethod
    def tearDownClass(cls):
        # Pop the application context and drop all tables.
        cls.app_context.pop()
        with cls.app.app_context():
            db.drop_all()

    def setUp(self):
        self.db_crud = DbCrud()

    @patch('app.db_crud.db.session.add')
    @patch('app.db_crud.db.session.commit')
    def test_create_user(self, mock_add, mock_commit):
        user = self.db_crud.create_user("testuser", "Test", "User", "hash123", "test@example.com")
        self.assertIsNotNone(user)
        mock_add.assert_called_once()
        mock_commit.assert_called_once()

    @patch('app.models.models.User.query')
    def test_get_user_by_username_found(self, mock_query):
        mock_user = User(username="existing_user")
        mock_query.filter_by.return_value.first.return_value = mock_user
        user = self.db_crud.get_user_by_username("existing_user")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "existing_user")

    @patch('app.models.models.User.query')
    def test_get_user_by_username_not_found(self, mock_query):
        mock_query.filter_by.return_value.first.return_value = None
        user = self.db_crud.get_user_by_username("non_existing_user")
        self.assertIsNone(user)

    @patch('app.db_crud.db.session.add')
    @patch('app.db_crud.db.session.commit')
    def test_create_quiz(self, mock_add, mock_commit):
        quiz = self.db_crud.create_quiz(1, "Math", "Math Quiz")
        self.assertIsNotNone(quiz)
        mock_add.assert_called_once()
        mock_commit.assert_called_once()

    @patch('app.db_crud.db.session.add')
    @patch('app.db_crud.db.session.commit')
    @patch('app.db_crud.db.session.flush')
    def test_create_question_with_options(self, mock_flush, mock_commit, mock_add):
        question_data = [{"content": "4", "is_correct": True}]
        with patch('app.db_crud.Question') as mock_question_class:
            # Create a mock instance of Question
            mock_question_instance = MagicMock()
            mock_question_class.return_value = mock_question_instance
            # Call the method being tested
            question = self.db_crud.create_question_with_options(1, "What is 2+2?", question_data)
            # Assertions
            self.assertIsNotNone(question)
            mock_commit.assert_called_once()
            mock_flush.assert_called_once()


    @patch('app.db_crud.db.session.add')
    @patch('app.db_crud.db.session.commit')
    def test_create_game(self, mock_add, mock_commit):
        game = self.db_crud.create_game(1)
        self.assertIsNotNone(game)
        mock_add.assert_called_once()
        mock_commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()

