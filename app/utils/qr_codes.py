import qrcode
from flask import url_for
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def generate_qr_code(quiz_id):
    # Generate the URL for the quiz
    quiz_url = url_for('quiz_details', quiz_id=quiz_id, _external=True)
    # Create a QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(quiz_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    # Save the QR code to a file
    qr_code_path = f'static/qr_codes/quiz_{quiz_id}.png'
    img.save(qr_code_path)
    return qr_code_path

def export_qr_code_to_pdf(quiz_id, qr_code_path):
    pdf_path = f'static/qr_codes/quiz_{quiz_id}_qr.pdf'
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.drawImage(qr_code_path, 100, 650, width=200, height=200)  # Adjust as needed
    c.showPage()
    c.save()
    return pdf_path
