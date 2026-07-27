"""Config and options flows for Adaptive Room Manager."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult, OptionsFlowWithReload
from homeassistant.helpers import area_registry as ar, selector

from .const import (
    CONF_ABSENCE_DELAY,
    CONF_AREA_ID,
    CONF_COVERS,
    CONF_DAY_LIGHTS,
    CONF_ENTRY_TYPE,
    CONF_EVENING_LIGHTS,
    CONF_EVENING_START,
    CONF_LUX,
    CONF_LUX_THRESHOLD,
    CONF_MORNING_START,
    CONF_NIGHT_LIGHTS,
    CONF_NIGHT_START,
    CONF_PERSISTENT,
    CONF_TEMPORARY,
    DEFAULT_ABSENCE_DELAY,
    DEFAULT_EVENING_START,
    DEFAULT_LUX_THRESHOLD,
    DEFAULT_MORNING_START,
    DEFAULT_NIGHT_START,
    DOMAIN,
    ENTRY_TYPE_HOME,
    ENTRY_TYPE_ROOM,
    HOME_UNIQUE_ID,
)


def _home_settings_schema(defaults: dict[str, Any]) -> dict[Any, Any]:
    return {
        vol.Required(
            CONF_EVENING_START,
            default=defaults.get(CONF_EVENING_START, DEFAULT_EVENING_START),
        ): selector.TimeSelector(),
        vol.Required(
            CONF_NIGHT_START,
            default=defaults.get(CONF_NIGHT_START, DEFAULT_NIGHT_START),
        ): selector.TimeSelector(),
        vol.Required(
            CONF_MORNING_START,
            default=defaults.get(CONF_MORNING_START, DEFAULT_MORNING_START),
        ): selector.TimeSelector(),
        vol.Required(
            CONF_LUX_THRESHOLD,
            default=defaults.get(CONF_LUX_THRESHOLD, DEFAULT_LUX_THRESHOLD),
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0,
                max=2000,
                step=1,
                unit_of_measurement="lx",
                mode=selector.NumberSelectorMode.BOX,
            )
        ),
        vol.Required(
            CONF_ABSENCE_DELAY,
            default=defaults.get(CONF_ABSENCE_DELAY, DEFAULT_ABSENCE_DELAY),
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0,
                max=7200,
                step=10,
                unit_of_measurement="s",
                mode=selector.NumberSelectorMode.BOX,
            )
        ),
    }


def _home_schema(defaults: dict[str, Any]) -> vol.Schema:
    """Return the schema for defaults used when new rooms are created."""
    return vol.Schema(_home_settings_schema(defaults))


def _room_schema(defaults: dict[str, Any], *, include_area: bool) -> vol.Schema:
    fields: dict[Any, Any] = {}
    if include_area:
        fields[vol.Required(CONF_AREA_ID)] = selector.AreaSelector()

    fields.update(
        {
            vol.Optional(
                CONF_TEMPORARY, default=defaults.get(CONF_TEMPORARY, [])
            ): selector.EntitySelector(selector.EntitySelectorConfig(multiple=True)),
            vol.Optional(
                CONF_PERSISTENT, default=defaults.get(CONF_PERSISTENT, [])
            ): selector.EntitySelector(selector.EntitySelectorConfig(multiple=True)),
            vol.Optional(CONF_LUX, default=defaults.get(CONF_LUX, [])): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", multiple=True)
            ),
            vol.Optional(
                CONF_COVERS, default=defaults.get(CONF_COVERS, [])
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="cover", multiple=True)
            ),
            vol.Optional(
                CONF_DAY_LIGHTS, default=defaults.get(CONF_DAY_LIGHTS, [])
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="light", multiple=True)
            ),
            vol.Optional(
                CONF_EVENING_LIGHTS, default=defaults.get(CONF_EVENING_LIGHTS, [])
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="light", multiple=True)
            ),
            vol.Optional(
                CONF_NIGHT_LIGHTS, default=defaults.get(CONF_NIGHT_LIGHTS, [])
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="light", multiple=True)
            ),
        }
    )
    fields.update(
        {
            vol.Required(
                CONF_LUX_THRESHOLD,
                default=defaults.get(CONF_LUX_THRESHOLD, DEFAULT_LUX_THRESHOLD),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=2000,
                    step=1,
                    unit_of_measurement="lx",
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Required(
                CONF_ABSENCE_DELAY,
                default=defaults.get(CONF_ABSENCE_DELAY, DEFAULT_ABSENCE_DELAY),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=7200,
                    step=10,
                    unit_of_measurement="s",
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
        }
    )
    return vol.Schema(fields)


def _home_defaults(hass) -> dict[str, Any]:
    """Return configured home defaults, or built-in defaults."""
    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.data.get(CONF_ENTRY_TYPE) == ENTRY_TYPE_HOME:
            return {**entry.data, **entry.options}
    return {}


class AdaptiveRoomManagerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configure Adaptive Room Manager."""

    VERSION = 3

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Show the entry type menu."""
        return self.async_show_menu(
            step_id="user",
            menu_options=["home", "room"],
        )

    async def async_step_home(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Create the single Home Settings entry."""
        await self.async_set_unique_id(HOME_UNIQUE_ID)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(
                title="Home Settings",
                data={CONF_ENTRY_TYPE: ENTRY_TYPE_HOME, **user_input},
            )

        return self.async_show_form(
            step_id="home",
            data_schema=_home_schema({}),
        )

    async def async_step_room(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Create one room entry associated with an existing HA area."""
        if user_input is not None:
            area_id = user_input[CONF_AREA_ID]
            await self.async_set_unique_id(f"room_{area_id}")
            self._abort_if_unique_id_configured()
            area = ar.async_get(self.hass).async_get_area(area_id)
            return self.async_create_entry(
                title=area.name if area else "Adaptive Room",
                data={CONF_ENTRY_TYPE: ENTRY_TYPE_ROOM, **user_input},
            )

        return self.async_show_form(
            step_id="room",
            data_schema=_room_schema(_home_defaults(self.hass), include_area=True),
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        return AdaptiveRoomManagerOptionsFlow()


class AdaptiveRoomManagerOptionsFlow(OptionsFlowWithReload):
    """Edit Home Settings or room-specific settings."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        current = {**self.config_entry.data, **self.config_entry.options}
        entry_type = self.config_entry.data.get(CONF_ENTRY_TYPE, ENTRY_TYPE_ROOM)

        if user_input is not None:
            return self.async_create_entry(data=user_input)

        if entry_type == ENTRY_TYPE_HOME:
            return self.async_show_form(
                step_id="init",
                data_schema=_home_schema(current),
                description_placeholders={"entry_type": "home"},
            )

        return self.async_show_form(
            step_id="init",
            data_schema=_room_schema(current, include_area=False),
            description_placeholders={"entry_type": "room"},
        )
