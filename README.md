# Pivot Firmware

[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

Custom ESPHome firmware for the Home Assistant Voice Preview Edition (VPE) that turns it into a physical control dial for Home Assistant while preserving its core voice functionality.

Pivot firmware works alongside the [Pivot integration](https://github.com/alistairmerritt/pivot-integration), which handles entity provisioning and bank configuration on the Home Assistant side.

---

### Full documentation

**This README is a quick overview of this repository only.**
For installation, setup, configuration, examples and troubleshooting, use the full Pivot documentation:

**https://alistairmerritt.github.io/pivot/**

---

## What this repository contains

- ESPHome YAML firmware for the Home Assistant Voice Preview Edition
- Pivot bank switching behaviour (four colour-coded control banks)
- Rotary dial and button handling
- LED ring feedback and colour control
- Voice functionality preservation
- Communication support for the Pivot HA integration

For full documentation on how these components work and how to set them up, see the [Pivot documentation site](https://alistairmerritt.github.io/pivot/).

## How the firmware is distributed

| File | What it is | Do you use it directly? |
| --- | --- | --- |
| `home-assistant-voice.yaml` | Full shared firmware source | **No** — ESPHome fetches this automatically |
| `devices/example.yaml` | Minimal per-device config template | **Yes** — copy this into ESPHome for each device |

**You never need to open or copy `home-assistant-voice.yaml`.** It is fetched automatically from this repository when ESPHome compiles your device. The only file you work with is `devices/example.yaml`.

## Requirements

- Home Assistant Voice Preview Edition (VPE)
- **ESPHome Device Builder 2026.5.0 or later** — Pivot firmware depends on components merged into ESPHome core in this release. Older versions will fail to compile. Update the add-on before flashing.
- The [Pivot integration](https://github.com/alistairmerritt/pivot-integration) installed in Home Assistant

## Installation

Firmware flashing and full setup instructions are covered in the Pivot documentation:

https://alistairmerritt.github.io/pivot/firmware/

For a full getting started guide covering both firmware and integration setup, see:

https://alistairmerritt.github.io/pivot/getting-started/

---

## Related links

- [Pivot documentation](https://alistairmerritt.github.io/pivot/) — installation, setup, examples and troubleshooting
- [Pivot project page](https://madewithmerritt.com/pivot/) — hardware overview and demonstrations
- [Pivot integration](https://github.com/alistairmerritt/pivot-integration) — HACS integration for Home Assistant

## License

Pivot firmware includes work derived from the official [Home Assistant Voice Preview Edition](https://github.com/esphome/home-assistant-voice-pe) ESPHome configuration and is licensed under the [Apache License 2.0](LICENSE).
