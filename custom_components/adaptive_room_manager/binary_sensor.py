from homeassistant.components.binary_sensor import BinarySensorEntity
from .const import DOMAIN,KIND_ROOM,CONF_KIND
from .entity import ArmEntity
async def async_setup_entry(hass,entry,add):
    if entry.data.get(CONF_KIND)!=KIND_ROOM:return
    m=hass.data[DOMAIN][entry.entry_id]; add([Presence(m),LightNeeded(m)])
class Presence(ArmEntity,BinarySensorEntity):
    _attr_name="Presence"; _attr_device_class="occupancy"
    @property
    def is_on(self):return self.manager.occupied
class LightNeeded(ArmEntity,BinarySensorEntity):
    _attr_name="Light needed"; _attr_device_class="light"
    @property
    def is_on(self):return self.manager.light_needed
