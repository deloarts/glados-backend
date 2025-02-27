"""
    Loads the config.yml configuration file.
"""

# pylint: disable=C0115
# pylint: disable=C0116
# pylint: disable=R0902
# pylint: disable=R0903

import os
from dataclasses import dataclass
from dataclasses import fields
from typing import List

import yaml
from const import CONFIG


@dataclass(slots=True, kw_only=True, frozen=True)
class ConfigLocale:
    tz: str


@dataclass(slots=True, kw_only=True, frozen=True)
class ConfigSecurity:
    min_pw_len: int
    algorithm: str
    expire_minutes: int
    allow_rfid_login: bool


@dataclass(slots=True, kw_only=True)
class ConfigServerAPI:
    web: str
    pat: str
    key: str


@dataclass(slots=True, kw_only=True)
class ConfigServerSSL:
    keyfile: str | None
    certfile: str | None

    def __init__(self, keyfile: str | None, certfile: str | None):
        if keyfile and certfile:
            if os.path.exists(keyfile) and os.path.exists(certfile):
                self.keyfile = keyfile
                self.certfile = certfile
            else:
                raise FileNotFoundError("SSL certificate files not found")
        else:
            self.keyfile = None
            self.certfile = None


@dataclass(slots=True, kw_only=True)
class ConfigServerStatic:
    enable: bool
    folder: str
    url: str

    def __init__(self, enable: bool | None, folder: str | None, url: str | None):
        if enable is True and folder and url:
            if os.path.exists(folder):
                self.enable = enable
                self.folder = folder
                self.url = url
            else:
                raise OSError("Static folder not found")
        else:
            self.enable = False
            self.folder = ""
            self.url = ""


@dataclass(slots=True, kw_only=True)
class ConfigServer:
    host: str
    port: int
    domain: str
    api: ConfigServerAPI
    static: ConfigServerStatic
    ssl: ConfigServerSSL
    headers_server: bool
    headers_proxy: bool
    forwarded_allowed_ips: str | None

    def __post_init__(self) -> None:
        self.api = ConfigServerAPI(**dict(self.api))  # type: ignore
        self.static = ConfigServerStatic(**dict(self.static))  # type: ignore
        self.ssl = ConfigServerSSL(**dict(self.ssl))  # type: ignore


@dataclass(slots=True, kw_only=True, frozen=True)
class ConfigItemsBoughtValidation:
    project: str | None
    product: str | None


@dataclass(slots=True, kw_only=True, frozen=True)
class ConfigItemsBoughtStatus:
    open: str
    requested: str
    ordered: str
    late: str
    partial: str
    delivered: str
    canceled: str
    lost: str

    @property
    def default(self) -> str:
        return self.open

    @property
    def keys(self) -> List[str]:
        return [f.name for f in fields(self)]

    @property
    def values(self) -> List[str]:
        return [getattr(self, f.name) for f in fields(self)]


@dataclass(slots=True, kw_only=True, frozen=True)
class ConfigItemsBoughtUnits:
    default: str
    values: List[str]


@dataclass(slots=True, kw_only=True, frozen=True)
class ConfigItemsBoughtOrderBy:
    high_priority: str
    created: str
    project: str
    product: str
    group_1: str
    manufacturer: str
    supplier: str

    @property
    def default(self) -> str:
        return self.created

    @property
    def keys(self) -> List[str]:
        return [f.name for f in fields(self)]

    @property
    def values(self) -> List[str]:
        return [getattr(self, f.name) for f in fields(self)]


@dataclass(slots=True, kw_only=True)
class ConfigItemsBought:
    validation: ConfigItemsBoughtValidation
    status: ConfigItemsBoughtStatus
    units: ConfigItemsBoughtUnits
    order_by: ConfigItemsBoughtOrderBy

    def __post_init__(self) -> None:
        self.validation = ConfigItemsBoughtValidation(**dict(self.validation))  # type: ignore
        self.status = ConfigItemsBoughtStatus(**dict(self.status))  # type: ignore
        self.units = ConfigItemsBoughtUnits(**dict(self.units))  # type: ignore
        self.order_by = ConfigItemsBoughtOrderBy(**dict(self.order_by))  # type: ignore


