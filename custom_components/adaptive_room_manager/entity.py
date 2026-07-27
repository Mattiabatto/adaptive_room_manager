"""Base entities for Adaptive Room Manager."""
from __future__ import annotations

from homeassistant.helpers import area_registry as ar
from homeassistant.helpers.entity import DeviceInfo, Entity

from .const import DOMAIN, MANUFACTURER, MODEL, VERSION


class ArmEntity(Entity):
    """Base entity attached to the room device."""

    _attr_has_entity_name = True

    def __init__(self, manager, key: str) -> None:
        self.manager = manager
        self._attr_unique_id = f"{manager.area_id}_{key}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.manager.area_id)},
            name=self.manager.room_name,
            manufacturer=MANUFACTURER,
            model=MODEL,
            sw_version=VERSION,
            suggested_area=self.manager.room_name,
            configuration_url=f"homeassistant://config/integrations/integration/{DOMAIN}",
        )


    @property
    def icon(self) -> str | None:
        """Return the icon configured on the linked Home Assistant area."""
        if self.hass is None:
            return None
        area = ar.async_get(self.hass).async_get_area(self.manager.area_id)
        return area.icon if area else None

    async def async_added_to_hass(self) -> None:
        self.manager.add_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        self.manager.remove_callback(self.async_write_ha_state)
