import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

db = SQLAlchemy()  # moved outside without app
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "app_routes.login"



def create_app():
    app = Flask(__name__, template_folder='../templates')
#    app.secret_key = "secret123"

    app.secret_key = os.environ.get("SECRET_KEY", "fallback-secret")

    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, '../data.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['SESSION_COOKIE_SECURE'] = True  # use HTTPS
    app.config['REMEMBER_COOKIE_SECURE'] = True

    db.init_app(app)         # initialize with app context
    migrate.init_app(app, db)
    login_manager.init_app(app)

    login_manager.login_message = "Please log in to access this page."

    from mainapp.models import User  # import after db init
    from mainapp.routes import app_routes
    app.register_blueprint(app_routes)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
