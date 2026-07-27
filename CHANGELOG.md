# Changelog

## 0.4.0

- Renamed `temporary_presence` to `trigger_presence_sensors`.
- Renamed the stored persistent presence key to `persistent_presence_sensors`.
- Added automatic config-entry migration from version 0.3.x.
- Changed vacant-to-occupied activation to require at least one active trigger sensor **and** at least one active persistent sensor.
- Allowed the same entity to be configured in both presence groups and satisfy both activation conditions.
- Kept an occupied room active while at least one sensor from either presence group remains active.
- Started the absence delay only after every trigger and persistent sensor becomes inactive.
- Added detailed field descriptions to room creation, room options, Home Settings creation, and Home Settings options.
- Split Home Settings and Room options into separately translated flows.
- Rewrote the README with the full presence state machine, lux behavior, installation, migration, and update instructions.

## 0.3.1

- Removed morning, evening, and night schedule fields from room creation and room options.
- Made every room read the schedule exclusively from the global Home Settings entry.
- Kept illuminance threshold and absence delay configurable per room.
- Existing 0.3.0 room entries remain compatible; legacy room schedule values are ignored.

## 0.3.0

- Added a config-flow menu for **Home Settings** and **Room** entries.
- Added one optional Home Settings entry containing defaults for newly added rooms.
- Preserved independent per-room settings through each room entry's options flow.
- Preserved one dedicated Home Assistant device per configured room and associated it with the selected existing area.
- Updated integration metadata and documentation for the new entry model.

## 0.2.0

- Reworked rooms as native config entries associated with existing Home Assistant areas.
- Added a dedicated device for every configured room.
- Added per-room options flow.
- Removed helper integration classification.

## 0.1.0

- Initial technical preview.
