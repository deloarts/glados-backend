"""
    Loads the bought items configuration file.
"""

import atexit
import json
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from typing import Dict

from const import CONFIG_BOUGHT_ITEMS
from multilog import log


@dataclass(slots=True, kw_only=True)
class ConfigBoughtItemsFilter:
    limit: str = field(default="100")
    ignoreDelivered: bool = False
    ignoreCanceled: bool = False
    ignoreLost: bool = False
    highPriority: bool | None = None
    creatorId: str = field(default="")
    createdDate: str = field(default="")
    changedDateFrom: str = field(default="")
    desiredDate: str = field(default="")
    requesterId: str = field(default="")
    requestedDate: str = field(default="")
    ordererId: str = field(default="")
    orderedDate: str = field(default="")
    expectedDate: str = field(default="")
    deliveredDate: str = field(default="")
    sortBy: str = field(default="id")
    id: str = field(default="")
    status: str = field(default="")
    project: str = field(default="")
    machine: str = field(default="")
    quantity: str = field(default="")
    unit: str = field(default="")
    partnumber: str = field(default="")
    orderNumber: str = field(default="")
    manufacturer: str = field(default="")
    supplier: str = field(default="")
    group1: str = field(default="")
    noteGeneral: str = field(default="")
    noteSupplier: str = field(default="")
    storagePlace: str = field(default="")
    takeOverId: str = field(default="")


@dataclass(slots=True, kw_only=True)
class ConfigBoughtItems:
    filters: Dict[str, ConfigBoughtItemsFilter]


class Configuration:
    def __init__(self) -> None:
        self._config: ConfigBoughtItems

        try:
            self.read()
            assert self._config.filters
        except Exception as e:
            log.warning(f"Failed to load config file {str(CONFIG_BOUGHT_ITEMS)}. Applying default values. {e}")
            self._config = ConfigBoughtItems(filters={"default": ConfigBoughtItemsFilter()})
            self.write()

        atexit.register(self.write)

    @property
    def filters(self) -> Dict[str, ConfigBoughtItemsFilter]:
        return self._config.filters

    def write(self) -> None:
        with open(CONFIG_BOUGHT_ITEMS, "w", encoding="utf8") as f:
            json.dump(asdict(self._config), f)

    def read(self) -> None:
        with open(CONFIG_BOUGHT_ITEMS, "r", encoding="utf8") as f:
            self._config = ConfigBoughtItems(**json.load(f))

    def add_filter(self, name: str, filter: ConfigBoughtItemsFilter) -> None:
        self._config.filters[name] = filter
        self.write()

    def remove_filter(self, name: str) -> None:
        if name in self._config.filters:
            self._config.filters.pop(name)
        self.write()


bought_item_config = Configuration()
