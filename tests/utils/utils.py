import random
import string
from typing import Dict

from faker import Faker
from fastapi.testclient import TestClient

from app.config import cfg
from app.const import API_WEB_V1
from app.const import SYSTEM_USER

fake = Faker()
Faker.seed(random.randint(0, 999))


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_lower_string()}@glados.com"


def random_username() -> str:
    return f"t{random.randint(1, 999999):06d}"


def random_name() -> str:
    return fake.name()


def random_project() -> str:
    return f"P{random.randint(1, 99999):05d}"


def get_superuser_token_headers(client: TestClient) -> Dict[str, str]:
    login_data = {
        "username": SYSTEM_USER,
        "password": cfg.init.password,
    }
    r = client.post(f"{API_WEB_V1}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
