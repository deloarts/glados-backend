"""
Locale enGB
"""

from dataclasses import dataclass
from string import Template


@dataclass(slots=True, frozen=True)
class deAT:
    class API:
        class DEPS:
            INACTIVE = "Dieses Konto ist inaktiv"
            SUPERUSER_REQUIRED = "Superuser-Rechte erforderlich"
            ADMINUSER_REQUIRED = "Adminuser-Rechte erforderlich"
            GUESTUSER_REQUIRED = "Gastuser-Rechte erforderlich"

        class BOUGHTITEM:
            ITEM_NOT_FOUND = "Dieser Artikel existiert nicht"
            PROJECT_NOT_FOUND = "Das Projekt existiert nicht"
            PROJECT_INACTIVE = "Das Projekt ist nicht aktiv"
            CREATE_NO_PERMISSION = "Du kannst keine Artikel erstellen"
            UPDATE_NO_PERMISSION = "Du kannst diesen Artikel nicht ändern"
            DELETE_NO_PERMISSION = "Du kannst diesen Artikel nicht löschen"
            CANNOT_CHANGE_OTHER_USER_ITEM = "Du kannst keine Artikel anderer Benutzer ändern"
            CANNOT_DELETE_OTHER_USER_ITEM = "Du kannst keine Artikel anderer Benutzer löschen"
            CANNOT_CHANGE_PLANNED_ITEM = "Du kannst keine bereits geplanten Artikel ändern"
            CANNOT_DELETE_PLANNED_ITEM = "Du kannst keine bereits geplanten Artikel löschen"
            CANNOT_CHANGE_TO_OPEN = "Der Status kann nicht auf Offen zurückgesetzt werden"
            UNKNOWN_STATUS = "Unbekannter Status"
            VALUE_MUST_BE_SET = "Dieses Feld muss ausgefüllt sein"
            FAILED_EXCEL_GENERATION = "Die EXCEL Datei konnte nicht generiert werden"
            TEMPLATE_NOT_FOUND = "Die Vorlage-Datei ist nicht verfügbar"
            IMPORT_COLUMN_X_NOT_FOUND = Template("Spalte `$x` nicht gefunden")
            IMPORT_PROJECT_X_NOT_FOUND = Template("Ein Projekt mit der Nummer `$x` existiert nicht")
            IMPORT_PROJECT_X_NOT_ACTIVE = Template("Das Projekt `$x` ist nicht aktiv")

        class HOST:
            CONFIGURATION_ALREADY_EXISTS = "Eine Konfiguration mit diesem Namen existiert bereits"
            CONFIGURATION_NOT_FOUND = "Diese Konfiguration existiert nicht"

        class LOGIN:
            INCORRECT_CREDS = "Zugangsdaten nicht korrekt"
            INACTIVE_ACCOUNT = "Dieses Konto ist inaktiv"

        class LOGS:
            FILE_NOT_FOUND = "Log-Datei existiert nicht"

        class PROJECT:
            ALREADY_EXISTS = "Dieses Projekt existiert bereits"
            NOT_FOUND = "Dieses Projekt existiert nicht"
            UPDATE_NO_PERMISSION = "Du kannst dieses Projekt nicht bearbeiten"
            DELETE_NO_PERMISSION = "Du kannst dieses Projekt nicht löschen"
            GUEST_USER_NO_PERMISSION = "Gastbenutzer können keine Projekte anlegen"
            DESIGNATE_NOT_EXISTS = "Der zugeteilte Benutzer existiert nicht"

        class USER:
            ALREADY_EXISTS = "Der Benutzer existiert bereits im System"
            NOT_FOUND = "Dieser Benutzer existiert nicht"
            USERNAME_IN_USE = "Der Benutzername ist bereits vergeben"
            MAIL_IN_USE = "Die Mailaddresse ist bereits in Verwendung"
            RFID_IN_USE = "Diese RFID ist bereits einem Konto zugeordnet"
            USERNAME_OR_MAIL_IN_USE = "Dieser Benutzername oder diese Mail sind in Verwendung"
            ID_NOT_FOUND = "Ein Benutzer mit dieser ID existiert nicht"
            PASSWORD_WEAK = "Dieses Passwort ist nicht sicher"
            UPDATE_NO_PERMISSION = "Nicht genügend Rechte zum Aktualsieren dieses Benutzers"
            TOKEN_GUEST_NO_PERMISSION = "Gastbenutzer können keine Schlüssel erstellen"
