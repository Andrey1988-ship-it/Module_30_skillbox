from flask import Blueprint, request, jsonify
from .database import db
from .models import Client, Parking, ClientParking
from datetime import datetime
from sqlalchemy import select  # Импортируем select для запросов списка

api_bp = Blueprint('api', __name__)


# POST /clients — создание клиента
@api_bp.route('/clients', methods=['POST'])
def create_client():
    data = request.json
    new_client = Client(
        name=data['name'],
        surname=data['surname'],
        credit_card=data.get('credit_card'),
        car_number=data.get('car_number')
    )
    db.session.add(new_client)
    db.session.commit()
    return jsonify({"message": "Client created",
                    "id": new_client.id}), 201


# POST /parkings — создание парковки
@api_bp.route('/parkings', methods=['POST'])
def create_parking():
    data = request.json
    new_parking = Parking(
        address=data['address'],
        opened=data.get('opened', True),
        count_places=data['count_places'],
        count_available_places=data['count_places']
    )
    db.session.add(new_parking)
    db.session.commit()
    # Убрали лишнюю запятую и добавили 201
    return jsonify({"message": "Parking created",
                    "id": new_parking.id}), 201


# GET /clients — список всех клиентов
@api_bp.route('/clients', methods=['GET'])
def get_clients():
    # НОВЫЙ СТИЛЬ: используем select
    clients = db.session.execute(select(Client)).scalars().all()
    return jsonify([{"id": c.id, "name": c.name,
                     "car_number": c.car_number} for c in clients]), 200


# GET /clients/<id> — инфо о клиенте
@api_bp.route('/clients/<int:client_id>', methods=['GET'])
def get_client(client_id):
    # НОВЫЙ СТИЛЬ: db.get_or_404 теперь вызывается от объекта db
    client = db.get_or_404(Client, client_id)
    return jsonify({"id": client.id, "name": client.name,
                    "surname": client.surname,
                    "card": client.credit_card}), 200


# POST /clients и /parkings остаются без изменений, там db.session.add - это актуальный метод

# POST /client_parkings — заезд
@api_bp.route('/client_parkings', methods=['POST'])
def enter_parking():
    data = request.json
    client_id = data['client_id']
    parking_id = data['parking_id']

    # НОВЫЙ СТИЛЬ
    parking = db.get_or_404(Parking, parking_id)

    if not parking.opened:
        return jsonify({"error": "Parking is closed"}), 400
    if parking.count_available_places <= 0:
        return jsonify({"error": "No available places"}), 400

    new_log = ClientParking(client_id=client_id,
                            parking_id=parking_id, time_in=datetime.now())
    parking.count_available_places -= 1

    db.session.add(new_log)
    db.session.commit()
    return jsonify({"message": "Welcome"}), 201


# DELETE /client_parkings — выезд
@api_bp.route('/client_parkings', methods=['DELETE'])
def exit_parking():
    data = request.json
    client_id = data['client_id']
    parking_id = data['parking_id']

    # НОВЫЙ СТИЛЬ: используем select с фильтрами
    stmt = select(ClientParking).where(
        ClientParking.client_id == client_id,
        ClientParking.parking_id == parking_id,
        ClientParking.time_out.is_(None)
    )
    log = db.session.execute(stmt).scalar_one_or_none()

    if not log:
        return jsonify({"error": "Active parking session not found"}), 404

    # НОВЫЙ СТИЛЬ: db.session.get вместо Model.query.get
    client = db.session.get(Client, client_id)

    if not client.credit_card:
        return jsonify({"error": "Payment method (card) missing"}), 400

    log.time_out = datetime.now()
    parking = db.session.get(Parking, parking_id)
    parking.count_available_places += 1

    db.session.commit()
    return jsonify({"message": "Goodbye, payment successful"}), 200
