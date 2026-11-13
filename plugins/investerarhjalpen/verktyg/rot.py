"""Var verktyget och användarens data ligger.

VERKTYG = tilläggets mapp (metod, skript, webbsidans mall). Uppdateras från GitHub.
DATA    = användarens egen mapp (bolag, journal, strategi, sidan). Rörs aldrig av uppdateringar.
DATA hittas så här: miljövariabeln INVESTERAR_DATA, annars närmaste mapp uppåt från den
aktuella mappen som innehåller installningar.json, annars den aktuella mappen.
"""
import os
from pathlib import Path

VERKTYG = Path(__file__).resolve().parent.parent


def _data():
    e = os.environ.get("INVESTERAR_DATA")
    if e:
        return Path(e).expanduser().resolve()
    p = Path.cwd().resolve()
    for d in [p, *p.parents]:
        if (d / "installningar.json").exists():
            return d
    return p


DATA = _data()
