"""Config flow for Adaptive Room Manager."""
from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from homeassistant.helpers import area_registry as ar
from .const import *

class AdaptiveRoomManagerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return await (self.async_step_house() if user_input[CONF_KIND] == KIND_HOUSE else self.async_step_room())
        return self.async_show_form(step_id="user", data_schema=vol.Schema({vol.Required(CONF_KIND): selector.SelectSelector(selector.SelectSelectorConfig(options=[KIND_HOUSE,KIND_ROOM], mode=selector.SelectSelectorMode.DROPDOWN))}))

    async def async_step_house(self, user_input=None):
        if any(e.data.get(CONF_KIND)==KIND_HOUSE for e in self._async_current_entries()):
            return self.async_abort(reason="house_exists")
        if user_input is not None:
            data={CONF_KIND:KIND_HOUSE, **user_input}
            return self.async_create_entry(title="Adaptive Room Manager", data=data)
        return self.async_show_form(step_id="house", data_schema=vol.Schema({
            vol.Required(CONF_NIGHT_START, default=DEFAULT_NIGHT_START): selector.TimeSelector(),
            vol.Required(CONF_MORNING_START, default=DEFAULT_MORNING_START): selector.TimeSelector(),
        }))

    async def async_step_room(self, user_input=None):
        if user_input is not None:
            area=ar.async_get(self.hass).async_get_area(user_input[CONF_AREA_ID])
            title=area.name if area else "Room"
            await self.async_set_unique_id(f"room_{user_input[CONF_AREA_ID]}")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=title, data={CONF_KIND:KIND_ROOM, **user_input})
        ent_any=selector.EntitySelector(selector.EntitySelectorConfig(multiple=True))
        ent_lux=selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor", multiple=True))
        ent_cover=selector.EntitySelector(selector.EntitySelectorConfig(domain="cover", multiple=True))
        ent_light=selector.EntitySelector(selector.EntitySelectorConfig(domain="light", multiple=True))
        return self.async_show_form(step_id="room", data_schema=vol.Schema({
            vol.Required(CONF_AREA_ID): selector.AreaSelector(),
            vol.Optional(CONF_TEMPORARY, default=[]): ent_any,
            vol.Optional(CONF_PERSISTENT, default=[]): ent_any,
            vol.Optional(CONF_LUX, default=[]): ent_lux,
            vol.Optional(CONF_COVERS, default=[]): ent_cover,
            vol.Optional(CONF_DAY_LIGHTS, default=[]): ent_light,
            vol.Optional(CONF_EVENING_LIGHTS, default=[]): ent_light,
            vol.Optional(CONF_NIGHT_LIGHTS, default=[]): ent_light,
        }))
