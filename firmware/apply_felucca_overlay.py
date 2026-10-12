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

    # The original CH_POW arpeggiator fixture assumes key 7 is always C4.
    # With the ROOT-based fixed-chord keyboard this is true when ROOT = F.
    p = repo / "tests/scale_test.c"
    patch_once(p, "    t->p[P_CHRD] = CH_POW;",
               "    t->p[P_ROOT] = 5;\n    t->p[P_CHRD] = CH_POW;")
    patch_once(p,
               "    assert(arp_seen[0] == 60 && arp_seen[1] == 67 && arp_seen[2] == 72);",
               "    assert(arp_seen[0] == 60 && arp_seen[1] == 67 && arp_seen[2] == 72);\n    t->p[P_ROOT] = 7;   /* ROOT G: the held chord follows the keyboard up 2 semitones */\n    arp_run(t, 3);\n    assert(arp_seen[0] == 62 && arp_seen[1] == 69 && arp_seen[2] == 74);\n    t->p[P_ROOT] = 5;")
    p = repo / "firmware/src/ui_graph.c"
    patch_once(p, "        cv_rrect(x, BLACK[note % 12u] ? 36 : 62, (int32_t)w - 2, 48, w > 6u ? 3 : 2,\n                 !on ? T_RAISE : note % 12u == (uint32_t)r % 12u ? T_ACCENT : c, T_SURF);", "        /* FM-XY: hard vertical bars with clean negative-space cuts, kept\n         * inside the original piano geometry for 240x240 readability. */\n        {\n            int32_t top = BLACK[note % 12u] ? 36 : 62;\n            int32_t width = (int32_t)w - 2;\n            uint16_t shade = !on ? T_RAISE : note % 12u == (uint32_t)r % 12u ? T_ACCENT : c;\n            cv_rect(x, top, width, 48, shade);\n            cv_rect(x + width / 2, top + 5, 1, on ? 3 : 7, T_SURF);\n        }")
    p = repo / "firmware/src/params.c"
    patch_once(p, "    {\"CHORD\", FAM_SCL, SC_TRACK, GR_CHORD, {P_CHRD, P_VOIC, 0xFF, 0xFF}},", "    {\"CHORD\", FAM_SCL, SC_TRACK, GR_CHORD, {P_ROOT, P_CHRD, P_VOIC, P_AMODE}},")
    p = repo / "firmware/src/ui_draw.c"
    patch_once(p, "static void draw_columns(void)\n{", "/* FM-XY four hardware knobs on CHORD. */\nstatic const char *fmxy_chord_card_label(uint32_t c)\n{\n    static const char *const labels[4] = {\"ROOT\", \"TYPE\", \"VOICE\", \"ARP\"};\n    return labels[c & 3u];\n}\nstatic void draw_columns(void)\n{")
    p = repo / "firmware/src/ui_draw.c"
    patch_once(p, "        draw_column(c, d->label, val, unit, VAL(c), d->fmt == F_ENUM && d->max < 2 ? -1 : RATIO(d, enum_rank(d, *vp)),", "        draw_column(c, cur_page()->graph == GR_CHORD ? fmxy_chord_card_label(c) : d->label, val, unit,\n                    VAL(c), d->fmt == F_ENUM && d->max < 2 ? -1 : RATIO(d, enum_rank(d, *vp)),")
    p = repo / "firmware/src/ui_input.c"
    patch_once(p, "static uint32_t song_leds(void);", "/* Suggestions illuminate triggers but never edit or sound notes.\n * UI work only, not inside the audio ISR. */\nstatic uint32_t fmxy_chord_hint_leds(uint32_t *first)\n{\n    const track_t *t = TSEL;\n    fmxy_hint_t hints[2];\n    uint32_t k, second = 0;\n    *first = 0;\n    if (ui.home || ui.menu || ui.layer || ui.confirm || name_on() ||\n        cur_page()->graph != GR_CHORD || chord_kit(t) ||\n        t->p[P_CHRD] < CH_MAJ || t->p[P_CHRD] > CH_POW ||\n        (t->p[P_SCALE] != 1 && t->p[P_SCALE] != 2))\n        return 0;\n    fmxy_suggest((uint8_t)t->p[P_ROOT], (uint8_t)t->p[P_ROOT],\n                 (uint8_t)(t->p[P_SCALE] == 2), hints);\n    for (k = 0; k < 12u; k++) {\n        uint32_t note = kb_map(t, k);\n        if (note == KB_SILENT)\n            continue;\n        if (note % 12u == hints[0].root)\n            *first |= 1u << k;\n        else if (note % 12u == hints[1].root)\n            second |= 1u << k;\n    }\n    return second;\n}\nstatic uint32_t song_leds(void);")
    p = repo / "firmware/src/ui_input.c"
    patch_once(p, "    uint32_t k, c, g, br, beat, sc, sr = 0;", "    uint32_t k, c, g, br, beat, sc, sr = 0, fmxy_first = 0, fmxy_second;")
    p = repo / "firmware/src/ui_input.c"
    patch_once(p, "    sc = keys_map ? 0u : scale_leds(&sr);", "    fmxy_second = keys_map ? 0u : fmxy_chord_hint_leds(&fmxy_first);\n    sc = keys_map || fmxy_first || fmxy_second ? 0u : scale_leds(&sr);")
    p = repo / "firmware/src/ui_input.c"
    patch_once(p, "        led_put(nb, 14u + k, (int)((br >> k) & 1u));", "        led_put(nb, 14u + k, (int)((br >> k) & 1u));\n        led_put(sm, 14u + k, (int)((fmxy_first >> k) & 1u));\n        led_put(sg, 14u + k, (int)((fmxy_second >> k) & 1u));")
    p = repo / "tests/ui_test.c"
    patch_once(p, "    bad += check(\"SCL tapped again: the CHORD page (CHRD VOIC, the chord graph)\", ok && cur_page()->id[0] == P_CHRD &&\n                 cur_page()->id[1] == P_VOIC);", "    bad += check(\"FM-XY CHORD page: ROOT TYPE VOICE ARP\", ok &&\n                 cur_page()->id[0] == P_ROOT && cur_page()->id[1] == P_CHRD &&\n                 cur_page()->id[2] == P_VOIC && cur_page()->id[3] == P_AMODE);")
    p = repo / "tests/ui_test.c"
    patch_once(p, "    turn(EN_K1, 1); frame();\n    turn(EN_K2, 1); frame();\n    bad += check(\"  KNOB 1: CHRD DIA3, KNOB 2: VOIC OPEN\", t->p[P_CHRD] == CH_DIA3 && t->p[P_VOIC] == VC_OPEN);", "    turn(EN_K2, 1); frame();\n    turn(EN_K3, 1); frame();\n    bad += check(\"  FM-XY KNOB 2 TYPE DIA3, KNOB 3 VOICE OPEN\", t->p[P_CHRD] == CH_DIA3 && t->p[P_VOIC] == VC_OPEN);\n    turn(EN_K4, 1); frame();\n    bad += check(\"  FM-XY KNOB 4 controls native ARP\", t->p[P_AMODE] == AM_UP);\n    turn(EN_K4, -1); frame();")
    p = repo / "tests/ui_test.c"
    patch_once(p, "    key_down(7); frame();                                          /* C4 in C (SCALE CHR: the major of C) */", "    t->p[P_ROOT] = 5; t->p[P_SCALE] = 1; t->p[P_CHRD] = CH_MAJ;\n    {\n        uint32_t first = 0, second = fmxy_chord_hint_leds(&first);\n        bad += check(\"FM-XY LEDs: C then D as suggestion triggers in F major\",\n                     first == (1u << 7) && second == (1u << 9));\n        bad += check(\"  hints leave the chosen chord untouched\",\n                     t->p[P_ROOT] == 5 && t->p[P_CHRD] == CH_MAJ && t->p[P_VOIC] == VC_OPEN);\n        t->p[P_SCALE] = 0;\n        bad += check(\"  chromatic: no misleading diatonic LEDs\",\n                     fmxy_chord_hint_leds(&first) == 0u && first == 0u);\n    }\n    t->p[P_ROOT] = 0; t->p[P_CHRD] = CH_DIA3; t->p[P_SCALE] = 0;\n    key_down(7); frame();                                          /* C4 in C (SCALE CHR: the major of C) */")
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
