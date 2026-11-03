# Blobby Volley 2 for AmigaOS 3.x / AmiCradle

Blobby Volley 2 is a head-to-head volleyball game for two players (or one
against a bot): two blobs, a net and a beach ball, first to 15 points with
the serve. GPL-2.0-or-later (`COPYING`), the code by Jonathan Sieber,
Daniel Knobe, Sven Rech and contributors, the graphics by Silvio Mummert and
the beach image by Richard Bertrand (`AUTHORS`). The graphics, sounds and bots
ship with the source. This repository holds the upstream tree as imported
(upstream [angelonuffer/blobby-volley-2](https://github.com/angelonuffer/blobby-volley-2)
at `0e998a1f0307e80a7efb088f4c2164a2cd60341c`, the SourceForge project's code
mirrored on GitHub: Blobby Volley 2 0.9c, `src/Global.h`) and the AmiCradle
port around it: 68040 + FPU, libnix, SDL 2 through GFOpenGPU, OpenAmigaGCC
16.2.0 (open3, open4 or GFOpenAmigaGCC open5). Upstream's own documents are
`README`, `AUTHORS`, `ChangeLog`, `NEWS` and `TODO`.

## Feasibility

Blobby Volley 2 0.9c draws with SDL 1.2 (a software renderer of surfaces and
blits, `RenderManagerSDL`, besides an OpenGL one and a GP2X one), plays its
three sounds through SDL's audio callback, reads its data through PhysicsFS
(from `.zip` archives or drawers), runs its bots in Lua 5.1 and reads its
settings with TinyXML (both bundled in `src/`), and plays online and on a
network through RakNet (bundled). It uses five small pieces of Boost
(`shared_ptr`, `lexical_cast`, `crc`, `circular_buffer`, `scope_exit`). The
SDK has SDL 2 (2.32.10, GFOpenGPU's `SDL2.module`) and SDL2_mixer, and no
SDL 1.2, PhysicsFS or Boost.

The choice, 3 November 2026:

- **The game's own SDL calls move to SDL 2**, as patches, as amigakobodeluxe
  did for Kobo Deluxe: `patches/0001-sdl2.patch`. The SDL renderer draws only
  with surfaces and blits, so most of it builds as it is. The display is one
  SDL 2 window and its surface (`SDL_SetVideoMode` and `SDL_Flip` become
  `SDL_CreateWindow`, `SDL_GetWindowSurface` and `SDL_UpdateWindowSurface`;
  full screen is SDL's real full screen, a screen of the game's own size,
  800x600); a small header, `src/blobby_sdl2.h` (with `blobby_sdl2.cpp`),
  gives the SDL 1.2 calls SDL 2 dropped with the meaning SDL 1.2 gave them
  (`SDL_SetAlpha`, the `SDL_SRCALPHA`/`SDL_SRCCOLORKEY` flags,
  `SDL_DisplayFormat`, `SDL_DisplayFormatAlpha`, the surface alpha SDL 1.2
  kept in `format->alpha`, `SDL_GetKeyState`, `SDL_WM_SetCaption`). The
  key names in the input settings are SDL 2's key codes (SDL 2 has no
  `SDLK_WORLD_` keys); the mouse wheel is SDL 2's wheel event; joystick
  events name the stick by its number again. Upstream coloured the blobs and
  lit the menu font by reading each 32-bit pixel as R, G, B bytes in memory,
  which holds only on a little-endian machine: those surfaces now have their
  masks set so the bytes are R, G, B on either byte order (the 68040 is
  big-endian). The OpenGL and GP2X renderers are not built, and the Graphics
  options offer SDL only. Upstream's audio callback stays for now (SDL 2
  keeps `SDL_OpenAudio`); its mute switch unlocked SDL's audio lock without
  having locked it, which SDL 2's mutex does not allow, and no longer does.
- `patches/0002-no-boost.patch`: the four Boost pieces the game itself uses,
  as a few lines of standard C++ each (a CRC-32 that gives the same value as
  `boost::crc_32_type`, so replays keep their checksum; a fixed-size ring for
  the bots' delayed ball positions; `std::ostringstream` for a replay's
  name; freeing the file buffer before returning instead of `scope_exit`).
- `patches/0003-no-network.patch`: built with `BLOBBY_NO_NETWORK`, the main
  menu offers no online or network game. RakNet's sockets are not built, so
  the port needs no TCP/IP stack; only RakNet's `BitStream.cpp` is compiled,
  which the physics' (unused) network state calls name.
- `patches/0004-amiga-files.patch`: `src/dirfs/`, the PhysicsFS calls the game
  makes (search path, write directory, open, read, write, length, exists, is a
  directory, make directory, delete, list) on plain drawers through libnix,
  with PhysicsFS 2.0's names and meanings; no `.zip` archives, so the data
  ships as drawers. On AmigaOS (`__amigaos__`) the data is
  `PROGDIR:data` and the settings and replays are written in `PROGDIR:User`,
  made on the first start and searched before the data, as upstream searches
  `~/.blobby` before its installed data.
- `patches/0005-text-manager-return.patch`: upstream's
  `TextManager::createTextManager` returned nothing; GCC 16 takes a missing
  return for a path never taken, and the program would run on into the next
  code at start-up. It returns the text manager.

