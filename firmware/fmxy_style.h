/* SPDX-License-Identifier: GPL-3.0-only
 * FM-XY: fixed-memory staging of chord note-ons.
 *
 * Pure scheduling primitive for a future native STYLE integration. This
 * header is NOT wired to the on-device keyboard path yet.
 * No malloc, no sleeps, no floating point, no flash/storage changes.
 * Times are 32-bit sample counters, with deltas always < INT32_MAX.
 * Call process once per audio block; release/panic cancels pending note-ons.
 * The caller owns note sharing across keys, MIDI and voice allocation.
 */
#ifndef FMXY_STYLE_H
#define FMXY_STYLE_H
#include <stdint.h>

enum {
    FMXY_STYLE_BLOCK,
    FMXY_STYLE_STRUM,
    FMXY_STYLE_SPREAD,
    FMXY_STYLE_ARP,
    FMXY_STYLE_KEY_COUNT = 27,
    FMXY_STYLE_NOTES_PER_KEY = 4
};
typedef void (*fmxy_style_emit_t)(uint8_t key, uint8_t note, uint8_t on, void *context);
typedef struct {
    uint8_t held, count, started;
    uint8_t note[FMXY_STYLE_NOTES_PER_KEY];
    uint32_t due[FMXY_STYLE_NOTES_PER_KEY];
} fmxy_style_key_t;
typedef struct {
    fmxy_style_key_t key[FMXY_STYLE_KEY_COUNT];
    uint16_t pending;
} fmxy_style_queue_t;

static inline void fmxy_style_reset(fmxy_style_queue_t *q)
{
    uint32_t k;
    if (!q) return;
    q->pending = 0;
    for (k = 0; k < FMXY_STYLE_KEY_COUNT; ++k)
        q->key[k] = (fmxy_style_key_t){0};
}

/* Returns 1 for an accepted press. ARP is deliberately delegated to
 * Felucca's existing arpeggiator; it never queues duplicate chord ons. */
static inline int fmxy_style_down(fmxy_style_queue_t *q, uint32_t key,
                                  const uint8_t *notes, uint32_t count,
                                  uint32_t style, uint32_t now,
                                  uint32_t sample_rate)
{
    fmxy_style_key_t *s;
    uint32_t i, j, step = 0;
    if (!q || !notes || key >= FMXY_STYLE_KEY_COUNT ||
        count == 0 || count > FMXY_STYLE_NOTES_PER_KEY ||
        style > FMXY_STYLE_ARP || style == FMXY_STYLE_ARP ||
        sample_rate < 8000u || sample_rate > 192000u ||
        q->key[key].held)
        return 0;
    for (i = 0; i < count; ++i) {
        if (notes[i] > 127u) return 0;
        for (j = 0; j < i; ++j)
            if (notes[j] == notes[i]) return 0;
    }
    if (style == FMXY_STYLE_STRUM) step = sample_rate / 50u; /* 20 ms */
    if (style == FMXY_STYLE_SPREAD) step = sample_rate / 20u; /* 50 ms */
    s = &q->key[key];
    s->held = 1;
    s->count = (uint8_t)count;
    s->started = 0;
    for (i = 0; i < count; ++i) {
        s->note[i] = notes[i];
        s->due[i] = now + i * step;
    }
    q->pending = (uint16_t)(q->pending + count);
    return 1;
}

/* Called at a deterministic block boundary, never inside UI rendering.
 * Constant-time fast path when all note-ons have been dispatched. */
static inline void fmxy_style_process(fmxy_style_queue_t *q, uint32_t now,
                                      fmxy_style_emit_t emit, void *context)
{
    uint32_t k, i;
    if (!q || !emit || !q->pending) return;
    for (k = 0; k < FMXY_STYLE_KEY_COUNT; ++k) {
        fmxy_style_key_t *s = &q->key[k];
        if (!s->held) continue;
        for (i = 0; i < s->count; ++i) {
            uint8_t bit = (uint8_t)(1u << i);
            /* Defined unsigned wrap check; deltas must stay below 2^31. */
            if ((s->started & bit) || ((now - s->due[i]) & UINT32_C(0x80000000)))
                continue;
            s->started |= bit;
            q->pending--;
            emit((uint8_t)k, s->note[i], 1, context);
        }
    }
}

/* Never send OFF for a note whose delayed ON never happened. */
static inline void fmxy_style_up(fmxy_style_queue_t *q, uint32_t key,
                                 fmxy_style_emit_t emit, void *context)
{
    fmxy_style_key_t *s;
    uint32_t i;
    if (!q || !emit || key >= FMXY_STYLE_KEY_COUNT || !q->key[key].held) return;
    s = &q->key[key];
    for (i = 0; i < s->count; ++i) {
        if (s->started & (1u << i))
            emit((uint8_t)key, s->note[i], 0, context);
        else
            q->pending--;
    }
    *s = (fmxy_style_key_t){0};
}

/* Use for panic, transport cleanup and engine replacement. */
static inline void fmxy_style_panic(fmxy_style_queue_t *q,
                                    fmxy_style_emit_t emit, void *context)
{
    uint32_t k;
    if (!q || !emit) return;
    for (k = 0; k < FMXY_STYLE_KEY_COUNT; ++k)
        fmxy_style_up(q, k, emit, context);
}
#endif
