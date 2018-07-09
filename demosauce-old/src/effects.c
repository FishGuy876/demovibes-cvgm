/*
*   demosauce - fancy icecast source client
*
*   this source is published under the GPLv3 license.
*   http://www.gnu.org/licenses/gpl.txt
*   also, this is beerware! you are strongly encouraged to invite the
*   authors of this software to a beer when you happen to meet them.
*   copyright MMXIII by maep
*/

#include <math.h>
#include <string.h>
#include <limits.h>
#include <assert.h>
#include <samplerate.h>
#include "effects.h"
#include "log.h"

float db_to_amp(float db)
{
    return powf(10, db / 20);
}

float amp_to_db(float amp)
{
    return log10f(amp) * 20;
}

//-----------------------------------------------------------------------------

struct fx_resampler {
    int         channels;
    double      ratio;
    SRC_STATE*  state[MAX_CHANNELS];
};


void* fx_resample_init(int channels, int sr_from, int sr_to)
{
    assert(channels >= 1 && channels <= MAX_CHANNELS);
    int err = 0;
    struct fx_resampler* r = util_malloc(sizeof(struct fx_resampler));
    r->channels = channels;
    r->ratio    = (double)sr_to / sr_from;
    if (!src_is_valid_ratio(r->ratio))
        goto error;
    for (int ch = 0; ch < channels; ch++) {
        r->state[ch] = src_new(SRC_SINC_FASTEST, 1, &err);
        if (err)
            goto error;
    }
    LOG_DEBUG("[resample] init, %d channels, %f ratio", channels, r->ratio);
    return r;

error:
    LOG_ERROR("[resample] init failed (%s)", src_strerror(err));
    fx_resample_free(r);
    return NULL;
}

void fx_resample_free(void* handle)
{
    if (!handle)
        return;
    struct fx_resampler* r = handle;
    for (int ch = 0; ch < r->channels; ch++)
        src_delete(r->state[ch]);
    util_free(r);
}

void fx_resample(void* handle, struct stream* s1, struct stream* s2)
{
    struct fx_resampler* r = handle;
    // TODO deal with leftover internal samples
    s2->end_of_stream = s1->end_of_stream; 
    stream_resize(s2, s1->frames * r->ratio + 1, s1->channels);
    for (int ch = 0; ch < r->channels; ch++) {
        SRC_DATA src = {
            s1->buffer[ch],     // data_in
            s2->buffer[ch],     // data_out
            s1->frames,         // input_frames
            s2->max_frames,     // output_frames
            0,                  // input_frames_used
            0,                  // output_frames_gen
            s1->end_of_stream,  // end_of_input
            r->ratio            // src_ratio
        };
        int err = src_process(r->state[ch], &src);
        if (err)
            LOG_ERROR("[resample] error (%s)", src_strerror(err));
        assert(src.input_frames_used == s1->frames);
        s2->frames = src.output_frames_gen;
    }
}

//-----------------------------------------------------------------------------

void fx_map(struct stream* s, int channels)
{
    // only handles 1 and 2, not MAX_CHANNELS
    assert(channels >= 1 && channels <= 2);
    if (s->channels == 1 && channels == 2) {
        stream_resize(s, s->frames, 2);
        memmove(s->buffer[1], s->buffer[0], s->frames * sizeof (float));
    } else if (s->channels == 2 && channels == 1) {
        s->channels = 1;
        float* left = s->buffer[0];
        float* right = s->buffer[1];
        for (int i = 0; i < s->frames; i++) 
            left[i] = (left[i] + right[i]) / 2;
    }
}

//-----------------------------------------------------------------------------

void fx_fade_init(struct fx_fade* fx, long start_frame, long end_frame, float begin_amp, float end_amp)
{
    if (start_frame >= end_frame || begin_amp < 0 || end_amp < 0) 
        return;
    fx->start_frame = start_frame;
    fx->end_frame   = end_frame;
    fx->current_frame = 0;
    fx->amp         = begin_amp;
    fx->amp_inc     = (end_amp - begin_amp) / (end_frame - start_frame);
}

