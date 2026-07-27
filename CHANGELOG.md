# Changelog

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
