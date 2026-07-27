# Adaptive Room Manager

Adaptive Room Manager is a Home Assistant custom integration that creates an adaptive controller and a dedicated Home Assistant device for every configured room.

> **Status:** early technical preview. Test each release carefully before relying on it in a production home.

## What it creates

The integration uses native Home Assistant config entries and devices. It does not require YAML, helpers, blueprints, template sensors, or separate automations.

- One optional **Home Settings** config entry for the global day/evening/night schedule and defaults.
- One independent config entry for every managed room.
- One dedicated device for every room, associated with an existing Home Assistant area.
- Room entities for occupancy, lighting decisions, diagnostics, automation state, mode, lux threshold, and absence delay.
- An options flow, opened from the integration entry's settings gear, with descriptions below every configurable field.

## Presence model

Presence uses two configurable sensor groups.

### Trigger presence sensors

Trigger sensors are allowed to start occupancy. Typical examples are PIR motion sensors, door sensors, or any entity that represents an entry or movement event.

A vacant room does **not** become occupied from a trigger sensor alone.

### Persistent presence sensors

Persistent sensors confirm and maintain occupancy. Typical examples are mmWave presence sensors, bed occupancy, a television playing, a computer in use, or a room-specific night mode.

A vacant room does **not** become occupied from a persistent sensor alone.

### Activation rule

A vacant room becomes occupied only when both conditions are true at the same time:

```text
at least one trigger presence sensor is active
AND
at least one persistent presence sensor is active
```

The order does not matter. A persistent sensor may already be active before the trigger, or the trigger may activate first.

The same entity may be selected in both groups. In that configuration, one active entity satisfies both activation conditions. This is useful for a sensor that should both start and maintain occupancy.

### Occupancy hold and vacancy

After the room has become occupied, an active sensor from **either** group keeps it occupied:

```text
at least one trigger sensor is active
OR
at least one persistent sensor is active
```

When every sensor in both groups becomes inactive, the room starts its configured absence delay. The room becomes vacant only if all sensors remain inactive for the complete delay. Any trigger or persistent sensor becoming active during the delay cancels the timer.

### Example

```text
PIR ON, mmWave OFF       -> room remains vacant
PIR ON, mmWave ON        -> room becomes occupied
PIR OFF, mmWave ON       -> room remains occupied
PIR OFF, mmWave OFF      -> absence delay starts
no sensor reactivates    -> room becomes vacant
```

## Natural illuminance model

- Multiple illuminance sensors can be selected for a room.
- Their average is stored only while all lights managed by the room are off.
- The stored value represents the best available estimate of natural illuminance before automatic lighting affects the sensors.
- The integration never turns lights off temporarily to measure lux and never performs a visible off/on test.
- If no stored lux value is available, room covers and sun elevation are used as a fallback.
- Covers in `unavailable` or `unknown` state are ignored. Any other cover state except `closed` is considered open.

## Lighting profiles

Each room can have separate groups of lights for:

- Day
- Evening
- Night

The current period is calculated from the schedule configured in Home Settings. Schedule fields are intentionally not duplicated in individual room settings.

Managed lights turn on only when:

```text
room is occupied
AND
artificial light is needed
AND
room automation is enabled
```

## Home Settings

Add Home Settings once. It contains:

- Morning start
- Evening start
- Night start
- Default illuminance threshold
- Default absence delay

The three schedule values are global and are read by every room in real time.

The threshold and delay are only defaults offered while creating a new room. Existing rooms keep their own room-specific values when the defaults change.

## Room settings

Add one room entry for each existing Home Assistant area you want to manage. A room options page contains:

- Trigger presence sensors
- Persistent presence sensors
- Illuminance sensors
- Covers
- Day lights
- Evening lights
- Night lights
- Illuminance threshold
- Absence delay

Every option includes an explanation directly in the Home Assistant UI.

## Entities created for each room

The room device exposes entities similar to:

- `binary_sensor.<room>_presence`
- `binary_sensor.<room>_light_needed`
- `sensor.<room>_presence_reason`
- `sensor.<room>_lighting_reason`
- `sensor.<room>_period`
- `sensor.<room>_stored_natural_illuminance`
- `switch.<room>_automation`
- `select.<room>_mode`
- `number.<room>_illuminance_threshold`
- `number.<room>_absence_delay`

Entity IDs are assigned by Home Assistant and may differ depending on the room name and existing entities.

## Installation with HACS

1. In HACS, open the three-dot menu and select **Custom repositories**.
2. Add `https://github.com/Mattiabatto/adaptive_room_manager` as an **Integration** repository.
3. Install **Adaptive Room Manager**.
4. Restart Home Assistant.
5. Open **Settings → Devices & services → Add integration**.
6. Search for **Adaptive Room Manager**.
7. Create Home Settings once, then add one Room entry for each area to manage.

## Updating

Publish each version as a complete GitHub release, for example `v0.4.0`. HACS periodically checks tracked repositories and creates an update entity when it detects a newer release. Installing the repository update is not automatic unless the user has created a separate Home Assistant automation for the HACS update entity.

To update manually:

1. Publish the new release on GitHub.
2. Wait for HACS to detect it, or open the repository's three-dot menu and select **Update information**.
3. Install the update from **Settings → Updates**, or use **Redownload** from the HACS repository menu.
4. Restart Home Assistant after updating the integration.

## Updating from version 0.3.x

Version 0.4.0 automatically migrates these stored option names:

- `temporary_presence` → `trigger_presence_sensors`
- `persistent_presence` → `persistent_presence_sensors`

Existing room and Home Settings entries should not need to be deleted. After installing the update and restarting Home Assistant, open each room's settings and verify the migrated sensor selections.

## License

MIT License. Copyright Mattia Batto.
