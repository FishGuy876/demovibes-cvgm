#include <libswresample/swresample.h>
#include <libavcodec/avcodec.h>
#include <libavutil/opt.h>
#include "stream.h"
#include "all.h"

static_assert((int)STREAM_FMT_S16 == (int)AV_SAMPLE_FMT_S16, "constant mismatch");
static_assert((int)STREAM_FMT_FLT == (int)AV_SAMPLE_FMT_FLT, "constant mismatch");

void stream_resize(struct stream* s, int frames, int channels)
{
    assert(channels > 0 && channels <= STREAM_MAX_CHANNELS);
    if (frames <= s->max_frames && channels == s->channels)
        return;
    if (frames > s->max_frames)
        log_debug("[stream] %p resize to %d frames", s, frames);
    s->channels = channels;
    s->max_frames = imax(frames, s->max_frames);
    for (int ch = 0; ch < channels; ch++)
        s->buffer[ch] = util_realign(s->buffer[ch], s->max_frames * sizeof(float), STREAM_ALIGN);
}

void stream_free(struct stream* s)
{
    for (int i = 0; i < STREAM_MAX_CHANNELS; i++)
        free(s->buffer[i]);
    memset(s, 0, sizeof *s);
}

void stream_append(struct stream* s, struct stream* source, int frames)
{
    assert(source->channels > 0 && source->channels <= STREAM_MAX_CHANNELS);
    frames = iclamp(0, frames, source->frames);
    s->frames += frames;
    stream_resize(s, s->frames, source->channels);
    for (int ch = 0; ch < s->channels; ch++)
        memmove(s->buffer[ch], source->buffer[ch], frames * sizeof(float));
}

void stream_drop(struct stream* s, int frames)
{
    frames = iclamp(0, frames, s->frames);
    s->frames -= frames;
    if (s->frames > 0)
        for (int ch = 0; ch < s->channels; ch++)
            memmove(s->buffer[ch], s->buffer[ch] + frames, s->frames * sizeof(float));
}

void stream_zero(struct stream* s, int offset, int frames)
{
    frames = iclamp(0, frames, imax(s->max_frames - offset, 0));
    for (int ch = 0; ch < s->channels; ch++)
        memset(s->buffer[ch] + offset, 0, frames * sizeof(float));
    s->frames = offset + frames;
}

void stream_fade_init(struct fadefx* fx, long start_frame, long end_frame, double begin_amp, double end_amp)
{
    if (start_frame >= end_frame || begin_amp < 0 || end_amp < 0)
        return;
    fx->start_frame = start_frame;
    fx->end_frame   = end_frame;
    fx->current_frame = 0;
    fx->amp         = begin_amp;
    fx->amp_inc     = (end_amp - begin_amp) / (end_frame - start_frame);
}

void stream_fade(struct stream* s, struct fadefx* fx)
{
    int64_t enda = (fx->start_frame < fx->current_frame) ? 0 :
        imin(s->frames, fx->start_frame - fx->current_frame);
    int64_t endb = (fx->end_frame < fx->current_frame) ? 0 :
        imin(s->frames, fx->end_frame - fx->current_frame);
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

void stream_gain(struct stream* s, double amp)
{
    for (int ch = 0; ch < s->channels; ch++) {
        float* out = s->buffer[ch];
        for (int i = 0; i < s->frames; i++)
            out[i] *= amp;
    }
}

// passive downmix. should only be used with uncorrelated channels.s
void stream_mix(struct stream* s, double ratio)
{
    assert(s->channels == 1 || s->channels == 2);
    if (s->channels == 1)
        return;
    double r = sqrt(1 - ratio); // energy preserving, but can clip theoretically
    float* left = s->buffer[0];
    float* right = s->buffer[1];
    for (int i = 0; i < s->frames; i++) {
        float new_left = ratio * left[i] + r * right[i];
        float new_right = ratio * right[i] + r * left[i];
        left[i] = new_left;
        right[i] = new_right;
    }
}

SwrContext* stream_swr_new_src(int src_channels, int src_samplerate, int src_format,
                                   int dst_channels, int dst_samplerate)
{
    SwrContext* swr = swr_alloc_set_opts(NULL, av_get_default_channel_layout(dst_channels),
                                         AV_SAMPLE_FMT_FLTP, dst_samplerate,
                                         av_get_default_channel_layout(src_channels),
                                         src_format, src_samplerate, 0, NULL);
    return swr_init(swr) ? swr_free(&swr), NULL : swr;
}

SwrContext* stream_swr_new_dst(int src_channels, int src_samplerate,
                                   int dst_channels, int dst_samplerate, int dst_format)
{
    SwrContext* swr = swr_alloc_set_opts(NULL, av_get_default_channel_layout(dst_channels),
                                         dst_format, dst_samplerate,
                                         av_get_default_channel_layout(src_channels),
                                         AV_SAMPLE_FMT_FLTP, src_samplerate, 0, NULL);
    return swr_init(swr) ? swr_free(&swr), NULL : swr;
}

void stream_swr_free(SwrContext* swr)
{
    swr_free(&swr);
}

// TODO compensate for delay
int stream_swr_frames(SwrContext* swr, int frames)
{
    int64_t inrate = 0, outrate = 0;
    assert(av_opt_get_int(swr, "in_sample_rate", 0, &inrate) >= 0);
    assert(av_opt_get_int(swr, "out_sample_rate", 0, &outrate) >= 0);
    return av_rescale_rnd(frames, inrate, outrate, AV_ROUND_UP);
}

// TODO feed zeroes at end
void stream_append_convert(struct stream* s, SwrContext* swr, const uint8_t** source, int frames)
{
    int64_t inrate = 0, outrate = 0, layout = 0;

    assert(av_opt_get_int(swr, "in_sample_rate", 0, &inrate) >= 0);
    assert(av_opt_get_int(swr, "out_sample_rate", 0, &outrate) >= 0);
    assert(av_opt_get_int(swr, "out_channel_layout", 0, &layout) >= 0);

    int channels = (int)av_get_channel_layout_nb_channels(layout);
    assert(channels > 0 && channels <= STREAM_MAX_CHANNELS);
    int maxframes = av_rescale_rnd(frames, outrate, inrate, AV_ROUND_UP);// + swr_get_delay(swr, inrate);
    stream_resize(s, s->frames + maxframes, channels);

    float* outbuf[STREAM_MAX_CHANNELS] = {0};
    for (int ch = 0; ch < STREAM_MAX_CHANNELS; ch++)
        outbuf[ch] = s->buffer[ch] + s->frames;

    int outframes = swr_convert(swr, (uint8_t**)outbuf, maxframes, source, frames);

    if (outframes < 0) {
        log_warn("[stream] convert error");
        stream_zero(s, s->frames, maxframes);
    } else {
        s->frames += outframes;
    }
}

// TODO: add check, etc... see append_convert
void stream_read_convert(struct stream* s, SwrContext* swr, uint8_t** dest, int frames)
{
    int outframes = swr_convert(swr, dest, frames, (const uint8_t**)s->buffer, s->frames);
    if (outframes < frames)
        log_warn("[stream] convert error");
}
