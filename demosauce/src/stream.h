#ifndef STREAM_H
#define STREAM_H

#include "all.h"

// don't depend on avresample.h
typedef struct SwrContext SwrContext;

enum {
    STREAM_MAX_CHANNELS = 2,
    STREAM_ALIGN        = 32,
    STREAM_FMT_S16      = 1, // mirrors samplefmt.h
    STREAM_FMT_FLT      = 3
};

struct stream {
    int     frames;                         // number of samples in the buffer, same for mono and stereo
    int     max_frames;                     // capacity of allocated buffers
    int     channels;                       // 1 mono, 2 stereo
    bool    end_of_stream;                  // is set when stream ended
    float*  buffer[STREAM_MAX_CHANNELS];    // buffer[0] left channel, buffer[1] right channel
};

struct fadefx {
    int64_t start_frame;
    int64_t end_frame;
    int64_t current_frame;
    double  amp;
    double  amp_inc;
};

/*  stream_resize
 *      resize <stream> to hold at least <frames> frames in <channels> channels. if <frames> is
 *      smaller than s->max_frames this function has no effect, unless <channels> changes number
 *      of channels.
 *  stream_free
 *      frees the buffers and set all members of <stream> to zero.
 *      stream_append
 *      append <frames> frames of <source> to stream. <source> will not be changed.
 *      <stream> might be increased to hold all data.
 *  stream_drop
 *      remove <frames> frames from the beginning of the <stream>.
 *  stream_zero
 *      set <frames> frames to zero, starting with <offset> frames.
 */
void stream_resize(struct stream* s, int frames, int channels);
void stream_free(struct stream* s);
void stream_append(struct stream* s, struct stream* source, int frames);
void stream_drop(struct stream* s, int frames);
void stream_zero(struct stream* s, int offset, int frames);
void stream_gain(struct stream* s, double gain);
void stream_mix(struct stream* s, double ratio);
void stream_fade_init(struct fadefx* fx, long start_frame, long end_frame, double begin_amp, double end_amp);
void stream_fade(struct stream* s, struct fadefx* fx);

/*  stream_append_convert
 *      append <frames> frames of source to stream and convert using <swr>,
 *      format of <source> depends on swr. stream internal format is planar float.
 */
SwrContext* stream_swr_new_src(int src_channels, int src_samplerate, int src_format,
                               int dst_channels, int dst_samplerate);
SwrContext* stream_swr_new_dst(int src_channels, int src_samplerate,
                               int dst_channels, int dst_samplerate, int dst_format);
int  stream_swr_frames(SwrContext* swr, int frames);
void stream_swr_free(SwrContext* swr);
void stream_append_convert(struct stream* s, SwrContext* swr, const uint8_t** source, int frames);
void stream_read_convert(struct stream* s, SwrContext* swr, uint8_t** dest, int frames);

#endif
