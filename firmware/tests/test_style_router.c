/* SPDX-License-Identifier: GPL-3.0-only
 * Four-track STYLE ownership and delayed-attack host regression. */
#include "../fmxy_style_router.h"
#include <assert.h>
#include <stdio.h>

typedef struct { uint8_t track, note, on; } event_t;
static event_t events[256];
static uint32_t nevents;

static void emit(uint8_t track, uint8_t note, uint8_t on, void *ctx)
{
    (void)ctx;
    assert(nevents < sizeof events / sizeof events[0]);
    events[nevents++] = (event_t){track, note, on};
}
static void expect(uint32_t index, uint8_t track, uint8_t note, uint8_t on)
{
    assert(index < nevents);
    assert(events[index].track == track);
    assert(events[index].note == note);
    assert(events[index].on == on);
}
static uint32_t owned(const fmxy_style_router_t *r)
{
    uint32_t t, n, count = 0;
    for (t = 0; t < FMXY_STYLE_TRACK_COUNT; ++t)
        for (n = 0; n < 128u; ++n)
            count += r->gate[t].references[n];
    return count;
}
int main(void)
{
    static const uint8_t fm7[4] = {53, 56, 60, 63};
    static const uint8_t am7[4] = {57, 60, 64, 67};
    static const uint8_t same[4] = {60, 64, 67, 71};
    fmxy_style_router_t r = {0};
    uint32_t k, t;

    assert(sizeof r < 2048u);
    fmxy_style_route_init(&r, emit, 0);
    assert(!fmxy_style_route_down(&r, 0, 4, fm7, 4, FMXY_STYLE_BLOCK, 0, 48000u));
    assert(!fmxy_style_route_down(&r, 27, 0, fm7, 4, FMXY_STYLE_BLOCK, 0, 48000u));
    assert(!fmxy_style_route_down(&r, 0, 0, fm7, 4, FMXY_STYLE_ARP, 0, 48000u));
    assert(fmxy_style_route_down(&r, 0, 0, fm7, 4, FMXY_STYLE_BLOCK, 10u, 48000u));
    assert(fmxy_style_route_down(&r, 1, 1, fm7, 4, FMXY_STYLE_BLOCK, 10u, 48000u));
    assert(fmxy_style_route_down(&r, 2, 0, am7, 4, FMXY_STYLE_BLOCK, 10u, 48000u));
    fmxy_style_route_process(&r, 10u);
    assert(nevents == 11u && owned(&r) == 12u);
    assert(fmxy_style_route_active(&r, 0, 60u) == 2u);
    assert(fmxy_style_route_active(&r, 1, 60u) == 1u);
    expect(0, 0, 53, 1); expect(4, 1, 53, 1); expect(8, 0, 57, 1);
    fmxy_style_route_up(&r, 0);
    assert(nevents == 14u && owned(&r) == 8u);
    assert(fmxy_style_route_active(&r, 0, 60u) == 1u);
    assert(fmxy_style_route_active(&r, 1, 60u) == 1u);
    fmxy_style_route_panic_track(&r, 1);
    assert(nevents == 18u && owned(&r) == 4u);
    assert(fmxy_style_route_active(&r, 1, 60u) == 0u);
    assert(fmxy_style_route_active(&r, 0, 60u) == 1u);
    fmxy_style_route_up(&r, 2);
    assert(nevents == 22u && owned(&r) == 0u && r.queue.pending == 0u);

    /* Delayed note ownership survives a track-selection change, and an
     * early release never reports the remaining pending notes as active. */
    nevents = 0;
    assert(fmxy_style_route_down(&r, 3, 2, same, 4, FMXY_STYLE_STRUM, 100u, 48000u));
    assert(fmxy_style_route_down(&r, 4, 3, same, 4, FMXY_STYLE_SPREAD, 100u, 48000u));
    assert(fmxy_style_route_active(&r, 2, 60u) == 0u);
    fmxy_style_route_process(&r, 100u);
    assert(nevents == 2u && owned(&r) == 2u);
    expect(0, 2, 60, 1); expect(1, 3, 60, 1);
    fmxy_style_route_up(&r, 3);
    assert(nevents == 3u && owned(&r) == 1u && r.queue.pending == 3u);
    expect(2, 2, 60, 0);
    fmxy_style_route_process(&r, 2500u);
    assert(nevents == 4u && owned(&r) == 2u);
    expect(3, 3, 64, 1);
    fmxy_style_route_panic(&r);
    assert(nevents == 6u && owned(&r) == 0u && r.queue.pending == 0u);
    fmxy_style_route_process(&r, 100000u);
    assert(nevents == 6u);

    /* All 27 physical keys can keep their original tracks independently.
     * Four separate four-note gates, not one cross-track pitch gate. */
    nevents = 0;
    for (k = 0; k < FMXY_STYLE_KEY_COUNT; ++k)
        assert(fmxy_style_route_down(&r, k, k % 4u, same, 4, FMXY_STYLE_BLOCK, 0u, 48000u));
    fmxy_style_route_process(&r, 0u);
    assert(nevents == 16u && owned(&r) == 108u && r.queue.pending == 0u);
    for (t = 0; t < 4u; ++t)
        assert(fmxy_style_route_active(&r, t, 60u) == (t == 3u ? 6u : 7u));
    fmxy_style_route_panic_track(&r, 0u);
    assert(nevents == 20u && owned(&r) == 80u);
    fmxy_style_route_panic(&r);
    assert(nevents == 32u && owned(&r) == 0u && r.queue.pending == 0u);
    fmxy_style_route_up(&r, 0u);   /* duplicate OFF must not leak */
    assert(nevents == 32u);

    puts("FM-XY STYLE router: independent four-track ownership, STRUM/SPREAD, panic and 27-key limit passed");
    return 0;
}
