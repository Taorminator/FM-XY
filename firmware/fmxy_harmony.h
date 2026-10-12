/* SPDX-License-Identifier: GPL-3.0-only
 * FM-XY by Middle Age Engineering.
 * Pure harmony-suggestion prototype for later Felucca integration.
 * No heap allocation, no state mutation, no audio scheduling.
 */
#ifndef FMXY_HARMONY_H
#define FMXY_HARMONY_H
#include <stdint.h>
typedef struct { uint8_t root; uint8_t quality; uint8_t mood; } fmxy_hint_t;
enum { FMXY_MAJ7, FMXY_MIN7, FMXY_DOM7, FMXY_DIM };
enum { FMXY_ANSWER, FMXY_LIFT, FMXY_RESOLVE, FMXY_PUSH, FMXY_OPEN, FMXY_WARM };
static const uint8_t FMXY_MAJ_STEPS[7]={0,2,4,5,7,9,11};
static const uint8_t FMXY_MIN_STEPS[7]={0,2,3,5,7,8,10};
static const uint8_t FMXY_MAJ_Q[7]={FMXY_MAJ7,FMXY_MIN7,FMXY_MIN7,FMXY_MAJ7,FMXY_DOM7,FMXY_MIN7,FMXY_DIM};
static const uint8_t FMXY_MIN_Q[7]={FMXY_MIN7,FMXY_DIM,FMXY_MAJ7,FMXY_MIN7,FMXY_MIN7,FMXY_MAJ7,FMXY_DOM7};
static const uint8_t FMXY_MAJ_NEXT[7][2]={{4,5},{4,0},{5,3},{4,0},{0,5},{3,1},{0,2}};
static const uint8_t FMXY_MIN_NEXT[7][2]={{3,5},{4,0},{6,5},{6,0},{0,5},{2,6},{0,2}};
static inline uint8_t fmxy_degree(uint8_t root,uint8_t key,uint8_t minor) {
  const uint8_t *steps=minor?FMXY_MIN_STEPS:FMXY_MAJ_STEPS;
  uint8_t relative=(uint8_t)((root+12u-key)%12u),best=0,distance=12,i;
  for(i=0;i<7;i++) {
    uint8_t diff=(uint8_t)((relative+12u-steps[i])%12u);
    uint8_t dist=diff>6u?(uint8_t)(12u-diff):diff;
    if(dist<distance){distance=dist;best=i;}
  }
  return best;
}
static inline void fmxy_suggest(uint8_t current_root,uint8_t key,uint8_t minor,fmxy_hint_t out[2]) {
  const uint8_t i=fmxy_degree(current_root,key,minor);
  const uint8_t (*next)[2]=minor?FMXY_MIN_NEXT:FMXY_MAJ_NEXT;
  const uint8_t *steps=minor?FMXY_MIN_STEPS:FMXY_MAJ_STEPS;
  const uint8_t *quality=minor?FMXY_MIN_Q:FMXY_MAJ_Q;
  uint8_t a=next[i][0],b=next[i][1];
  out[0]=(fmxy_hint_t){(uint8_t)((key+steps[a])%12u),quality[a],FMXY_ANSWER};
  out[1]=(fmxy_hint_t){(uint8_t)((key+steps[b])%12u),quality[b],FMXY_LIFT};
}
#endif
