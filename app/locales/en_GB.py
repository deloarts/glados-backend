"""
Locale enGB
"""

from dataclasses import dataclass
from string import Template


@dataclass(slots=True, frozen=True)
class enGB:
    class API:
        class DEPS:
            INACTIVE = "This account is inactive"
            SUPERUSER_REQUIRED = "This requires super-user privileges"
            ADMINUSER_REQUIRED = "This requires admin-user privileges"
            GUESTUSER_REQUIRED = "This requires guest-user privileges"

        class HOST:
            CONFIGURATION_ALREADY_EXISTS = "A configuration with this name already exists"
            CONFIGURATION_NOT_FOUND = "Configuration does not exist"

        class BOUGHTITEM:
            ITEM_NOT_FOUND = "This item doesn't exist"
            PROJECT_NOT_FOUND = "The project doesn't exist"
            PROJECT_INACTIVE = "The project is inactive"
            CREATE_NO_PERMISSION = "You cannot create items"
            UPDATE_NO_PERMISSION = "You are not allowed to change this item"
            DELETE_NO_PERMISSION = "You are not allowed to delete this item"
            CANNOT_CHANGE_OTHER_USER_ITEM = "You cannot change the item of another user"
            CANNOT_DELETE_OTHER_USER_ITEM = "You cannot delete the item of another user"
            CANNOT_CHANGE_PLANNED_ITEM = "You cannot changed planned items"
            CANNOT_DELETE_PLANNED_ITEM = "You cannot delete planned items"
            CANNOT_CHANGE_TO_OPEN = "You cannot change the status back to open"
            UNKNOWN_STATUS = "Unknown status"
            VALUE_MUST_BE_SET = "This field requires a value"
            FAILED_EXCEL_GENERATION = "The EXCEL file could not be generated"
            TEMPLATE_NOT_FOUND = "Template file not found"
            IMPORT_COLUMN_X_NOT_FOUND = Template("Column `$x` not found")
            IMPORT_PROJECT_X_NOT_FOUND = Template("A project with the number `$x` doesn't exist")
            IMPORT_PROJECT_X_NOT_ACTIVE = Template("The project `$x` is inactive")

        class LOGIN:
            INCORRECT_CREDS = "Incorrect credentials"
            INACTIVE_ACCOUNT = "This account is inactive"

        class LOGS:
            FILE_NOT_FOUND = "Log file not found"

        class PROJECT:
            ALREADY_EXISTS = "The project already exists"
            NOT_FOUND = "The project does not exist"
            UPDATE_NO_PERMISSION = "You are not allowed to change this project"
            DELETE_NO_PERMISSION = "You are not allowed to delete this project"
            GUEST_USER_NO_PERMISSION = "A guest user cannot create projects"
            DESIGNATE_NOT_EXISTS = "The designated user does not exist"

        class USER:
            ALREADY_EXISTS = "The user already exists in the system"
            NOT_FOUND = "The user with this id doesn't exists in the system"
            USERNAME_IN_USE = "This username is already in use"
            MAIL_IN_USE = "This email is already in use"
            RFID_IN_USE = "This RFID is already assigned to an account"
            USERNAME_OR_MAIL_IN_USE = "A user with this username or email already exists"
            ID_NOT_FOUND = "The user with this id does not exist in the system"
            PASSWORD_WEAK = "This password is too weak"
            UPDATE_NO_PERMISSION = "You are not allowed to update this user"
            TOKEN_GUEST_NO_PERMISSION = "A guest user cannot create an access token"
