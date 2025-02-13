"""
    Module that holds all custom exceptions.
"""

import sys
import traceback

from multilog import log


class BaseError(Exception):
    """Base class for all exceptions. Logs exceptions as error messages"""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)
        if traceback.extract_tb(sys.exc_info()[2]):
            log.exception(msg)
        else:
            log.error(msg)


class InsufficientPermissionsError(BaseError):
    ...


class UserError(BaseError):
    ...


class UserAlreadyExistsError(UserError):
    ...


class UserDoesNotExistError(UserError):
    ...


class UsernameAlreadyExistsError(UserError):
    ...


class EmailAlreadyExistsError(UserError):
    ...


class RfidAlreadyExistsError(UserError):
    ...


class UserTimeError(BaseError):
    ...


class LoginTimeRequiredError(UserTimeError):
    ...


class AlreadyLoggedInError(UserTimeError):
    ...


class AlreadyLoggedOutError(UserTimeError):
    ...


class ProjectError(BaseError):
    ...


class ProjectNotFoundError(ProjectError):
    ...


class ProjectAlreadyExistsError(ProjectError):
    ...


class ProjectInactiveError(ProjectError):
    ...


class BoughtItemError(BaseError):
    ...


class BoughtItemRequiredFieldNotSetError(BoughtItemError):
    ...


class BoughtItemUnknownStatusError(BoughtItemError):
    ...


class BoughtItemCannotChangeToOpenError(BoughtItemError):
    ...


class BoughtItemOfAnotherUserError(InsufficientPermissionsError):
    ...


class BoughtItemAlreadyPlannedError(InsufficientPermissionsError):
    ...


class ExcelImportError(BaseError):
    ...


class ExcelImportHeaderMissingError(ExcelImportError):
    ...


class ExcelImportHeaderInvalidError(ExcelImportError):
    ...


class ExcelImportDataInvalidError(ExcelImportError):
    ...


class PasswordCriteriaError(BaseError):
    ...
