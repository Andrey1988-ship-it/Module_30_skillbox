from flask import Blueprint, request, jsonify
from .database import db
from .models import Client, Parking, ClientParking
from datetime import datetime

# Создаем чертеж (Blueprint) для роутов
api_bp = Blueprint('api', __name__)


# GET /clients — список всех клиентов
@api_bp.route('/clients', methods=['GET'])
def get_clients():
    clients = Client.query.all()
    return jsonify([{"id": c.id, "name": c.name, "car_number": c.car_number} for c in clients]), 200


# GET /clients/<id> — инфо о клиенте
@api_bp.route('/clients/<int:client_id>', methods=['GET'])
def get_client(client_id):
    client = Client.query.get_or_404(client_id)
    return jsonify({"id": client.id, "name": client.name, "surname": client.surname, "card": client.credit_card}), 200


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
    return jsonify({"message": "Client created", "id": new_client.id}), 201


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
    return jsonify({"message": "Parking created", "id": new_parking.id}), 201


# POST /client_parkings — заезд
@api_bp.route('/client_parkings', methods=['POST'])
def enter_parking():
    data = request.json
    client_id = data['client_id']
    parking_id = data['parking_id']

    parking = Parking.query.get_or_404(parking_id)

    # Проверки: открыта ли и есть ли места
    if not parking.opened:
        return jsonify({"error": "Parking is closed"}), 400
    if parking.count_available_places <= 0:
        return jsonify({"error": "No available places"}), 400

    # Фиксируем заезд
    new_log = ClientParking(client_id=client_id, parking_id=parking_id, time_in=datetime.now())
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

    log = ClientParking.query.filter_by(client_id=client_id, parking_id=parking_id, time_out=None).first()
    if not log:
        return jsonify({"error": "Active parking session not found"}), 404

    client = Client.query.get(client_id)
    # Проверка карты перед выездом
    if not client.credit_card:
        return jsonify({"error": "Payment method (card) missing"}), 400

    # Фиксируем выезд
    log.time_out = datetime.now()
    parking = Parking.query.get(parking_id)
    parking.count_available_places += 1

    db.session.commit()
    return jsonify({"message": "Goodbye, payment successful"}), 200


