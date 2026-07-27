# Changelog

## 0.6.0

- Replaced external sleep activation entities with a room-owned `Sleep mode` switch.
- Removed forced sleep occupancy.
- Replaced the forced occupancy timeout with `Sleep absence delay`.
- While Sleep mode is active, the sleep absence delay replaces the room's normal absence delay after all presence sensors become inactive.
- Added an option to turn off the room Sleep mode switch automatically when the room becomes vacant.
- Managed lights are switched off when the room becomes vacant, even when Sleep mode remains enabled.
- Sleep lighting is reapplied when the room becomes occupied again while Sleep mode remains enabled.
- Pre-sleep snapshots now include only lights that Sleep mode actually changes.
- Added migration from 0.5.x settings.

## 0.5.0

- Added sleep mode with per-light brightness, RGB color, color temperature and transitions.
- Added persistent pre-sleep light snapshots.
