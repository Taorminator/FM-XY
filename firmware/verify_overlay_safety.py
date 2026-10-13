#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Allow only the reviewed keyboard mapping inside Felucca's sequencer file."""
from pathlib import Path
import subprocess
import sys

repo = Path(sys.argv[1])
path = "firmware/src/seq.c"
def git(*args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True)

changed = set(git("diff", "--name-only").splitlines())
allowed = {
    path, "firmware/src/ui_graph.c", "firmware/src/ui_draw.c",
    "firmware/src/ui_menu.c", "firmware/src/params.c", "firmware/src/ui_input.c",
    "tests/ui_render.c", "tests/chord_test.c", "tests/scale_test.c", "tests/ui_test.c",
    "firmware/src/midi_control.c",
}
extra = changed - allowed
if extra:
    raise SystemExit(f"Unexpected modified upstream paths: {sorted(extra)}")
original = git("show", "HEAD:" + path)
actual = (repo / path).read_text(encoding="utf-8")
anchor = "static uint32_t kb_pitch(const track_t *t, uint32_t k, int32_t oct)\n{\n"
addition = ('#include "fmxy_keyboard.h"\n' + anchor +
            '    if (t->p[P_CHRD] >= FMXY_FIXED_FIRST && t->p[P_CHRD] <= FMXY_FIXED_LAST)\n' +
            '        return fmxy_keyboard_note((uint32_t)t->p[P_ROOT], k, oct, t->p[P_TRANS]);\n')
if original.count(anchor) != 1 or actual != original.replace(anchor, addition):
    raise SystemExit("Unexpected sequencer diff outside reviewed keyboard mapping")
# Only a test-only MIDI ownership hook is permitted. The hardware firmware
# compiles it out, and this exact diff is audited alongside the keyboard diff.
mpath = "firmware/src/midi_control.c"
base_midi = git("show", "HEAD:" + mpath)
applied_midi = (repo / mpath).read_text(encoding="utf-8")
old_midi = "    return 0;\n}\n\nstatic void midi_release(uint32_t ch, uint32_t note)"
new_midi = "#if defined(FMXY_STYLE_TEST_OWNER)\n    /* Test-only owner lookup, excluded from the production firmware.\n     * Pending delayed notes are not sounding MIDI owners. */\n    if (fmxy_test_router && fmxy_style_route_active(fmxy_test_router,\n                                                    trk_index(t), note))\n        return 1;\n#endif\n    return 0;\n}\n\nstatic void midi_release(uint32_t ch, uint32_t note)"
if base_midi.count(old_midi) != 1 or applied_midi != base_midi.replace(old_midi, new_midi):
    raise SystemExit("Unexpected MIDI change outside test-only STYLE ownership")
print("Protected audio, scheduler, storage and loader paths unchanged; sequencer and test-only MIDI changes audited.")
