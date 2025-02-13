"""
    CRUD tests (CREATE ONLY) for the project model
"""

import pytest
from api.schemas.project import ProjectCreateSchema
from crud.project import crud_project
from exceptions import InsufficientPermissionsError
from exceptions import ProjectAlreadyExistsError
from exceptions import UserDoesNotExistError
from sqlalchemy.orm import Session

from tests.utils.project import get_test_project
from tests.utils.user import get_test_admin_user
from tests.utils.user import get_test_guest_user
from tests.utils.user import get_test_super_user
from tests.utils.user import get_test_user
from tests.utils.utils import random_manufacturer
from tests.utils.utils import random_note
from tests.utils.utils import random_product_number
from tests.utils.utils import random_project


def test_create_project_normal_user(db: Session) -> None:
    """
    Test the creation of a project by a normal user.
    This test performs the following steps:

    1. Preparation: Generate test data including a test user, project number, product number, customer, and description.
    2. Ensure the generated project number is unique.
    3. Create a ProjectCreateSchema object with the generated test data.
    4. Call the CRUD method to create the project in the database.
    5. Validate that the created project has the expected attributes and is associated with the test user.

    Args:
        db (Session): The database session used for the test.

    Asserts:
        - The created project's attributes match the generated test data.
        - The created project is active.
        - The created project is associated with the test user.
    """

    # ----------------------------------------------
    # CREATE PROJECT: PREPARATION
    # ----------------------------------------------

    t_normal_user = get_test_user(db)
    t_number = random_project()
    t_product_number = random_product_number()
    t_customer = random_manufacturer()
    t_description = random_note()

    while crud_project.get_by_number(db, number=t_number):
        t_number = random_project()

    t_project_in = ProjectCreateSchema(
        number=t_number,
        product_number=t_product_number,
        customer=t_customer,
        description=t_description,
        designated_user_id=t_normal_user.id,
        is_active=True,
    )

    # ----------------------------------------------
    # CREATE PROJECT: METHODS TO TEST
    # ----------------------------------------------

    project = crud_project.create(db=db, db_obj_user=t_normal_user, obj_in=t_project_in)

    # ----------------------------------------------
    # CREATE PROJECT: VALIDATION
    # ----------------------------------------------

    assert project.number == t_number
    assert project.product_number == t_product_number
    assert project.customer == t_customer
    assert project.description == t_description
    assert project.designated_user_id == t_normal_user.id
    assert project.is_active is True

    assert project in t_normal_user.projects


def test_create_project_normal_user_different_designated_user(db: Session) -> None:
    """
    Test the creation of a project by a normal user with a different designated user.

    This test performs the following steps:
    1. Preparation:
        - Retrieve a test normal user and a test admin user from the database.
        - Generate random values for project number, product number, customer, and description.
        - Ensure the generated project number is unique.
        - Create a ProjectCreateSchema instance with the generated values and the admin user as the designated user.
    2. Methods to Test:
        - Create a project using the normal user and the prepared ProjectCreateSchema instance.
    3. Validation:
        - Assert that the designated user ID of the created project is the normal user's ID.
        - Assert that the created project is in the normal user's projects.
        - Assert that the created project is not in the admin user's projects.

    Args:
        db (Session): The database session used for the test.
    """

    # ----------------------------------------------
    # CREATE PROJECT: PREPARATION
    # ----------------------------------------------

    t_normal_user = get_test_user(db)
    t_admin_user = get_test_admin_user(db)

    t_number = random_project()
    t_product_number = random_product_number()
    t_customer = random_manufacturer()
    t_description = random_note()

    while crud_project.get_by_number(db, number=t_number):
        t_number = random_project()

    t_project_in = ProjectCreateSchema(
        number=t_number,
        product_number=t_product_number,
        customer=t_customer,
        description=t_description,
        designated_user_id=t_admin_user.id,
        is_active=True,
    )

    # ----------------------------------------------
    # CREATE PROJECT: METHODS TO TEST
    # ----------------------------------------------

    project = crud_project.create(db=db, db_obj_user=t_normal_user, obj_in=t_project_in)

    # ----------------------------------------------
    # CREATE PROJECT: VALIDATION
    # ----------------------------------------------

    assert project.designated_user_id == t_normal_user.id
    assert project in t_normal_user.projects
    assert project not in t_admin_user.projects