@dataclass(slots=True, kw_only=True, frozen=True)
class ConfigDirectoriesElement:
    path: str
    is_mount: bool


@dataclass(slots=True, kw_only=True)
class ConfigFilesystem:
    disc_space_warning: float
    db_backup: ConfigDirectoriesElement

    def __post_init__(self) -> None:
        self.db_backup = ConfigDirectoriesElement(**dict(self.db_backup))  # type: ignore


@dataclass(slots=True, kw_only=True)
class ConfigItems:
    bought: ConfigItemsBought

    def __post_init__(self) -> None:
        self.bought = ConfigItemsBought(**dict(self.bought))  # type: ignore


@dataclass(slots=True, kw_only=True, frozen=True)
class ConfigInit:
    full_name: str
    mail: str
    password: str


@dataclass(slots=True, kw_only=True, frozen=True)
class ConfigExcelStyle:
    font: str
    size: int
    header_color: str
    header_bg_color: str
    data_color_1: str
    data_bg_color_1: str
    data_color_2: str
    data_bg_color_2: str


@dataclass(slots=True, kw_only=True)
class ConfigExcel:
    header_row: int
    data_row: int
    style: ConfigExcelStyle

    def __post_init__(self) -> None:
        self.style = ConfigExcelStyle(**dict(self.style))  # type: ignore


@dataclass(slots=True, kw_only=True, frozen=True)
class ConfigSchedules:
    database_hour: int
    system_hour: int
    email_notifications_hour: int
    backup_db_hour: int
    delete_temp_hour: int
    delete_uploads_hour: int


@dataclass(slots=True, kw_only=True, frozen=True)
class ConfigMailing:
    server: str | None
    port: int | None
    account: str | None
    password: str | None
    debug_receiver: str | None
    debug_no_send: bool | None


@dataclass(slots=True, kw_only=True, frozen=True)
class ConfigTemplates:
    bought_item_excel_import: str
    mail_item_notification: str
    mail_schedule_error: str
    mail_disc_space_warning: str
    mail_welcome: str


@dataclass(slots=True, kw_only=True)
class Config:
    debug: bool
    locale: ConfigLocale
    security: ConfigSecurity
    server: ConfigServer
    schedules: ConfigSchedules
    filesystem: ConfigFilesystem
    items: ConfigItems
    excel: ConfigExcel
    mailing: ConfigMailing
    templates: ConfigTemplates
    init: ConfigInit

    def __post_init__(self) -> None:
        self.locale = ConfigLocale(**dict(self.locale))  # type: ignore
        self.security = ConfigSecurity(**dict(self.security))  # type: ignore
        self.server = ConfigServer(**dict(self.server))  # type: ignore
        self.schedules = ConfigSchedules(**dict(self.schedules))  # type: ignore
        self.filesystem = ConfigFilesystem(**dict(self.filesystem))  # type: ignore
        self.items = ConfigItems(**dict(self.items))  # type: ignore
        self.excel = ConfigExcel(**dict(self.excel))  # type: ignore
        self.mailing = ConfigMailing(**dict(self.mailing))  # type: ignore
        self.templates = ConfigTemplates(**dict(self.templates))  # type: ignore
        self.init = ConfigInit(**dict(self.init))  # type: ignore


class Configuration:
    @staticmethod
    def read() -> Config:
        """Reads the yaml config file."""
        if os.path.exists(CONFIG):
            # Due to security issues, it is recommended to use yaml.safe_load()
            # (or the SafeLoader) instead of yaml.load() (or the FullLoader) to avoid
            # code injection in the configuration file.
            with open(CONFIG, "r", encoding="utf8") as yaml_file:
                return Config(**yaml.safe_load(yaml_file))
        else:
            raise FileNotFoundError("Config file doesn't exist.")


cfg = Configuration.read()
