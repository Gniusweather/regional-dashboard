#!/usr/bin/env python3
"""Plot latest TNCC (78988) observed sounding with SounderPy."""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import sounderpy as spy

OUT = Path("plots/sounderpy-78988.png")
STAMP = Path("plots/sounderpy-78988.txt")
OUT.parent.mkdir(parents=True, exist_ok=True)


def latest_slots():
    now = datetime.now(timezone.utc)
    if now.hour >= 13:
        t = now.replace(hour=12, minute=0, second=0, microsecond=0)
    elif now.hour >= 1:
        t = now.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        t = (now - timedelta(days=1)).replace(hour=12, minute=0, second=0, microsecond=0)
    slots = []
    for i in range(6):
        slots.append(t - timedelta(hours=12 * i))
    return slots


def fetch():
    last_err = None
    for t in latest_slots():
        y, m, d, hh = f"{t.year}", f"{t.month:02d}", f"{t.day:02d}", f"{t.hour:02d}"
        for stn in ("TNCC", "78988"):
            try:
                print(f"try {stn} {y}-{m}-{d} {hh}Z")
                data = spy.get_obs_data(stn, y, m, d, hh, hush=True)
                return data, t, stn
            except Exception as e:
                last_err = e
                print(" fail", stn, e)
    raise RuntimeError(f"no TNCC sounding: {last_err}")


def main():
    data, t, stn = fetch()
    spy.build_sounding(
        data,
        style="full",
        dark_mode=True,
        radar=None,
        map_zoom=0,
        special_parcels="simple",
        dpi=130,
        save=True,
        filename=str(OUT.with_suffix("")),
    )
    # SounderPy may write .png from filename without suffix or with it
    produced = OUT if OUT.exists() else Path(str(OUT.with_suffix("")) + ".png")
    if not produced.exists():
        # some versions write exactly filename as given
        for p in Path(".").glob("sounderpy*") :
            print("found", p)
        for p in Path("plots").glob("*"):
            print("plots", p)
    STAMP.write_text(
        f"{stn} {t.strftime('%Y-%m-%d %H')}Z  source=Wyoming  style=full dark\n",
        encoding="utf-8",
    )
    print("wrote", produced if produced.exists() else OUT, "stamp", STAMP.read_text())


if __name__ == "__main__":
    main()
