import logging
import os
import random
import string
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from base64 import b64encode
from io import BytesIO
import qrcode
from flask import request, url_for
from flask import current_app
from app.models.models import Option
from typing import List
import os
from werkzeug.utils import secure_filename
from app import db

def save_image(image):
    filename = secure_filename(image.filename)
    uploads_directory = os.path.join(current_app.static_folder, 'uploads')
    if not os.path.exists(uploads_directory):
        os.makedirs(uploads_directory)
    file_path = os.path.join(uploads_directory, filename)
    image.save(file_path)
    return os.path.join('uploads', filename)

# No changes needed here as it's configuration
logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')


def generate_qr_code(question_id):
    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(f'http://127.0.0.1:5000/answer_question/{question_id}')
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    # Make sure the 'qr_codes' directory exists
    qr_directory = os.path.join(current_app.static_folder, 'qr_codes')
    if not os.path.exists(qr_directory):
        os.makedirs(qr_directory)

    # Create the full file path
    qr_code_path = os.path.join(qr_directory, f'qr_{question_id}.png')
    
    # Save the QR code image to the filesystem
    img.save(qr_code_path)

    # Return the relative path to be used in the templates
    relative_path = os.path.join('qr_codes', f'qr_{question_id}.png')
    
    return relative_path


def generate_tourney_code(length: int = 5) -> str:  # Added default length value
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def add_options(request, question):
    option_keys = [key for key in request.form if key.startswith('option_text_')]
    for key in option_keys:
        option_index = key.split('_')[-1]
        option_text = request.form[key]
        is_correct = request.form.get(f'is_correct_{option_index}') == 'on'
        option = Option(content=option_text, is_correct=is_correct, question_id=question.id)
        db.session.add(option)