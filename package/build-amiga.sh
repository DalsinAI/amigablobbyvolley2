#!/bin/sh
# The release archive, for Cradle's stove_build (target package, STOVE= and
# OUT= set): the game built as build-amiga.sh builds it and the data packed
# as runtime-data/build-amiga.sh packs it, then tools/make_package.py:
# blobbyvolley2-VERSION-68040.lha with its .sha256 and .readme, the unpacked
# BlobbyVolley2 drawer and its icon (for a lab) and package.json.
# VERSION is package/VERSION. Nothing is published from here.
# As amigachocolatedoom's package/build-amiga.sh.
# MIT, Copyright (c) 2026 AmiCradle Team.
set -eu

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(CDPATH= cd -- "$HERE/.." && pwd)
OUT=${OUT:-"$ROOT/build-amiga-package"}
VERSION=$(cat "$HERE/VERSION")
mkdir -p "$OUT"
OUT=$(CDPATH= cd -- "$OUT" && pwd)
BUILD=$(mktemp -d "${TMPDIR:-/tmp}/blobby-package.XXXXXX")
trap 'rm -rf "$BUILD"' EXIT INT TERM

OUT=$BUILD sh "$ROOT/build-amiga.sh" > "$OUT/build-output.txt" 2>&1 || { tail -n 80 "$OUT/build-output.txt"; exit 1; }
tail -n 25 "$OUT/build-output.txt"
cp "$BUILD/receipt.json" "$OUT/receipt.json"
cp "$BUILD/build.log" "$OUT/build.log"
OUT=$BUILD sh "$ROOT/runtime-data/build-amiga.sh" > "$OUT/data-output.txt" 2>&1 || { tail -n 40 "$OUT/data-output.txt"; exit 1; }
cp "$BUILD/data-receipt.json" "$OUT/data-receipt.json"
python3 "$ROOT/tools/make_package.py" --build "$BUILD" --version "$VERSION" --out "$OUT"
