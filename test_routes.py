import unittest
from flask import Flask
from app import app, db
from app.models.models import User, Quiz, Question, Game

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        # Konfigūruojame aplikaciją testavimui
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app = app.test_client()
        # Sukuriame duomenų bazės schemas
        with app.app_context():
            db.create_all()
            
    def tearDown(self):
        # Ištriname duomenų bazę po kiekvieno testo
        with app.app_context():
            db.session.remove()
            db.drop_all()

class FlaskTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        with app.app_context():
            # Užtikriname, kad nėra konfliktuojančių vartotojų
            existing_user = User.query.filter((User.username == 'newuser') | (User.email == 'newuser@example.com')).first()
            if existing_user:
                db.session.delete(existing_user)
                db.session.commit()
            
    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Sveiki atvykę!', response.data.decode())

    def test_login_page(self):
        # Testuojame prisijungimo puslapio atvaizdavimą
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Prisijungti', response.data.decode())

        # Testuojame klaidingą prisijungimą
        response = self.app.post('/login', data=dict(
            username='neteisingas', password='neteisingas'), follow_redirects=True)
        self.assertIn('Invalid username or password', response.data.decode())

    def test_registration(self):
        # Užtikriname, kad formos duomenys atitinka visus reikalavimus
        response = self.app.post('/register', data={
            'username': 'newuser',
            'name': 'TestName',
            'surname': 'TestSurname',
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'confirm_password': 'newpassword123'  # Įsitikinkite, kad šis laukas atitinka 'password' lauką
        }, follow_redirects=True)
        self.assertIn('Registration successful', response.data.decode(), "Registracija nesėkminga, patikrinkite formos klaidas: " + response.data.decode())

