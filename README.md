# Pivot — Firmware

ESPHome firmware for the Home Assistant Voice Preview Edition (VPE) that turns it into a physical control knob for Home Assistant.

> **New to Pivot?** Start at the [Pivot documentation site](https://alistairmerritt.github.io/pivot) for a full getting started guide, integration setup, and troubleshooting.

## What is Pivot firmware?

Pivot firmware extends the stock VPE firmware with four colour-coded control banks. Each bank can be assigned to a Home Assistant entity — turn the knob to adjust it, press the button to toggle it. The LED ring shows the active bank colour and control values in real time.

Pivot firmware works alongside the [Pivot HA integration](https://github.com/alistairmerritt/pivot-integration), which provisions all the required entities and automation logic automatically.

## Requirements

- Home Assistant Voice Preview Edition (VPE)
- ESPHome installed (via the ESPHome add-on or ESPHome dashboard)
- The [Pivot HA integration](https://github.com/alistairmerritt/pivot-integration) installed in Home Assistant

## Quick start

1. Download `home-assistant-voice.yaml` from this repository
2. Open it and fill in the substitutions block at the top (see below)
3. Flash it to your VPE via the ESPHome dashboard or `esphome run`
4. Add the device to Home Assistant via the ESPHome integration
5. Install the [Pivot HA integration](https://github.com/alistairmerritt/pivot-integration) and add your device

## Substitutions block

All device-specific configuration is at the top of the YAML file. You only need to edit this section:

```yaml
substitutions:
  # ESPHome device name (slug, no spaces) — shown in ESPHome dashboard
  device_name: home_assistant_voice_lounge

  # Friendly name — shown in Home Assistant and ESPHome UI
  device_friendly_name: Lounge VPE

  # Pivot device suffix — must be unique per device, no spaces or dashes.
  # Must match exactly what you enter in the Pivot integration setup.
  device_suffix: ha_voice_lounge

  # WiFi credentials
  wifi_ssid: "YourWiFiName"
  wifi_password: "YourWiFiPassword"

  # API encryption key — generate a new one per device at:
  # https://esphome.io/components/api.html#configuration-variables
  api_encryption_key: "your_generated_key_here"
```

The `device_suffix` value must be unique for each device and must match exactly what you enter when setting up the Pivot integration in Home Assistant.

## Multiple devices

Flash a separate copy of the firmware for each VPE, with a unique `device_suffix` for each. For example:

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
