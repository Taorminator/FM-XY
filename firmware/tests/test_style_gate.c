/* SPDX-License-Identifier: GPL-3.0-only
 * Host tests for common-pitch ownership during timed chord attacks.
 * This is a staging layer only, not yet connected to live MIDI/recording.
 */
#include "../fmxy_style.h"
#include "../fmxy_style_gate.h"
#include <assert.h>
#include <stdio.h>

typedef struct { uint8_t note, on; } event_t;
static event_t log_event[256];
static unsigned logged;
static void note_emit(uint8_t note, uint8_t on, void *ctx)
{
    (void)ctx;
    assert(logged < sizeof log_event / sizeof log_event[0]);
    log_event[logged++] = (event_t){note, on};
}
static void expect(unsigned at, uint8_t note, uint8_t on)
{
    assert(at < logged);
    assert(log_event[at].note == note && log_event[at].on == on);
}
static unsigned refs_total(const fmxy_style_gate_t *g)
{
    unsigned i, total = 0;
    for (i = 0; i < 128u; ++i) total += g->references[i];
    return total;
}
int main(void)
{
    fmxy_style_queue_t q = {0};
    fmxy_style_gate_t g = {0};
    static const uint8_t fm7[4] = {53, 56, 60, 63};
    static const uint8_t am7[4] = {57, 60, 64, 67};
    static const uint8_t same[4] = {60, 64, 67, 71};
    unsigned k;

    fmxy_style_gate_init(&g, note_emit, 0);
    fmxy_style_reset(&q);
    assert(sizeof q + sizeof g < 1024u);
    assert(fmxy_style_down(&q, 0, fm7, 4, FMXY_STYLE_BLOCK, 100u, 48000u));
    assert(fmxy_style_down(&q, 1, am7, 4, FMXY_STYLE_BLOCK, 100u, 48000u));
    fmxy_style_process(&q, 100u, fmxy_style_gate_event, &g);
    assert(logged == 7u && refs_total(&g) == 8u && g.references[60] == 2u);
    expect(0, 53, 1); expect(1, 56, 1); expect(2, 60, 1);
    expect(3, 63, 1); expect(4, 57, 1); expect(5, 64, 1);
    expect(6, 67, 1);
    fmxy_style_up(&q, 0, fmxy_style_gate_event, &g);
    assert(logged == 10u && refs_total(&g) == 4u && g.references[60] == 1u);
    expect(7, 53, 0); expect(8, 56, 0); expect(9, 63, 0);
    fmxy_style_up(&q, 1, fmxy_style_gate_event, &g);
    assert(logged == 14u && refs_total(&g) == 0u);
    expect(10, 57, 0); expect(11, 60, 0); expect(12, 64, 0); expect(13, 67, 0);

    /* Shared pitch starts at different stages of a STRUM. A partial
     * release may not silence the other owner or sound unheard notes. */
    logged = 0;
    assert(fmxy_style_down(&q, 0, fm7, 4, FMXY_STYLE_STRUM, 0u, 48000u));
    assert(fmxy_style_down(&q, 1, am7, 4, FMXY_STYLE_STRUM, 0u, 48000u));
    fmxy_style_process(&q, 0u, fmxy_style_gate_event, &g);
    assert(logged == 2u && refs_total(&g) == 2u);
    fmxy_style_process(&q, 960u, fmxy_style_gate_event, &g);
    assert(logged == 4u && g.references[60] == 1u);
    fmxy_style_process(&q, 1920u, fmxy_style_gate_event, &g);
    assert(logged == 5u && g.references[60] == 2u);
    fmxy_style_up(&q, 0, fmxy_style_gate_event, &g);
    assert(g.references[60] == 1u && refs_total(&g) == 3u);
    fmxy_style_panic(&q, fmxy_style_gate_event, &g);
    assert(q.pending == 0u && refs_total(&g) == 0u);
    fmxy_style_process(&q, 100000u, fmxy_style_gate_event, &g);
    assert(refs_total(&g) == 0u);

    /* At most 27 physical keys can own one pitch: 4 actual note-ons,
     * 4 actual note-offs, even during maximum overlapping chord attacks. */
    logged = 0;
    for (k = 0; k < 27u; ++k)
        assert(fmxy_style_down(&q, k, same, 4, FMXY_STYLE_BLOCK, 3u, 48000u));
    fmxy_style_process(&q, 3u, fmxy_style_gate_event, &g);
    assert(logged == 4u && refs_total(&g) == 108u);
    for (k = 0; k < 4u; ++k) assert(g.references[same[k]] == 27u);
    fmxy_style_panic(&q, fmxy_style_gate_event, &g);
    assert(logged == 8u && q.pending == 0u && refs_total(&g) == 0u);
    fmxy_style_gate_event(0, 60, 0, &g); /* stray OFF cannot underflow */
    assert(logged == 8u && refs_total(&g) == 0u);
    puts("FM-XY STYLE gate: shared pitch, staggered attack, cancellation, panic and 27-key ownership passed");
    return 0;
}
