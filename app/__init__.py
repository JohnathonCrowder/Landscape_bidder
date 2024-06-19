from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    app.secret_key = 'your_secret_key'  # Replace with a strong secret key

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    from app.routes import bp
    app.register_blueprint(bp)

    with app.app_context():
        db.create_all()

    return app