from sqlalchemy.orm import Session

from app.api.schemas.project import ProjectCreateSchema
from app.config import cfg
from app.crud.project import crud_project
from app.crud.user import crud_user
from app.db.models import ProjectModel
from app.db.models import UserModel
from tests.utils.user import TEST_ADMIN_USERNAME
from tests.utils.user import TEST_USERNAME
from tests.utils.user import get_test_admin_user
from tests.utils.user import get_test_user
from tests.utils.utils import random_lower_string
from tests.utils.utils import random_project

TEST_NUMBER = "P24000"
TEST_PRODUCT = "M24000"
TEST_CUSTOMER = "TEST"
TEST_DESC = "Project Test"


def create_project(
    db: Session,
    user: UserModel,
    number: str,
    product_number: str | None,
    customer: str,
    description: str,
    designated_user_id: int,
    is_active: bool,
):
    project_in = ProjectCreateSchema(
        number=number,
        product_number=product_number,
        customer=customer,
        description=description,
        designated_user_id=designated_user_id,
        is_active=is_active,
    )
    return crud_project.create(db=db, db_obj_user=user, obj_in=project_in)


def create_random_project(db: Session) -> ProjectModel:
    admin_user = crud_user.get_by_username(db, username=TEST_ADMIN_USERNAME)
    normal_user = crud_user.get_by_username(db, username=TEST_USERNAME)
    if not admin_user:
        admin_user = get_test_admin_user(db)
    if not normal_user:
        normal_user = get_test_user(db)
    number = random_project()

    while crud_project.get_by_number(db, number=number):
        number = random_project()

    return create_project(
        db,
        user=admin_user,
        number=number,
        product_number=None,
        customer=random_lower_string(),
        description=random_lower_string(),
        designated_user_id=normal_user.id,
        is_active=True,
    )


def get_test_project(db: Session) -> ProjectModel:
    """Returns the test project, creates it if doesn't exists."""
    admin_user = crud_user.get_by_username(db, username=TEST_ADMIN_USERNAME)
    normal_user = crud_user.get_by_username(db, username=TEST_USERNAME)
    if not admin_user:
        admin_user = get_test_admin_user(db)
    if not normal_user:
        normal_user = get_test_user(db)

    project = crud_project.get_by_number(db, number=TEST_NUMBER)
    if not project:
        return create_project(
            db,
            user=admin_user,
            number=TEST_NUMBER,
            product_number=TEST_PRODUCT,
            customer=TEST_CUSTOMER,
            description=TEST_DESC,
            designated_user_id=normal_user.id,
            is_active=True,
        )
    return project