void fx_fade(struct fx_fade* fx, struct stream* s)
{
    long enda = (fx->start_frame < fx->current_frame) ? 0 :
        MIN(s->frames, fx->start_frame - fx->current_frame);
    long endb = (fx->end_frame < fx->current_frame) ? 0 :
        MIN(s->frames, fx->end_frame - fx->current_frame);
    fx->current_frame += s->frames;
    if (fx->amp == 1 && (enda >= s->frames || endb == 0)) 
        return; // nothing to do; amp mignt not be exacly on target, so proximity check would be better
    float a = fx->amp;
    for (int ch = 0; ch < s->channels; ch++) {
        float* out = s->buffer[ch];
        for (int i = 0; i < enda; i++) 
            out[i] *= a;
        for (int i = 0; i < endb; i++, a += fx->amp_inc) 
            out[i] *= a;
        for (int i = 0; i < s->frames; i++) 
            *out++ *= a;
    }
    fx->amp += fx->amp_inc * (endb - enda);
}

//-----------------------------------------------------------------------------

void fx_gain(struct stream* s, float amp)
{
    for (int ch = 0; ch < s->channels; ch++) {
        float* out = s->buffer[ch];
        for (int i = 0; i < s->frames; i++) 
            out[i] *= amp;
    }
}

//-----------------------------------------------------------------------------

void fx_mix_init(struct fx_mix* fx, float llamp, float lramp, float rramp, float rlamp)
{
    fx->llamp = llamp;
    fx->lramp = lramp;
    fx->rramp = rramp;
    fx->rlamp = rlamp;
}

void fx_mix(struct fx_mix* fx, struct stream* s)
{
    if (s->channels != 2)
        return;
    float* left = s->buffer[0];
    float* right = s->buffer[1];
    for (int i = 0; i < s->frames; i++) {
        float new_left = fx->llamp * left[i] + fx->lramp * right[i];
        float new_right = fx->rramp * right[i] + fx->rlamp * left[i];
        left[i] = new_left;
        right[i] = new_right;
    }
}

//-----------------------------------------------------------------------------

void fx_clip(struct stream* s)
{
    for (int ch = 0; ch < s->channels; ch++) {
        float* buf = s->buffer[ch];
        for (int i = 0; i < s->frames; i++)
            buf[i] = CLAMP(-1.0f, buf[i], 1.0f);
    }
}

//-----------------------------------------------------------------------------

static void ci16i(const void** vin, float** out, int len, int channels)
{
    const int16_t* in = vin[0]; 
    float* lout = out[0];
    if (channels == 1) {
        for (int i = 0; i < len; i++) 
            lout[i] = (float)in[i] / -INT16_MIN;
    } else { // channels == 2
        float* rout = out[1];
        for (int i = 0; i < len; i++) {
            lout[i] = (float)in[i * 2] / -INT16_MIN;
            rout[i] = (float)in[i * 2 + 1] / -INT16_MIN;
        }
    }
}

static void ci16p(const void** vin, float** out, int len, int channels)
{
    for (int ch = 0; ch < channels; ch++) {
        const int16_t* in = vin[ch];
        float* lout = out[ch];
        for (int i = 0; i < len; i++) 
            lout[i] = (float)in[i] / -INT16_MIN;
    }
}

static void cf32i(const void** vin, float** out, int len, int channels)
{
    if (channels == 1) {
        memmove(out[0], vin[0], len * sizeof(float));
    } else { // channels == 2
        const float* in = vin[0];
        float* lout = out[0];
        float* rout = out[1];
        for (int i = 0; i < len; i++) {
            lout[i] = in[i * 2];
            rout[i] = in[i * 2 + 1];
        }
    }
}

static void cf32p(const void** vin, float** out, int len, int channels)
{
    for (int ch = 0; ch < channels; ch++) 
        memmove(out[ch], vin[ch], len * sizeof(float));
}

static void (*convert[])(const void**, float**, int, int) = {ci16i, ci16p, cf32i, cf32p}; 

void fx_convert_to_float(void** in, float** out, int type, int size, int channels)
{
    // some converter functions only support 2, not MAX_CHANNELS
    assert(channels >= 1 && channels <= 2); 
    assert(type >= SF_INT16I && type <= SF_FLOAT32P);
    convert[type]((const void**)in, out, size, channels);
}
