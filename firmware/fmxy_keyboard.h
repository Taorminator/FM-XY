/* SPDX-License-Identifier: GPL-3.0-only
 * FM-XY chromatic keyboard for Felucca's fixed chord shapes.
 * Key 0 is ROOT in octave 3; other keys add one semitone each.
 */
#ifndef FMXY_KEYBOARD_H
#define FMXY_KEYBOARD_H
#include <stdint.h>

enum { FMXY_FIXED_FIRST = 3, FMXY_FIXED_LAST = 9 }; /* CH_MAJ .. CH_POW */

static inline uint32_t fmxy_keyboard_note(uint32_t root, uint32_t key,
                                          int32_t octave, int32_t transpose)
{
    int32_t n = 48 + (int32_t)(root % 12u) + (int32_t)key + 12 * octave + transpose;
    return (uint32_t)(n < 0 ? 0 : n > 127 ? 127 : n);
}
#endif
