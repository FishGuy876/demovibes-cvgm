/*
*   libReplayGain, based on mp3gain 1.5.1
*   LGPL 2.1
*   http://www.gnu.org/licenses/old-licenses/lgpl-2.1.txt
*/

#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <assert.h>
#include "replay_gain.h"
#include "gain_analysis.h"

struct rg_context {
    struct rg_state state;
    int             samplerate;
    int             type;
    int             channels;
    int             interleaved;
    void*           buffer;
    int             buffer_size;
};

struct rg_context* rg_new(int samplerate, int sampletype, int channels, int interleaved)
{
    if (channels != 1 && channels != 2)
        return NULL;

    struct rg_context* ctx = malloc(sizeof(struct rg_context));
    memset(ctx, 0, sizeof(struct rg_context));
    
    int err = InitGainAnalysis(&ctx->state, samplerate);
    if (err == INIT_GAIN_ANALYSIS_ERROR) {
        free(ctx);
        return NULL;
    }
    ctx->samplerate     = samplerate;
    ctx->type           = sampletype;
    ctx->channels       = channels;
    ctx->interleaved    = interleaved;
    return ctx;
}

void rg_free(struct rg_context* ctx)
{
    free(ctx->buffer);
    free(ctx);
}

static void convert_f32(struct rg_context* ctx, void* data, int frames)
{
    float** buffer = data;
    if (ctx->channels == 2 && ctx->interleaved) {
        const float* in = buffer[0];
        Float_t* outl = (Float_t*)ctx->buffer;
        Float_t* outr = (Float_t*)ctx->buffer + ctx->buffer_size / 2;
        for (int i = 0; i < frames; i++) {
            outl[i] = (Float_t)in[i * 2]     * 0x7fff;
            outr[i] = (Float_t)in[i * 2 + 1] * 0x7fff;
        }
    } else {
        for (int ch = 0; ch < ctx->channels; ch++) {
            const float* in = buffer[ch];
            Float_t* out = (Float_t*)ctx->buffer + (frames * ch);
            for (int i = 0; i < frames; i++)
               out[i] = (Float_t)in[i] * 0x7fff;
        }
    }
}

static void convert_s32(struct rg_context* ctx, void* data, int frames)
{
    static const Float_t scaling = (Float_t)0x7fff / 0x7fffffff;
    int32_t** buffer = data;
    if (ctx->channels == 2 && ctx->interleaved) {
        const int32_t* in = buffer[0];
        Float_t* outl = (Float_t*)ctx->buffer;
        Float_t* outr = (Float_t*)ctx->buffer + ctx->buffer_size / 2;
        for (int i = 0; i < frames; i++) {
            outl[i] = (Float_t)in[i * 2]     * scaling;
            outr[i] = (Float_t)in[i * 2 + 1] * scaling;
        }
    } else {
        for (int ch = 0; ch < ctx->channels; ch++) {
            const int32_t* in = buffer[ch];
            Float_t* out = (Float_t*)ctx->buffer + (frames * ch);
            for (int i = 0; i < frames; i++)
               out[i] = (Float_t)in[i] * scaling;
        }
    }
}

static void convert_s16(struct rg_context* ctx, void* data, int frames)
{
    int16_t** buffer = data;
    if (ctx->channels == 2 && ctx->interleaved) {
        const int16_t* in = buffer[0];
        Float_t* outl = (Float_t*)ctx->buffer;
        Float_t* outr = (Float_t*)ctx->buffer + ctx->buffer_size / 2;
        for (int i = 0; i < frames; i++) {
            outl[i] = (Float_t)in[i * 2];
            outr[i] = (Float_t)in[i * 2 + 1];
        }
    } else {
        for (int ch = 0; ch < ctx->channels; ch++) {
            const int16_t* in = buffer[ch];
            Float_t* out = (Float_t*)ctx->buffer + (frames * ch);
            for (int i = 0; i < frames; i++)
               out[i] = (Float_t)in[i];
        }
    }
}

void rg_analyze(struct rg_context* ctx, void* data, int frames)
{
    assert(ctx);
    assert(data);
    assert(frames % 2 == 0); // having odd number of frames sometimes causes odd behaviour

    int need_size = frames * sizeof(Float_t) * ctx->channels;
    if (ctx->buffer_size < need_size)
        ctx->buffer = realloc(ctx->buffer, need_size);

    switch (ctx->type) {
    case RG_SIGNED16:
        convert_s16(ctx, data, frames);
        break;
    case RG_SIGNED32:
        convert_s32(ctx, data, frames);
        break;
    case RG_FLOAT32:
        convert_f32(ctx, data, frames);
        break;
    default:
        assert(!"unexpected sample type");
    }

    Float_t* lbuf = ctx->buffer;
    Float_t* rbuf = lbuf + frames;
    AnalyzeSamples(&ctx->state, lbuf, rbuf, frames, ctx->channels);
}

float rg_title_gain(struct rg_context* ctx)
{
    float gain = GetTitleGain(&ctx->state);
    return gain == GAIN_NOT_ENOUGH_SAMPLES ? 0 : gain;
}

float rg_album_gain(struct rg_context* ctx)
{
    float gain = GetAlbumGain(&ctx->state);
    return gain == GAIN_NOT_ENOUGH_SAMPLES ? 0 : gain;
}

