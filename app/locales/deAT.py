"""
Locale enGB
"""

from locales.languageModel import LanguageModel


class deAT(LanguageModel):
    API_CREATE_USER_ALREADY_EXISTS = "Der Benutzer existiert bereits im System"

    API_UPDATE_USER_USERNAME_IN_USE = "Der Benutzername ist bereits vergeben"
    API_UPDATE_USER_MAIL_IN_USE = "Die Mailaddresse ist bereits in Verwendung"
    API_UPDATE_USER_USERNAME_OR_MAIL_IN_USE = "Dieser Benutzername oder diese Mail sind in Verwendung"
    API_UPDATE_USER_ID_NOT_FOUND = "Ein Benutzer mit dieser ID existiert nicht"
    API_UPDATE_USER_PASSWORD_WEAK = "Dieses Passwort ist nicht sicher"
    API_UPDATE_USER_NO_PERMISSION = "Nicht genügend Rechte zum Aktualsieren dieses Benutzers"

    API_READ_USER_NOT_FOUND = "Dieser Benutzer existiert nicht"

    API_UPDATE_USER_TOKEN_GUEST_NO_PERMISSION = "gastbenutzer können keine Schlüssel erstellen"