def test_create_project_super_user(db: Session) -> None:
    """
    Test the creation of a project by a super user.
    This test performs the following steps:

    1. Preparation: Create test users (normal user and super user) and generate random project details.
    2. Ensure the generated project number is unique.
    3. Create a ProjectCreateSchema object with the generated details.
    4. Call the `crud_project.create` method to create the project using the super user.
    5. Validate that the created project's details match the input details.
    6. Verify that the created project is associated with the normal user.

    Args:
        db (Session): The database session used for the test.

    Asserts:
        - The created project's number, product number, customer, description, designated user ID, and active status match the input details.
        - The created project is associated with the normal user.
    """

    # ----------------------------------------------
    # CREATE PROJECT: PREPARATION
    # ----------------------------------------------

    t_normal_user = get_test_user(db)
    t_super_user = get_test_super_user(db)

    t_number = random_project()
    t_product_number = random_product_number()
    t_customer = random_manufacturer()
    t_description = random_note()

    while crud_project.get_by_number(db, number=t_number):
        t_number = random_project()

    t_project_in = ProjectCreateSchema(
        number=t_number,
        product_number=t_product_number,
        customer=t_customer,
        description=t_description,
        designated_user_id=t_normal_user.id,
        is_active=True,
    )

    # ----------------------------------------------
    # CREATE PROJECT: METHODS TO TEST
    # ----------------------------------------------

    project = crud_project.create(db=db, db_obj_user=t_super_user, obj_in=t_project_in)

    # ----------------------------------------------
    # CREATE PROJECT: VALIDATION
    # ----------------------------------------------

    assert project.number == t_number
    assert project.product_number == t_product_number
    assert project.customer == t_customer
    assert project.description == t_description
    assert project.designated_user_id == t_normal_user.id
    assert project.is_active is True

    assert project in t_normal_user.projects


def test_create_project_admin_user(db: Session) -> None:
    """
    Test the creation of a project by an admin user.
    This test performs the following steps:

    1. Preparation:
        - Retrieve a test normal user and a test admin user from the database.
        - Generate random values for project number, product number, customer, and description.
        - Ensure the generated project number is unique.
        - Create a ProjectCreateSchema object with the generated values and the normal user's ID.
    2. Methods to Test:
        - Use the CRUD operation to create a project in the database with the admin user and the ProjectCreateSchema object.
    3. Validation:
        - Assert that the created project's attributes match the generated values.
        - Assert that the project is active.
        - Assert that the project is associated with the normal user.

    Args:
        db (Session): The database session used for the test.

    Returns:
        None
    """

    # ----------------------------------------------
    # CREATE PROJECT: PREPARATION
    # ----------------------------------------------

    t_normal_user = get_test_user(db)
    t_admin_user = get_test_admin_user(db)

    t_number = random_project()
    t_product_number = random_product_number()
    t_customer = random_manufacturer()
    t_description = random_note()

    while crud_project.get_by_number(db, number=t_number):
        t_number = random_project()

    t_project_in = ProjectCreateSchema(
        number=t_number,
        product_number=t_product_number,
        customer=t_customer,
        description=t_description,
        designated_user_id=t_normal_user.id,
        is_active=True,
    )

    # ----------------------------------------------
    # CREATE PROJECT: METHODS TO TEST
    # ----------------------------------------------

    project = crud_project.create(db=db, db_obj_user=t_admin_user, obj_in=t_project_in)

    # ----------------------------------------------
    # CREATE PROJECT: VALIDATION
    # ----------------------------------------------

    assert project.number == t_number
    assert project.product_number == t_product_number
    assert project.customer == t_customer
    assert project.description == t_description
    assert project.designated_user_id == t_normal_user.id
    assert project.is_active is True

    assert project in t_normal_user.projects


