#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Apply the FM-XY proof-of-concept overlay to the pinned Felucca checkout.

Never touches engine, scheduler, OTA loader, storage or backup code.
Run against hugelton/Felucca at ef1f561b6b105f20350f6b1eac0dc0789a357f00.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import subprocess

UPSTREAM = "ef1f561b6b105f20350f6b1eac0dc0789a357f00"
STAGED = {}


def patch_once(path: Path, old: str, new: str) -> None:
    source = STAGED.get(path)
    if source is None:
        source = path.read_text(encoding="utf-8")
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one anchor, found {count} for {old[:80]!r}")
    STAGED[path] = source.replace(old, new, 1)
    print(f"FM-XY PATCH {path}")


def install(repo: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    sha = subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
    ).strip()
    if sha != UPSTREAM:
        raise RuntimeError(f"Wrong upstream commit {sha}; expected {UPSTREAM}")
    target = repo / "firmware/src/fmxy_harmony.h"
    keyboard = repo / "firmware/src/fmxy_keyboard.h"
    if target.exists() or keyboard.exists():
        raise RuntimeError("FM-XY overlay already applied")
    p = repo / "firmware/src/seq.c"
    anchor = "static uint32_t kb_pitch(const track_t *t, uint32_t k, int32_t oct)\n{\n"
    # Fixed CHRD shapes use ROOT on key zero, independent of SCALE/QUANT.
    patch_once(p, anchor, '#include "fmxy_keyboard.h"\n' + anchor +
               '    if (t->p[P_CHRD] >= FMXY_FIXED_FIRST && t->p[P_CHRD] <= FMXY_FIXED_LAST)\n'
               '        return fmxy_keyboard_note((uint32_t)t->p[P_ROOT], k, oct, t->p[P_TRANS]);\n')
    p = repo / "firmware/src/ui_graph.c"
    patch_once(p, '#include "ui_fm6op.c"',
               '#include "fmxy_harmony.h"\n#include "ui_fm6op.c"')
    old = """    chord_name(b, (uint32_t)r, mask);
    cv_text_on(14, 8, &AF_M, b, T_TEXT, T_SURF);"""
    new = """    chord_name(b, (uint32_t)r, mask);
    cv_text_on(14, 8, &AF_M, b, T_TEXT, T_SURF);
    if (t->p[P_SCALE] == 1 || t->p[P_SCALE] == 2) {
        fmxy_hint_t hints[2];
        static const char *const quality[] = {"maj7", "m7", "7", "dim"};
        char first[16], second[16];
        fmxy_suggest((uint8_t)((uint32_t)r % 12u),
                     (uint8_t)t->p[P_ROOT],
                     (uint8_t)(t->p[P_SCALE] == 2), hints);
        str_cpy(first, N_NOTE[hints[0].root], sizeof first);
        str_cpy(first + str_len(first), quality[hints[0].quality],
                sizeof first - str_len(first));
        str_cpy(second, N_NOTE[hints[1].root], sizeof second);
        str_cpy(second + str_len(second), quality[hints[1].quality],
                sizeof second - str_len(second));
        cv_text_on(14, 24, &AF_S, "NEXT", T_MID, T_SURF);
        cv_text_on(76, 24, &AF_S, first, T_THEME, T_SURF);
        cv_text_on(156, 24, &AF_S, second, T_THEME, T_SURF);
    }"""
    patch_once(p, old, new)

    p = repo / "firmware/src/ui_draw.c"
    patch_once(p,
               'static const char *const SPLASH_LINES[] = {"Felucca", FELUCCA_VERSION, "H\\xFCgelton Instruments", "with community"};',
               'static const char *const SPLASH_LINES[] = {"FM-XY", FELUCCA_VERSION, "Middle Age", "Engineering"};')
    p = repo / "firmware/src/ui_menu.c"
    patch_once(p,
               'static const menu_credit_t MENU_CREDITS[] = {\n',
               '''static const menu_credit_t MENU_CREDITS[] = {
    {"FM-XY", MC_TITLE},
    {"Middle Age Engineering", MC_TEXT},
    {"Felucca fork / based on work by Leo Kuroshita", MC_TEXT},
    {"https://github.com/Taorminator/FM-XY", MC_URL},
    {"Independent project. No warranty.", MC_TEXT},
    {"", MC_TEXT},
''')
    p = repo / "tests/chord_test.c"
    patch_once(p, 'int main(void)\n{', "/* FM-XY: physical key zero follows ROOT; every key plays a complete fixed TYPE. */\nstatic int fmxy_root_type_keys(void)\n{\n    int bad = 0, ok = 1;\n    track_t *t = &trk[0];\n    static const uint8_t notes[3][4] = {\n        {53, 56, 60, 63}, {54, 57, 61, 64}, {55, 58, 62, 65}\n    };\n    uint32_t key, i;\n    reset();\n    song.octave = 0;\n    t->p[P_ROOT] = 5; t->p[P_CHRD] = CH_MIN7; t->p[P_VOIC] = VC_CLOSE;\n    t->p[P_QUANT] = QN_WHITE;  /* Fixed TYPE stays chromatic, even with WHITE set. */\n    for (key = 0; key < 3u; key++) {\n        key_down(key);\n        ok &= kb_note[key] == 53u + key && ngated(t) == 4u;\n        for (i = 0; i < 4u; i++) ok &= gate_note(t, notes[key][i]);\n        ok &= t->p[P_ROOT] == 5 && t->p[P_CHRD] == CH_MIN7 && t->p[P_VOIC] == VC_CLOSE;\n        key_up(key);\n        ok &= !ngated(t);\n    }\n    bad += check(\"FM-XY F m7: physical F, F#, G each plays its full chromatic m7\", ok);\n    key_down(7); bad += check(\"FM-XY transposition crosses octave (C4m7)\",\n                              kb_note[7] == 60 && gate_note(t, 60) && gate_note(t, 63) &&\n                              gate_note(t, 67) && gate_note(t, 70));\n    key_up(7);\n    song.octave = 1;\n    key_down(0); bad += check(\"FM-XY octave button retains F4m7\",\n                              kb_note[0] == 65 && gate_note(t, 65) && gate_note(t, 68) &&\n                              gate_note(t, 72) && gate_note(t, 75));\n    key_up(0); song.octave = 0;\n    t->p[P_ROOT] = 0;\n    key_down(0); bad += check(\"FM-XY ROOT C moves physical first key to C3m7\",\n                              kb_note[0] == 48 && gate_note(t, 48) && gate_note(t, 51) &&\n                              gate_note(t, 55) && gate_note(t, 58));\n    key_up(0);\n    t->p[P_ROOT] = 5;\n    t->p[P_VOIC] = VC_OPEN;\n    key_down(0); bad += check(\"FM-XY OPEN voicing retained\",\n                              gate_note(t, 53) && gate_note(t, 60) && gate_note(t, 63) && gate_note(t, 68));\n    key_up(0);\n    t->p[P_VOIC] = VC_CLOSE;\n    key_down(0); key_down(1); key_down(2);\n    bad += check(\"FM-XY multi-key chords respect global eight-voice limit\",\n                 voices_busy() <= NVOICE && voices_busy() > 0u);\n    key_up(0); key_up(1); key_up(2);\n    bad += check(\"FM-XY all held notes eventually release\", !ngated(t));\n    song.rec = 1; song.playing = 1; t->seq_idx = 4; t->seq_pos = 0;\n    key_down(0);\n    ok = t->step[4].n == 4u && t->step[4].time == ST_NOTE;\n    for (i = 0; ok && i < 4u; i++) ok &= t->step[4].note[i] == notes[0][i];\n    bad += check(\"FM-XY live recording preserves full chord notes and octaves\", ok);\n    key_up(0); song.rec = 0; song.playing = 0;\n    t->p[P_AMODE] = AM_UP;\n    key_down(0);\n    ok = t->nheld == 4u;\n    for (i = 0; ok && i < 4u; i++) ok &= t->held[i] == notes[0][i];\n    bad += check(\"FM-XY arpeggiator holds the translated chord pitches\", ok);\n    key_up(0);\n    t->p[P_AMODE] = AM_OFF;\n    return bad;\n}\n\n" + 'int main(void)\n{')
    patch_once(p, 'int bad = theory() + shapes_voicings() + keys() + arp_rec() + midi_in() + kits();',
               'int bad = theory() + shapes_voicings() + keys() + arp_rec() + midi_in() + kits() + fmxy_root_type_keys();')
    # An upstream fixed-chord test expects C4 on physical key 7; use ROOT F
    # to preserve that expectation after the new ROOT-anchored keyboard mapping.
    patch_once(p, 't->p[P_CHRD] = CH_MAJ7; t->p[P_VOIC] = VC_BASS;\n    t->seq_idx = 4;',
               't->p[P_ROOT] = 5; t->p[P_CHRD] = CH_MAJ7; t->p[P_VOIC] = VC_BASS;\n    t->seq_idx = 4;')
    p = repo / "tests/ui_render.c"
    patch_once(
        p,
        'static const char WANT[] = "Felucca|" FELUCCA_VERSION "|H\\xFCgelton Instruments|with community";',
        'static const char WANT[] = "FM-XY|" FELUCCA_VERSION "|Middle Age|Engineering";',
    )

    for path, content in STAGED.items():
        path.write_text(content, encoding="utf-8")
    shutil.copyfile(root / "firmware/fmxy_harmony.h", target)
    shutil.copyfile(root / "firmware/fmxy_keyboard.h", keyboard)
    print("FM-XY overlay applied. Audio, update and storage code unchanged.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("felucca", type=Path)
    opts = parser.parse_args()
    install(opts.felucca.resolve())
