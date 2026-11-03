#!/bin/sh
# Blobby Volley 2's game data for AmigaOS 3.x / AmiCradle, as one archive and
# the small unpacker that puts it beside the program (PROGDIR:data).
# This is what Cradle's stove_build runs for the target runtime-data (STOVE=
# and OUT= set; the stove compiles only untar.c, the unpacker from
# amigapowermanga, as amigakobodeluxe has it). The data is upstream's, as
# imported into this repository: GPL like the engine (COPYING), so it ships
# with the port. Upstream packs gfx, sounds, scripts and backgrounds into
# .zip files for PhysicsFS; the port reads plain drawers (patches/0004), so
# they ship as they are in the repository, with the settings files the game
# reads (gameports/catalog.json lists what is in and what is left out).
#   STOVE  the stove (default ~/AmiCradle/stoves/os32-gcc16)
#   OUT    the output directory (default build-amiga beside this script)
# Outputs: blobby-data.tar (plain ustar, every name under data/), untar
# (Amiga program: "untar blobby-data.tar <drawer>"), SHA256SUMS (one line a
# data file) and data-receipt.json.
# MIT, Copyright (c) 2026 AmiCradle Team.
set -eu

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(dirname "$HERE")
if [ -z "${STOVE:-}" ]; then
    STOVE="$HOME/AmiCradle/stoves/os32-gcc16"
    [ -d "$STOVE" ] || STOVE="$HOME/AmigaChrome/stoves/os32-gcc16"
fi
OUT=${OUT:-"$HERE/build-amiga"}
CC="$STOVE/prefix/bin/m68k-amigaos-gcc"
EPOCH=$(git -C "$ROOT" show -s --format=%ct HEAD 2>/dev/null || echo 0)
mkdir -p "$OUT"

# what gameports/catalog.json's runtimeData names, from the repository root
LIST="$OUT/.list"
python3 - "$ROOT" > "$LIST" <<'PY'
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
data = json.loads((root / "gameports/catalog.json").read_text())["ports"]["blobbyvolley2"]["runtimeData"]
names = []
for d in data["dirs"]:
    names += [str(p.relative_to(root)) for p in (root / d).rglob("*") if p.is_file()]
names += data["files"]
# upstream installs only the bots at the top of scripts/ (data/CMakeLists.txt)
names = [n for n in names if not n.startswith("data/scripts/") or n.count("/") == 2]
for n in sorted(set(names)):
    if not (root / n).is_file():
        sys.exit(f"missing: {n}")
    print(n)
PY
# the patches touch data too (patches/0006: the settings' defaults), so the
# data is packed from a patched copy, as build-amiga.sh builds the code
WORK=$(mktemp -d "${TMPDIR:-/tmp}/blobby-data.XXXXXX")
trap 'rm -rf "$WORK"' EXIT INT TERM
cp -R "$ROOT/src" "$ROOT/data" "$WORK/"
for patch in "$ROOT"/patches/*.patch; do
    [ -f "$patch" ] || continue
    patch --batch --forward --fuzz=0 -p1 -d "$WORK" < "$patch" > /dev/null
done
(cd "$WORK" && while read -r f; do sha256sum "$f"; done < "$LIST") > "$OUT/SHA256SUMS"
# the same bytes from the same files: names sorted, owners and times fixed
(cd "$WORK" && tar --format=ustar --no-recursion --owner=0 --group=0 --numeric-owner \
    --mode='u=rw,go=r' --mtime="@$EPOCH" -cf "$OUT/blobby-data.tar" -T "$LIST")
rm -f "$LIST"

"$CC" --version | head -n 1
"$CC" -noixemul -m68040 -O2 -Wall -Wno-stringop-truncation \
    -ffile-prefix-map="$HERE"=. -o "$OUT/untar" "$HERE/untar.c"
[ "$(od -An -tx1 -N4 "$OUT/untar" | tr -d ' \n')" = "000003f3" ] || { echo "untar is not an Amiga HUNK executable"; exit 2; }

python3 - "$ROOT" "$OUT" <<'PY'
import hashlib, json, subprocess, sys
from pathlib import Path
root, out = Path(sys.argv[1]), Path(sys.argv[2])
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
sums = (out / "SHA256SUMS").read_bytes()
pin = json.loads((root / "gameports/catalog.json").read_text())["ports"]["blobbyvolley2"]["source"]["commit"]
try:
    rev = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
except Exception:
    rev = "unknown"
receipt = {
    "upstream_commit": pin, "repository_commit": rev,
    "files": len(sums.splitlines()),
    "sha256sums_sha256": hashlib.sha256(sums).hexdigest(),
    "archive_sha256": sha(out / "blobby-data.tar"),
    "archive_bytes": (out / "blobby-data.tar").stat().st_size,
    "untar_sha256": sha(out / "untar"),
    "licence": "GPL-2.0-or-later (upstream COPYING); the Blobby Volley 2 team (AUTHORS)",
}
(out / "data-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt, indent=2))
PY
