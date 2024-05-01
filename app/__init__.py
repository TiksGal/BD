import os
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, static_url_path='', static_folder='static')

qr_directory = os.path.join(app.static_folder, 'qr_codes')
if not os.path.exists(qr_directory):
    os.makedirs(qr_directory)
    
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "game.db")
app.config["SECRET_KEY"] = "7e00696cd12d5df1dea20f5056a5f47e"
app.config['WTF_CSRF_ENABLED'] = True
csrf = CSRFProtect(app)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['UPLOAD_FOLDER'] = '/path/to/your/uploads'


app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"


with app.app_context():
    from app.models.models import User
    db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app import routes

