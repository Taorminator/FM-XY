# FM-XY firmware

Based on [Felucca](https://github.com/hugelton/Felucca), GPL-3.0-only, pinned to `ef1f561b6b105f20350f6b1eac0dc0789a357f00`.

This source overlay adds an FM-XY splash, original credits and **read-only harmonic suggestions** to Felucca's existing CHORD display. Audio, input timing, sequencer, OTA, storage and all 10 original palettes remain unchanged.

The browser demo's three named themes and ROOT/TYPE keyboard interaction are **not yet ported** to native firmware.

Run `python3 firmware/apply_felucca_overlay.py PATH_TO_FELUCCA`, then follow [Felucca's build instructions](https://github.com/hugelton/Felucca/blob/main/BUILDING.md).

CI builds original Felucca and the patched copy separately and runs upstream regressions. No firmware is approved for installation.

[Installer and release requirements](INSTALLER.md) · [Credits](../CREDITS.md)
