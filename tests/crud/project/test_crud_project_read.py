"""
    CRUD tests (READ ONLY) for the project model
"""

from crud.project import crud_project
from sqlalchemy.orm import Session

from tests.utils.project import get_test_project
from tests.utils.user import get_test_user


def test_get_project(db: Session) -> None:
    """
    Test the retrieval of a project from the database.
    This test performs the following steps:

    1. Preparation: Retrieve a test project from the database.
    2. Method to Test: Use the CRUD operation to get the project by its ID.
    3. Validation: Assert that the retrieved project matches the test project.

    Args:
        db (Session): The database session used for the test.
    """

    # ----------------------------------------------
    # GET PROJECT: PREPARATION
    # ----------------------------------------------

    t_project = get_test_project(db)

    # ----------------------------------------------
    # GET PROJECT: METHODS TO TEST
    # ----------------------------------------------

    project = crud_project.get(db=db, id=t_project.id)

    # ----------------------------------------------
    # GET PROJECT: VALIDATION
    # ----------------------------------------------

    assert project == t_project


def test_get_project_non_existent(db: Session) -> None:
    """
    Test case for retrieving a non-existent project from the database.
    This test ensures that attempting to retrieve a project with an ID that does not exist
    in the database returns None.

    Args:
        db (Session): The database session used for the test.

    Steps:
        1. Attempt to retrieve a project with ID 0 using the crud_project.get method.
        2. Validate that the returned project is None, indicating that the project does not exist.

    Asserts:
        - The retrieved project is None.
    """

    # ----------------------------------------------
    # GET PROJECT: PREPARATION
    # ------------------------------------

    # ----------------------------------------------
    # GET PROJECT: METHODS TO TEST
    # ----------------------------------------------

    project = crud_project.get(db=db, id=0)

    # ----------------------------------------------
    # GET PROJECT: VALIDATION
    # ----------------------------------------------

    assert project is None


def test_get_by_id(db: Session) -> None:
    """
    Test the retrieval of a project by its ID from the database.
    This test performs the following steps:

    1. Preparation: Create a test project in the database.
    2. Method to Test: Retrieve the project by its ID using the CRUD operation.
    3. Validation: Assert that the retrieved project matches the test project.

    Args:
        db (Session): The database session used for the test.
    """

    # ----------------------------------------------
    # GET PROJECT BY ID: PREPARATION
    # ----------------------------------------------

    t_project = get_test_project(db)

    # ----------------------------------------------
    # GET PROJECT BY ID: METHODS TO TEST
    # ----------------------------------------------

    project = crud_project.get_by_id(db=db, id=t_project.id)

    # ----------------------------------------------
    # GET PROJECT BY ID: VALIDATION
    # ----------------------------------------------

    assert project == t_project


def test_get_by_id_non_existent(db: Session) -> None:
    """
    Test the `get_by_id` method of the `crud_project` module with a non-existent project ID.

    This test ensures that when attempting to retrieve a project by an ID that does not exist in the database,
    the method returns `None`.

    Test Steps:
    1. Prepare the test by setting up any necessary preconditions (none in this case).
    2. Call the `get_by_id` method with a non-existent project ID (0).
    3. Validate that the returned project is `None`.

    Args:
        db (Session): The database session used for the test.

    """

    # ----------------------------------------------
    # GET PROJECT BY ID: PREPARATION
    # ----------------------------------------------

    # ----------------------------------------------
    # GET PROJECT BY ID: METHODS TO TEST
    # ----------------------------------------------

    project = crud_project.get_by_id(db=db, id=0)

    # ----------------------------------------------
    # GET PROJECT BY ID: VALIDATION
    # ----------------------------------------------

    assert project is None


def test_get_by_designated_user_id(db: Session) -> None:
    """
    Test the retrieval of projects by designated user ID.

    This test performs the following steps:
    1. Preparation: Retrieve a test project and a test user from the database.
       Note: The test project has the test user as its designated user.
    2. Method Execution: Call the `get_by_designated_user_id` method from the `crud_project` module
       to retrieve projects associated with the designated user ID.
    3. Validation: Assert that the retrieved projects list is not empty and that the test project
       is included in the retrieved projects.

    Args:
        db (Session): The database session used for the test.
    """

    # ----------------------------------------------
    # GET PROJECT BY NUMBER: PREPARATION
    # ----------------------------------------------

    t_project = get_test_project(db)
    t_user = get_test_user(db)
    # Note: get_test_project has the get_test_user as designated user (see test utils)

    # ----------------------------------------------
    # GET PROJECT BY NUMBER: METHODS TO TEST
    # ----------------------------------------------

    projects = crud_project.get_by_designated_user_id(db=db, user_id=t_user.id)

    # ----------------------------------------------
    # GET PROJECT BY NUMBER: VALIDATION
    # ----------------------------------------------

    assert projects
    assert t_project in projects


def test_get_by_designated_non_existent_user_id(db: Session) -> None:
    """
    Test case for retrieving projects by a designated user ID that does not exist.

    This test ensures that when attempting to retrieve projects using a user ID
    that does not exist in the database, the function returns an empty list.

    Args:
        db (Session): The database session used for the test.

    Asserts:
        projects (list): The list of projects retrieved by the designated user ID.
                         This should be an empty list when the user ID does not exist.
    """

    # ----------------------------------------------
    # GET PROJECT BY NUMBER: PREPARATION
    # ----------------------------------------------

    # ----------------------------------------------
    # GET PROJECT BY NUMBER: METHODS TO TEST
    # ----------------------------------------------

    projects = crud_project.get_by_designated_user_id(db=db, user_id=0)

    # ----------------------------------------------
    # GET PROJECT BY NUMBER: VALIDATION
    # ----------------------------------------------

    assert projects == []


def test_get_by_product_number(db: Session) -> None:
    """
    Test the functionality of retrieving a project by its product number.

    This test performs the following steps:
    1. Preparation: Retrieve a test project from the database and ensure it has a product number.
    2. Method Execution: Use the CRUD operation to get projects by the product number.
    3. Validation: Verify that the retrieved projects list is not empty and contains the test project.

    Args:
        db (Session): The database session used for the test.
    """

    # ----------------------------------------------
    # GET PROJECT BY NUMBER: PREPARATION
    # ----------------------------------------------

    t_project = get_test_project(db)
    assert t_project.product_number

    # ----------------------------------------------
    # GET PROJECT BY NUMBER: METHODS TO TEST
    # ----------------------------------------------

    projects = crud_project.get_by_product_number(db=db, product_number=t_project.product_number)

    # ----------------------------------------------
    # GET PROJECT BY NUMBER: VALIDATION
    # ----------------------------------------------

    assert projects
    assert t_project in projects


def test_get_by_non_existent_product_number(db: Session) -> None:
    """
    Test case for retrieving a project by a non-existent product number.

    This test ensures that when attempting to retrieve a project using a product number
    that does not exist in the database, the function returns an empty list.

    Args:
        db (Session): The database session used for the test.

    Assertions:
        Asserts that the returned projects list is empty when a non-existent product number is queried.
    """

    # ----------------------------------------------
    # GET PROJECT BY NUMBER: PREPARATION
    # ----------------------------------------------

    # ----------------------------------------------
    # GET PROJECT BY NUMBER: METHODS TO TEST
    # ----------------------------------------------

    projects = crud_project.get_by_product_number(db=db, product_number="non-existing-product-number")

    # ----------------------------------------------
    # GET PROJECT BY NUMBER: VALIDATION
    # ----------------------------------------------

    assert projects == []
