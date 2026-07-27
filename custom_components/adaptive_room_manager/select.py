from homeassistant.components.select import SelectEntity
from .const import *
from .entity import ArmEntity
async def async_setup_entry(hass,entry,add):
    if entry.data.get(CONF_KIND)==KIND_ROOM:add([Mode(hass.data[DOMAIN][entry.entry_id])])
class Mode(ArmEntity,SelectEntity):
    _attr_name="Mode";_attr_options=["automatic","disabled","force_day","force_evening","force_night"]
    def __init__(self,m):super().__init__(m,"mode")
    @property
    def current_option(self):return self.manager.mode
    async def async_select_option(self,opt):self.manager.mode=opt;await self.manager.async_evaluate()
