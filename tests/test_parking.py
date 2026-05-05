import pytest
from sqlalchemy import select, func
from tests.factories import ClientFactory, ParkingFactory
from app.models import Client, Parking
from app.database import db


# 1. Параметризованный тест GET-методов
@pytest.mark.parametrize("url", ["/clients", "/clients/1"])
def test_get_status_200(client, url):
    resp = client.get(url)
    assert resp.status_code == 200


# ... (тесты 2 и 3 без изменений, они работают через клиент) ...

# 4. Исправленный тест на уменьшение мест
def test_parking_places_decrease(client, app):
    # Заезд
    client.post("/client_parkings", json={"client_id": 1, "parking_id": 1})

    # НОВЫЙ СТИЛЬ: Проверяем в базе через db.session.get
    with app.app_context():
        p = db.session.get(Parking, 1)  # Вместо Parking.query.get(1)
        assert p.count_available_places == 9


# 5. Тест выезда без карты
def test_exit_no_card(client, app):
    with app.app_context():
        # Создаем клиента без карты
        c2 = Client(name="No", surname="Card", car_number="B222BB")
        db.session.add(c2)
        db.session.commit()
        c2_id = c2.id

    client.post("/client_parkings", json={"client_id": c2_id, "parking_id": 1})
    resp = client.delete("/client_parkings", json={"client_id": c2_id, "parking_id": 1})
    assert resp.status_code == 400
    assert "Payment method (card) missing" in resp.json["error"]


# 6. Тесты с фабриками (самые "желтые" места)
def test_create_client_factory(client, app):
    fake_client = ClientFactory.build()
    data = {
        "name": fake_client.name,
        "surname": fake_client.surname,
        "car_number": fake_client.car_number,
        "credit_card": fake_client.credit_card
    }

    with app.app_context():
        # НОВЫЙ СТИЛЬ: Подсчет через func.count()
        count_before = db.session.scalar(select(func.count()).select_from(Client))

    resp = client.post("/clients", json=data)

    assert resp.status_code == 201
    with app.app_context():
        count_after = db.session.scalar(select(func.count()).select_from(Client))
        assert count_after == count_before + 1

        # НОВЫЙ СТИЛЬ: Поиск через select
        found = db.session.execute(
            select(Client).where(Client.car_number == fake_client.car_number)
        ).scalar_one_or_none()
        assert found is not None


def test_create_parking_factory(client, app):
    fake_parking = ParkingFactory.build(opened=True)
    data = {
        "address": fake_parking.address,
        "count_places": fake_parking.count_places,
        "opened": fake_parking.opened
    }

    with app.app_context():
        count_before = db.session.scalar(select(func.count()).select_from(Parking))

    resp = client.post("/parkings", json=data)

    assert resp.status_code == 201
    with app.app_context():
        count_after = db.session.scalar(select(func.count()).select_from(Parking))
        assert count_after == count_before + 1
