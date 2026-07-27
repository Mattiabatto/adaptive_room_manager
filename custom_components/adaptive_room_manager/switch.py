from homeassistant.components.switch import SwitchEntity
from .const import *
from .entity import ArmEntity
async def async_setup_entry(hass,entry,add):
    if entry.data.get(CONF_KIND)==KIND_ROOM:add([Automation(hass.data[DOMAIN][entry.entry_id])])
class Automation(ArmEntity,SwitchEntity):
    _attr_name="Automation"
    def __init__(self,m):super().__init__(m,"automation")
    @property
    def is_on(self):return self.manager.enabled
    async def async_turn_on(self,**kw):self.manager.enabled=True;await self.manager.async_evaluate()
    async def async_turn_off(self,**kw):self.manager.enabled=False;self.manager._notify()
