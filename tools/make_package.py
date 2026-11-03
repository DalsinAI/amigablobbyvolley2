#!/usr/bin/env python3
"""The release archive: the BlobbyVolley2 drawer, as an LhA archive.

    python3 tools/make_package.py --build BUILD --version 0.9c-amigaos3-test1 --out OUT

BUILD holds what build-amiga.sh and runtime-data/build-amiga.sh made
(BlobbyVolley2/blobby, BlobbyVolley2/COPYING, receipt.json, blobby-data.tar
and data-receipt.json). The drawer gets the game, its data drawer (every
file of blobby-data.tar, as untar would put it beside the program), the
icons from icons/, ReadMe (package/ReadMe.in with the version and the
checksums filled in) and the GPL text (COPYING). Nothing else: the game
makes PROGDIR:User itself.

OUT gets:
  blobbyvolley2-VERSION-68040.lha     the archive (level-1 headers, -lh5-, as
                                      Amiga LhA writes it: tools/lha_archive.py)
  blobbyvolley2-VERSION-68040.lha.sha256
  blobbyvolley2-VERSION-68040.readme  the Aminet-style description
  BlobbyVolley2/, BlobbyVolley2.info  the drawer as it unpacks, for a lab
  package.json                        every member's size and SHA-256

The archive's dates are the source commit's (source_date_epoch in
receipt.json), in UTC, so the same inputs make the same bytes.
As amigachocolatedoom's tools/make_package.py.
MIT, Copyright (c) 2026 AmiCradle Team.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import sys
import tarfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import lha_archive  # noqa: E402

DRAWER = "BlobbyVolley2"
# (name in the drawer, where it comes from: "build", "repo" or "readme", path)
FILES = [
    ("blobby", "build", f"{DRAWER}/blobby"),
    ("blobby.info", "repo", "icons/blobby.info"),
    ("ReadMe", "readme", ""),
    ("ReadMe.info", "repo", "icons/ReadMe.info"),
    ("COPYING", "build", f"{DRAWER}/COPYING"),
    ("COPYING.info", "repo", "icons/COPYING.info"),
]
MAX_LINE = 78


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compiler_name(release: str) -> str:
    """The compiler as its release calls itself: open5 and later are GFOpenAmigaGCC."""
    m = re.fullmatch(r"\d+\.\d+\.\d+-open(\d+)", release)
    return ("GFOpenAmigaGCC " if m and int(m.group(1)) >= 5 else "OpenAmigaGCC ") + release


def readme(version: str, receipt: dict, data: dict) -> bytes:
    text = (ROOT / "package" / "ReadMe.in").read_text(encoding="utf-8")
    fills = {
        "@VERSION@": version,
        "@UPSTREAM@": receipt["upstream_commit"],
        "@SOURCE@": receipt["repository_commit"],
        "@COMPILER@": compiler_name(receipt["compiler_release"]),
        "@EXE_SHA256@": receipt["executable_sha256"],
        "@DATA_FILES@": str(data["files"]),
    }
    for k, v in fills.items():
        text = text.replace(k, v)
    lines = text.split("\n")                       # the title's rule as long as the title
    lines[1] = "=" * len(lines[0])
    text = "\n".join(lines)
    left = re.findall(r"@[A-Z0-9_]+@", text)
    if left:
        raise SystemExit(f"package/ReadMe.in has fields left unfilled: {left}")
    long = [i + 1 for i, line in enumerate(text.splitlines()) if len(line) > MAX_LINE]
    if long:
        raise SystemExit(f"ReadMe lines over {MAX_LINE} characters: {long}")
    return text.encode("latin-1")                  # MultiView and the Shell read Latin-1


def aminet_readme(version: str, text: bytes) -> bytes:
    fields = [
        ("Short", "Blobby Volley 2, volleyball for two, 68040+FPU"),
        ("Author", "Blobby Volley 2: Jonathan Sieber, Daniel Knobe, Sven Rech and contributors; port: AmiCradle Team"),
        ("Uploader", "AmiCradle Team"),
        ("Type", "game/misc"),
        ("Version", version),
        ("Requires", "AmigaOS 3.2, 68040/68060 with FPU, RTG, GFOpenGPU SDL2 and SDL2_mixer, AHI"),
        ("Architecture", "m68k-amigaos >= 3.2"),
    ]
    width = max(len(k) for k, _ in fields) + 2
    head = "\n".join(f"{(k + ':').ljust(width)}{v}" for k, v in fields if v)
    return (head + "\n\n").encode("latin-1") + text


def data_members(tar_path: Path) -> list[tuple[str, bytes]]:
    """Every file of blobby-data.tar (names under data/), in archive order."""
    out = []
    with tarfile.open(tar_path) as tar:
        for info in tar.getmembers():
            if not info.isfile():
                continue
            if not info.name.startswith("data/") or ".." in info.name.split("/"):
                raise SystemExit(f"blobby-data.tar holds {info.name}")
            out.append((info.name, tar.extractfile(info).read()))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--build", required=True, type=Path)
    ap.add_argument("--version", required=True)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    receipt = json.loads((args.build / "receipt.json").read_text())
    data = json.loads((args.build / "data-receipt.json").read_text())
    tar = args.build / "blobby-data.tar"
    if sha256(tar.read_bytes()) != data["archive_sha256"]:
        raise SystemExit("blobby-data.tar is not the one data-receipt.json names")
    stamp = float(receipt["source_date_epoch"])
    os.environ["TZ"] = "UTC"                         # LhA stamps are local time: make local UTC
    time.tzset()

    base = f"blobbyvolley2-{args.version}-68040"
    members, listing = [], []

    def add(path: str, blob: bytes) -> None:
        members.append(lha_archive.Member(path, blob, 0, "", stamp))
        listing.append({"path": path, "bytes": len(blob), "sha256": sha256(blob)})

    for name, where, path in FILES:
        if where == "build":
            blob = (args.build / path).read_bytes()
        elif where == "repo":
            blob = (ROOT / path).read_bytes()
        else:
            blob = readme(args.version, receipt, data)
        if name == "blobby" and sha256(blob) != receipt["executable_sha256"]:
            raise SystemExit("the executable is not the one receipt.json names")
        add(f"{DRAWER}/{name}", blob)
    files = data_members(tar)
    if len(files) != data["files"]:
        raise SystemExit(f"blobby-data.tar has {len(files)} files, data-receipt.json says {data['files']}")
    for name, blob in files:
        add(f"{DRAWER}/{name}", blob)
    add(f"{DRAWER}.info", (ROOT / "icons" / f"{DRAWER}.info").read_bytes())

    args.out.mkdir(parents=True, exist_ok=True)
    lha = lha_archive.write(args.out / f"{base}.lha", members)
    back = lha_archive.read(lha.read_bytes())     # it reads back, member for member
    if [(m.path, m.data) for m in back] != [(m.path, m.data) for m in members]:
        raise SystemExit("the archive does not read back as written")
    digest = sha256(lha.read_bytes())
    (args.out / f"{base}.lha.sha256").write_text(f"{digest}  {lha.name}\n")
    (args.out / f"{base}.readme").write_bytes(aminet_readme(args.version, members[2].data))

    drawer = args.out / DRAWER                     # the drawer as it unpacks, for a lab
    if drawer.exists():
        shutil.rmtree(drawer)
    for m in members:
        target = args.out / m.path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(m.data)

    summary = {"archive": lha.name, "bytes": lha.stat().st_size, "sha256": digest, "version": args.version,
               "repository_commit": receipt["repository_commit"], "executable_sha256": receipt["executable_sha256"],
               "data_archive_sha256": data["archive_sha256"], "members": listing}
    (args.out / "package.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "members"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
