import pytest
from app import app, db
import tempfile
import os

@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    app.config['SERVER_NAME'] = 'localhost'  # Add SERVER_NAME for URL building

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client

    os.close(db_fd)
    os.unlink(db_path)
