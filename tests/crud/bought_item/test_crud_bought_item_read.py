"""
    CRUD tests (READ ONLY) for the bought item model
"""

from crud.bought_item import crud_bought_item
from sqlalchemy.orm import Session

from tests.utils.bought_item import create_random_item
from tests.utils.project import get_test_project
from tests.utils.user import get_test_user


def test_get_item(db: Session) -> None:
    """
    Test the retrieval of a bought item from the database.
    This test performs the following steps:

    1. Preparation:
        - Retrieve a test user and a test project from the database.
        - Create a random item associated with the test user and project.
        - Assert that the item creator is the test user and the project's designated user is the test user.
    2. Methods to Test:
        - Retrieve the item from the database using the CRUD method.
    3. Validation:
        - Assert that the retrieved item exists.
        - Validate that the retrieved item's attributes match the created item's attributes.
        - Validate that the item's creator and project are correctly associated.
        - Assert that the item is part of the project's bought items and the user's created bought items.

    Args:
        db (Session): The database session used for the test.
    """

    # ----------------------------------------------
    # GET ITEM: PREPARATION
    # ----------------------------------------------

    t_user = get_test_user(db)
    # About t_user:
    #   This is the same user who creates the random item in the utils method below.
    #   It is also the same user, who is the designated user in the test project below.
    t_project = get_test_project(db)
    # About t_project:
    #   This is the same project, that serves as parent project for the create_random_item utils method below.
    t_item = create_random_item(db, test_fn_name=test_get_item.__name__)

    # This assertion is to check if the test utils are correct...
    # If this fails, maybe the test user hasn't been created correctly.
    assert t_item.creator == t_user
    assert t_project.designated_user == t_user

    # ----------------------------------------------
    # GET ITEM: METHODS TO TEST
    # ----------------------------------------------

    item = crud_bought_item.get(db=db, id=t_item.id)

    # ----------------------------------------------
    # GET ITEM: VALIDATION
    # ----------------------------------------------

    assert item

    assert item.project == t_item.project
    assert item.quantity == t_item.quantity
    assert item.unit == t_item.unit
    assert item.partnumber == t_item.partnumber
    assert item.order_number == t_item.order_number
    assert item.manufacturer == t_item.manufacturer

    assert item.creator_id == t_item.creator_id
    assert item.creator == t_user

    assert item.project == t_project
    assert item.project_id == t_project.id

    assert item in t_project.bought_items
    assert item in t_user.created_bought_items
