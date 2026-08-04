#!/usr/bin/env python3
"""
Generate local value-announcement audio clips for Pivot.

WHY THIS EXISTS
---------------
On ESPHome 2026.6+ the Voice PE crashes when it plays HA-fetched (URL) TTS audio
(home-assistant-voice-pe#613). Local baked clips (audio_file source) are immune.
Composing phrases from separate word clips was tried and rejected — the
announcement pipeline spins up per clip, so every clip has a ~0.5 s lead-in and
stitched words sound like "Brightness ... forty ... seven ... percent".

So each announceable phrase is rendered as ONE whole clip in your configured TTS
voice ("Brightness forty seven percent"). The TTS speaks the digits naturally, so
we just feed it "Brightness 47 percent". As low-bitrate mono MP3 each clip is
~7 KB, so the full 505-clip set is ~3.3 MB — fine for 16 MB flash and gapless.

CLIP SET (id -> spoken text), n = 0..100:
  ann_brightness_{n}  "Brightness {n} percent"   (light)
  ann_volume_{n}      "Volume {n} percent"       (media_player)
  ann_speed_{n}       "Speed {n} percent"        (fan)
  ann_temp_{n}        "Temperature {n} degrees"  (climate)
  ann_cover_{n}       "{n} percent open"         (cover; 0 -> "Closing", 100 -> "Opening")

USAGE
-----
  export HA_BASE_URL="https://<your>.ui.nabu.casa"
  export HA_TOKEN="$(cat ~/.ha_token)"
  python3 tools/generate_announcement_clips.py --tts-entity tts.home_assistant_cloud
  # resumes: already-rendered clips are skipped. Then commit sounds/announcements/.

  python3 tools/generate_announcement_clips.py --emit-yaml    # write the audio_file block only
  python3 tools/generate_announcement_clips.py --dry-run       # list, contact nothing

Requires: python3, `requests`, `ffmpeg`.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

import requests

CLIP_DIR = Path("sounds/announcements")
# Branch the firmware currently pulls for testing; flip to /main when merged.
RAW_URL_BASE = ("https://github.com/alistairmerritt/pivot-firmware"
                "/raw/feature/local-value-announcements/sounds/announcements")
N_MAX = 100  # values 0..100 inclusive


def build_clips() -> dict[str, str]:
    """id -> spoken text for every announceable phrase."""
    clips: dict[str, str] = {}
    for n in range(N_MAX + 1):
        clips[f"ann_brightness_{n}"] = f"Brightness {n} percent"
        clips[f"ann_volume_{n}"] = f"Volume {n} percent"
        clips[f"ann_speed_{n}"] = f"Speed {n} percent"
        clips[f"ann_temp_{n}"] = f"Temperature {n} degrees"
        if n == 0:
            clips["ann_cover_0"] = "Closing"
        elif n == N_MAX:
            clips[f"ann_cover_{N_MAX}"] = "Opening"
        else:
            clips[f"ann_cover_{n}"] = f"{n} percent open"
    return clips


def ha_tts_bytes(base_url: str, token: str, tts_entity: str, message: str,
                 language: str | None) -> bytes:
    payload: dict = {"engine_id": tts_entity, "message": message}
    if language:
        payload["language"] = language
    r = requests.post(f"{base_url.rstrip('/')}/api/tts_get_url", json=payload,
                      headers={"Authorization": f"Bearer {token}"}, timeout=30)
    r.raise_for_status()
    body = r.json()
    path = body.get("path")
    audio_url = f"{base_url.rstrip('/')}{path}" if path else body["url"]
    audio = requests.get(audio_url, headers={"Authorization": f"Bearer {token}"}, timeout=30)
    audio.raise_for_status()
    return audio.content


def to_trimmed_mp3(raw: bytes, out_path: Path) -> None:
    """Silence-trimmed mono 24 kHz / 32 kbps MP3 (~7 KB per phrase)."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    filt = ("silenceremove=start_periods=1:start_silence=0.02:start_threshold=-50dB,"
            "areverse,"
            "silenceremove=start_periods=1:start_silence=0.02:start_threshold=-50dB,"
            "areverse")
    proc = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", "pipe:0",
         "-af", filt, "-ac", "1", "-ar", "24000", "-b:a", "32k", str(out_path)],
        input=raw, capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed for {out_path.name}: "
                           f"{proc.stderr.decode(errors='replace')}")


def write_yaml_snippet(ids: list[str]) -> Path:
    files = "\n".join(f"  - id: {cid}\n    file: {RAW_URL_BASE}/{cid}.mp3" for cid in ids)
    out = Path("tools/_generated_audio_file.yaml")
    out.write_text("# Auto-generated value-announcement clips — append to `audio_file:`.\n"
                   f"{files}\n")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tts-entity", default="tts.home_assistant_cloud")
    ap.add_argument("--base-url", default=os.environ.get("HA_BASE_URL"))
    ap.add_argument("--token", default=os.environ.get("HA_TOKEN"))
    ap.add_argument("--language", default=None)
    ap.add_argument("--only", nargs="*", help="only these clip ids")
    ap.add_argument("--emit-yaml", action="store_true", help="write audio_file block, render nothing")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--throttle", type=float, default=0.15, help="seconds between TTS calls")
    args = ap.parse_args()

    all_clips = build_clips()
    if args.emit_yaml:
        print(f"Wrote {write_yaml_snippet(list(all_clips))} ({len(all_clips)} entries).")
        return 0

    items = {k: v for k, v in all_clips.items() if not args.only or k in args.only}
    if args.dry_run:
        for cid, text in list(items.items())[:12]:
            print(f"{cid:22} <- {text!r}")
        print(f"… {len(items)} clips total -> {CLIP_DIR}/")
        return 0

    if not args.base_url or not args.token:
        ap.error("need HA base URL + token (flags or HA_BASE_URL / HA_TOKEN)")

    done = skipped = 0
    total = len(items)
    print(f"Rendering {total} clips via {args.tts_entity} …")
    for i, (cid, text) in enumerate(items.items(), 1):
        out = CLIP_DIR / f"{cid}.mp3"
        if out.exists() and out.stat().st_size > 0:
            skipped += 1
            continue
        last_err = None
        for attempt in range(5):  # retry transient network/SSL drops
            try:
                raw = ha_tts_bytes(args.base_url, args.token, args.tts_entity, text, args.language)
                to_trimmed_mp3(raw, out)
                last_err = None
                break
            except Exception as err:  # noqa: BLE001
                last_err = err
                time.sleep(1.5 * (attempt + 1))
        if last_err is not None:
            print(f"  ✗ {cid} {text!r}: {last_err}", file=sys.stderr)
            return 1
        done += 1
        if done % 25 == 0 or i == total:
            print(f"  {i}/{total}  (rendered {done}, skipped {skipped})")
        time.sleep(args.throttle)

    write_yaml_snippet(list(all_clips))
    print(f"\nDone: {done} rendered, {skipped} already present. "
          f"Clips in {CLIP_DIR}/, block in tools/_generated_audio_file.yaml.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
