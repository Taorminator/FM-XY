# CHORDON BLEU v0.4: Four FM1 knobs (design spec)

**Browser first, no installable hardware firmware yet.**

| FM1 control | Parameter | Options | Initial |
|---|---|---|---|
| KNOB 1 | RATE | 1/4, 1/8, 1/16, 1/32 | 1/16 |
| KNOB 2 | GATE | 15–100% (5% increments) | 62% |
| KNOB 3 | DIRECTION | UP / DOWN / UP-DOWN / RANDOM | UP |
| KNOB 4 | ORDER | PITCH / ROOT 1ST / OUT-IN / FIFTH 1ST | PITCH |

These are real browser playback parameters: RATE changes note count, GATE changes note-off timing, DIRECTION traverses the notes and ORDER constructs the base pattern. The hardware-specific four-encoder binding is **not yet coded**.

FLIP defaults to KEEP 1: the selected chord stays unchanged (even with ROOT/TYPE=AUTO) while other slots are re-harmonized using their manual constraints. ALL 4 explicitly replaces all chords and clears manual constraints, with UNDO available. FEEL (WARM/CRISPY/CHEESY) changes harmony candidate scores and voice-leading weights; SPICE independently changes novelty.

Roadmap: Integrate on an actual fork of [Felucca](https://github.com/hugelton/Felucca) preserving its GPL-3.0-only code notices and hardware interfaces. Use existing `panel.c` for real matrix/encoder mapping, `seq.c` for scheduling, `chord.c` for voicings, and `project.c` for reliable storage. Verify with real-toolchain builds, WASM emulation and actual FM1 hardware before any `.fwsc` release. The standalone C core from ELSEWHERE v0.2 **does not yet support FEEL or ARP** and requires parity work.
