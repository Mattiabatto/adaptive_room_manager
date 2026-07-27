"""Select entities for Adaptive Room Manager."""
from homeassistant.components.select import SelectEntity

from .const import DOMAIN
from .entity import ArmEntity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([Mode(hass.data[DOMAIN][entry.entry_id])])


class Mode(ArmEntity, SelectEntity):
    _attr_name = "Mode"
    _attr_options = ["automatic", "disabled", "force_day", "force_evening", "force_night"]

    def __init__(self, manager):
        super().__init__(manager, "mode")

    @property
    def current_option(self):
        return self.manager.mode

    async def async_select_option(self, option):
        self.manager.mode = option
        await self.manager.async_evaluate()
