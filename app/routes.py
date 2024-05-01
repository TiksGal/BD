import os
from flask import render_template, flash, redirect, url_for, make_response, session, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib.utils import ImageReader
from app import app, db, bcrypt
from app import db
from flask import jsonify
import logging
from app.db_crud import DbCrud
from app.functions import generate_qr_code, save_image, add_options
from app.forms.forms import LoginForm, RegistrationForm, OptionForm, QuestionForm, QuizForm
from app.models.models import Quiz, Question, Option, Game, User


db_crud = DbCrud()
logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = DbCrud().get_user_by_username(form.username.data)
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for("home"))
        flash("Invalid username or password", "danger")
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = DbCrud().get_user_by_username(form.username.data)
        if existing_user:
            flash("Username already exists! Please choose another username.", "danger")
        else:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
            new_user = DbCrud().create_user(username=form.username.data, email=form.email.data, name=form.name.data, surname=form.surname.data, password_hash=hashed_password)
            if new_user:
                flash("Registration successful! Please log in.", "success")
                return redirect(url_for("login"))
            else:
                flash("Error creating new user!", "danger")
    return render_template("register.html", form=form)


@app.route('/create_quiz', methods=['GET', 'POST'])
@login_required
def create_quiz():
    form = QuizForm()
    if form.validate_on_submit():
        quiz_name = form.title.data
        quiz_category = form.description.data
        creator_id = current_user.id

        new_quiz = db_crud.create_quiz(creator_id=creator_id, category=quiz_category, name=quiz_name)
        if new_quiz:
            flash('Turnyras sėkmingai sukurtas!', 'success')
            return redirect(url_for('add_question', quiz_id=new_quiz.id))
        else:
            flash('Nepavyko sukurti turnyro. Bandykite dar kartą.', 'danger')

    return render_template('create_quiz.html', form=form)
    

