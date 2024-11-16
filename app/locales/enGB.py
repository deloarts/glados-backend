"""
Locale enGB
"""

from locales.languageModel import LanguageModel


class enGB(LanguageModel):
    API_CREATE_USER_ALREADY_EXISTS = "The user already exists in the system"

    API_UPDATE_USER_USERNAME_IN_USE = "This username is already in use"
    API_UPDATE_USER_MAIL_IN_USE = "This email is already in use"
    API_UPDATE_USER_USERNAME_OR_MAIL_IN_USE = "A user with this username or email already exists"
    API_UPDATE_USER_ID_NOT_FOUND = "The user with this id does not exist in the system"
    API_UPDATE_USER_PASSWORD_WEAK = "This password is too weak"
    API_UPDATE_USER_NO_PERMISSION = "You are not allowed to update this user"

    API_READ_USER_NOT_FOUND = "The user with this id doesn't exists in the system"

    API_UPDATE_USER_TOKEN_GUEST_NO_PERMISSION = "A guest user cannot create an access token"
