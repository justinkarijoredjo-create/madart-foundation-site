#!/usr/bin/env python3
"""Byte-voor-byte diff van build/ tegen de repository.

De repository is tijdens de reconstructie de maatstaf: pas als elk bestand
identiek is, produceert de generator weer wat er live staat.
"""
import hashlib, sys, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RAW = ("https://raw.githubusercontent.com/justinkarijoredjo-create/"
       "madart-foundation-site/main/")
BUILD = Path(__file__).parent / "build"
EXT = (".html", ".css", ".xml", ".txt", ".json", ".webmanifest")


def check(p):
    lokaal = p.read_bytes()
    for poging in range(3):
        try:
            req = urllib.request.Request(RAW + p.name + "?cb=%d" % time.time_ns(),
                                         headers={"Cache-Control": "no-cache"})
            with urllib.request.urlopen(req, timeout=40) as r:
                repo = r.read()
            if hashlib.md5(repo).hexdigest() == hashlib.md5(lokaal).hexdigest():
                return ("gelijk", p.name, 0)
            return ("anders", p.name, len(lokaal) - len(repo))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return ("nieuw", p.name, len(lokaal))
            return ("fout", f"{p.name}: {e}", 0)
        except Exception as e:
            if poging == 2:
                return ("fout", f"{p.name}: {e}", 0)
            time.sleep(2)


bestanden = sorted(p for p in BUILD.iterdir()
                   if p.is_file() and (p.suffix.lower() in EXT or p.name == "CNAME"))
tally = {"gelijk": [], "anders": [], "nieuw": [], "fout": []}
with ThreadPoolExecutor(max_workers=6) as pool:
    for soort, naam, delta in pool.map(check, bestanden):
        tally[soort].append((naam, delta))

print(f"{len(bestanden)} bestanden vergeleken met de repository")
print(f"  identiek : {len(tally['gelijk'])}")
print(f"  anders   : {len(tally['anders'])}")
print(f"  niet live: {len(tally['nieuw'])}")
if tally["fout"]:
    print(f"  fout     : {len(tally['fout'])}")
for soort in ("anders", "nieuw", "fout"):
    if tally[soort] and "--kort" not in sys.argv:
        print(f"\n{soort.upper()}:")
        for naam, delta in sorted(tally[soort]):
            print(f"    {naam}  {delta:+d} bytes" if delta else f"    {naam}")
