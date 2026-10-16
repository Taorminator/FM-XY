# OP-XY workflow research → FM-XY decisions (2026-10-13)

## Source correction

[awesome-music-gear-firmware](https://github.com/Lapin/awesome-music-gear-firmware#op-xy) is a **curated link list**, not OP-XY custom firmware. Its three OP-XY entries are:

1. [kmorrill/xy-format](https://github.com/kmorrill/xy-format): reverse-engineered project **file structure** and writer; **not** operational firmware source.
2. [kmorrill/op-xy-vibing](https://github.com/kmorrill/op-xy-vibing): JSON loop spec + external Python/USB-MIDI conductor; **not** OP-XY replacement firmware.
3. [sixthlaw/opxy-multisampler-preset-builder](https://github.com/sixthlaw/opxy-multisampler-preset-builder): browser multisampler preset creator; **not** device firmware.

The nearby **FM-1** section links to working FM1 firmware implementations [FoMni](https://github.com/charlesvestal/fm1-fomni), [ORBIT](https://github.com/dspaudio/orbit) and [Felucca](https://github.com/hugelton/Felucca); these are better sources for concrete FM1-specific implementation patterns. Do not copy OP-XY binary structures, graphics, or protected sound assets.

## What the sources actually establish

- `xy-format` maps OP-XY project data as an RLE-compressed decoded image with per-track notes (tick, gate, pitch, velocity), step components, parameter locks, independent patterns, scenes, mutes, and song chains. This is **evidence about stored musical state**, not access to the proprietary sequencer implementation. Sources: [README](https://github.com/kmorrill/xy-format), [authoring](https://github.com/kmorrill/xy-format/blob/main/docs/engineering/authoring.md), [scenes](https://github.com/kmorrill/xy-format/blob/main/docs/format/scenes_songs.md), [brain read-only inspection](https://github.com/kmorrill/xy-format/blob/main/xy/brain_inspection.py).
- Brain inspection establishes route-mask + a small set of raw parameter fields (mode, key, scale, link), **not** the OP-XY's proprietary key-detection/voice-leading algorithm. No exact Brain replication can be inferred from these bytes.
- Its current image writer accepts 14 named step-component bits and can rotate **notes, parameter locks, and components together**. A legacy `xy/step_components.py` raw-body encoder is **superseded**; do not copy its old byte encodings or inferred restrictions. Source: [image_writer.py](https://github.com/kmorrill/xy-format/blob/main/xy/image_writer.py).
- `op-xy-vibing` separates musical intent from note realization. The [JSON spec](https://github.com/kmorrill/op-xy-vibing/blob/main/docs/opxyloop-1.0.md) contains degree / Roman-numeral or absolute chord, inversion/register/voicing hints, gate, probability, microtiming, ratchet, per-tone velocities and rollMs. However its [actual current MIDI engine](https://github.com/kmorrill/op-xy-vibing/blob/main/conductor/midi_engine.py) explicitly **ignores inversion/omit/roll in its MVP chord expansion**; a spec field is not proof of a working feature.
- Official OP-XY workflows: [Brain](https://teenage.engineering/guides/op-xy/auxiliary) can route selected tracks through live harmonic transposition, [sequencer](https://teenage.engineering/guides/op-xy/sequencer) supports hold-step/edit-note and hold-step/turn-knob locks, [step components](https://teenage.engineering/guides/op-xy/step-components) add variation without manually rewriting patterns, [punch-in FX](https://teenage.engineering/guides/op-xy/get-started) are momentary performance gestures. These workflow primitives, not pixel-perfect graphics or feature counts, are the reference.
- `FoMni`: an FM1-specific proof of chord buttons, keyboard-as-strum-surface, four-knob pages and direct root/type assignment when a chord key is held. `ORBIT`: native FM1 event-tape UI and screenshot/host verification for 240×240; its published validation shows tight image/RAM budgets **for ORBIT's own build**, which are **not** measurements of FM-XY.

## Current FM-XY delta

- Browser preview already offers four CHORD controls **ROOT / TYPE / VOICE / STYLE**, BLOCK/STRUM/SPREAD/ARP sound simulation, two harmonic suggestions, four patterns and four tracks. Browser suggestion tables are **fixed templates**, not autonomous/voice-led progressions; browser state and audio are **not** the native firmware.
- Native Felucca overlay currently exposes **ROOT / TYPE / VOICE / ARP** (fourth knob maps to existing `P_AMODE`; it is *not* STYLE). Native fixed-chord chromatic key layout and read-only root suggestion LEDs are functional in CI. STRUM/SPREAD queue, pitch gate and four-track router have passed host/regression tests but remain **disconnected from the real keyboard ISR**.
- Native firmware remains pinned to Felucca `ef1f561...` (1.5.1). Upstream Felucca 1.6 added conditional steps, Euclid, double/half and related functionality. **Evaluate migration as an isolated compatibility project, not a silent wholesale rebase**.
- The latest audited, green state when researched: check the PR HEAD and all three GitHub Actions checks afresh; no binary/installer is approved for FM1 installation.

## Recommended user-facing contract (design proposal, not implemented)

**ONE chord page, no configuration maze:**

| Direct controls | Gesture | Meaning |
| --- | --- | --- |
| KNOB 1 ROOT | turn | explicit pitch or **AUTO** (per chord slot, not global forced random) |
| KNOB 2 TYPE | turn | explicit maj/min/m7/maj7/etc or **AUTO** (independent of ROOT) |
| KNOB 3 VOICE | turn | nearest/close/open/inversion; prefer minimum movement from previous chord |
| KNOB 4 STYLE | turn | BLOCK / STRUM / SPREAD / ARP, after resolving how to preserve Felucca's `P_AMODE` |
| first playable chord key | tap/hold | sound a full chord immediately |
| two adjacent suggestion keys | tap/hold | audition two next chords, **without editing the currently configured root/type** |
| recording | play a suggestion then REC/step | commit a variation; repeated playback is deterministic |

Two complementary modes, not a giant menu:

1. **PLAY**: audition any suggestion, hear it immediately, never silently overwrite the edited chord.
2. **MUTATE**: alter only unlocked fields (ROOT AUTO and/or TYPE AUTO), constrain by key/scale, prefer shared chord tones, small melodic motion and sensible bass register. Locking either field stays independent. Use a fixed seed so restarting a loop yields repeatable notes until explicitly rerolled.

Possible second layer (later): **BRAIN-LITE** chooses a key/scale (manual first, optional detection after adequate tests), links melodic tracks through a compact four-bit mask (never force drums), and maps pre-existing melodic material to the active chord degrees. This requires explicit MIDI and voice-sharing tests before live use.

## Development order (measurable gates)

| Priority | Work item | Done when |
| --- | --- | --- |
| P0 safety | Finish both-order MIDI ownership and native STYLE routing without stuck notes | hardware-key press/release, changing track, ARP toggle, MIDI pedal, MIDI out and live REC regressions pass; no new audio deadline failures |
| P1 feel | Root/Quality independent **AUTO or LOCKED**, with deterministic constrained suggestions | tests prove independent locks; suggestions are playable but do not mutate manual settings |
| P1 feel | **VOICE LEADING** on whole chord changes | adjacent chords minimize voice jumps under the global eight-voice limit; preserving harmonic quality, predictable inversion, no surprise octave clipping |
| P1 gesture | **STEP + CHORD**: hold step and play chord, or hold chord then tap step | one gesture commits all chord tones, and undo restores previous state |
| P1 variation | Single **MUTATE** action for a chord/phrase with preview and commit | repeatable on loop, can keep bass/key fixed, no accidental permanent overwrite |
| P2 sequencer | **RATCH / CHANCE / CONDITIONAL / SHIFT** as a few accessible step gestures | reuse Felucca primitives where possible; notes, modifiers and locks remain coherent on rotate/copy |
| P2 performance | Three or four **momentary** punch gestures, not 24 FX pages | only active while held; clean release on stop, track/preset change and panic; host cost proof |
| P2 UI | 240×240 grayscale bars / black cuts / tiny but readable text / red REC only | real C renderer snapshots across palettes, UI clipping/contrast checks, real-panel legibility |
| P3 future | scene/chord progression A/B and export to the browser companion | format migration/versioning tested, round-trip backup/restore and recovery validated |

## Explicit non-goals

- No copy of proprietary OP-XY firmware, closed-source Brain algorithm, graphics assets or commercial sample banks.
- No 14-component clone, 24 punch-in FX, 16-track architecture or true PCM tape deck for the first FM1 alpha.
- No transplant of OP-XY `.xy` binary layout onto Felucca's persisted project format.
- No new audio ISR work without static instruction/RAM budget checks, real MIDI/arpeggio/recording tests, hardware test and recovery plan.
- Do not present browser-only UI behavior as available on the native FM1 build.

## Core principle

**The OP-XY experience is in direct, reversible musical gestures:** one action produces an audible idea; the next action varies it; a third records it. Prefer a few excellent, reliable behaviors over a copied menu or a large inventory of experimental engines.
