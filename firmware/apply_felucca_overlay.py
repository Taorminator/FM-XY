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
    p = repo / "tests/ui_render.c"
    patch_once(
        p,
        'static const char WANT[] = "Felucca|" FELUCCA_VERSION "|H\\xFCgelton Instruments|with community";',
        'static const char WANT[] = "FM-XY|" FELUCCA_VERSION "|Middle Age|Engineering";',
    )

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
