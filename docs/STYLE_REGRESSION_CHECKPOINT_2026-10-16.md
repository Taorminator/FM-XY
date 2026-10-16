# Native STYLE host regression checkpoint — 2026-10-16

## Tested commit

- FM-XY commit: [`f329c1b7ee3e60d9a709d93ca63a97819156d4d8`](https://github.com/Taorminator/FM-XY/commit/f329c1b7ee3e60d9a709d93ca63a97819156d4d8)
- Parent: `20be0fbbb3fd4f61bc4df855d4ff842eb7e7deb1`
- Pinned Felucca source: `ef1f561b6b105f20350f6b1eac0dc0789a357f00`

This commit extends the generated Felucca host fixture in
`firmware/apply_felucca_overlay.py`. The additions run in
`tests/chord_test.c` after applying the overlay. They do not connect STYLE to
the production keyboard ISR or change the device's MIDI implementation.

## Added regression cases

- Sustain pedal with MIDI owning C4 before STYLE starts, then STYLE releasing
  before pedal-up.
- Sustain pedal with STYLE sounding before MIDI takes ownership, then the STYLE
  key releasing before pedal-up.
- ARP switched on while SPREAD notes are pending; already started and delayed
  notes are released or removed from ARP without leaving held notes.
- ARP already on at key-down, then switched off before key-up; held pitches and
  ARP state are cleared.
- Live recording of a delayed SPREAD chord: only notes whose scheduled attacks
  occurred are recorded, and releasing cancels the remaining attacks.
- Live recording of a held BLOCK chord across a sequencer step: the next step
  becomes a TIE and releasing clears the recording hold while preserving the
  completed tie.

The existing host fixture also covers both STYLE/MIDI ownership orders and
shared pitches. The STYLE router tests assert that simultaneous owners produce
one pitch attack and one final release, while the Felucca adapter checks that
the actual host voice and MIDI-note owner state survives either release order.

## Results for `f329c1b7`

All checks below completed successfully:

- [Full Felucca baseline and FM-XY build/regressions](https://github.com/Taorminator/FM-XY/actions/runs/38857241191): pinned baseline build and complete upstream tests passed; overlay applied; complete FM-XY build and host regressions passed; offline installer staging validation passed; overlay safety check passed.
- [Native overlay checks — push](https://github.com/Taorminator/FM-XY/actions/runs/38857241183) and [pull request](https://github.com/Taorminator/FM-XY/actions/runs/38857245047): passed.
- [FM-XY checks — push](https://github.com/Taorminator/FM-XY/actions/runs/38857241184) and [pull request](https://github.com/Taorminator/FM-XY/actions/runs/38857245013): passed.
- Local standalone FM-XY harmony, keyboard, STYLE scheduler, gate, and router host tests: passed.
- Local generated Felucca `chord_test`: passed, including the new sustain, ARP-switching, and recording cases.

No production note-path bug was reproduced by these regressions, so no device
code was changed. The result validates host behavior only. STRUM/SPREAD remain
disconnected from the production keyboard/audio path; this is not hardware
verification and does not authorize or provide installable firmware or a flash.