def test_create_project_guest_user(db: Session) -> None:
    """
    Test the creation of a project by a guest user.

    This test ensures that a guest user does not have sufficient permissions
    to create a project. It prepares the necessary data, including a guest user,
    project number, product number, customer, and description. It then attempts
    to create a project using the guest user's credentials and expects an
    InsufficientPermissionsError to be raised.

    Args:
        db (Session): The database session used for the test.

    Raises:
        InsufficientPermissionsError: If the guest user attempts to create a project.
    """

    # ----------------------------------------------
    # CREATE PROJECT: PREPARATION
    # ----------------------------------------------

    t_guest_user = get_test_guest_user(db)

    t_number = random_project()
    t_product_number = random_product_number()
    t_customer = random_manufacturer()
    t_description = random_note()

    while crud_project.get_by_number(db, number=t_number):
        t_number = random_project()

    t_project_in = ProjectCreateSchema(
        number=t_number,
        product_number=t_product_number,
        customer=t_customer,
        description=t_description,
        designated_user_id=t_guest_user.id,
        is_active=True,
    )

    # ----------------------------------------------
    # CREATE PROJECT: METHODS TO TEST
    # ----------------------------------------------

    with pytest.raises(InsufficientPermissionsError):
        crud_project.create(db=db, db_obj_user=t_guest_user, obj_in=t_project_in)


def test_create_project_already_existing(db: Session) -> None:
    """
    Test case for creating a project that already exists in the database.

    This test ensures that attempting to create a project with a number that
    already exists in the database raises a ProjectAlreadyExistsError.

    Args:
        db (Session): The database session used for the test.

    Steps:
        1. Retrieve a test user and an existing project's number from the database.
        2. Generate random values for product number, customer, and description.
        3. Create a ProjectCreateSchema object with the existing project number and
           other generated values.
        4. Attempt to create a new project using the crud_project.create method.
        5. Verify that a ProjectAlreadyExistsError is raised.
    """

    # ----------------------------------------------
    # CREATE PROJECT: PREPARATION
    # ----------------------------------------------

    t_normal_user = get_test_user(db)
    t_number = get_test_project(db).number

    t_product_number = random_product_number()
    t_customer = random_manufacturer()
    t_description = random_note()

    t_project_in = ProjectCreateSchema(
        number=t_number,
        product_number=t_product_number,
        customer=t_customer,
        description=t_description,
        designated_user_id=t_normal_user.id,
        is_active=True,
    )

    # ----------------------------------------------
    # CREATE PROJECT: METHODS TO TEST
    # ----------------------------------------------
    with pytest.raises(ProjectAlreadyExistsError):
        crud_project.create(db=db, db_obj_user=t_normal_user, obj_in=t_project_in)


def test_create_project_missing_designated_user(db: Session) -> None:
    """
    Test case for creating a project with a missing designated user.

    This test ensures that attempting to create a project with a non-existent
    designated user raises a UserDoesNotExistError.

    Steps:
        1. Prepare test data including a random project number, product number,
           customer, and description.
        2. Ensure the project number is unique.
        3. Create a ProjectCreateSchema object with the test data and a
           designated_user_id that does not exist (9999999).
        4. Attempt to create the project using the crud_project.create method
           and assert that a UserDoesNotExistError is raised.

    Args:
        db (Session): The database session used for the test.

    Raises:
        UserDoesNotExistError: If the designated user does not exist.
    """

    # ----------------------------------------------
    # CREATE PROJECT: PREPARATION
    # ----------------------------------------------

    t_admin_user = get_test_admin_user(db)

    t_number = random_project()
    t_product_number = random_product_number()
    t_customer = random_manufacturer()
    t_description = random_note()

    while crud_project.get_by_number(db, number=t_number):
        t_number = random_project()

    t_project_in = ProjectCreateSchema(
        number=t_number,
        product_number=t_product_number,
        customer=t_customer,
        description=t_description,
        designated_user_id=9999999,
        is_active=True,
    )

    # ----------------------------------------------
    # CREATE PROJECT: METHODS TO TEST
    # ----------------------------------------------

    with pytest.raises(UserDoesNotExistError):
        crud_project.create(db=db, db_obj_user=t_admin_user, obj_in=t_project_in)
