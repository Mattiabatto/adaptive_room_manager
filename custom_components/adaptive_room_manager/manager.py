"""Event-driven room controller."""
from __future__ import annotations

from datetime import datetime, time

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    STATE_CLOSED,
    STATE_OFF,
    STATE_ON,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers.event import async_call_later, async_track_state_change_event

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
    CONF_TRIGGER_PRESENCE,
    DEFAULT_ABSENCE_DELAY,
    DEFAULT_EVENING_START,
    DEFAULT_LUX_THRESHOLD,
    DEFAULT_MORNING_START,
    DEFAULT_NIGHT_START,
    DOMAIN,
    ENTRY_TYPE_HOME,
)


class RoomManager:
    """Calculate presence and control lighting for one area."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.listeners: list = []
        self.callbacks: list = []
        self.occupied = False
        self.light_needed = False
        self.presence_reason = "No active presence sensors"
        self.light_reason = "Not evaluated"
        self.enabled = True
        self.mode = "automatic"
        self.last_natural_lux: float | None = None
        self.auto_lights: set[str] = set()
        self.manual_overrides: set[str] = set()
        self._absence_cancel = None

    @property
    def config(self) -> dict:
        return {**self.entry.data, **self.entry.options}

    @property
    def home_config(self) -> dict:
        """Return the global Home Settings configuration."""
        for entry in self.hass.config_entries.async_entries(DOMAIN):
            if entry.data.get(CONF_ENTRY_TYPE) == ENTRY_TYPE_HOME:
                return {**entry.data, **entry.options}
        return {}

    @property
    def area_id(self) -> str:
        return self.entry.data[CONF_AREA_ID]

    @property
    def room_name(self) -> str:
        area = ar.async_get(self.hass).async_get_area(self.area_id)
        return area.name if area else self.entry.title

    @property
    def absence_delay(self) -> int:
        return int(self.config.get(CONF_ABSENCE_DELAY, DEFAULT_ABSENCE_DELAY))

    @property
    def lux_threshold(self) -> float:
        return float(self.config.get(CONF_LUX_THRESHOLD, DEFAULT_LUX_THRESHOLD))

    @property
    def entities(self) -> list[str]:
        out: list[str] = []
        for key in (
            CONF_TRIGGER_PRESENCE,
            CONF_PERSISTENT,
            CONF_LUX,
            CONF_COVERS,
            CONF_DAY_LIGHTS,
            CONF_EVENING_LIGHTS,
            CONF_NIGHT_LIGHTS,
        ):
            out.extend(self.config.get(key, []))
        out.append("sun.sun")
        return list(dict.fromkeys(out))

    async def async_start(self) -> None:
        self.listeners.append(
            async_track_state_change_event(self.hass, self.entities, self._state_changed)
        )
        await self.async_evaluate()

    async def async_stop(self) -> None:
        for remove_listener in self.listeners:
            remove_listener()
        if self._absence_cancel:
            self._absence_cancel()

    def add_callback(self, callback_func) -> None:
        self.callbacks.append(callback_func)

    def remove_callback(self, callback_func) -> None:
        if callback_func in self.callbacks:
            self.callbacks.remove(callback_func)

    @callback
    def _state_changed(self, event) -> None:
        self.hass.async_create_task(self.async_evaluate(event.data.get("entity_id")))

    def _is_active(self, entity_id: str) -> bool:
        state = self.hass.states.get(entity_id)
        return state is not None and state.state not in (
            STATE_OFF,
            STATE_CLOSED,
            STATE_UNAVAILABLE,
            STATE_UNKNOWN,
            "idle",
            "standby",
        )

    def _active_presence(self) -> tuple[list[str], list[str]]:
        triggers = [
            entity_id
            for entity_id in self.config.get(CONF_TRIGGER_PRESENCE, [])
            if self._is_active(entity_id)
        ]
        persistent = [
            entity_id
            for entity_id in self.config.get(CONF_PERSISTENT, [])
            if self._is_active(entity_id)
        ]
        return triggers, persistent

    def _all_lights(self) -> set[str]:
        return set(
            self.config.get(CONF_DAY_LIGHTS, [])
            + self.config.get(CONF_EVENING_LIGHTS, [])
            + self.config.get(CONF_NIGHT_LIGHTS, [])
        )

    def _lights_on(self) -> set[str]:
        return {
            entity_id
            for entity_id in self._all_lights()
            if (state := self.hass.states.get(entity_id)) and state.state == STATE_ON
        }

    def period(self) -> str:
        if self.mode.startswith("force_"):
            return self.mode.removeprefix("force_")
        now = datetime.now().time()
        home = self.home_config
        morning = time.fromisoformat(
            home.get(CONF_MORNING_START, DEFAULT_MORNING_START)
        )
        evening = time.fromisoformat(
            home.get(CONF_EVENING_START, DEFAULT_EVENING_START)
        )
        night = time.fromisoformat(home.get(CONF_NIGHT_START, DEFAULT_NIGHT_START))
        if now >= night or now < morning:
            return "night"
        if now >= evening:
            return "evening"
        return "day"

    def _cancel_absence_timer(self) -> None:
        if self._absence_cancel:
            self._absence_cancel()
            self._absence_cancel = None

    def _update_presence(self) -> None:
        """Apply the trigger-and-persistent presence state machine.

        A vacant room becomes occupied only when at least one trigger sensor AND at
        least one persistent sensor are active. Once occupied, either group may keep
        the room occupied. The same entity may be configured in both groups.
        """
        triggers, persistent = self._active_presence()

        if not self.occupied:
            self._cancel_absence_timer()
            if triggers and persistent:
                self.occupied = True
                self.presence_reason = (
                    f"Activated by trigger {triggers[0]} and persistent {persistent[0]}"
                )
            elif triggers:
                self.presence_reason = "Waiting for a persistent presence sensor"
            elif persistent:
                self.presence_reason = "Waiting for a trigger presence sensor"
            else:
                self.presence_reason = "No active presence sensors"
            return

        # After activation, an active sensor from either group keeps occupancy latched.
        if triggers or persistent:
            self._cancel_absence_timer()
            if triggers and persistent:
                self.presence_reason = (
                    f"Held by trigger {triggers[0]} and persistent {persistent[0]}"
                )
            elif triggers:
                self.presence_reason = f"Held by trigger {triggers[0]}"
            else:
                self.presence_reason = f"Held by persistent {persistent[0]}"
            return

        if self._absence_cancel:
            self.presence_reason = "Vacancy delay"
            return

        self.presence_reason = "Vacancy delay"

        @callback
        def clear_presence(_now) -> None:
            self._absence_cancel = None
            current_triggers, current_persistent = self._active_presence()
            if current_triggers or current_persistent:
                self.hass.async_create_task(self.async_evaluate())
                return
            self.occupied = False
            self.presence_reason = "Absence timeout"
            self.manual_overrides.clear()
            self.hass.async_create_task(self.async_apply())
            self._notify()

        self._absence_cancel = async_call_later(
            self.hass, self.absence_delay, clear_presence
        )

    async def async_evaluate(self, changed: str | None = None) -> None:
        self._update_presence()

        lights_on = self._lights_on()
        lux_values: list[float] = []
        for entity_id in self.config.get(CONF_LUX, []):
            state = self.hass.states.get(entity_id)
            try:
                lux_values.append(float(state.state))
            except (TypeError, ValueError, AttributeError):
                continue

        # Natural lux is updated only while managed lights are off. Opening a cover
        # never causes a visible off/on measurement cycle.
        if not lights_on and lux_values:
            self.last_natural_lux = sum(lux_values) / len(lux_values)

        valid_covers = []
        for entity_id in self.config.get(CONF_COVERS, []):
            state = self.hass.states.get(entity_id)
            if state and state.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                valid_covers.append(state)
        any_open = any(state.state != STATE_CLOSED for state in valid_covers)

        sun = self.hass.states.get("sun.sun")
        try:
            elevation = float(sun.attributes.get("elevation", 0)) if sun else 0
        except (TypeError, ValueError):
            elevation = 0

        period = self.period()
        if period == "night":
            self.light_needed = True
            self.light_reason = "Night profile"
        elif self.last_natural_lux is not None:
            self.light_needed = self.last_natural_lux < self.lux_threshold
            self.light_reason = (
                f"Stored natural lux: {self.last_natural_lux:.1f} lx"
            )
        else:
            self.light_needed = not (any_open and elevation > 3)
            self.light_reason = "Cover and sun fallback"

        await self.async_apply()
        self._notify()

    async def async_apply(self) -> None:
        if not self.enabled or self.mode == "disabled":
            return

        groups = {
            "day": CONF_DAY_LIGHTS,
            "evening": CONF_EVENING_LIGHTS,
            "night": CONF_NIGHT_LIGHTS,
        }
        desired = (
            set(self.config.get(groups[self.period()], []))
            if self.occupied and self.light_needed
            else set()
        )
        currently_on = self._lights_on()
        to_on = (desired - currently_on) - self.manual_overrides
        to_off = (self.auto_lights - desired) - self.manual_overrides

        if to_on:
            await self.hass.services.async_call(
                "light", "turn_on", {"entity_id": list(to_on)}, blocking=False
            )
            self.auto_lights.update(to_on)
        if to_off:
            await self.hass.services.async_call(
                "light", "turn_off", {"entity_id": list(to_off)}, blocking=False
            )
            self.auto_lights.difference_update(to_off)

    def _notify(self) -> None:
        for callback_func in list(self.callbacks):
            callback_func()
