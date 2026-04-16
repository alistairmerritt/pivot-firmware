# Contributing to Pivot Firmware

Thanks for your interest in contributing. Contributions of all kinds are welcome — bug reports, fixes, documentation improvements, and feature suggestions.

## Before you start

- Check the [open issues](https://github.com/alistairmerritt/pivot-firmware/issues) to see if your bug or idea is already tracked.
- For large changes, open an issue first to discuss the approach before writing code.

## How to contribute

1. Fork the repository and create a branch from `main`.
2. Make your changes in `home-assistant-voice.yaml` or `devices/example.yaml`.
3. Test on real hardware — Pivot firmware changes can only be verified on a physical VPE. State what you tested in the PR.
4. Open a pull request. Fill in the PR template — describe what changed, why, and how you tested it.

## What to test

Before opening a PR, verify:

- The firmware compiles cleanly in ESPHome Device Builder
- Basic bank control still works (turn adjusts value, press toggles)
- LED feedback is correct for the active bank
- The voice assistant still activates via wake word
- Double press correctly toggles Control Mode on and off

If your change touches bank switching, LED effects, or voice assistant interaction, test those paths specifically.

## ESPHome version

Pivot firmware requires **ESPHome Device Builder 2026.4.0 or later**. Do not introduce dependencies on ESPHome features newer than this without updating `min_version` and noting the change clearly in the PR.

## Coding style

Follow the patterns already used in `home-assistant-voice.yaml`. Keep substitutions in the `substitutions:` block. Keep lambdas concise and comment non-obvious logic.

## Reporting bugs

Use the [bug report template](https://github.com/alistairmerritt/pivot-firmware/issues/new?template=bug_report.md). Include your firmware version, ESPHome version, and a build log if the issue is a compile failure.

## Questions

If you have a question about how Pivot works, open a [discussion](https://github.com/alistairmerritt/pivot-firmware/discussions) rather than an issue.
