#!/usr/bin/env python3
"""Svarar "ja" om tillägget har uppdaterats sedan sidan senast byggdes (då ska sidan byggas om och publiceras), annars "nej"."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from rot import DATA, verktygsversion  # noqa: E402
f = DATA / "site" / ".verktyg-version"
print("ja" if not f.exists() or f.read_text().strip() != verktygsversion() else "nej")
