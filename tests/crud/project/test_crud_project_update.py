"""
    CRUD tests (UPDATE ONLY) for the project model
"""

import pytest
from api.schemas.project import ProjectCreateSchema
from api.schemas.project import ProjectUpdateSchema
from crud.project import crud_project
from exceptions import InsufficientPermissionsError
from exceptions import ProjectAlreadyExistsError
from exceptions import UserDoesNotExistError
from sqlalchemy.orm import Session

from tests.utils.project import get_test_project
from tests.utils.user import create_random_user
from tests.utils.user import get_test_admin_user
from tests.utils.user import get_test_guest_user
from tests.utils.user import get_test_super_user
from tests.utils.user import get_test_user
from tests.utils.utils import random_manufacturer
from tests.utils.utils import random_note
from tests.utils.utils import random_product_number
from tests.utils.utils import random_project


def test_update_project_normal_user(db: Session) -> None:
    """
    Test the update functionality of a project for a normal user.

    This test performs the following steps:
    1. Preparation:
       - Create a test user.
       - Generate random project details for two projects.
       - Ensure the generated project numbers are unique.
       - Create a ProjectCreateSchema instance for the first project.
       - Create a ProjectUpdateSchema instance for the second project.
    2. Methods to Test:
       - Create the first project using the CRUD create method.
       - Update the first project with the details of the second project using the CRUD update method.
    3. Validation:
       - Assert that the updated project exists.
       - Assert that the updated project's ID matches the original project's ID.
       - Assert that the updated project is associated with the test user.

    Args:
        db (Session): The database session used for the test.
    """

    # ----------------------------------------------
    # UPDATE ITEM: PREPARATION
    # ----------------------------------------------

    t_normal_user = get_test_user(db)

    t_number_1 = random_project()
    t_product_number_1 = random_product_number()
    t_customer_1 = random_manufacturer()
    t_description_1 = random_note()

    t_number_2 = random_project()
    t_product_number_2 = random_product_number()
    t_customer_2 = random_manufacturer()
    t_description_2 = random_note()

    while crud_project.get_by_number(db, number=t_number_1):
        t_number_1 = random_project()

    while crud_project.get_by_number(db, number=t_number_2):
        t_number_2 = random_project()

    t_project_1 = ProjectCreateSchema(
        number=t_number_1,
        product_number=t_product_number_1,
        customer=t_customer_1,
        description=t_description_1,
        designated_user_id=t_normal_user.id,
        is_active=True,
    )

    t_project_2 = ProjectUpdateSchema(
        number=t_number_2,
        product_number=t_product_number_2,
        customer=t_customer_2,
        description=t_description_2,
        designated_user_id=t_normal_user.id,
        is_active=True,
    )

    project_1 = crud_project.create(db=db, db_obj_user=t_normal_user, obj_in=t_project_1)
    assert project_1 in t_normal_user.projects

    # ----------------------------------------------
    # UPDATE ITEM: METHODS TO TEST
    # ----------------------------------------------

    project_2 = crud_project.update(db, db_obj_user=t_normal_user, db_obj=project_1, obj_in=t_project_2)

    # ----------------------------------------------
    # UPDATE ITEM: VALIDATION
    # ----------------------------------------------

    assert project_2
    assert project_2.id == project_1.id
    assert project_2 in t_normal_user.projects


