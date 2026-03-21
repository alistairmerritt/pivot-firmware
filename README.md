# Pivot — Firmware

ESPHome firmware for the Home Assistant Voice Preview Edition (VPE) that turns it into a physical control knob for Home Assistant.

> **New to Pivot?** Start at the [Pivot documentation site](https://alistairmerritt.github.io/pivot) for a full getting started guide, integration setup, and troubleshooting.

## What is Pivot firmware?

Pivot firmware extends the stock VPE firmware with four colour-coded control banks. Each bank can be assigned to a Home Assistant entity — turn the knob to adjust it, press the button to toggle it. The LED ring shows the active bank colour and control values in real time.

Pivot firmware works alongside the [Pivot HA integration](https://github.com/alistairmerritt/pivot-integration), which provisions all the required entities and automation logic automatically.

## Requirements

- Home Assistant Voice Preview Edition (VPE)
- ESPHome installed (via the ESPHome Device Builder add-on)
- The [Pivot HA integration](https://github.com/alistairmerritt/pivot-integration) installed in Home Assistant

## Quick start

1. Copy `devices/example.yaml` into your ESPHome dashboard as a new device
2. Fill in the substitutions (device name, suffix, WiFi, API key)
3. Click **Install → Wirelessly** — or via USB for the very first flash
4. Add the device to Home Assistant via the ESPHome integration
5. Install the [Pivot HA integration](https://github.com/alistairmerritt/pivot-integration) and add your device

The example file uses ESPHome's `packages:` feature to pull the full firmware from GitHub automatically — you only maintain the handful of lines unique to your device. When a new version of Pivot firmware is released, just hit **Install** in ESPHome and it pulls the latest.

## Per-device configuration

Each device needs only these values. Everything else comes from the shared firmware:

```yaml
substitutions:
  device_name: home_assistant_voice_lounge      # ESPHome slug — no spaces or dashes
  device_friendly_name: Lounge VPE             # Display name in HA and ESPHome
  device_suffix: ha_voice_lounge               # Unique per device — must match Pivot integration
  wifi_ssid: !secret wifi_ssid                 # From secrets.yaml (recommended)
  wifi_password: !secret wifi_password
  api_encryption_key: "generate-unique-per-device"
  led_offset: '6'                              # '6' = flat, '0' = upright on stand

packages:
  pivot:
    url: https://github.com/alistairmerritt/pivot-firmware
    ref: main
    file: home-assistant-voice.yaml
    refresh: 1d
```

See `devices/example.yaml` for the full annotated template.

The `device_suffix` must be unique for each device and must match exactly what you enter when setting up the Pivot integration in Home Assistant.

## Multiple devices

Each VPE gets its own minimal config file in ESPHome with a unique `device_suffix`. The shared firmware is pulled from GitHub automatically — no copying or maintaining separate full YAML files per device.

| Device | `device_suffix` |
| --- | --- |
| Lounge VPE | `ha_voice_lounge` |
| Bedroom VPE | `ha_voice_bedroom` |
| Study VPE | `ha_voice_study` |

## Bank colours

Default LED colours per bank. These can be changed from within Home Assistant using the bank colour light entities created by the integration.

| Bank | Default Colour |
| --- | --- |
| 1 | Blue `#2889FF` |
| 2 | Orange `#FF7D19` |
| 3 | Green `#97FF3D` |
| 4 | Purple `#C800FF` |

## Full documentation

For a full getting started guide, integration setup, and troubleshooting see the [Pivot documentation site](https://alistairmerritt.github.io/pivot).

## Related repositories

- [pivot-integration](https://github.com/alistairmerritt/pivot-integration) — HACS integration for Home Assistant
- [pivot docs](https://alistairmerritt.github.io/pivot/) — documentation site

---

## License

Pivot firmware includes work derived from the official [Home Assistant Voice Preview Edition](https://github.com/esphome/home-assistant-voice-pe) ESPHome configuration and is licensed under the [Apache License 2.0](LICENSE).
