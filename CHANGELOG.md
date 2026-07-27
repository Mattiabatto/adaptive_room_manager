# Changelog

## 0.6.2

- Fixed saving Home Settings and room options on Home Assistant versions that reject config entry update listeners together with `OptionsFlowWithReload`.
- Changed the options flow to the standard `OptionsFlow`, retaining the existing update listener so Home Settings changes still reload all room entries and re-register the Morning, Evening and Night schedules.
- No lighting, presence, lux or Sleep mode behavior was otherwise changed from 0.6.1.

## 0.6.1

- Changed normal lighting to a one-shot profile per occupancy cycle: after ARM applies the Day, Evening or Night profile, later evaluations no longer resend `light.turn_on`.
- A light switched off manually while the room remains occupied stays off until the user turns it on again or the room becomes vacant and is occupied again.
- Enabled Day/Evening/Night transition synchronization remains an explicit exception and may apply the newly entered profile.
- Reset the one-shot lighting cycle only after the configured absence delay expires and the room becomes vacant.
- Fixed the room entity-list builder so boolean period-synchronization options are not treated as entity lists.
- Fixed the room Options menu labels and added a root `strings.json` translation source.
- Added exact daily scheduling at Morning, Evening and Night boundaries.
- Added per-room synchronization switches for entering Day, Evening and Night.
- When synchronization is enabled, managed lights outside the new period profile are turned off and missing profile lights are turned on when lighting is required.
- When synchronization is disabled, lights retained from the previous period are not removed merely because the period changed.
- Home Settings changes now reload room entries so period schedules are registered again.
- Refined Sleep mode snapshots so only lights whose state, brightness or color will actually change are saved.
- Avoided sending Sleep mode commands to lights already matching their configured sleep profile.

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
