import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import cfg

if not cfg.debug:
    raise Exception("Debug mode is not enabled.")

from random import randint

import faker_commerce
from api.schemas.bought_item import BoughtItemCreateSchema
from api.schemas.project import ProjectCreateSchema
from crud.bought_item import crud_bought_item
from crud.project import crud_project
from crud.user import crud_user
from faker import Faker

from app.db.session import SessionLocal

db = SessionLocal()
system_user = crud_user.get_by_email(db, email=cfg.init.mail)

fake = Faker()
fake.add_provider(faker_commerce.Provider)
Faker.seed(randint(0, 9999))

count = 0
projects = 10
items = 20

if system_user:
    for i in range(projects):
        project_in = ProjectCreateSchema(
            number=fake.bothify(text="P24###"),
            product_number=fake.bothify(text="M24###"),
            customer=fake.company(),
            description=fake.text(),
            designated_user_id=system_user.id,
        )
        project = crud_project.create(db, db_obj_user=system_user, obj_in=project_in)

        for j in range(items):
            name = fake.ecommerce_name()
            order_number = fake.bothify(text="????-########")
            manufacturer = fake.company()
            partnumber = f"{name} - {order_number} - {manufacturer}"
            quantity = randint(1, 100)

            data_in = BoughtItemCreateSchema(  # type: ignore
                project_id=project.id,
                quantity=quantity,
                unit=cfg.items.bought.units.default,
                partnumber=partnumber,
                order_number=order_number,
                manufacturer=manufacturer,
            )
            item = crud_bought_item.create(db, db_obj_user=system_user, obj_in=data_in)
            count += 1

            print(f"{count}/{projects * items}: Created item {partnumber!r}")
