"""Binary sensors for Adaptive Room Manager."""
from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity

from .const import DOMAIN
from .entity import ArmEntity


async def async_setup_entry(hass, entry, async_add_entities):
    manager = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([Presence(manager), LightNeeded(manager)])


class Presence(ArmEntity, BinarySensorEntity):
    _attr_name = "Presence"
    _attr_device_class = BinarySensorDeviceClass.OCCUPANCY

    def __init__(self, manager):
        super().__init__(manager, "presence")

    @property
    def is_on(self):
        return self.manager.occupied


class LightNeeded(ArmEntity, BinarySensorEntity):
    _attr_name = "Light needed"
    _attr_device_class = BinarySensorDeviceClass.LIGHT

    def __init__(self, manager):
        super().__init__(manager, "light_needed")

    @property
    def is_on(self):
        return self.manager.light_needed
