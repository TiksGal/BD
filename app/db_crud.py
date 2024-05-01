from os import path
import logging
import logging.config
from typing import List, Dict, Union
from sqlalchemy.exc import SQLAlchemyError

from run import db  # Adjusted import to reflect your new project structure
from app.models.models import User, Quiz, Question, Option, Game

# Setting up logging
log_file_path = path.join(path.dirname(path.abspath(__file__)), "logging.conf")
logging.config.fileConfig(log_file_path)
logger = logging.getLogger("sLogger")

class DbCrud:
    
    # User Methods
    def create_user(self, username: str, name: str, surname: str, password_hash: str, email: str) -> User:
        try:
            user = User(username=username, name=name, surname=surname, password_hash=password_hash, email=email)
            db.session.add(user)
            db.session.commit()
            logger.info(f"User '{username}' has been created successfully!")
            return user
        except SQLAlchemyError as e:
            logger.error(f"An error occurred while creating user: {e}")
            return None

    def get_user_by_username(self, username: str) -> Union[User, None]:
        try:
            user = User.query.filter_by(username=username).first()
            if user:
                logger.info(f"User '{username}' retrieved successfully!")
                return user
            else:
                logger.error(f"User with username '{username}' does not exist!")
                return None
        except SQLAlchemyError as e:
            logger.error(f"An error occurred while retrieving user '{username}': {e}")
            return None

    def create_quiz(self, creator_id, category, name):
        try:
            quiz = Quiz(creator_id=creator_id, category=category, name=name)
            db.session.add(quiz)
            db.session.commit()
            return quiz
        except Exception as e:
            print(e)
            return None


    
    def create_question_with_options(self, quiz_id: int, content: str, options: list) -> Question:
        try:
            question = Question(quiz_id=quiz_id, content=content)
            db.session.add(question)
            db.session.flush()  # This obtains the question ID before committing

            for option in options:
                new_option = Option(question_id=question.id, content=option['content'], is_correct=option['is_correct'])
                db.session.add(new_option)

            db.session.commit()
            return question
        except Exception as e:
            db.session.rollback()  # Rollback the session on error
            print(f"Error adding question with options: {e}")
            return None




    # Game Methods
    def create_game(self, quiz_id: int) -> Game:
        try:
            game = Game(quiz_id=quiz_id)
            db.session.add(game)
            db.session.commit()
            logger.info(f"Game for quiz ID '{quiz_id}' created successfully!")
            return game
        except SQLAlchemyError as e:
            logger.error(f"An error occurred while creating game: {e}")
            return None

    
