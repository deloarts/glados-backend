from const import SERVER_DEFAULT_LANGUAGE
from const import SERVER_DEFAULT_THEME
from const import VERSION
from locales import Locales


def test_version():
    assert VERSION == "0.13.1"


def test_server_default():
    assert SERVER_DEFAULT_LANGUAGE == "enGB"
    assert SERVER_DEFAULT_THEME == "dark"


def test_language():
    assert Locales.EN_GB == "enGB" == SERVER_DEFAULT_LANGUAGE
    assert Locales.DE_AT == "deAT"
