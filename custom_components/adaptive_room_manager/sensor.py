"""Sensors for Adaptive Room Manager."""
from homeassistant.components.sensor import SensorEntity

from .const import DOMAIN
from .entity import ArmEntity


async def async_setup_entry(hass, entry, async_add_entities):
    manager = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        Reason(manager, "presence_reason", "Presence reason"),
        Reason(manager, "light_reason", "Lighting reason"),
        Period(manager),
        NaturalLux(manager),
    ])


class Reason(ArmEntity, SensorEntity):
    def __init__(self, manager, key, name):
        super().__init__(manager, key)
        self.key = key
        self._attr_name = name

    @property
    def native_value(self):
        return getattr(self.manager, self.key)


class Period(ArmEntity, SensorEntity):
    _attr_name = "Period"

    def __init__(self, manager):
        super().__init__(manager, "period")

    @property
    def native_value(self):
        return self.manager.period()


class NaturalLux(ArmEntity, SensorEntity):
    _attr_name = "Stored natural illuminance"
    _attr_native_unit_of_measurement = "lx"
    _attr_icon = "mdi:brightness-6"

    def __init__(self, manager):
        super().__init__(manager, "stored_natural_lux")

    @property
    def native_value(self):
        return self.manager.last_natural_lux
