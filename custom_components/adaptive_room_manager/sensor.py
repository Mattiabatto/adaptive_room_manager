from homeassistant.components.sensor import SensorEntity
from .const import *
from .entity import ArmEntity
async def async_setup_entry(hass,entry,add):
    if entry.data.get(CONF_KIND)==KIND_ROOM:
        m=hass.data[DOMAIN][entry.entry_id]; add([Reason(m,"presence_reason","Presence reason"),Reason(m,"light_reason","Lighting reason"),Period(m)])
class Reason(ArmEntity,SensorEntity):
    def __init__(self,m,key,name):super().__init__(m,key);self.key=key;self._attr_name=name
    @property
    def native_value(self):return getattr(self.manager,self.key)
class Period(ArmEntity,SensorEntity):
    _attr_name="Period"
    def __init__(self,m):super().__init__(m,"period")
    @property
    def native_value(self):return self.manager._period()
