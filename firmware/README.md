# FM-XY native firmware

Based on [Felucca](https://github.com/hugelton/Felucca), GPL-3.0-only, pinned to `ef1f561b6b105f20350f6b1eac0dc0789a357f00`.

This small, reproducible source overlay keeps Felucca's audio, eight-voice allocator, sequencer, storage and OTA mechanisms. It adds FM-XY splash/credits, read-only chord suggestions and a **ROOT-anchored chromatic hardware keyboard for Felucca's fixed CHRD types (MAJ through POW)**.

With `ROOT=F` and `CHRD=MIN7`, the first three physical keys play Fm7, F#m7 and Gm7. The selected CHRD and VOIC settings never change on key press. Octave and TRANS remain active. For these fixed shapes, SCALE/QUANT keyboard snapping is intentionally bypassed; OFF and diatonic modes retain Felucca's original mapping. Kit-specific mappings remain unchanged. MIDI inputs still use their incoming pitches, not the physical keyboard offset.

Existing Felucca polyphonic chord note-on/off, live and step recording, arpeggiator and global eight-voice stealing are reused. The native UI is still Felucca-based; the browser demo's four-card ROOT/TYPE/VOICE/STYLE interface and three themes are **not ported**. Further native UI/LED integration and real FM1 testing are pending.

Run `python3 firmware/apply_felucca_overlay.py PATH_TO_PINNED_FELUCCA`, then follow [Felucca's build instructions](https://github.com/hugelton/Felucca/blob/main/BUILDING.md).

CI builds the upstream baseline and patched tree independently. **No release is approved for hardware installation.** [Installer gates](INSTALLER.md) · [Credits](../CREDITS.md)
