# Security Policy

## Scope

Pivot firmware runs on your local network via the ESPHome API. It does not introduce any cloud services, telemetry, or outbound network connections beyond what is already present in the stock Home Assistant Voice PE firmware.

## Over-the-air (OTA) updates

Both the API connection and OTA updates are authenticated with the device's
`api_encryption_key`:

- **API:** encrypted with the key.
- **OTA:** every upload must be encrypted with the same key. The device
  refuses unencrypted uploads, so there is no separate password to set, guess
  or leak.

The key is **required**. ESPHome refuses to build without a valid one, so
there is no usable default. Use a unique key for each device and keep it
secret: anyone holding it can control the device and replace its firmware.

### Moving from the OTA password

Pivot firmware v0.0.29 and earlier used an `ota_password`. From v0.0.30 it uses
OTA encryption instead, which ESPHome requires from 2027.3.0. To update a
device that has a password:

1. Update ESPHome Device Builder to 2026.10.0 or later.
2. Click **Install**. If the device's current firmware was built with ESPHome
   2026.9.0 or later, it already accepts encrypted uploads and this is all
   you need.
3. If ESPHome stops with *"the device did not offer encryption; refusing to
   send the image in plaintext"*, the current firmware is older than that.
   Change `ref: stable` to `ref: v0.0.29` in the device YAML and install, which
   gives the device firmware that accepts encrypted uploads. Then change it
   back to `ref: stable` and install again.
4. Once the device is on v0.0.30, delete the `ota_password` line from its
   substitutions, and `pivot_ota_password` from `secrets.yaml` when no device
   uses it.

Keep `ota_password` until step 4: v0.0.29 still needs it to build.

### Changing the key

A device only accepts an update encrypted with the key it already has, so
installing with a new key is refused. Changing a device's key means flashing
it over USB. Home Assistant then asks for the new key.

### If you lose the key

Without the `api_encryption_key`, the device must be re-flashed over USB.
Keep the key somewhere that survives a machine rebuild.

See [ESPHome's Security Best Practices](https://esphome.io/guides/security_best_practices/),
which recommends a unique API key per device.

## Reporting a vulnerability

If you discover a security vulnerability in Pivot firmware, please **do not open a public issue**. Instead, report it privately by emailing the maintainer (contact via GitHub profile) or using [GitHub's private vulnerability reporting](https://github.com/alistairmerritt/pivot-firmware/security/advisories/new).

Include:
- A description of the vulnerability
- Steps to reproduce or proof of concept
- Any relevant firmware version or ESPHome version details

You will receive a response as soon as reasonably possible. Confirmed vulnerabilities will be addressed in a patch release, and the reporter will be credited (unless anonymity is requested).

## Supported versions

Only the latest release of Pivot firmware is actively maintained. If you are running an older version, update to the latest before reporting.
