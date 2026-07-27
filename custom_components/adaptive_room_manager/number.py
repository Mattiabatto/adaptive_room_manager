from homeassistant.components.number import NumberEntity,NumberMode
from .const import *
from .entity import ArmEntity
async def async_setup_entry(hass,entry,add):
    if entry.data.get(CONF_KIND)==KIND_ROOM:
        m=hass.data[DOMAIN][entry.entry_id];add([Absence(m),Lux(m)])
class Absence(ArmEntity,NumberEntity):
    _attr_name="Absence delay";_attr_native_min_value=0;_attr_native_max_value=3600;_attr_native_step=30;_attr_native_unit_of_measurement="s";_attr_mode=NumberMode.BOX
    def __init__(self,m):super().__init__(m,"absence_delay")
    @property
    def native_value(self):return self.manager.absence_delay
    async def async_set_native_value(self,v):self.manager.absence_delay=int(v);self.manager._notify()
class Lux(ArmEntity,NumberEntity):
    _attr_name="Lux threshold";_attr_native_min_value=0;_attr_native_max_value=1000;_attr_native_step=1;_attr_native_unit_of_measurement="lx";_attr_mode=NumberMode.BOX
    def __init__(self,m):super().__init__(m,"lux_threshold")
    @property
    def native_value(self):return self.manager.lux_threshold
    async def async_set_native_value(self,v):self.manager.lux_threshold=float(v);await self.manager.async_evaluate()
