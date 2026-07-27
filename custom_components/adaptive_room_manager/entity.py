"""Base entities."""
from homeassistant.helpers.entity import Entity
from .const import DOMAIN, CONF_AREA_ID
class ArmEntity(Entity):
    _attr_has_entity_name=True
    def __init__(self,manager,key):
        self.manager=manager; self._attr_unique_id=f"{manager.entry.entry_id}_{key}"
    async def async_added_to_hass(self): self.manager.add_callback(self.async_write_ha_state)
    async def async_will_remove_from_hass(self): self.manager.remove_callback(self.async_write_ha_state)
