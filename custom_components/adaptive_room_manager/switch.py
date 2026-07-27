"""Switches for Adaptive Room Manager."""
from homeassistant.components.switch import SwitchEntity

from .const import DOMAIN
from .entity import ArmEntity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([Automation(hass.data[DOMAIN][entry.entry_id])])


class Automation(ArmEntity, SwitchEntity):
    _attr_name = "Automation"
    _attr_icon = "mdi:home-automation"

    def __init__(self, manager):
        super().__init__(manager, "automation")

    @property
    def is_on(self):
        return self.manager.enabled

    async def async_turn_on(self, **kwargs):
        self.manager.enabled = True
        await self.manager.async_evaluate()

    async def async_turn_off(self, **kwargs):
        self.manager.enabled = False
        self.manager._notify()
