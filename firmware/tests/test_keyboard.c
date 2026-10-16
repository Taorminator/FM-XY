/* SPDX-License-Identifier: GPL-3.0-only */
#include "../fmxy_keyboard.h"
#include <assert.h>
#include <stdio.h>

int main(void)
{
    unsigned count = 0;
    for (uint32_t root = 0; root < 12u; root++)
        for (uint32_t key = 0; key < 27u; key++)
            for (int32_t octave = -2; octave <= 2; octave++) {
                int32_t want = 48 + (int32_t)root + (int32_t)key + 12 * octave;
                if (want < 0) want = 0;
                if (want > 127) want = 127;
                assert(fmxy_keyboard_note(root, key, octave, 0) == (uint32_t)want);
                count++;
            }
    assert(fmxy_keyboard_note(5, 0, 0, 0) == 53u); /* F3 */
    assert(fmxy_keyboard_note(5, 1, 0, 0) == 54u); /* F#3 */
    assert(fmxy_keyboard_note(5, 2, 0, 0) == 55u); /* G3 */
    assert(fmxy_keyboard_note(5, 7, 0, 0) == 60u); /* C4 */
    assert(fmxy_keyboard_note(5, 0, 1, 0) == 65u); /* F4 */
    assert(fmxy_keyboard_note(5, 0, 0, 12) == 65u);
    assert(fmxy_keyboard_note(5, 0, 0, -12) == 41u);
    puts("FM-XY keyboard: 1620 note mappings and octave/transpose checks passed");
    assert(count == 1620u);
    return 0;
}
