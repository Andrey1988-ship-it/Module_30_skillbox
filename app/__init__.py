from flask import Flask
from .database import db
from .routes import api_bp  # Импортируем роуты

def create_app(config_class="app.config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    # Регистрация роутов
    app.register_blueprint(api_bp)

    with app.app_context():
        db.create_all()

    return app
