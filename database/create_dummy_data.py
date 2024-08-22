import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import cfg

if not cfg.debug:
    raise Exception("Debug mode is not enabled.")

from random import randint

import faker_commerce
from api.schemas.bought_item import BoughtItemCreateSchema
from crud.bought_item import crud_bought_item
from crud.user import crud_user
from faker import Faker

from app.db.session import SessionLocal

db = SessionLocal()
crud_user = crud_user.get_by_email(db, email=cfg.init.mail)

fake = Faker()
fake.add_provider(faker_commerce.Provider)
Faker.seed(randint(0, 9999))

count = 0
projects = 10
items = 20

if crud_user:
    for i in range(projects):
        project = fake.bothify(text="P23###")
        for j in range(items):
            name = fake.ecommerce_name()
            definition = fake.bothify(text="????-########")
            manufacturer = fake.company()
            partnumber = f"{name} - {definition} - {manufacturer}"
            quantity = randint(1, 100)

            data_in = BoughtItemCreateSchema(  # type: ignore
                project=project,
                quantity=quantity,
                unit=cfg.items.bought.units.default,
                partnumber=partnumber,
                definition=definition,
                manufacturer=manufacturer,
            )
            item = crud_bought_item.create(db, db_obj_user=crud_user, obj_in=data_in)
            count += 1

            print(f"{count}/{projects * items}: Created item {partnumber!r}")