def test_update_project_admin_user(db: Session) -> None:
    """
    Test the update functionality of a project for an admin user.

    This test performs the following steps:
    1. Preparation:
        - Create a normal user and an admin user.
        - Generate random project numbers, product numbers, customers, and descriptions.
        - Ensure the generated project numbers are unique.
        - Create a ProjectCreateSchema instance with the generated data.
        - Create a ProjectUpdateSchema instance with different generated data.
    2. Methods to Test:
        - Create a project using the admin user and the ProjectCreateSchema instance.
        - Update the created project using the admin user and the ProjectUpdateSchema instance.
    3. Validation:
        - Verify that the project was created and associated with the normal user.
        - Verify that the project was updated and associated with the admin user.
        - Ensure the project ID remains the same after the update.
    """

    # ----------------------------------------------
    # UPDATE ITEM: PREPARATION
    # ----------------------------------------------

    t_normal_user = get_test_user(db)
    t_admin_user = get_test_admin_user(db)

    t_number_1 = random_project()
    t_product_number_1 = random_product_number()
    t_customer_1 = random_manufacturer()
    t_description_1 = random_note()

    t_number_2 = random_project()
    t_product_number_2 = random_product_number()
    t_customer_2 = random_manufacturer()
    t_description_2 = random_note()

    while crud_project.get_by_number(db, number=t_number_1):
        t_number_1 = random_project()

    while crud_project.get_by_number(db, number=t_number_2):
        t_number_2 = random_project()

    t_project_1 = ProjectCreateSchema(
        number=t_number_1,
        product_number=t_product_number_1,
        customer=t_customer_1,
        description=t_description_1,
        designated_user_id=t_normal_user.id,
        is_active=True,
    )

    t_project_2 = ProjectUpdateSchema(
        number=t_number_2,
        product_number=t_product_number_2,
        customer=t_customer_2,
        description=t_description_2,
        designated_user_id=t_admin_user.id,
        is_active=True,
    )

    project_1 = crud_project.create(db=db, db_obj_user=t_admin_user, obj_in=t_project_1)
    assert project_1 in t_normal_user.projects
    assert project_1 not in t_admin_user.projects

    # ----------------------------------------------
    # UPDATE ITEM: METHODS TO TEST
    # ----------------------------------------------

    project_2 = crud_project.update(db, db_obj_user=t_admin_user, db_obj=project_1, obj_in=t_project_2)

    # ----------------------------------------------
    # UPDATE ITEM: VALIDATION
    # ----------------------------------------------

    assert project_2
    assert project_2.id == project_1.id

    assert project_2 not in t_normal_user.projects
    assert project_2 in t_admin_user.projects


def test_update_project_of_another_user_as_normal_user(db: Session) -> None:
    """
    Test case for updating a project of another user as a normal user.

    This test ensures that a normal user cannot update a project that belongs to another user.
    It performs the following steps:
    1. Prepares test data by creating two normal users and two projects with random attributes.
    2. Ensures that the project numbers are unique.
    3. Creates a project for the first normal user.
    4. Asserts that the created project is associated with the first normal user and not with the second normal user.
    5. Attempts to update the project of the first normal user using the second normal user.
    6. Asserts that an InsufficientPermissionsError is raised when the second normal user tries to update the project.

    Args:
        db (Session): The database session used for the test.

    Raises:
        InsufficientPermissionsError: If the second normal user tries to update the project of the first normal user.
    """

    # ----------------------------------------------
    # UPDATE ITEM: PREPARATION
    # ----------------------------------------------

    t_normal_user = get_test_user(db)
    t_another_normal_user = create_random_user(db)

    t_number_1 = random_project()
    t_product_number_1 = random_product_number()
    t_customer_1 = random_manufacturer()
    t_description_1 = random_note()

    t_number_2 = random_project()
    t_product_number_2 = random_product_number()
    t_customer_2 = random_manufacturer()
    t_description_2 = random_note()

    while crud_project.get_by_number(db, number=t_number_1):
        t_number_1 = random_project()

    while crud_project.get_by_number(db, number=t_number_2):
        t_number_2 = random_project()

    t_project_1 = ProjectCreateSchema(
        number=t_number_1,
        product_number=t_product_number_1,
        customer=t_customer_1,
        description=t_description_1,
        designated_user_id=t_normal_user.id,
        is_active=True,
    )

    t_project_2 = ProjectUpdateSchema(
        number=t_number_2,
        product_number=t_product_number_2,
        customer=t_customer_2,
        description=t_description_2,
        designated_user_id=t_another_normal_user.id,
        is_active=True,
    )

    project_1 = crud_project.create(db=db, db_obj_user=t_normal_user, obj_in=t_project_1)
    assert project_1 in t_normal_user.projects
    assert project_1 not in t_another_normal_user.projects

    # ----------------------------------------------
    # UPDATE ITEM: METHODS TO TEST
    # ----------------------------------------------

    with pytest.raises(InsufficientPermissionsError):
        crud_project.update(db, db_obj_user=t_another_normal_user, db_obj=project_1, obj_in=t_project_2)


