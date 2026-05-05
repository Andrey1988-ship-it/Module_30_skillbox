from datetime import datetime
from .database import db


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from flask_sqlalchemy.model import Model
    Base = Model
else:
    Base = db.Model


class Client(db.Model):  # type: ignore
    __tablename__ = "client"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    credit_card = db.Column(db.String(50))
    car_number = db.Column(db.String(10))


class Parking(db.Model):  # type: ignore
    __tablename__ = "parking"
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), nullable=False)
    opened = db.Column(db.Boolean, default=True)
    count_places = db.Column(db.Integer, nullable=False)
    count_available_places = db.Column(db.Integer, nullable=False)


class ClientParking(db.Model):  # type: ignore
    __tablename__ = "client_parking"
    __table_args__ = (
        db.UniqueConstraint('client_id', 'parking_id', name='unique_client_parking'),
    )
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"))
    parking_id = db.Column(db.Integer, db.ForeignKey("parking.id"))
    time_in = db.Column(db.DateTime, default=datetime.now)
    time_out = db.Column(db.DateTime)


