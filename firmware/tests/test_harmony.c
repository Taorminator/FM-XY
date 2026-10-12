/* SPDX-License-Identifier: GPL-3.0-only */
#include "../fmxy_harmony.h"
#include <assert.h>
#include <stdio.h>
int main(void){
  fmxy_hint_t a[2]; unsigned tests=0;
  for(unsigned m=0;m<2;m++)for(unsigned k=0;k<12;k++)for(unsigned r=0;r<12;r++){
    unsigned saved=r;
    fmxy_suggest((uint8_t)r,(uint8_t)k,(uint8_t)m,a);
    assert(r==saved);
    for(int i=0;i<2;i++){
      assert(a[i].root<12 && a[i].quality<=FMXY_DIM);
      ++tests;
    }
  }
  fmxy_suggest(0,0,1,a);
  assert(a[0].root==5 && a[0].quality==FMXY_MIN7);
  assert(a[1].root==8 && a[1].quality==FMXY_MAJ7);
  printf("FM-XY harmony: %u cases passed\n",tests);
  return 0;
}
