# CHORDON BLEU — FM1 porting plan

## What exists

- The **FM-XY** repository already documents a 240 × 240 Canvas design, 4-track browser simulator, separate pure-C suggestion header and host test, GPL credits, and an installer placeholder intentionally disabled.
- The separate **ELSEWHERE** prototype added a deeper 4-chord harmony scorer with per-chord ROOT/TYPE locking, contextual transitions, loop closure, mobile Web Audio, save/export, portable C99 prototype and tests.
- The **CHORDON BLEU** Git branch begins from FM-XY while keeping its existing main untouched, and ships a new standalone interactive browser app.
- Browser/Web Audio and C-code behavior are **not yet parity-tested**; do not describe this as a native device emulator.

## Verified upstream reference

[Felucca](https://github.com/hugelton/Felucca), Leo Kuroshita / Hügelton Instruments, GPL-3.0-only. `main` was commit `9f6a8858afd71b4faed9dfea3a5f94d3ecfdf002` on 2026-10-13, version 1.5.6 (pin exact SHA for integration; upstream changes over time).

Useful existing files: `firmware/src/chord.c` (chord voice selection and voicings), `seq.c` (sequencing), `panel.c` (physical button/encoder roles and calibration), `ui_input.c` (gesture mapping), `audio.c`, `voice.c`, `project.c` (storage), `web/emu/` (real firmware-to-WebAssembly emulation).

Its documented tooling needs JieLi pi32v2/Linux x86-64 toolchain and parts of the JieLi AC79 SDK; review upstream `BUILDING.md`.

## What to build first

1. Agree FM1 physical button map: PLAY, FLIP, SAVE, SPICE, selectable chord slot, ROOT, TYPE, momentary performance and REC.
2. Port harmonic engine into a small deterministic C module, using little RAM and no allocations in time-critical audio.
3. Define one canonical set of music rules and shared vectors for browser/C implementations.
4. Use Felucca voices/scheduler to sound only one 4-chord loop; avoid adding tracks/drums/sampling.
5. Render a readable 240 × 240 color-temperature UI (text must be understandable even without color).
6. Implement versioned, reliable save, load, undo and safe firmware upgrade behavior.
7. Build and test the unmodified Felucca baseline; then integrate and test host suites, WASM, and finally real FM1 hardware.
8. Release a verified `.fwsc` only after real hardware and backup/recovery checks.

## Non-goals

DAW, MPC, multiple tracks, 808/909 drums, audio sampling, 200 sound presets, menus within menus, feature-completeness against FM-XY.

## Test status

Browser-prototype local Chromium checks: 320, 390, 430, 768 and 1440px; playback/nonzero PCM; record, 25 FLIP variations per viewport; lock behavior, undo and saved loop. Portable ELSEWHERE C engine previously passed 52,800 seeded mutation property checks. Real Safari hardware, C/browser parity, cross-compiled Felucca integration, native WASM, physical FM1 CPU/voice budgets and firmware flashing remain **untested**.

**No flashable firmware is provided here.**
