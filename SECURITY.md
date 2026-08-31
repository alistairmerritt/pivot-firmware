# Security Policy

## Scope

Pivot firmware runs on your local network via the ESPHome API. It does not introduce any cloud services, telemetry, or outbound network connections beyond what is already present in the stock Home Assistant Voice PE firmware.

## Over-the-air (OTA) updates

Both the API connection and OTA updates are authenticated:

- **API:** encrypted with a unique per-device `api_encryption_key`.
- **OTA:** protected by a unique per-device `ota_password`.

Both are **required**. There is no usable default for either.

### Why this is enforced at build time

ESPHome does not validate the OTA password, so a missing one fails quietly:
an unset substitution passes through as the literal string `${ota_password}`,
and an empty password is accepted. Either would produce a device whose
firmware anyone on the local network could replace — and this device is a
microphone. API encryption does **not** protect the OTA endpoint.

Pivot therefore fails the **compile** rather than shipping an unprotected
device. Building without a password stops with:

```
error: static assertion failed: Set a unique ota_password in your device YAML - see SECURITY.md
```

### Setting it

Generate a unique value per device and store it in your ESPHome
`secrets.yaml` (never commit that file):

```bash
openssl rand -hex 16
```

**Requirements:** at least 12 characters. Use the hexadecimal output above.
The build-time guard embeds the password in a C++ string literal, so quotes,
backslashes and other escape characters are not safely supported — stick to
hex and there is nothing to think about.

```yaml
# secrets.yaml
pivot_ota_lounge: "a1b2c3d4e5f6..."

# devices/<your-device>.yaml
substitutions:
  ota_password: !secret pivot_ota_lounge
```

### Upgrading an existing device

Adding a password is **not** a bricking risk. The first upload still succeeds
unauthenticated, because the firmware currently running on the device has no
password set. Enforcement begins with the update after that.

### Rotating the password

Changing the password is **not** a one-step edit. ESPHome uses the configured
password for two different things at once: authenticating the upload, *and*
setting the password baked into the firmware being uploaded. So if you simply
swap in a new value and install, the upload authenticates with the **new**
password against firmware that still expects the **old** one, and fails.

ESPHome's documented workaround is a two-stage transition.

**Stage 1** — keep the OLD password so the upload can authenticate, and have the
new firmware set the new one at boot:

```yaml
substitutions:
  ota_password: !secret pivot_ota_lounge      # still the OLD value

esphome:
  on_boot:
    # List form, and a priority ABOVE Pivot's own 375 automation. Both matter:
    # ESPHome concatenates lists when merging packages, so a mapping-form
    # on_boot here would be appended to the end of Pivot's automation — after
    # its ten-minute delay — and the new password would not be set for ten
    # minutes.
    - priority: 800
      then:
        - lambda: |-
            id(ota_esphome).set_auth_password("THE-NEW-PASSWORD");
```

Install. The device authenticates with the old password and reboots using the
new one. This runs as its own automation, so Pivot's boot behaviour is
unaffected and there is no delay to wait out.

**Stage 2** — remove that `on_boot` block, put the new value in `secrets.yaml`,
and install again to confirm the new password authenticates.

See [Changing the OTA password](https://esphome.io/components/ota/esphome/) for
the upstream description.

If that feels fiddly, re-flashing over USB is a perfectly reasonable
alternative — it is the same amount of physical work and has fewer steps.

### If you lose the password

There is **no network recovery path**. The device must be re-flashed over USB.
Keep these values somewhere that survives a machine rebuild.

See [ESPHome's Security Best Practices](https://esphome.io/guides/security_best_practices/),
which recommends unique API keys and OTA passwords per device.

## Reporting a vulnerability

If you discover a security vulnerability in Pivot firmware, please **do not open a public issue**. Instead, report it privately by emailing the maintainer (contact via GitHub profile) or using [GitHub's private vulnerability reporting](https://github.com/alistairmerritt/pivot-firmware/security/advisories/new).

Include:
- A description of the vulnerability
- Steps to reproduce or proof of concept
- Any relevant firmware version or ESPHome version details

You will receive a response as soon as reasonably possible. Confirmed vulnerabilities will be addressed in a patch release, and the reporter will be credited (unless anonymity is requested).

## Supported versions

Only the latest release of Pivot firmware is actively maintained. If you are running an older version, update to the latest before reporting.
