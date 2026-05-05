import pytest
from app import create_app
from app.database import db
from app.models import Client, Parking


@pytest.fixture
def app():
    # Создаем приложение с тестовым конфигом
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # База в оперативной памяти
    })

    with app.app_context():
        db.create_all()

        # Создаем тестовые данные для фикстуры
        c1 = Client(name="Test", surname="User",
                    credit_card="1111", car_number="T111TT")
        p1 = Parking(address="Test St",
                     count_places=10,
                     count_available_places=10, opened=True)
        db.session.add_all([c1, p1])
        db.session.commit()

        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def _db(app):
    return db