@app.route('/add_question/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def add_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    if request.method == 'POST':
        question_text = request.form.get('question_text')
        question_type = request.form.get('question_type')
        correct_answer = request.form.get('open_answer')  # Gauname teisingą atsakymą
        image = request.files.get('image')
        external_url = request.form.get('external_url')

        if not question_text:
            flash('Klausimo laukas negali būti tuščias', 'danger')
            return redirect(url_for('add_question', quiz_id=quiz_id))

        max_question_number = db.session.query(db.func.max(Question.question_number)).filter_by(quiz_id=quiz_id).scalar()
        question_number = max_question_number + 1 if max_question_number else 1

        question = Question(
            content=question_text,
            question_type=question_type,
            quiz_id=quiz_id,
            question_number=question_number,
            correct_answer=correct_answer,
            external_url=external_url
        )

        if image:
            image_path = save_image(image)
            question.image_url = image_path

        db.session.add(question)
        db.session.flush()

        if question_type == 'testinis':
            add_options(request, question)

        try:
            qr_code_path = generate_qr_code(question.id)
            question.qr_code_path = qr_code_path
            db.session.commit()
            flash('Klausimas buvo sėkmingai išsaugotas!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while saving the question and its options: {str(e)}', 'danger')

        return redirect(url_for('add_question', quiz_id=quiz_id))

    return render_template('add_question.html', quiz_id=quiz_id)


@app.route('/quiz_summary/<int:quiz_id>')
def quiz_summary(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    # Čia pridedame order_by, kad užtikrintume, jog klausimai bus išdėstyti pagal jų numerį kvize
    questions = Question.query.filter_by(quiz_id=quiz_id).order_by(Question.question_number).all()
    return render_template('quiz_summary.html', quiz=quiz, questions=questions)


@app.route('/generate_pdf/<int:quiz_id>')
def generate_pdf(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    # Create a PDF buffer
    buffer = BytesIO()

    # Create a canvas
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Add quiz name, category, and tournament code
    c.setFont("Helvetica", 18)
    c.drawString(72, height - 72, f'Turnyras: {quiz.name}')
    c.drawString(72, height - 96, f'Aprašymas: {quiz.category}')
    c.drawString(72, height - 120, f'Turnyro kodas: {quiz.tourney_code}')

    # Adjust initial y_position after adding category
    y_position = height - 170
    c.setFont("Helvetica", 12)
    for question in questions:
        if y_position < 200:  # Check for end of page and create new one if needed
            c.showPage()
            y_position = height - 72

        # Add question text
        c.drawString(72, y_position, f'Klausimas nr:{question.question_number}')
        y_position -= 20

        # Add QR code for question if it exists
        if question.qr_code_path:
            qr_code_path = os.path.join(app.static_folder, question.qr_code_path)
            qr_code_image = ImageReader(qr_code_path)
            c.drawImage(qr_code_image, 72, y_position - 100, width=100, height=100, mask='auto')
            y_position -= 120  # Adjust space for QR code height

    # Finish up
    c.save()
    buffer.seek(0)

    # Create response with PDF content
    response = make_response(buffer.getvalue())
    buffer.close()
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=quiz_summary_{quiz_id}.pdf'

    return response

@app.route('/connect_to_tournament', methods=['GET', 'POST'])
@login_required
def connect_to_tournament():
    if request.method == 'POST':
        tournament_code = request.form.get('tournament_code')
        quiz = Quiz.query.filter_by(tourney_code=tournament_code).first()

        if quiz:
            # Tikriname, ar jau egzistuoja Game objektas dabartiniam vartotojui ir pasirinktam kvizui
            existing_game = Game.query.filter_by(user_id=current_user.id, quiz_id=quiz.id).first()

            # Jei Game objektas neegzistuoja, sukuriame naują
            if not existing_game:
                new_game = Game(user_id=current_user.id, quiz_id=quiz.id, score=0)
                db.session.add(new_game)
                db.session.commit()

            # Nustatome dabartinį kvizo ID į sesiją
            session['current_quiz_id'] = quiz.id

            # Nukreipiame į kvizo peržiūros puslapį
            return redirect(url_for('view_tournament', quiz_id=quiz.id))
        else:
            flash('Turnyras su nurodytu kodu nerastas.', 'danger')

    return render_template('connect_to_tournament.html')


@app.route('/view_tournament/<int:quiz_id>', methods=['GET'])
def view_tournament(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    user_id = current_user.id  # or however you're tracking the current user

    game = Game.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
    if not game:
        flash('You have not started this tournament yet.', 'info')
        return redirect(url_for('home'))

    return render_template('view_tournament.html', quiz=quiz, game=game)

@app.route('/answer_question/<int:question_id>', methods=['GET', 'POST'])
@login_required
def answer_question(question_id):
    question = Question.query.get_or_404(question_id)
    current_quiz_id = session.get('current_quiz_id')
    
    if not current_quiz_id or current_quiz_id != question.quiz_id:
        flash('You are not allowed to answer this question.', 'danger')
        return redirect(url_for('view_tournament', quiz_id=current_quiz_id))

    if request.method == 'POST':
        if question.question_type == 'testinis':
            selected_option_id = request.form.get('option')
            selected_option = Option.query.get_or_404(selected_option_id)
            correct = selected_option.is_correct
        else:
            correct_answer = request.form.get('open_answer')
            correct = (correct_answer.strip().lower() == question.correct_answer.strip().lower())

        game = Game.query.filter_by(user_id=current_user.id, quiz_id=current_quiz_id).first()
        if not game:
            game = Game(user_id=current_user.id, quiz_id=current_quiz_id, score=0)
            db.session.add(game)

        if correct:
            game.score += 1
            db.session.commit()
            return redirect(url_for('correct_answer', quiz_id=current_quiz_id))
        else:
            return redirect(url_for('incorrect_answer', quiz_id=current_quiz_id))

    return render_template('answer_question.html', question=question)




@app.route('/correct_answer/<int:quiz_id>')
def correct_answer(quiz_id):
    return render_template('correct_answer.html', quiz_id=quiz_id)


@app.route('/incorrect_answer/<int:quiz_id>')
def incorrect_answer(quiz_id):
    return render_template('incorrect_answer.html', quiz_id=quiz_id)


@app.route('/leaderboard')
@login_required
def leaderboard():
    current_quiz_id = session.get('current_quiz_id')
    if not current_quiz_id:
        flash('Please join a quiz to view the leaderboard.', 'warning')
        return redirect(url_for('home'))
    
    leaderboard_entries = db.session.query(
        Quiz.name, User.username, Game.score
    ).join(Game, Game.quiz_id == Quiz.id)\
    .join(User, Game.user_id == User.id)\
    .filter(Game.quiz_id == current_quiz_id)\
    .order_by(Game.score.desc()).all()

    quiz_name = Quiz.query.get(current_quiz_id).name if current_quiz_id else "Quiz"

    return render_template('leaderboard.html', leaderboard_entries=leaderboard_entries, quiz_name=quiz_name)


@app.errorhandler(403)
def error_403(error):
    return render_template("403.html"), 403


@app.errorhandler(404)
def error_404(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def error_500(error):
    return render_template("500.html"), 500
