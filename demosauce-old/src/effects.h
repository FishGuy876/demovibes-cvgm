/*
*   demosauce - fancy icecast source client
*
*   this source is published under the GPLv3 license.
*   http://www.gnu.org/licenses/gpl.txt
*   also, this is beerware! you are strongly encouraged to invite the
*   authors of this software to a beer when you happen to meet them.
*   copyright MMXIII by maep
*/

#ifndef EFFECTS_H
#define EFFECTS_H

#include <stdint.h>
#include "util.h"

struct fx_fade {
    long    start_frame;
    long    end_frame;
    long    current_frame;
    float   amp;
    float   amp_inc;
};

// left = left*llAmp + left*lrAmp; rigt = right*rrAmp + left*rlAmp;
struct fx_mix {
    float   llamp;
    float   lramp;
    float   rramp;
    float   rlamp;
};

float   db_to_amp(float db);
float   amp_to_db(float amp);

void    fx_gain(struct stream* s, float gain);

void    fx_clip(struct stream* s);

void    fx_map(struct stream* s, int channels);

void*   fx_resample_init(int channels, int sr_from, int sr_to);
void    fx_resample_free(void* handle);
void    fx_resample(void* handle, struct stream* s1, struct stream* s2);

void    fx_fade_init(struct fx_fade* fx, long start_frame, long end_frame, float begin_amp, float end_amp);
void    fx_fade(struct fx_fade* fx, struct stream* s);

void    fx_mix_init(struct fx_mix* fx, float llamp, float lramp, float rramp, float rlamp);
void    fx_mix(struct fx_mix* fx, struct stream* s);

void    fx_convert_to_float(void** in, float** out, int type, int size, int channels);

#endif // EFFECTS_H

