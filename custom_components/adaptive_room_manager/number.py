"""Editable room controls for Adaptive Room Manager."""
from homeassistant.components.number import NumberEntity, NumberMode

from .const import (
    CONF_ABSENCE_DELAY,
    CONF_LUX_THRESHOLD,
    DOMAIN,
)
from .entity import ArmEntity


async def async_setup_entry(hass, entry, async_add_entities):
    manager = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AbsenceDelay(manager), LuxThreshold(manager)])


class AbsenceDelay(ArmEntity, NumberEntity):
    _attr_name = "Absence delay"
    _attr_native_min_value = 0
    _attr_native_max_value = 7200
    _attr_native_step = 10
    _attr_native_unit_of_measurement = "s"
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:timer-outline"

    def __init__(self, manager):
        super().__init__(manager, "absence_delay")

    @property
    def native_value(self):
        return self.manager.absence_delay

    async def async_set_native_value(self, value):
        options = {**self.manager.entry.options, CONF_ABSENCE_DELAY: int(value)}
        self.hass.config_entries.async_update_entry(self.manager.entry, options=options)
        await self.manager.async_evaluate()


class LuxThreshold(ArmEntity, NumberEntity):
    _attr_name = "Illuminance threshold"
    _attr_native_min_value = 0
    _attr_native_max_value = 2000
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "lx"
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:brightness-5"

    def __init__(self, manager):
        super().__init__(manager, "lux_threshold")

    @property
    def native_value(self):
        return self.manager.lux_threshold

    async def async_set_native_value(self, value):
        options = {**self.manager.entry.options, CONF_LUX_THRESHOLD: float(value)}
        self.hass.config_entries.async_update_entry(self.manager.entry, options=options)
        await self.manager.async_evaluate()
