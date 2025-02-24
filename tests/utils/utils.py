import random
import string
from typing import Dict

import faker_commerce
from faker import Faker
from fastapi.testclient import TestClient

from app.config import cfg
from app.const import SYSTEM_USER

fake = Faker()
fake.add_provider(faker_commerce.Provider)
Faker.seed(random.randint(0, 999))


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_lower_string()}@glados.com"


def random_username() -> str:
    return f"test_{random.randint(1000, 9999):06d}"


def random_project() -> str:
    return f"P{random.randint(10000, 99999):05d}"


def random_product_number() -> str:
    return f"M{random.randint(10000, 99999):05d}"


def random_name() -> str:
    return fake.name()


def random_bought_item_name() -> str:
    return fake.ecommerce_name()


def random_bought_item_order_number() -> str:
    return fake.isbn10()


def random_manufacturer() -> str:
    return fake.company()


def random_supplier() -> str:
    return fake.company()


def random_note() -> str:
    return fake.text()
