"""
    CRUD tests (COMMON METHODS ONLY) for the project model
"""

from crud.project import crud_project
from sqlalchemy.orm import Session

from tests.utils.project import get_test_project


def test_project_is_active(db: Session) -> None:
    """
    Test the `is_active` method of the `crud_project` module.
    This test verifies that the `is_active` method correctly identifies
    an active project.

    Preparation:
        - Retrieve a test project from the database.
    Methods to Test:
        - `crud_project.is_active(project=t_project)`
    Validation:
        - Assert that the project is active.

    Args:
        db (Session): The database session used for the test.
    """

    # ----------------------------------------------
    # PROJECT IS ACTIVE: PREPARATION
    # ----------------------------------------------

    t_project = get_test_project(db)

    # ----------------------------------------------
    # PROJECT IS ACTIVE: METHODS TO TEST
    # ----------------------------------------------

    project_is_active = crud_project.is_active(project=t_project)

    # ----------------------------------------------
    # PROJECT IS ACTIVE: VALIDATION
    # ----------------------------------------------

    assert project_is_active is True
