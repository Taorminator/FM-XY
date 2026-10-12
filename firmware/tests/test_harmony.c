/* SPDX-License-Identifier: GPL-3.0-only */
#include "../fmxy_harmony.h"
#include <assert.h>
#include <stdio.h>

int main(void)
{
    fmxy_hint_t out[2];
    unsigned cases = 0;
    for (uint8_t mode = 0; mode < 2; mode++)
        for (uint8_t key = 0; key < 12; key++)
            for (uint8_t root = 0; root < 12; root++) {
                uint8_t before = root;
                fmxy_suggest(root, key, mode, out);
                assert(root == before);
                for (unsigned i = 0; i < 2; i++) {
                    assert(out[i].root < 12);
                    assert(out[i].quality <= FMXY_DIM);
                }
                cases++;
            }
    fmxy_suggest(0, 0, 1, out);
    assert(out[0].root == 5 && out[0].quality == FMXY_MIN7);
    assert(out[1].root == 8 && out[1].quality == FMXY_MAJ7);
    puts("FM-XY harmony: 288 scale/key/root combinations passed");
    assert(cases == 288);
    return 0;
}
