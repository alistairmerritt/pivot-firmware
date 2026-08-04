#!/usr/bin/env python3
"""
Generate local number/word audio clips for Pivot value announcements.

WHY THIS EXISTS
---------------
On ESPHome 2026.6+ the Voice PE crashes when it plays HA-fetched (URL) TTS
audio — see home-assistant-voice-pe#613. Local baked clips (audio_file source)
are unaffected. This script renders a small vocabulary of word clips in YOUR
configured TTS voice, so the firmware can assemble spoken values locally
("Brightness" + "forty" + "seven" + "percent") without ever touching the
crashing path.

Whole-phrase clips (every "Brightness N percent") would be ~30 MB and won't fit
the 16 MB flash, so we compose phrases from ~38 tiny word clips (<2 MB total).

WHAT IT PRODUCES
----------------
  sounds/announcements/*.flac        one clip per vocabulary word (mono/48k/16-bit,
                                     silence-trimmed so they concatenate cleanly)
  tools/_generated_audio_file.yaml   ready-to-paste `audio_file:` + substitutions
                                     blocks referencing the committed clips

USAGE
-----
  export HA_BASE_URL="http://homeassistant.local:8123"   # or your Nabu Casa URL
  export HA_TOKEN="$(cat ~/.ha_token)"                    # long-lived token
  python3 tools/generate_announcement_clips.py --tts-entity tts.piper

  # then commit sounds/announcements/ to the repo so ESPHome can bake the clips.

Requires: python3, `requests`, and `ffmpeg` on PATH.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Vocabulary — the ~38 atoms the firmware composes at playback time.
# Key = clip id (also the filename stem); value = the text spoken into the clip.
# ---------------------------------------------------------------------------
NUMBER_WORDS: dict[str, str] = {
    "num_0": "zero", "num_1": "one", "num_2": "two", "num_3": "three",
    "num_4": "four", "num_5": "five", "num_6": "six", "num_7": "seven",
    "num_8": "eight", "num_9": "nine", "num_10": "ten", "num_11": "eleven",
    "num_12": "twelve", "num_13": "thirteen", "num_14": "fourteen",
    "num_15": "fifteen", "num_16": "sixteen", "num_17": "seventeen",
    "num_18": "eighteen", "num_19": "nineteen",
    "num_20": "twenty", "num_30": "thirty", "num_40": "forty", "num_50": "fifty",
    "num_60": "sixty", "num_70": "seventy", "num_80": "eighty", "num_90": "ninety",
    "num_100": "one hundred",
}
PREFIX_WORDS: dict[str, str] = {
    "prefix_brightness": "Brightness",
    "prefix_speed": "Speed",
    "prefix_volume": "Volume",
    "prefix_temperature": "Temperature",
}
UNIT_WORDS: dict[str, str] = {
    "unit_percent": "percent",
    "unit_degrees": "degrees",
    "unit_open": "percent open",   # cover: "47 percent open"
    "state_closing": "Closing",    # cover at 0
    "state_opening": "Opening",    # cover at 100
}
VOCAB: dict[str, str] = {**NUMBER_WORDS, **PREFIX_WORDS, **UNIT_WORDS}

# Where the committed clips will live / be fetched from at compile time.
CLIP_DIR = Path("sounds/announcements")
RAW_URL_BASE = ("https://github.com/alistairmerritt/pivot-firmware"
                "/raw/main/sounds/announcements")


def ha_tts_bytes(base_url: str, token: str, tts_entity: str, message: str,
                 language: str | None) -> bytes:
    """Ask Home Assistant to render `message` and return the raw audio bytes."""
    payload: dict = {"engine_id": tts_entity, "message": message}
    if language:
        payload["language"] = language
    r = requests.post(
        f"{base_url.rstrip('/')}/api/tts_get_url",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    r.raise_for_status()
    body = r.json()
    # Prefer the relative `path` on our own base_url — the absolute `url` can be an
    # internal address (homeassistant.local) unreachable over a Nabu Casa remote link.
    path = body.get("path")
    audio_url = f"{base_url.rstrip('/')}{path}" if path else body["url"]
    audio = requests.get(audio_url, headers={"Authorization": f"Bearer {token}"}, timeout=30)
    audio.raise_for_status()
    return audio.content


def to_trimmed_flac(raw: bytes, out_path: Path) -> None:
    """Convert arbitrary audio bytes to mono/48k/16-bit FLAC, trimming silence
    from both ends so the clips concatenate without gaps."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # -af silenceremove: strip leading + trailing silence (<-50 dB).
    filt = ("silenceremove=start_periods=1:start_silence=0.02:start_threshold=-50dB,"
            "areverse,"
            "silenceremove=start_periods=1:start_silence=0.02:start_threshold=-50dB,"
            "areverse")
    proc = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", "pipe:0", "-af", filt,
         "-ac", "1", "-ar", "48000", "-sample_fmt", "s16",
         str(out_path)],
        input=raw, capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed for {out_path.name}: "
                           f"{proc.stderr.decode(errors='replace')}")


