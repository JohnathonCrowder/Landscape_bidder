from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    app.secret_key = 'your_secret_key'  # Replace with a strong secret key

    from app.routes import bp
    app.register_blueprint(bp)

    return app