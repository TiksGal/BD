from flask_testing import TestCase
from app import app, db
from app.models.models import User
import unittest

class BaseTestCase(TestCase):
    def create_app(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    def setUp(self):
        db.create_all()
        self.create_user('testuser', 'test@example.com', 'Test', 'User', 'password')

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def create_user(self, username, email, name, surname, password):
        from app import bcrypt
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(
            username=username,
            email=email,
            name=name,
            surname=surname,
            password_hash=hashed_password
        )
        db.session.add(user)
        db.session.commit()

    def login(self, username, password):
        return self.client.post('/login', data=dict(
            username=username, password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

class TestAuth(BaseTestCase):
    
    def test_login_page(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)

    def test_valid_login(self):
        response = self.client.post('/login', data=dict(
            username='testuser', password='password'
        ), follow_redirects=True)
        self.assertIn(b'Sveikas sugr\xc4\xaf\xc5\xbe\xc4\x99s, testuser!', response.data)

    def test_invalid_login(self):
        response = self.client.post('/login', data=dict(
            username='wronguser', password='wrongpass'
        ), follow_redirects=True)
        self.assertIn(b'Invalid username or password', response.data)

    def test_registration_page(self):
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)

    def test_valid_registration(self):
        response = self.client.post('/register', data=dict(
            username='newuser', email='newuser@example.com',
            name='New', surname='User', password='newpassword',
            confirm_password='newpassword'
        ), follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

    def test_invalid_registration(self):
        response = self.client.post('/register', data=dict(
            username='testuser', email='testuser@example.com',
            name='Test', surname='User', password='password',
            confirm_password='password'
        ), follow_redirects=True)
        self.assertIn(b'Username already in use', response.data)


class TestUserSession(BaseTestCase):
    def test_login_logout(self):
        # Test login
        response = self.login('testuser', 'password')
        self.assertIn(b'Sveikas sugr\xc4\xaf\xc5\xbe\xc4\x99s, testuser!', response.data)

        # Test logout
        response = self.logout()
        self.assertIn(b'Sveiki atvyk\xc4\x99!', response.data)

if __name__ == '__main__':
    unittest.main()
