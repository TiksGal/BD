import unittest
from unittest.mock import patch, MagicMock
from werkzeug.datastructures import FileStorage
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
import string
import os

# Mock the functions module where your business logic resides.
from app.functions import save_image, generate_qr_code, add_options, generate_tourney_code

app = Flask(__name__)
app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

with app.app_context():
    db.create_all()

class TestFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

    @classmethod
    def tearDownClass(cls):
        cls.app_context.pop()
        with cls.app.app_context():
            db.drop_all()

    @patch('os.makedirs')
    @patch('os.path.exists', return_value=False)
    @patch('werkzeug.datastructures.FileStorage.save')
    def test_save_image_new_directory(self, mock_save, mock_exists, mock_makedirs):
        image = FileStorage(filename='test.png')
        with self.app.app_context():
            result = save_image(image)
            mock_makedirs.assert_called_once()
            mock_save.assert_called_once()
            self.assertIn(os.path.join('uploads', 'test.png'), result)

    @patch('os.path.exists', return_value=True)
    @patch('werkzeug.datastructures.FileStorage.save')
    def test_save_image_existing_directory(self, mock_save, mock_exists):
        image = FileStorage(filename='test.png')
        with self.app.app_context():
            result = save_image(image)
            mock_save.assert_called_once()
            self.assertIn(os.path.join('uploads', 'test.png'), result)

    @patch('os.makedirs')
    @patch('os.path.exists', return_value=False)
    @patch('qrcode.QRCode.make_image')
    def test_generate_qr_code(self, mock_make_image, mock_exists, mock_makedirs):
        mock_img = MagicMock()
        mock_make_image.return_value = mock_img
        with self.app.app_context():
            result = generate_qr_code(123)
            mock_makedirs.assert_called_once()
            mock_img.save.assert_called_once()
            self.assertIn(os.path.join('qr_codes', 'qr_123.png'), result)


    def test_generate_tourney_code_default_length(self):
        code = generate_tourney_code()
        self.assertEqual(len(code), 5)
        self.assertTrue(all(c in string.ascii_uppercase + string.digits for c in code))

    def test_generate_tourney_code_custom_length(self):
        lengths = [6, 10, 15]  # Different lengths to test
        for length in lengths:
            with self.subTest(length=length):
                code = generate_tourney_code(length)
                self.assertEqual(len(code), length)
                self.assertTrue(all(c in string.ascii_uppercase + string.digits for c in code))

if __name__ == '__main__':
    unittest.main()