def write_yaml_snippet(ids: list[str]) -> Path:
    """Emit the audio_file: + substitutions blocks to paste into the firmware."""
    subs = "\n".join(f"  {cid}_file: {RAW_URL_BASE}/{cid}.flac" for cid in ids)
    files = "\n".join(f"  - id: {cid}\n    file: ${{{cid}_file}}" for cid in ids)
    out = Path("tools/_generated_audio_file.yaml")
    out.write_text(
        "# --- paste into the `substitutions:` block ---\n"
        f"{subs}\n\n"
        "# --- append to the `audio_file:` block (line ~2596) ---\n"
        f"{files}\n"
    )
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tts-entity", required=True,
                    help="HA TTS entity id, e.g. tts.piper (match your entity-name voice)")
    ap.add_argument("--base-url", default=os.environ.get("HA_BASE_URL"),
                    help="HA base URL (or set HA_BASE_URL)")
    ap.add_argument("--token", default=os.environ.get("HA_TOKEN"),
                    help="HA long-lived token (or set HA_TOKEN)")
    ap.add_argument("--language", default=None, help="optional TTS language override")
    ap.add_argument("--only", nargs="*",
                    help="generate only these clip ids (for the sequencing test), "
                         "e.g. --only prefix_brightness num_40 num_7 unit_percent")
    ap.add_argument("--dry-run", action="store_true",
                    help="list what would be generated, contact nothing")
    args = ap.parse_args()

    items = {k: v for k, v in VOCAB.items() if not args.only or k in args.only}
    if args.only:
        missing = [c for c in args.only if c not in VOCAB]
        if missing:
            ap.error(f"unknown clip ids: {', '.join(missing)}")

    if args.dry_run:
        for cid, text in items.items():
            print(f"{cid:22} <- {text!r}")
        print(f"\n{len(items)} clips would be generated into {CLIP_DIR}/")
        return 0

    if not args.base_url or not args.token:
        ap.error("HA base URL and token required (flags or HA_BASE_URL / HA_TOKEN)")

    print(f"Rendering {len(items)} clips via {args.tts_entity} …")
    for cid, text in items.items():
        try:
            raw = ha_tts_bytes(args.base_url, args.token, args.tts_entity,
                               text, args.language)
            to_trimmed_flac(raw, CLIP_DIR / f"{cid}.flac")
            print(f"  ✓ {cid:22} {text!r}")
        except Exception as err:  # noqa: BLE001 — report and keep going
            print(f"  ✗ {cid:22} {text!r}: {err}", file=sys.stderr)
            return 1

    snippet = write_yaml_snippet(list(VOCAB.keys()))
    print(f"\nDone. Clips in {CLIP_DIR}/, YAML to paste in {snippet}.")
    print("Next: commit sounds/announcements/ to the repo so ESPHome can bake them.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
