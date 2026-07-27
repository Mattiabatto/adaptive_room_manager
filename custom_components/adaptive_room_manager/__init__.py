"""Adaptive Room Manager integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN, PLATFORMS, KIND_ROOM, CONF_KIND
from .manager import RoomManager

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    if entry.data.get(CONF_KIND) == KIND_ROOM:
        manager = RoomManager(hass, entry)
        hass.data[DOMAIN][entry.entry_id] = manager
        await manager.async_start()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    manager = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if manager:
        await manager.async_stop()
    return ok
