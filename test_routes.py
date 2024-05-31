import pytest
from flask import url_for
from app import db, bcrypt
from app.models.models import User, Quiz, Question, Game, Option

@pytest.fixture
def authenticated_request(client):
    with client.application.app_context():
        # Register a user
        client.post(url_for('register'), data={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'name': 'Test',
            'surname': 'User',
            'password': 'password',
            'password2': 'password'
        }, follow_redirects=True)

        # Log in the user
        client.post(url_for('login'), data={
            'username': 'testuser',
            'password': 'password'
        }, follow_redirects=True)

        yield client

        # Log out the user
        client.get(url_for('logout'))

def test_home_page(client):
    response = client.get(url_for('home'))
    assert response.status_code == 200
    assert 'Home' in response.data.decode()

def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert 'Prisijungti' in response.data.decode()

    response = client.post('/login', data=dict(
        username='neteisingas', password='neteisingas'), follow_redirects=True)
    assert 'Neteisingas vartotojo vardas arba slaptažodis' in response.data.decode()

def test_register_user(client):
    response = client.post(url_for('register'), data={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'name': 'Test',
        'surname': 'User',
        'password': 'password',
        'password2': 'password'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert 'Registration successful! Please log in.' in response.data.decode()

def test_login_user(client):
    hashed_password = bcrypt.generate_password_hash('password').decode('utf-8')
    user = User(username='testuser', email='testuser@example.com', name='Test', surname='User', password_hash=hashed_password)
    db.session.add(user)
    db.session.commit()

    response = client.post(url_for('login'), data={
        'username': 'testuser',
        'password': 'password'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert 'Home' in response.data.decode()
    assert 'Logout' in response.data.decode()

def test_create_quiz(authenticated_request):
    client = authenticated_request
    response = client.post(url_for('create_quiz'), data={
        'title': 'Sample Quiz',
        'description': 'This is a sample quiz'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert 'Turnyras sėkmingai sukurtas!' in response.data.decode()

def test_add_question(authenticated_request):
    client = authenticated_request
    quiz = Quiz(name="Sample Quiz", category="General", creator_id=1)
    db.session.add(quiz)
    db.session.commit()

    response = client.post(url_for('add_question', quiz_id=quiz.id), data={
        'question_text': 'Sample Question',
        'question_type': 'testinis',
        'open_answer': 'Sample Answer'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert 'Klausimas buvo sėkmingai išsaugotas!' in response.data.decode()

def test_quiz_summary(authenticated_request):
    client = authenticated_request
    quiz = Quiz(name="Sample Quiz", category="General", creator_id=1)
    db.session.add(quiz)
    db.session.commit()

    question = Question(content='Sample Question', question_type='testinis', quiz_id=quiz.id, question_number=1)
    db.session.add(question)
    db.session.commit()

    response = client.get(url_for('quiz_summary', quiz_id=quiz.id))

    assert response.status_code == 200
    assert 'Sample Question' in response.data.decode()

def test_generate_pdf(authenticated_request):
    client = authenticated_request
    quiz = Quiz(name="Sample Quiz", category="General", creator_id=1)
    db.session.add(quiz)
    db.session.commit()

    question = Question(content='Sample Question', question_type='testinis', quiz_id=quiz.id, question_number=1)
    db.session.add(question)
    db.session.commit()

    response = client.get(url_for('generate_pdf', quiz_id=quiz.id))

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/pdf'

def test_connect_to_tournament(authenticated_request):
    client = authenticated_request
    quiz = Quiz(name="Sample Quiz", category="General", creator_id=1, tourney_code='TESTCODE')
    db.session.add(quiz)
    db.session.commit()

    response = client.post(url_for('connect_to_tournament'), data={
        'tournament_code': 'TESTCODE'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert 'Sample Quiz' in response.data.decode()

def test_view_tournament(authenticated_request):
    client = authenticated_request
    quiz = Quiz(name="Sample Quiz", category="General", creator_id=1)
    db.session.add(quiz)
    db.session.commit()

    game = Game(user_id=1, quiz_id=quiz.id, score=0)
    db.session.add(game)
    db.session.commit()

    response = client.get(url_for('view_tournament', quiz_id=quiz.id))

    assert response.status_code == 200
    assert 'Sample Quiz' in response.data.decode()

def test_answer_question(authenticated_request):
    client = authenticated_request
    quiz = Quiz(name="Sample Quiz", category="General", creator_id=1)
    db.session.add(quiz)
    db.session.commit()

    question = Question(content='Sample Question', question_type='testinis', quiz_id=quiz.id, question_number=1, correct_answer='Sample Answer')
    db.session.add(question)
    db.session.commit()

    response = client.post(url_for('answer_question', question_id=question.id), data={
        'open_answer': 'Sample Answer'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert 'correct' in response.data.decode().lower()

def test_leaderboard(authenticated_request):
    client = authenticated_request
    quiz = Quiz(name="Sample Quiz", category="General", creator_id=1)
    db.session.add(quiz)
    db.session.commit()

    user = User(username='testuser', email='testuser@example.com', name='Test', surname='User', password_hash=bcrypt.generate_password_hash('password').decode('utf-8'))
    db.session.add(user)
    db.session.commit()

    response = client.get(url_for('leaderboard', quiz_id=quiz.id))

    assert response.status_code == 200
    assert 'Sample Quiz' in response.data.decode()
