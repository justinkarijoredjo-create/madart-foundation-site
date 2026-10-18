#!/usr/bin/env python3
"""Fill assets/ from the repository.

The images are 78 MB, too much to move through a chat, so they are not in the
handover zip. They are all in the GitHub repository already, which is the one
place they are guaranteed to be current. This pulls down whatever assets/ is
missing and leaves anything already there alone.

    python3 fetch-assets.py

Needs nothing but Python 3. Safe to run twice.
"""
import os, re, subprocess, sys, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RAW = ("https://raw.githubusercontent.com/justinkarijoredjo-create/"
       "madart-foundation-site/main/")
HERE = Path(__file__).parent
ASSETS = HERE / "assets"
IMG = (".jpg", ".jpeg", ".png", ".webp", ".svg")


def wanted():
    """Every image the site actually asks for.

    Two earlier approaches failed: reading the data files missed the t-, h- and
    p- variants that build.py derives from a base name, and the GitHub API is
    rate-limited from most machines. So: build the site once — that works
    without any images, the pages simply point at files that are not there yet —
    and read the filenames straight out of the HTML it produced. Whatever the
    site references is by definition what the site needs."""
    print("  even bouwen om te zien welke beelden nodig zijn …")
    r = subprocess.run([sys.executable, "build.py"], cwd=HERE,
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit("build.py mislukte:\n" + (r.stderr or r.stdout)[-1500:])

    names = set()
    for f in (HERE / "build").glob("*.html"):
        text = f.read_text(encoding="utf-8")
        for m in re.finditer(r'(?:src|href|content)="([^"]+)"', text):
            u = m.group(1).split("?")[0].rsplit("/", 1)[-1]
            if u.lower().endswith(IMG):
                names.add(u)

    # The probe build above runs with an empty assets folder, and build.py only
    # names the light w- rendition of a work photograph when that file already
    # exists. So the probe never mentions them, and without this the work pages
    # silently fall back to the full-size originals: 430 KB instead of 165 KB on
    # a phone in the gallery. Ask for the w- form of every base image too; the
    # ones that do not exist simply 404 and are skipped.
    prefixes = ("w-", "t-", "h-", "p-", "c-")
    names |= {"w-" + n for n in list(names) if not n.startswith(prefixes)}
    return names


def grab(name):
    dest = ASSETS / name
    if dest.exists():
        return ("have", name)
    try:
        with urllib.request.urlopen(RAW + name, timeout=30) as r:
            dest.write_bytes(r.read())
        return ("got", name)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return ("missing", name)
        return ("error", f"{name}: {e}")
    except Exception as e:
        return ("error", f"{name}: {e}")


def main():
    ASSETS.mkdir(exist_ok=True)
    names = sorted(wanted())
    print(f"  {len(names)} beelden nodig")
    tally = {"have": 0, "got": 0, "missing": [], "error": []}
    with ThreadPoolExecutor(max_workers=8) as pool:
        for kind, what in pool.map(grab, names):
            if kind in ("have", "got"):
                tally[kind] += 1
            else:
                tally[kind].append(what)

    print(f"  al aanwezig : {tally['have']}")
    print(f"  opgehaald   : {tally['got']}")
    if tally["missing"]:
        print(f"  niet in de repository ({len(tally['missing'])}):")
        for n in tally["missing"][:10]:
            print("     ", n)
        print("  Dit zijn meestal namen die uit een sjabloonvariabele komen; "
              "controleer of ze echt nodig zijn.")
    if tally["error"]:
        print(f"  fouten ({len(tally['error'])}):")
        for n in tally["error"][:10]:
            print("     ", n)
        sys.exit(1)
    print("\nKlaar. Draai nu:  python3 build.py --check")


if __name__ == "__main__":
    main()
