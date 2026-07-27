from datetime import time
from homeassistant.components.time import TimeEntity
from .const import *
class NightStart(TimeEntity):
    _attr_name="Night start";_attr_has_entity_name=True
    def __init__(self,entry):self.entry=entry;self._attr_unique_id=f"{entry.entry_id}_night_start"
    @property
    def native_value(self):return time.fromisoformat(self.entry.options.get(CONF_NIGHT_START,self.entry.data.get(CONF_NIGHT_START,DEFAULT_NIGHT_START)))
    async def async_set_value(self,value):self.hass.config_entries.async_update_entry(self.entry,options={**self.entry.options,CONF_NIGHT_START:value.isoformat()});self.async_write_ha_state()
async def async_setup_entry(hass,entry,add):
    if entry.data.get(CONF_KIND)==KIND_HOUSE:add([NightStart(entry)])
