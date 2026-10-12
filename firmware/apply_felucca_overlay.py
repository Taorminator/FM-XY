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
    p = repo / "firmware/src/ui_graph.c"
    patch_once(p, '#include "ui_fm6op.c"',
               '#include "fmxy_harmony.h"\n#include "ui_fm6op.c"')
    old = """    chord_name(b, (uint32_t)r, mask);
    cv_text_on(14, 8, &AF_M, b, T_TEXT, T_SURF);"""
    new = """    chord_name(b, (uint32_t)r, mask);
    if (t->p[P_SCALE] == 1 || t->p[P_SCALE] == 2) {
        fmxy_hint_t suggestions[2];
        static const char *const QUALITY[4] = {"maj7", "m7", "7", "dim"};
        char first[12], second[12], names[28];
        fmxy_suggest((uint8_t)((uint32_t)r % 12u),
                     (uint8_t)t->p[P_ROOT],
                     (uint8_t)(t->p[P_SCALE] == 2), suggestions);
        str_cpy(first, N_NOTE[suggestions[0].root], sizeof first);
        str_cpy(first + str_len(first), QUALITY[suggestions[0].quality],
                sizeof first - str_len(first));
        str_cpy(second, N_NOTE[suggestions[1].root], sizeof second);
        str_cpy(second + str_len(second), QUALITY[suggestions[1].quality],
                sizeof second - str_len(second));
        names[0] = 0;
        for (i = 0; i < n; i++) {
            if (i)
                str_cpy(names + str_len(names), " ",
                        sizeof names - str_len(names));
            str_cpy(names + str_len(names), N_NOTE[nn[i] % 12u],
                    sizeof names - str_len(names));
        }
        cv_text_on(14, 5, &AF_M, b, T_TEXT, T_SURF);
        cv_text_r(226, 5 + AF_M.asc - AF_S.asc, &AF_S,
                  cap, T_MID, T_SURF);
        cv_text_r(226, 28, &AF_S, names, T_TEXT, T_SURF);
        cv_rrect(10, 46, 220, 20, 2, T_THEME, T_SURF);
        cv_text_on(18, 49, &AF_S, "ANSWER", T_INK, T_THEME);
        cv_text_r(222, 47, &AF_M, first, T_INK, T_THEME);
        cv_rrect(10, 73, 220, 20, 2, T_RAISE, T_SURF);
        cv_text_on(18, 76, &AF_S, "LIFT", T_TEXT, T_RAISE);
        cv_text_r(222, 74, &AF_M, second, T_TEXT, T_RAISE);
        return;
    }
    cv_text_on(14, 8, &AF_M, b, T_TEXT, T_SURF);"""
    patch_once(p, old, new)

    p = repo / "tools/gen_ui_palettes.py"
    old = ']\nBW = "MONO"'
    new = '''    # FM-XY additions (append-only: saved upstream palette ids stay stable).
    ("OP-XY Mono", (10, 10, 10), (34, 34, 34),
     (244, 244, 244), (232, 232, 232), (255, 255, 255)),
    ("OP-1 Color", (9, 11, 13), (30, 33, 37),
     (248, 250, 252), (100, 190, 244), (156, 235, 109)),
    ("OP-XY Color", (9, 9, 13), (30, 32, 43),
     (250, 250, 250), (141, 157, 254), (255, 180, 103)),
]
BW = "MONO"'''
    patch_once(p, old, new)

    p = repo / "firmware/src/ui_draw.c"
    patch_once(p,
               'static const char *const SPLASH_LINES[] = {"Felucca", FELUCCA_VERSION, "H\\xFCgelton Instruments", "with community"};',
               'static const char *const SPLASH_LINES[] = {"FM-XY", "Felucca fork", "Middle Age", "Engineering"};')
    patch_once(p,
               '    lcd_fill(SPL_X0, SPL_X0, SPL_SQ, SPL_SQ, T_RAISE);\n    splash_band(',
               '''    lcd_fill(SPL_X0, SPL_X0, SPL_SQ, SPL_SQ, T_RAISE);
    {
        static const uint8_t dust[][3] = {
            {8, 16, 3}, {19, 45, 6}, {13, 111, 4},
            {26, 194, 4}, {5, 229, 5}, {215, 13, 5},
            {228, 67, 4}, {218, 141, 5}, {228, 222, 6},
            {51, 7, 3}, {181, 230, 4}, {105, 10, 4},
        };
        uint32_t j;
        for (j = 0; j < sizeof dust / sizeof dust[0]; j++)
            lcd_fill(dust[j][0], dust[j][1], dust[j][2], dust[j][2],
                     j & 1u ? T_THEME : T_DIM);
    }
    splash_band(''')

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
    if target.exists():
        raise RuntimeError(f"Already applied: {target}")
    for path, content in STAGED.items():
        path.write_text(content, encoding="utf-8")
    shutil.copyfile(root / "firmware/fmxy_harmony.h", target)
    print("FM-XY overlay applied. Audio, update and storage code unchanged.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("felucca", type=Path)
    opts = parser.parse_args()
    install(opts.felucca.resolve())
