"""Adaptive Room Manager integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry as ar, device_registry as dr

from .const import (
    CONF_AREA_ID,
    CONF_ENTRY_TYPE,
    CONF_LEGACY_PERSISTENT,
    CONF_LEGACY_TEMPORARY,
    CONF_PERSISTENT,
    CONF_LEGACY_SLEEP_ENTITIES,
    CONF_LEGACY_SLEEP_TIMEOUT,
    CONF_SLEEP_ABSENCE_DELAY,
    CONF_TRIGGER_PRESENCE,
    DOMAIN,
    ENTRY_TYPE_HOME,
    ENTRY_TYPE_ROOM,
    HOME_TITLE,
    PLATFORMS,
)
from .manager import RoomManager


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate config entries to version 6."""
    if entry.version > 6:
        return False

    data = dict(entry.data)
    options = dict(entry.options)
    if entry.version < 4:
        for values in (data, options):
            if CONF_LEGACY_TEMPORARY in values:
                values.setdefault(CONF_TRIGGER_PRESENCE, values.pop(CONF_LEGACY_TEMPORARY))
            if CONF_LEGACY_PERSISTENT in values:
                values.setdefault(CONF_PERSISTENT, values.pop(CONF_LEGACY_PERSISTENT))

    if entry.version < 6:
        for values in (data, options):
            legacy_timeout = values.pop(CONF_LEGACY_SLEEP_TIMEOUT, None)
            values.pop(CONF_LEGACY_SLEEP_ENTITIES, None)
            if legacy_timeout is not None:
                values.setdefault(CONF_SLEEP_ABSENCE_DELAY, legacy_timeout)
        hass.config_entries.async_update_entry(
            entry, data=data, options=options, version=6
        )
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload changed entries and reschedule rooms after Home Settings changes."""
    if entry.data.get(CONF_ENTRY_TYPE) == ENTRY_TYPE_HOME:
        await hass.config_entries.async_reload(entry.entry_id)
        for room_entry in hass.config_entries.async_entries(DOMAIN):
            if room_entry.data.get(CONF_ENTRY_TYPE, ENTRY_TYPE_ROOM) == ENTRY_TYPE_ROOM:
                await hass.config_entries.async_reload(room_entry.entry_id)
        return
    await hass.config_entries.async_reload(entry.entry_id)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up an Adaptive Room Manager config entry."""
    hass.data.setdefault(DOMAIN, {})
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    entry_type = entry.data.get(CONF_ENTRY_TYPE, ENTRY_TYPE_ROOM)
    if entry_type == ENTRY_TYPE_HOME:
        if entry.title != HOME_TITLE:
            hass.config_entries.async_update_entry(entry, title=HOME_TITLE)
        hass.data[DOMAIN][entry.entry_id] = None
        return True

    manager = RoomManager(hass, entry)
    hass.data[DOMAIN][entry.entry_id] = manager

    area_id = entry.data[CONF_AREA_ID]
    area = ar.async_get(hass).async_get_area(area_id)
    device_registry = dr.async_get(hass)
    device = device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, area_id)},
        name=area.name if area else entry.title,
        manufacturer="Adaptive Room Manager",
        model="Adaptive Room",
        suggested_area=area.name if area else None,
        configuration_url=f"homeassistant://config/integrations/integration/{DOMAIN}",
    )
    if device.area_id != area_id:
        device_registry.async_update_device(device.id, area_id=area_id)

    await manager.async_start()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload an Adaptive Room Manager config entry."""
    entry_type = entry.data.get(CONF_ENTRY_TYPE, ENTRY_TYPE_ROOM)
    if entry_type == ENTRY_TYPE_HOME:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        return True

    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        manager = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        if manager:
            await manager.async_stop()
    return unloaded
