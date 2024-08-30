"""CRUD helper functions"""

from copy import deepcopy
from datetime import datetime
from typing import List
from typing import Optional

from db.models import BoughtItemModel
from db.models import UserModel


def get_changelog(
    changes: str,
    db_obj_user: UserModel,
    db_obj_item: Optional[BoughtItemModel] = None,
) -> List[str]:
    """Returns the full changelog from the item.

    Args:
        changes (str): The recent changes.
        db_obj_user (UserModel): The user, who made the changes.
        db_obj_item (Optional[BoughtItemModel], optional): The item model.

    Returns:
        List[str]: The full changelog from the item as list of strings.
    """
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if db_obj_item is not None:
        changelog = list(deepcopy(db_obj_item.changes))
    else:
        changelog = []
    changelog.append(f"{time}, {db_obj_user.full_name}, {changes}")
    return changelog
