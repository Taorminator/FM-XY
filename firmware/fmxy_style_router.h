/* SPDX-License-Identifier: GPL-3.0-only
 * FM-XY four-track STYLE router (host staging, NOT connected to audio).
 *
 * FM1 has 27 physical keys but four independent tracks. A key keeps the
 * track selected on key-down even if selection changes while it is held.
 * Each track owns its own pitch gate, so equal pitches on different
 * tracks produce independent note-on/note-off pairs. No allocations.
 *
 * IMPORTANT: callers must share external MIDI ownership with Felucca
 * before routing these events into input_on/input_off. This adapter
 * does not yet handle that external MIDI arbitration or recording.
 */
#ifndef FMXY_STYLE_ROUTER_H
#define FMXY_STYLE_ROUTER_H
#include "fmxy_style.h"
#include "fmxy_style_gate.h"
#include <stdint.h>

enum { FMXY_STYLE_TRACK_COUNT = 4 };

typedef void (*fmxy_style_route_emit_t)(uint8_t track, uint8_t note,
                                         uint8_t on, void *ctx);
typedef struct fmxy_style_router fmxy_style_router_t;
typedef struct {
    fmxy_style_router_t *router;
    uint8_t track;
} fmxy_style_channel_t;
struct fmxy_style_router {
    fmxy_style_queue_t queue;
    fmxy_style_gate_t gate[FMXY_STYLE_TRACK_COUNT];
    fmxy_style_channel_t channel[FMXY_STYLE_TRACK_COUNT];
    uint8_t key_track[FMXY_STYLE_KEY_COUNT];
    fmxy_style_route_emit_t emit;
    void *ctx;
};

static inline void fmxy_style_route_note(uint8_t note, uint8_t on, void *ctx)
{
    fmxy_style_channel_t *ch = (fmxy_style_channel_t *)ctx;
    if (ch && ch->router && ch->router->emit)
        ch->router->emit(ch->track, note, on, ch->router->ctx);
}

static inline void fmxy_style_route_event(uint8_t key, uint8_t note,
                                           uint8_t on, void *ctx)
{
    fmxy_style_router_t *r = (fmxy_style_router_t *)ctx;
    if (!r || key >= FMXY_STYLE_KEY_COUNT ||
        r->key_track[key] >= FMXY_STYLE_TRACK_COUNT)
        return;
    fmxy_style_gate_event(key, note, on,
                          &r->gate[r->key_track[key]]);
}

/* Call at boot, never in the middle of sounding notes. During playback
 * use fmxy_style_route_panic before resetting any state. */
static inline void fmxy_style_route_init(fmxy_style_router_t *r,
                                         fmxy_style_route_emit_t emit,
                                         void *ctx)
{
    uint32_t t, k;
    if (!r) return;
    fmxy_style_reset(&r->queue);
    r->emit = emit;
    r->ctx = ctx;
    for (k = 0; k < FMXY_STYLE_KEY_COUNT; ++k)
        r->key_track[k] = 0;
    for (t = 0; t < FMXY_STYLE_TRACK_COUNT; ++t) {
        r->channel[t].router = r;
        r->channel[t].track = (uint8_t)t;
        fmxy_style_gate_init(&r->gate[t], fmxy_style_route_note,
                             &r->channel[t]);
    }
}

static inline int fmxy_style_route_down(fmxy_style_router_t *r,
                                        uint32_t key, uint32_t track,
                                        const uint8_t *notes, uint32_t count,
                                        uint32_t style, uint32_t now,
                                        uint32_t sample_rate)
{
    if (!r || !r->emit || track >= FMXY_STYLE_TRACK_COUNT ||
        key >= FMXY_STYLE_KEY_COUNT)
        return 0;
    if (!fmxy_style_down(&r->queue, key, notes, count, style, now, sample_rate))
        return 0;
    r->key_track[key] = (uint8_t)track;
    return 1;
}

static inline void fmxy_style_route_process(fmxy_style_router_t *r,
                                            uint32_t now)
{
    if (r)
        fmxy_style_process(&r->queue, now, fmxy_style_route_event, r);
}

static inline void fmxy_style_route_up(fmxy_style_router_t *r, uint32_t key)
{
    if (r)
        fmxy_style_up(&r->queue, key, fmxy_style_route_event, r);
}

/* Engine/preset replacement may silence only one track. The other
 * track's keys continue to own and release their notes normally. */
static inline void fmxy_style_route_panic_track(fmxy_style_router_t *r,
                                                 uint32_t track)
{
    uint32_t key;
    if (!r || track >= FMXY_STYLE_TRACK_COUNT) return;
    for (key = 0; key < FMXY_STYLE_KEY_COUNT; ++key)
        if (r->key_track[key] == track && r->queue.key[key].held)
            fmxy_style_route_up(r, key);
}

static inline void fmxy_style_route_panic(fmxy_style_router_t *r)
{
    if (r)
        fmxy_style_panic(&r->queue, fmxy_style_route_event, r);
}

/* Only STYLE-owned, actually started notes count here. Pending delayed
 * notes must not make external MIDI think a pitch is already sounding. */
static inline uint32_t fmxy_style_route_active(const fmxy_style_router_t *r,
                                                uint32_t track, uint32_t note)
{
    return r && track < FMXY_STYLE_TRACK_COUNT && note < 128u
           ? r->gate[track].references[note] : 0u;
}
#endif
