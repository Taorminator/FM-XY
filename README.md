# FM-XY

**By Middle Age Engineering** · Browser prototype v0.1.15 · **not FM1 firmware**

An unofficial, open-source browser prototype of a small, OP-XY-inspired groovebox concept for the M-VAVE FM1. Built for quick chord ideas, 16-step patterns, short loops and filter automation.

## Try it now

- **Browser demo:** `docs/try/index.html` — playable in a modern browser (sound requires an interaction to activate).
- **Project website:** `docs/index.html` — publish with GitHub Pages from `main` / `/docs`.
- **Installation status:** `docs/installer/index.html` — intentionally disabled until a real, independently tested FM1 firmware release exists.

Three user-facing styles: **OP-XY Mono** (default), **OP-1 Color**, **OP-XY Color**. The field-inspired colors are approximations, not official palette data. On the virtual device, hold HOME for ~0.6 s to access Display settings; also available in the top bar.

## Current scope

- Browser-only Canvas rendering at 240 × 240 pixels.
- Independent JavaScript / Web Audio simulation; **no original Felucca C firmware is yet compiled or embedded**.
- Chords, harmony hints, four tracks, 16-step sequencer, loops, motion recording, simple synthetic drum/FM sounds, local project export/import.
- Sampling via iPhone (ELI7VH/Choppa) is a *future V2 study*, not implemented.

See also the detailed German guide: [PUBLISHING_DE.md](PUBLISHING_DE.md).

## Publish on GitHub Pages (quick path)

1. Create a new public GitHub repository called `FM-XY` (or use your selected repository name).
2. Upload/commit the files **inside** this folder; do not publish the ZIP as a single repository file.
3. In GitHub open **Settings → Pages → Build and deployment → Deploy from a branch → `main` → `/docs` → Save**.
4. The page will be at `https://YOUR-USERNAME.github.io/FM-XY/` (replace username and repository name).
5. Open `/try/` to play and `/installer/` to inspect the future installation path.

```bash
# Run from the folder containing this README:
git init
git add .
git commit -m "FM-XY browser preview and site"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/FM-XY.git
git push -u origin main
```

**Separate recommended firmware track:** Make an actual GitHub fork of [`hugelton/Felucca`](https://github.com/hugelton/Felucca) to preserve full commit history, its GPL-3.0 license, build system, loader and tests. Maintain the browser-preview repository while integrating FM-XY separately into this real fork. If you later merge the Pages site into the firmware fork, carry its static files into a dedicated Pages deployment branch or integrate them carefully under `/docs`, avoiding filename conflicts. **Do not overwrite Felucca's README, LICENSE, LICENSING.md, LICENSES/, or existing firmware build files.** Merge later modifications in the real fork, preserving authorship and license text. When a real firmware build exists, replace our *disabled* installer placeholder with a verified, properly attributed Felucca-derived installer. Do not publish a firmware binary without testing it.

## How to build the eventual FM1 firmware

See [FM1_PORTING.md](FM1_PORTING.md). In brief, firmware is **not a build of this HTML**: adapt existing Felucca C rendering, audio, HAL and event handling; build with the JieLi pi32v2 toolchain and required AC79 SDK files; run host tests and real-hardware safety tests; only then create/verify the `.fwsc` via upstream release scripts.

This ZIP deliberately contains **no `.fwsc`**, updater payload, installer executable or vendor firmware.

## Quality and compatibility

- JavaScript syntax and static-site regressions can be checked with `python3 -m unittest discover -s tests` and `node --check` on the browser script.
- A passing browser simulation does **not** establish safe audio, RAM, flash or latency behavior on the FM1.
- Prefer conservative CPU/RAM budgets and predictable latency over extra features.
- Preserve an existing hardware backup before any eventual experiment.

## Credits / licensing

See [CREDITS.md](CREDITS.md), [LICENSING.md](LICENSING.md) and [DISCLAIMER.md](DISCLAIMER.md). Source references are credited even where no files were copied. Planned firmware derivation from Felucca is under **GPL-3.0-only** and requires the full corresponding source and third-party attribution notices.

**FM-XY is unofficial and is not affiliated with or endorsed by M-VAVE, Teenage Engineering or Hügelton Instruments.** No warranty; future third-party flashing is at users' own risk.