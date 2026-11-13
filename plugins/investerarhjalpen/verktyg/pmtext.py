#!/usr/bin/env python3
"""Skriver ut texten i ett pressmeddelande (MFN-länk) utan HTML. Kör: python3 -I verktyg/pmtext.py <url> [maxtecken]"""
import html, re, sys, urllib.request
u = sys.argv[1]; mx = int(sys.argv[2]) if len(sys.argv) > 2 else 6000
h = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read().decode("utf-8", "replace")
kand = re.findall(r'<div class="(?:body|mfn-body)[^"]*"[^>]*>(.*?)(?=<div class="(?:footer|mfn-footer|attachments|source)|<footer)', h, re.S)
class _M:
    def __init__(s, t): s.t = t
    def group(s, i): return s.t
m = _M(max(kand, key=len)) if kand else (re.search(r'class="content s-cis"[^>]*>(.*)', h, re.S) or re.search(r"<body(.*?)</body>", h, re.S))
t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", m.group(1), flags=re.S)
t = html.unescape(re.sub(r"<[^>]+>", " ", t)); t = re.sub(r"[ \t]+", " ", t); t = re.sub(r"\n\s*\n+", "\n", t)
print(t.strip()[:mx])