What could stop it, and the stop rule: every frame is drawn by the CPU into
the window surface at 800x600, and in the menus the whole background is
drawn again each frame. If play cannot hold the game's own speed (75 steps a
second, `gamefps` in the settings; the game drops frames to keep the speed),
that is reported, not hidden. GFOpenMulticore has nothing to take here: one
serial game loop.

## Building

The port never edits the imported tree: `build-amiga.sh` copies `src/` and
`data/`, applies `patches/` with no fuzz, writes the `config.h` upstream's
CMake would write, and compiles upstream's own source lists
(`src/CMakeLists.txt`, `src/lua/CMakeLists.txt`,
`src/tinyxml/CMakeLists.txt`) less what is not built (above) and with the
port's two files, using the stove's compilers and linking the stove's
`libSDL2.a`.

Through Cradle (the build the lab tests use): `stove_build` with the stove
`os32-gcc16`, target `.` for the program and target `runtime-data` for the
game data. From a checkout, with a staged stove:

```sh
STOVE=/path/to/os32-gcc16 OUT=build-amiga sh build-amiga.sh
STOVE=/path/to/os32-gcc16 OUT=build-amiga/data sh runtime-data/build-amiga.sh
```

`build-amiga.sh` takes OpenAmigaGCC 16.2.0-open3 (archive SHA-256
`9fcc136ab59e3bb5b91d2764d0bf290b709d72d7380be4ce0cdf005edf8eff21`),
16.2.0-open4 (`495319a2ffd803278f8827cad70074029c7aa9ecbe05d037e8646ba43ab94ab2`)
or GFOpenAmigaGCC 16.2.0-open5 (Cradle's `os32-gcc16`; no archive is
published, so its receipt records the SHA-256 of the compiler's own programs)
and refuses any other. Its `receipt.json` names the compiler, the patches'
and the recipe's digests, the SDK inputs and the executable's SHA-256; the
receipts of the builds recorded here are in `receipts/`.

The game data (165 files, 2.5 MB: `data/gfx`, `data/sounds`, the six bots in
`data/scripts`, `data/backgrounds`, the settings, the three languages, the
rules and the window icon) ships as `blobby-data.tar`, a plain ustar archive
whose names all start with `data/`, with `untar`, a small Amiga unpacker
(`runtime-data/untar.c`, from amigapowermanga as amigakobodeluxe has it; OS
3.2 has no archiver). `SHA256SUMS` lists every data file. Left out:
`data/gf2x` (older graphics the game does not load), `data/scripts/old`
(older bots upstream does not install) and `data/server.xml` and
`data/onlineserver.xml` (network play is not built).

## Rights

Code and data: GPL-2.0-or-later, upstream's `COPYING` (the source files say
"version 2 or later"; the data has no notice of its own and comes with the
code). Debian ships the same game and data in main under GPL-2+
(`debian/copyright` of the `blobby` package, `Files: *`). Lua 5.1 (MIT) and
TinyXML (zlib) are built in; RakNet (BSD-3-Clause, `src/raknet/LICENSE`) is
not, bar `BitStream.cpp`. The port's own files are GPL-2.0-or-later as the
game; the build scripts are MIT.

## Status

**In progress**, not RELEASE (see the release gates in amicradle
`docs/porting/MEASUREMENT.md`).

| Gate | State |
|---|---|
| Pinned source, reproducible build, receipts | done (open5, Cradle) |
| Launch to the menu, 800x600 on a screen of its own | not yet |
| Keyboard play | not yet |
| Joystick / pad | not yet |
| Sound | not yet |
| Settings and replays across a restart | not yet |
| Drawer with GlowIcons, start from Workbench, LhA package | not yet |
| Network play | not built |

## Observed

### Build, 3 November 2026

Commit `58dec50`: clean compile and link of the imported source with
`patches/0001` to `0005`, no network code (`receipts/`). Two Cradle builds
gave the same executable and the same receipt. The compiler's warnings are
upstream's own (catching exceptions by value, an unhandled enumeration
value, a comparison of two arrays in `RenderManagerSDL::drawBlob`, one in
Lua's `ldump.c`), none in the patches.

| Compiler | Executable SHA-256 | Bytes |
|---|---|---|
| GFOpenAmigaGCC 16.2.0-open5 (Cradle `stove_build`, jobs `j20261103T025001-db880e` and `j20261103T025154-9a8613`) | `29b2137e74560761ab70fae49144d9b2cbe018261abae69277930d7167cac0c8` | 2,114,288 |

Game data (job `j20261103T025109-1f031a`): 165 files, `SHA256SUMS` digest
`517c2b35...9395` (the same from a local open3 run of the same commit's
data), archive `b6dbcf1e...15f8`, `untar` `2de6090b...b6d` (the same bytes
as amigakobodeluxe's). Lab tools (`tests/lab`, job
`j20261103T025132-d77fcb`): HoldKeys `dde62ad3...b0af`, JoyPort
`a7100d5b...7413`, Chop `d4f9b0fc...1199`.

A first start, to see that the build runs (not a gate of this step): in
`lab:blobby`, a copy of Instance-32, `blobby` from a Shell in a drawer with
the data unpacked beside it opened upstream's default 800x600 window on the
Workbench with the main menu, the title bar reading `FPS: 75` (upstream's
`gamefps`), and made `PROGDIR:User`.
