import factory
import random
from app.models import Client, Parking
from app.database import db


class ClientFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session = db.session

    name = factory.Faker("first_name")
    surname = factory.Faker("last_name")
    # credit_card: либо строка с цифрами, либо None
    credit_card = factory.LazyFunction(
        lambda: str(random.randint(1000, 9999))
        if random.choice([True, False]) else None
    )
    car_number = factory.Faker("bothify", text="?###??##")


class ParkingFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Parking
        sqlalchemy_session = db.session

    address = factory.Faker("address")
    opened = factory.Iterator([True, False])
    count_places = factory.Faker("random_int", min=5, max=50)

    # count_available_places берет значение из count_places этого же объекта
    count_available_places = factory.LazyAttribute(lambda obj: obj.count_places)
