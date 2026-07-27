# Adaptive Room Manager

Adaptive Room Manager is a Home Assistant custom integration that creates an adaptive controller and a dedicated Home Assistant device for each configured room.

> **Status:** early technical preview. Test carefully before relying on it in a production home.

## Features

- Native Home Assistant integration and config flow; no YAML, helpers, blueprints, or template sensors required.
- Optional **Home Settings** entry containing defaults for newly created rooms.
- One independent config entry and one device for every room.
- Rooms are selected from existing Home Assistant areas.
- Temporary and persistent presence sources.
- Multiple illuminance sensors and room covers.
- Separate day, evening, and night light groups.
- Per-room timing, lux threshold, and absence delay.
- Natural illuminance is stored only while managed lights are off; lights are never toggled to perform a lux test.
- Unavailable covers are ignored.
- Presence, lighting decision, period, automation, mode, threshold, and delay entities are grouped under the room device.

## Installation with HACS

1. Open HACS and choose **Custom repositories**.
2. Add `https://github.com/Mattiabatto/adaptive_room_manager` as an **Integration** repository.
3. Install **Adaptive Room Manager**.
4. Restart Home Assistant.
5. Open **Settings → Devices & services → Add integration** and search for Adaptive Room Manager.

## Configuration

### Home Settings

Add this entry once. It defines the defaults shown when adding new rooms:

- evening start;
- night start;
- morning start;
- illuminance threshold;
- absence delay.

Changing Home Settings does not overwrite existing room-specific settings.

### Room

Add one entry for each existing Home Assistant area you want to manage. Each room creates a dedicated device associated with that area. Use the entry's settings gear to edit its sensors, lights, schedules, thresholds, and delay.

## Updating from an earlier preview

Because the config-entry model changed during the preview phase, remove old Adaptive Room Manager entries before installing this version, restart Home Assistant, and configure Home Settings and rooms again.

## License

MIT License. Copyright Mattia Batto.