def test_update_project_of_super_user_as_normal_user(db: Session) -> None:
    """
    Test case for updating a project created by a super user as a normal user.

    This test ensures that a normal user cannot update a project that was created by a super user.
    It performs the following steps:
    1. Prepares test data including normal user, super user, and two sets of project details.
    2. Creates a project with the super user.
    3. Asserts that the created project is associated with the super user and not with the normal user.
    4. Attempts to update the project with the normal user and expects an InsufficientPermissionsError.

    Args:
        db (Session): The database session used for the test.

    Raises:
        InsufficientPermissionsError: If the normal user tries to update the project created by the super user.
    """

    # ----------------------------------------------
    # UPDATE ITEM: PREPARATION
    # ----------------------------------------------

    t_normal_user = get_test_user(db)
    t_super_user = get_test_super_user(db)

    t_number_1 = random_project()
    t_product_number_1 = random_product_number()
    t_customer_1 = random_manufacturer()
    t_description_1 = random_note()

    t_number_2 = random_project()
    t_product_number_2 = random_product_number()
    t_customer_2 = random_manufacturer()
    t_description_2 = random_note()

    while crud_project.get_by_number(db, number=t_number_1):
        t_number_1 = random_project()

    while crud_project.get_by_number(db, number=t_number_2):
        t_number_2 = random_project()

    t_project_1 = ProjectCreateSchema(
        number=t_number_1,
        product_number=t_product_number_1,
        customer=t_customer_1,
        description=t_description_1,
        designated_user_id=t_super_user.id,
        is_active=True,
    )

    t_project_2 = ProjectUpdateSchema(
        number=t_number_2,
        product_number=t_product_number_2,
        customer=t_customer_2,
        description=t_description_2,
        designated_user_id=t_normal_user.id,
        is_active=True,
    )

    project_1 = crud_project.create(db=db, db_obj_user=t_super_user, obj_in=t_project_1)
    assert project_1 not in t_normal_user.projects
    assert project_1 in t_super_user.projects

    # ----------------------------------------------
    # UPDATE ITEM: METHODS TO TEST
    # ----------------------------------------------

    with pytest.raises(InsufficientPermissionsError):
        crud_project.update(db, db_obj_user=t_normal_user, db_obj=project_1, obj_in=t_project_2)


def test_update_project_of_admin_user_as_normal_user(db: Session) -> None:
    """
    Test updating a project assigned to an admin user by a normal user.
    This test ensures that a normal user cannot update a project that is
    designated to an admin user. It performs the following steps:

    1. Prepares test data including normal and admin users, and two sets of project details.
    2. Ensures the generated project numbers are unique.
    3. Creates a project assigned to the admin user.
    4. Asserts that the created project is not in the normal user's projects and is in the admin user's projects.
    5. Attempts to update the project using the normal user's credentials and expects an InsufficientPermissionsError to be raised.

    Args:
        db (Session): The database session used for the test.
    """

    # ----------------------------------------------
    # UPDATE ITEM: PREPARATION
    # ----------------------------------------------

    t_normal_user = get_test_user(db)
    t_admin_user = get_test_admin_user(db)

    t_number_1 = random_project()
    t_product_number_1 = random_product_number()
    t_customer_1 = random_manufacturer()
    t_description_1 = random_note()

    t_number_2 = random_project()
    t_product_number_2 = random_product_number()
    t_customer_2 = random_manufacturer()
    t_description_2 = random_note()

    while crud_project.get_by_number(db, number=t_number_1):
        t_number_1 = random_project()

    while crud_project.get_by_number(db, number=t_number_2):
        t_number_2 = random_project()

    t_project_1 = ProjectCreateSchema(
        number=t_number_1,
        product_number=t_product_number_1,
        customer=t_customer_1,
        description=t_description_1,
        designated_user_id=t_admin_user.id,
        is_active=True,
    )

    t_project_2 = ProjectUpdateSchema(
        number=t_number_2,
        product_number=t_product_number_2,
        customer=t_customer_2,
        description=t_description_2,
        designated_user_id=t_normal_user.id,
        is_active=True,
    )

    project_1 = crud_project.create(db=db, db_obj_user=t_admin_user, obj_in=t_project_1)
    assert project_1 not in t_normal_user.projects
    assert project_1 in t_admin_user.projects

    # ----------------------------------------------
    # UPDATE ITEM: METHODS TO TEST
    # ----------------------------------------------

    with pytest.raises(InsufficientPermissionsError):
        crud_project.update(db, db_obj_user=t_normal_user, db_obj=project_1, obj_in=t_project_2)


