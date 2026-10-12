# FM-XY Native Firmware Port

FM-XY is entering the **native Felucca C port** stage. This repository's HTML groovebox remains a separate simulation, **not a flashable firmware**.

## Baseline
- Upstream: [Felucca](https://github.com/hugelton/Felucca) by Leo Kuroshita / Hügelton Instruments (GPL-3.0-only).
- Pinned reference commit: `ef1f561b6b105f20350f6b1eac0dc0789a357f00` (2026-10-11).
- Source layout: `firmware/src/felucca.c` includes other firmware source files in order. Existing `ui_graph.c` already draws a CHORD graph and `ui_draw.c` has a boot splash. `tools/gen_ui_palettes.py` generates device-safe palettes.

## Conservative development plan
1. Fork Felucca while preserving upstream ancestry, license files and credits.
2. Reproduce Felucca's host and browser-emulator tests before any changes.
3. Introduce the FM-XY splash and 3 palettes with tested, bounded LCD rendering.
4. Extend the existing `SCL > CHORD` screen with suggestions while keeping ROOT and TYPE separate and editable.
5. Bring over the sequencer and automation UI using Felucca's scheduler and engine, not the JavaScript audio simulator.
6. Test render overflow, contrast, CPU budget, latency, memory, flash storage, backup and recovery.
7. Only release a verified `.fwsc` for installation.

## Work in progress
- `firmware/fmxy_harmony.h` is a small pure-C **prototype** of deterministic harmonic suggestions.
- This new code is not wired into the Felucca display or music engine yet.
- No real device build or flash image is provided.

See [upstream build guide](https://github.com/hugelton/Felucca/blob/main/BUILDING.md). Firmware installation stays disabled.