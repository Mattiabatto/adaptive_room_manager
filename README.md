# Adaptive Room Manager

A Home Assistant custom integration that manages room presence and adaptive lighting without YAML, helpers, blueprints, or user-created automations.

## Status

Early preview (`0.1.0`). Test in a non-critical Home Assistant installation before daily use.

## Features

- UI setup with one global house entry and one entry per existing Home Assistant area.
- Temporary and persistent presence inputs.
- Binary or positional covers; unavailable covers are ignored.
- Natural lux is stored only while managed lights are off, preventing artificial light from corrupting the decision.
- Day, evening, and night light groups.
- Generated presence, light-needed, diagnostic, enable, mode, absence-delay, lux-threshold, and night-start entities.
- No disruptive lux test after opening a cover.

## Installation

Copy `custom_components/adaptive_room_manager` into `/config/custom_components`, restart Home Assistant, then add **Adaptive Room Manager** from Settings > Devices & services. HACS custom repository URL: `https://github.com/Mattiabatto/adaptive_room_manager` (category: Integration).

## Setup

1. Add a **house** entry.
2. Add one **room** entry for each existing Home Assistant area you want to manage.
3. Select presence sources, lux sensors, covers, and the lights for each period.

## Important preview limitations

- Manual on/off override detection is scaffolded conceptually but not yet reliable across all light integrations.
- Light profiles currently switch entities without per-light brightness or color-temperature settings.
- The first preview requires validation on a real Home Assistant 2026.7 system.

## License
MIT — Mattia Batto
