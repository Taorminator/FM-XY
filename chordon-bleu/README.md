# CHORDON BLEU

**A pocket-sized harmony kitchen.**  
**By Middle Age Engineering** (short: **MID Engineering**).

Cook up something beautiful.

A tiny musical instrument for harmonic happy accidents. Built for people who want to make music immediately, without music theory, menus, production workflow, or a full groovebox.

## Play now

- [Playable single-file browser version](browser/index.html). This contains actual Web Audio synthesis and four-chord loops, including Safari user-gesture audio activation.
- On iPhone, serve `browser/index.html` over HTTPS (e.g., Netlify Drop from the separate one-file ZIP) and then tap **PLAY**.
- A browser file preview is not a reliable iPhone audio test.
- No flashable FM1 firmware exists yet. **Do not install this HTML onto the FM1.**

## Identity

| Use | Name |
| --- | --- |
| Product | **CHORDON BLEU** |
| Logo art direction | **CHORD—ON—BLEU** |
| Future repository | `chordon-bleu` |
| Manufacturer homage | **Middle Age Engineering** |
| Short credit | **MID Engineering** |
| Tagline | **Cook up something beautiful.** |

Main interactions: **PLAY**, **FLIP**, **SAVE**. **SPICE** controls how surprising harmony mutations may be. ROOT and TYPE remain individually editable or AUTO per chord. Four chord slots, loop-based play, harmonic closure, 1-step reversal, and save.

## Temperature UI

Deep midnight / electric neon-blue, moving through violet, magenta, coral to orange. Colors are a **subjective visual metaphor for harmonic tension/richness**, not a scientific measure of musical warmth. Labels must remain independently legible.

## Source and integration status

This is a standalone Web Audio browser prototype evolved from the ELSEWHERE idea, now with new branding and live color feedback.

**Not yet Felucca firmware.** Original [Felucca](https://github.com/hugelton/Felucca) source is GPL-3.0-only; for a physical FM1 we plan to preserve the upstream hardware, audio, storage, calibration, bootloader and build/test infrastructure while replacing the workflow/UI. See [FM1 assessment](FM1_PLAN.md).

We analyzed [Taorminator/FM-XY](https://github.com/Taorminator/FM-XY) as a separate inspiration and technical reference, **not** as the product to rename. It has a browser groovebox simulation and a small C harmony-suggestion header, but not a Felucca-derived installable firmware yet.

### Important licensing

Future Felucca-derivative code must comply with GPL-3.0-only and retain copyright/third-party notices. No Felucca source has yet been copied into this subdirectory. Independent homage; **not affiliated with Teenage Engineering, M-VAVE or Hügelton Instruments**.

## Next

1. Stand up an **independent** GitHub repository named `chordon-bleu`, then migrate this project branch content there.
2. Add portable C99 harmonic search core from the ELSEWHERE development kit with attribution and compatibility tests.
3. Align JavaScript and C harmonic output/constraints, measured in repeatable golden-vector tests.
4. Fork the upstream Felucca firmware separately, reproduce baseline firmware/host/WASM tests, and integrate hardware-specific UI/audio.
5. Test on a real FM1 with safe backup/recovery before ever enabling an installer.

This folder has been staged on the `chordon-bleu` **branch of FM-XY** to protect FM-XY's main branch until the standalone repository is created.

## v0.4 — FLIP, FEEL, ARP

- **FLIP + KEEP 1** preserves the entire selected chord, even when ROOT and TYPE are AUTO. Manually set ROOT / TYPE on other slots remain respected.
- **FLIP + ALL 4** regenerates all four chords, clearing manual pins; **UNDO** returns to the previous loop.
- **FEEL** has three musically scored styles: **WARM** (smooth seventh/ninth colors), **CRISPY** (sus/add9 brightness), **CHEESY** (maj7/dominant/6 nostalgic movement). The emotional associations are subjective.
- **ARP** has four direct real-time settings: KNOB 1 RATE (1/4, 1/8, 1/16, 1/32), KNOB 2 GATE (15–100%), KNOB 3 DIRECTION (up/down/up-down/random), KNOB 4 ORDER (pitch/root-first/out-in/fifth-first). Browser playback uses all four parameters.
- **SAVE / RESTORE** retains FEEL and ARP settings with the loop; legacy ELSEWHERE browser storage keys are read as a migration fallback when on the same domain.

**Hardware status:** Four FM1 encoders are only a proposed direct mapping. The browser prototype is not flashable FM1 firmware; the original C harmony module is not yet ported to this updated JS feature set. See [FM1 encoder mapping](FM1_KNOBS.md).

**Checks:** `node chordon-bleu/tests/harmony.test.mjs` tests 1,080 FLIP mutations, musical bias, and ARP note scheduling; browser-level Chromium checks were also run independently across six viewport sizes and verified nonzero sound output. This does not establish iPhone Safari or hardware compatibility.
