# FM-XY firmware

Native firmware development uses [Felucca](https://github.com/hugelton/Felucca) (GPL-3.0-only), pinned to `ef1f561b6b105f20350f6b1eac0dc0789a357f00`.

## First source overlay
- Adds three display palettes and an FM-XY boot screen.
- Shows two read-only chord suggestions for major and minor.
- Preserves the upstream audio engine, sequencer, storage, OTA and version metadata.

Run `python3 firmware/apply_felucca_overlay.py PATH_TO_PINNED_FELUCCA`, then follow [Felucca's build and test instructions](https://github.com/hugelton/Felucca/blob/main/BUILDING.md).

CI tests the overlay and palette contrast. **No compiled firmware or hardware validation yet. Do not flash.**

[Installer plan](INSTALLER.md) · [Credits](../CREDITS.md)
