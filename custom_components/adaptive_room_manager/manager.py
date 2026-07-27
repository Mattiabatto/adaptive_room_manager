"""Event-driven room controller."""
from __future__ import annotations
from datetime import datetime, time, timedelta
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_state_change_event, async_call_later
from homeassistant.const import STATE_ON, STATE_OFF, STATE_OPEN, STATE_CLOSED, STATE_UNAVAILABLE, STATE_UNKNOWN
from .const import *

class RoomManager:
    def __init__(self,hass:HomeAssistant,entry:ConfigEntry):
        self.hass=hass; self.entry=entry; self.listeners=[]; self.callbacks=[]
        self.occupied=False; self.light_needed=False; self.presence_reason="No presence"; self.light_reason="Not evaluated"
        self.enabled=True; self.mode="automatic"; self.absence_delay=DEFAULT_ABSENCE_DELAY; self.lux_threshold=DEFAULT_LUX_THRESHOLD
        self.last_natural_lux=None; self.auto_lights=set(); self.manual_overrides=set(); self._absence_cancel=None
    @property
    def entities(self):
        d=self.entry.data
        out=[]
        for k in (CONF_TEMPORARY,CONF_PERSISTENT,CONF_LUX,CONF_COVERS,CONF_DAY_LIGHTS,CONF_EVENING_LIGHTS,CONF_NIGHT_LIGHTS): out += d.get(k,[])
        out += ["sun.sun"]
        return list(dict.fromkeys(out))
    async def async_start(self):
        self.listeners.append(async_track_state_change_event(self.hass,self.entities,self._state_changed))
        await self.async_evaluate()
    async def async_stop(self):
        for x in self.listeners: x()
        if self._absence_cancel: self._absence_cancel()
    def add_callback(self,cb): self.callbacks.append(cb)
    def remove_callback(self,cb):
        if cb in self.callbacks:self.callbacks.remove(cb)
    @callback
    def _state_changed(self,event): self.hass.async_create_task(self.async_evaluate(event.data.get("entity_id")))
    def _is_active(self,e):
        s=self.hass.states.get(e)
        return s is not None and s.state not in (STATE_OFF,STATE_CLOSED,STATE_UNAVAILABLE,STATE_UNKNOWN,"idle","standby")
    def _lights_on(self):
        all_lights=sum((self.entry.data.get(k,[]) for k in (CONF_DAY_LIGHTS,CONF_EVENING_LIGHTS,CONF_NIGHT_LIGHTS)),[])
        return {e for e in all_lights if (self.hass.states.get(e) and self.hass.states[e].state==STATE_ON)}
    def _period(self):
        now=datetime.now().time(); ns=time.fromisoformat(DEFAULT_NIGHT_START); ms=time.fromisoformat(DEFAULT_MORNING_START)
        houses=[e for e in self.hass.config_entries.async_entries(DOMAIN) if e.data.get(CONF_KIND)==KIND_HOUSE]
        if houses:
            ns=time.fromisoformat(houses[0].options.get(CONF_NIGHT_START,houses[0].data.get(CONF_NIGHT_START,DEFAULT_NIGHT_START)))
            ms=time.fromisoformat(houses[0].options.get(CONF_MORNING_START,houses[0].data.get(CONF_MORNING_START,DEFAULT_MORNING_START)))
        if now>=ns or now<ms:return "night"
        sun=self.hass.states.get("sun.sun"); elev=float(sun.attributes.get("elevation",0)) if sun else 0
        return "day" if elev>3 else "evening"
    async def async_evaluate(self,changed=None):
        tmp=[e for e in self.entry.data.get(CONF_TEMPORARY,[]) if self._is_active(e)]
        per=[e for e in self.entry.data.get(CONF_PERSISTENT,[]) if self._is_active(e)]
        active=tmp+per
        if active:
            if self._absence_cancel:self._absence_cancel();self._absence_cancel=None
            self.occupied=True; self.presence_reason=active[0]
        elif self.occupied and not self._absence_cancel:
            @callback
            def clear(_): self._absence_cancel=None; self.occupied=False; self.presence_reason="Absence timeout"; self.hass.async_create_task(self.async_apply())
            self._absence_cancel=async_call_later(self.hass,self.absence_delay,clear)
        lights_on=self._lights_on()
        lux_values=[]
        for e in self.entry.data.get(CONF_LUX,[]):
            st=self.hass.states.get(e)
            try: lux_values.append(float(st.state))
            except (TypeError,ValueError,AttributeError): pass
        if not lights_on and lux_values:self.last_natural_lux=sum(lux_values)/len(lux_values)
        covers=[self.hass.states.get(e) for e in self.entry.data.get(CONF_COVERS,[])]
        valid=[s for s in covers if s and s.state not in (STATE_UNAVAILABLE,STATE_UNKNOWN)]
        any_open=any(s.state==STATE_OPEN for s in valid)
        sun=self.hass.states.get("sun.sun"); elev=float(sun.attributes.get("elevation",0)) if sun else 0
        period=self._period()
        if period=="night": self.light_needed=True; self.light_reason="Night profile"
        elif self.last_natural_lux is not None:
            self.light_needed=self.last_natural_lux < self.lux_threshold
            self.light_reason=f"Stored natural lux: {self.last_natural_lux:.1f}"
            if any_open and elev>3 and self.last_natural_lux>=self.lux_threshold:self.light_needed=False
        else:
            self.light_needed=not(any_open and elev>3); self.light_reason="Cover and sun fallback"
        await self.async_apply(); self._notify()
    async def async_apply(self):
        if not self.enabled or self.mode=="disabled":return
        period=self._period(); groups={"day":CONF_DAY_LIGHTS,"evening":CONF_EVENING_LIGHTS,"night":CONF_NIGHT_LIGHTS}
        desired=set(self.entry.data.get(groups[period],[])) if self.occupied and self.light_needed else set()
        managed=(set(sum((self.entry.data.get(k,[]) for k in (CONF_DAY_LIGHTS,CONF_EVENING_LIGHTS,CONF_NIGHT_LIGHTS)),[]))-self.manual_overrides)
        to_on=desired-managed.intersection(self._lights_on()); to_off=(self.auto_lights-desired)-self.manual_overrides
        if to_on:
            await self.hass.services.async_call("light","turn_on",{"entity_id":list(to_on)},blocking=False); self.auto_lights|=to_on
        if to_off:
            await self.hass.services.async_call("light","turn_off",{"entity_id":list(to_off)},blocking=False); self.auto_lights-=to_off
        if not self.occupied:self.manual_overrides.clear()
    def _notify(self):
        for cb in list(self.callbacks):cb()