def test_update_project_number_already_exists(db: Session) -> None:
    """
    Test case for updating a project when the project number already exists.

    This test ensures that attempting to update a project with a number that already exists
    in the database raises a ProjectAlreadyExistsError.

    Steps:
        1. Prepare test data including a normal user, an admin user, and a unique project.
        2. Create a project with a unique number.
        3. Prepare an update schema with a project number that already exists in the database.
        4. Attempt to update the project and verify that a ProjectAlreadyExistsError is raised.

    Args:
        db (Session): The database session used for the test.

    Raises:
        ProjectAlreadyExistsError: If the project number already exists in the database.
    """

    # ----------------------------------------------
    # UPDATE ITEM: PREPARATION
    # ----------------------------------------------

    t_normal_user = get_test_user(db)
    t_admin_user = get_test_admin_user(db)

    t_number_1 = random_project()
    t_product_number_1 = random_product_number()
    t_customer_1 = random_manufacturer()
    t_description_1 = random_note()

    while crud_project.get_by_number(db, number=t_number_1):
        t_number_1 = random_project()

    t_project_1 = ProjectCreateSchema(
        number=t_number_1,
        product_number=t_product_number_1,
        customer=t_customer_1,
        description=t_description_1,
        designated_user_id=t_normal_user.id,
        is_active=True,
    )
    t_project = crud_project.create(db=db, db_obj_user=t_admin_user, obj_in=t_project_1)

    t_project_in = ProjectUpdateSchema(
        number=get_test_project(db).number,
        product_number=t_product_number_1,
        customer=t_customer_1,
        description=t_description_1,
        designated_user_id=t_normal_user.id,
        is_active=True,
    )

    # ----------------------------------------------
    # UPDATE ITEM: METHODS TO TEST
    # ----------------------------------------------

    with pytest.raises(ProjectAlreadyExistsError):
        crud_project.update(db, db_obj_user=t_normal_user, db_obj=t_project, obj_in=t_project_in)


def test_update_project_assign_non_existing_designated(db: Session) -> None:
    """
    Test updating a project by assigning a non-existing designated user.
    This test ensures that attempting to update a project with a designated user ID
    that does not exist in the database raises a UserDoesNotExistError.

    Args:
        db (Session): The database session used for the test.

    Raises:
        UserDoesNotExistError: If the designated user ID does not exist in the database.
    """

    # ----------------------------------------------
    # UPDATE ITEM: PREPARATION
    # ----------------------------------------------

    t_project = get_test_project(db)
    t_admin_user = get_test_admin_user(db)

    t_project_in = ProjectUpdateSchema(
        number=t_project.number,
        product_number=t_project.product_number,
        customer=t_project.customer,
        description=t_project.description or "",
        designated_user_id=9999999,
        is_active=True,
    )
    t_project_in_dict = t_project_in.model_dump()
    del t_project_in_dict["designated_user_id"]

    # ----------------------------------------------
    # UPDATE ITEM: METHODS TO TEST
    # ----------------------------------------------

    with pytest.raises(UserDoesNotExistError):
        crud_project.update(db, db_obj_user=t_admin_user, db_obj=t_project, obj_in=t_project_in)

    with pytest.raises(UserDoesNotExistError):
        crud_project.update(db, db_obj_user=t_admin_user, db_obj=t_project, obj_in=t_project_in_dict)
