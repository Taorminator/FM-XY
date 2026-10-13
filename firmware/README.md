# FM-XY native firmware

Based on [Felucca](https://github.com/hugelton/Felucca), GPL-3.0-only, pinned to `ef1f561b6b105f20350f6b1eac0dc0789a357f00`.

This small, reproducible source overlay keeps Felucca's audio, eight-voice allocator, sequencer, storage and OTA mechanisms. It adds FM-XY splash/credits, read-only chord suggestions and a **ROOT-anchored chromatic hardware keyboard for Felucca's fixed CHRD types (MAJ through POW)**.

With `ROOT=F` and `CHRD=MIN7`, the first three physical keys play Fm7, F#m7 and Gm7. The selected CHRD and VOIC settings never change on key press. Octave and TRANS remain active. For these fixed shapes, SCALE/QUANT keyboard snapping is intentionally bypassed; OFF and diatonic modes retain Felucca's original mapping. Kit-specific mappings remain unchanged. MIDI inputs still use their incoming pitches, not the physical keyboard offset.

Existing Felucca polyphonic chord note-on/off, live and step recording, arpeggiator and global eight-voice stealing are reused. The native SCL > CHORD page now offers four working knobs: **ROOT / TYPE / VOICE / ARP**. Knob 4 uses Felucca's existing ARP mode, not the browser prototype's separate STYLE parameter. Browser STYLE modes **STRUM, SPREAD and ARP note-staggering** remain unimplemented. With a major/minor scale selected and a fixed chord TYPE, the CHORD page illuminates two suggested root-trigger keys (first brighter, second dimmer) without changing the chosen chord. SCALE LEDS behave as before on other screens. This is an incremental native UI, not a port of all three browser themes or the entire OP-XY visual language. FM1 hardware and timing remain unverified.

The new `firmware/fmxy_style.h` is a **host-tested, fixed-memory scheduling primitive**, not yet connected to the FM1's note-on/off path. BLOCK starts all notes together; STRUM stages additional notes at 20 ms intervals and SPREAD at 50 ms intervals. It cancels future events on key release, suppresses OFF for unheard notes, survives sample-counter wrap, and explicitly delegates ARP to Felucca. A separate host-tested `fmxy_style_gate.h` now reference-counts pitches across all 27 hardware keys: overlapping chords send one ON and one final OFF, including partial releases and panic. It remains intentionally disconnected from playback. Live recording, MIDI-source sharing, hardware ISR budget and real note routing are not yet implemented or verified. No STRUM/SPREAD playback is claimed yet.

Run `python3 firmware/apply_felucca_overlay.py PATH_TO_PINNED_FELUCCA`, then follow [Felucca's build instructions](https://github.com/hugelton/Felucca/blob/main/BUILDING.md).

CI builds the upstream baseline and patched tree independently. **No release is approved for hardware installation.** [Installer gates](INSTALLER.md) · [Credits](../CREDITS.md)
