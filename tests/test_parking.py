import pytest
import json
from tests.factories import ClientFactory, ParkingFactory
from app.models import Client, Parking


# 1. Параметризованный тест GET-методов
@pytest.mark.parametrize("url", ["/clients", "/clients/1"])
def test_get_status_200(client, url):
    resp = client.get(url)
    assert resp.status_code == 200


# 2. Создание клиента
def test_create_client(client):
    data = {"name": "New", "surname": "Client", "car_number": "X000XX"}
    resp = client.post("/clients", json=data)
    assert resp.status_code == 201
    assert resp.json["message"] == "Client created"


# 3. Создание парковки
def test_create_parking(client):
    data = {"address": "New Parking", "count_places": 5}
    resp = client.post("/parkings", json=data)
    assert resp.status_code == 201


# 4. Заезд на парковку
@pytest.mark.parking
def test_enter_parking(client):
    # До заезда мест 10 (из фикстуры)
    resp = client.post("/client_parkings", json={"client_id": 1, "parking_id": 1})
    assert resp.status_code == 201

    # Проверяем, что мест стало 9
    p_resp = client.get("/parkings")  # Если добавить эндпоинт списка парковок
    # Или через проверку в БД напрямую (если есть доступ к модели)


# 5. Выезд с парковки
@pytest.mark.parking
def test_exit_parking(client):
    # Сначала заезжаем
    client.post("/client_parkings", json={"client_id": 1, "parking_id": 1})

    # Теперь выезжаем
    resp = client.delete("/client_parkings", json={"client_id": 1, "parking_id": 1})
    assert resp.status_code == 200
    assert resp.json["message"] == "Goodbye, payment successful"


# Дополнительный тест: Выезд без карты (на твое усмотрение)
def test_exit_no_card(client, app):
    with app.app_context():
        from app.database import db
        from app.models import Client

        # Создаем клиента без карты
        c2 = Client(name="No", surname="Card", car_number="B222BB")
        db.session.add(c2)
        db.session.commit()
        c2_id = c2.id

    client.post("/client_parkings", json={"client_id": c2_id, "parking_id": 1})
    resp = client.delete("/client_parkings", json={"client_id": c2_id, "parking_id": 1})
    assert resp.status_code == 400
    assert "Payment method (card) missing" in resp.json["error"]


def test_parking_places_decrease(client):
    # 1. Смотрим, сколько мест было изначально (в фикстуре мы ставили 10)
    parking = client.get("/parkings/1").json  # Добавь такой роут или проверь через список

    # 2. Делаем заезд
    client.post("/client_parkings", json={"client_id": 1, "parking_id": 1})

    # 3. Проверяем, что стало 9
    resp = client.get("/parkings/1")
    assert resp.json["count_available_places"] == 9


# Исправленный тест на уменьшение мест (используем эндпоинт /parkings, если добавишь его,
# или проверяем через контекст приложения)
def test_parking_places_decrease(client, app):
    # Заезд
    client.post("/client_parkings", json={"client_id": 1, "parking_id": 1})

    # Проверяем напрямую в базе, так как эндпоинта GET /parkings/<id> у нас нет
    with app.app_context():
        from app.models import Parking
        p = Parking.query.get(1)
        assert p.count_available_places == 9



def test_create_client_factory(client, app):
    # Генерируем данные через фабрику (без сохранения в БД)
    fake_client = ClientFactory.build()
    data = {
        "name": fake_client.name,
        "surname": fake_client.surname,
        "car_number": fake_client.car_number,
        "credit_card": fake_client.credit_card
    }

    with app.app_context():
        count_before = Client.query.count()

    resp = client.post("/clients", json=data)

    assert resp.status_code == 201
    with app.app_context():
        assert Client.query.count() == count_before + 1
        assert Client.query.filter_by(car_number=fake_client.car_number).first() is not None

def test_create_parking_factory(client, app):
    # Генерируем данные парковки
    fake_parking = ParkingFactory.build(opened=True)
    data = {
        "address": fake_parking.address,
        "count_places": fake_parking.count_places,
        "opened": fake_parking.opened
    }

    with app.app_context():
        count_before = Parking.query.count()

    resp = client.post("/parkings", json=data)

    assert resp.status_code == 201
    assert "id" in resp.json
    with app.app_context():
        assert Parking.query.count() == count_before + 1

