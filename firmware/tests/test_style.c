/* SPDX-License-Identifier: GPL-3.0-only
 * Fixed-buffer host regressions for future on-device STYLE integration. */
#include "../fmxy_style.h"
#include <assert.h>
#include <stdio.h>

typedef struct { uint8_t key, note, on; } event_t;
static event_t events[512];
static unsigned nevents;
static void emitted(uint8_t key, uint8_t note, uint8_t on, void *ctx)
{
    (void)ctx;
    assert(nevents < sizeof events / sizeof events[0]);
    events[nevents++] = (event_t){key, note, on};
}
static void expect_event(unsigned idx, uint8_t key, uint8_t note, uint8_t on)
{
    assert(idx < nevents);
    assert(events[idx].key == key);
    assert(events[idx].note == note);
    assert(events[idx].on == on);
}
static void clear_log(void) { nevents = 0; }

int main(void)
{
    fmxy_style_queue_t q = {0};
    static const uint8_t fm7[4] = {53, 56, 60, 63};
    static const uint8_t gm7[4] = {55, 58, 62, 65};
    static const uint8_t am7[4] = {57, 60, 64, 67};
    unsigned i;

    fmxy_style_reset(&q);
    assert(sizeof q < 1024u);
    assert(fmxy_style_down(&q, 0, fm7, 4, FMXY_STYLE_BLOCK, 100u, 48000u));
    assert(q.pending == 4u);
    fmxy_style_process(&q, 99u, emitted, 0);
    assert(nevents == 0u);
    fmxy_style_process(&q, 100u, emitted, 0);
    assert(nevents == 4u && q.pending == 0u);
    for (i = 0; i < 4u; ++i) expect_event(i, 0, fm7[i], 1);
    fmxy_style_up(&q, 0, emitted, 0);
    assert(nevents == 8u);
    for (i = 0; i < 4u; ++i) expect_event(i + 4u, 0, fm7[i], 0);

    clear_log();
    assert(fmxy_style_down(&q, 0, fm7, 4, FMXY_STYLE_STRUM, 0u, 48000u));
    assert(!fmxy_style_down(&q, 0, gm7, 4, FMXY_STYLE_STRUM, 0u, 48000u));
    fmxy_style_process(&q, 0u, emitted, 0);
    assert(nevents == 1u && q.pending == 3u);
    fmxy_style_process(&q, 959u, emitted, 0); assert(nevents == 1u);
    fmxy_style_process(&q, 960u, emitted, 0); assert(nevents == 2u);
    fmxy_style_process(&q, 1919u, emitted, 0); assert(nevents == 2u);
    fmxy_style_process(&q, 1920u, emitted, 0); assert(nevents == 3u);
    fmxy_style_process(&q, 2880u, emitted, 0); assert(nevents == 4u);
    for (i = 0; i < 4u; ++i) expect_event(i, 0, fm7[i], 1);
    fmxy_style_up(&q, 0, emitted, 0);
    assert(nevents == 8u && q.pending == 0u);

    /* Release while the strum is in flight: the remaining notes never fire. */
    clear_log();
    assert(fmxy_style_down(&q, 1, gm7, 4, FMXY_STYLE_STRUM, 1000u, 48000u));
    fmxy_style_process(&q, 1000u, emitted, 0);
    fmxy_style_up(&q, 1, emitted, 0);
    assert(nevents == 2u && q.pending == 0u);
    expect_event(0, 1, 55, 1);
    expect_event(1, 1, 55, 0);
    fmxy_style_process(&q, 300000u, emitted, 0);
    assert(nevents == 2u);

    /* Two physical keys are independent even when they share MIDI pitches. */
    clear_log();
    assert(fmxy_style_down(&q, 0, fm7, 4, FMXY_STYLE_SPREAD, 200u, 48000u));
    assert(fmxy_style_down(&q, 1, am7, 4, FMXY_STYLE_SPREAD, 200u, 48000u));
    fmxy_style_process(&q, 200u, emitted, 0);
    assert(nevents == 2u && q.pending == 6u);
    fmxy_style_process(&q, 2600u, emitted, 0);
    assert(nevents == 4u && q.pending == 4u);
    fmxy_style_up(&q, 0, emitted, 0);
    assert(q.pending == 2u);
    fmxy_style_process(&q, 7400u, emitted, 0);  /* last SPREAD note is due at 7400 */
    assert(nevents == 8u && q.pending == 0u);
    fmxy_style_panic(&q, emitted, 0);
    assert(q.pending == 0u);
    fmxy_style_process(&q, 100000u, emitted, 0);
    assert(nevents == 12u);  /* 2 + 2 + 2 + 2 ON/OFF events plus 4 final OFFs */

    /* A wrap of the unsigned sample clock does not hang or prematurely fire. */
    clear_log();
    fmxy_style_reset(&q);
    assert(fmxy_style_down(&q, 2, gm7, 4, FMXY_STYLE_STRUM, 0xFFFFFF00u, 48000u));
    fmxy_style_process(&q, 0xFFFFFF00u, emitted, 0);
    assert(nevents == 1u);
    fmxy_style_process(&q, 0x000002BFu, emitted, 0);  /* next due: 0x2c0 */
    assert(nevents == 1u);
    fmxy_style_process(&q, 0x000002C0u, emitted, 0);
    assert(nevents == 2u);
    fmxy_style_panic(&q, emitted, 0);
    assert(q.pending == 0u && nevents == 4u);

    /* Explicitly route ARP to existing Felucca logic, not this event queue. */
    clear_log();
    assert(!fmxy_style_down(&q, 0, fm7, 4, FMXY_STYLE_ARP, 0u, 48000u));
    assert(!fmxy_style_down(&q, 27, fm7, 4, FMXY_STYLE_BLOCK, 0u, 48000u));
    assert(!fmxy_style_down(&q, 0, fm7, 5, FMXY_STYLE_BLOCK, 0u, 48000u));
    assert(!fmxy_style_down(&q, 0, fm7, 4, FMXY_STYLE_BLOCK, 0u, 0u));
    assert(q.pending == 0u);
    fmxy_style_process(&q, 1000u, emitted, 0);
    assert(nevents == 0u);

    puts("FM-XY STYLE scheduler: block/strum/spread, cancellation, overlap, panic and clock wrap passed");
    return 0;
}
