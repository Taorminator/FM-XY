/* SPDX-License-Identifier: GPL-3.0-only
 * FM-XY by Middle Age Engineering
 */
#ifndef FMXY_HARMONY_H
#define FMXY_HARMONY_H

#include <stdint.h>

typedef struct { uint8_t root, quality; } fmxy_hint_t;
enum { FMXY_MAJ7, FMXY_MIN7, FMXY_DOM7, FMXY_DIM };

static const uint8_t fmxy_steps[2][7] = {
    {0, 2, 4, 5, 7, 9, 11},
    {0, 2, 3, 5, 7, 8, 10}
};
static const uint8_t fmxy_quality[2][7] = {
    {FMXY_MAJ7, FMXY_MIN7, FMXY_MIN7, FMXY_MAJ7, FMXY_DOM7, FMXY_MIN7, FMXY_DIM},
    {FMXY_MIN7, FMXY_DIM, FMXY_MAJ7, FMXY_MIN7, FMXY_MIN7, FMXY_MAJ7, FMXY_DOM7}
};
static const uint8_t fmxy_next[2][7][2] = {
    {{4, 5}, {4, 0}, {5, 3}, {4, 0}, {0, 5}, {3, 1}, {0, 2}},
    {{3, 5}, {4, 0}, {6, 5}, {6, 0}, {0, 5}, {2, 6}, {0, 2}}
};

/* Minor is 0 or 1; root and key are pitch classes (0..11). */
static inline uint8_t fmxy_degree(uint8_t root, uint8_t key, uint8_t minor)
{
    uint8_t rel = (uint8_t)((root + 12u - key) % 12u);
    uint8_t best = 0, distance = 12, i;
    for (i = 0; i < 7u; i++) {
        uint8_t diff = (uint8_t)((rel + 12u - fmxy_steps[minor][i]) % 12u);
        uint8_t d = diff > 6u ? (uint8_t)(12u - diff) : diff;
        if (d < distance) { distance = d; best = i; }
    }
    return best;
}

static inline void fmxy_suggest(uint8_t root, uint8_t key, uint8_t minor,
                                fmxy_hint_t out[2])
{
    uint8_t degree = fmxy_degree(root, key, minor), i;
    for (i = 0; i < 2u; i++) {
        uint8_t next = fmxy_next[minor][degree][i];
        out[i].root = (uint8_t)((key + fmxy_steps[minor][next]) % 12u);
        out[i].quality = fmxy_quality[minor][next];
    }
}
#endif
