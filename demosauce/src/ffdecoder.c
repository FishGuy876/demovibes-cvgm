/*
*   demosauce - fancy icecast source client
*
*   this source is published under the GPLv3 license.
*   http://www.gnu.org/licenses/gpl.txt
*   also, this is beerware! you are strongly encouraged to invite the
*   authors of this software to a beer when you happen to meet them.
*   copyright MMXIII by maep
*/

#define _POSIX_C_SOURCE 200809L // for strdup
#include <libavformat/avformat.h>
#include <libavcodec/avcodec.h>
#include <libswresample/swresample.h>
#include "decoder.h"

#define BUFFER_SIZE (AVCODEC_MAX_AUDIO_FRAME_SIZE)

struct ffdecoder {
    AVFormatContext*    format_context;
    AVCodecContext*     codec_context;
    SwrContext*         swr_context;
    AVCodec*            codec;
    AVPacket            packet;
    AVPacket            tmp_packet;
    struct stream       stream;
    int                 stream_index;
    int64_t             frames;
};

static void decode_frame(struct ffdecoder* d, AVPacket* p)
{
    void* packet_data = p->data;
    int   packet_size = p->size;

    while (p->size > 0) {
        int ret = 0;
        int got_frame = 0;
        AVFrame frame = {{0}};
        ret = avcodec_decode_audio4(d->codec_context, &frame, &got_frame, p);
        if (ret < 0 || !got_frame)
            break;
        int frames = frame.nb_samples;
        stream_append_convert(&d->stream, d->swr_context, (const uint8_t**)frame.extended_data, frames);

        p->data += ret;
        p->size -= ret;
    }

    p->data = packet_data;
    p->size = packet_size;
}

static void ff_decode(struct decoder* dec, struct stream* s, int frames)
{
    struct ffdecoder* d = dec->handle;

    // preallocate stream to avoid a bunch of incremental resizes
    stream_resize(&d->stream, frames * 2, d->codec_context->channels);

    while (d->stream.frames < frames) {
        AVPacket packet = {};
        int err = av_read_frame(d->format_context, &packet);
        if (err < 0) {
            d->stream.end_of_stream = true;
            break;
        }
        if (packet.stream_index == d->stream_index)
            decode_frame(d, &packet);
        av_free_packet(&packet);
    }

    s->frames = 0;
    stream_append(s, &d->stream, frames);
    stream_drop(&d->stream, frames);
    s->end_of_stream = !d->stream.frames && d->stream.end_of_stream;
    if (s->end_of_stream)
        log_debug("[ffmpeg] end of stream %i frames left", s->frames);
}

static void ff_seek(struct decoder* dec, double position)
{
    struct ffdecoder* d = dec->handle;
    if (av_seek_frame(d->format_context, -1, position * AV_TIME_BASE, 0) < 0)
        log_warn("[ffmpeg] seek failed");
}

static const char* codec_type(struct ffdecoder* d)
{
    enum AVCodecID codec_type = d->codec->id;
    if (codec_type >= AV_CODEC_ID_PCM_S16LE && codec_type < AV_CODEC_ID_ADPCM_IMA_QT)
        return "pcm";
    if (codec_type >= AV_CODEC_ID_ADPCM_IMA_QT && codec_type < AV_CODEC_ID_AMR_NB)
        return "adpcm";
    switch (codec_type) {
        case AV_CODEC_ID_RA_144:
        case AV_CODEC_ID_RA_288:    return "real";
        case AV_CODEC_ID_MP2:       return "mp2";
        case AV_CODEC_ID_MP3:       return "mp3";
        case AV_CODEC_ID_AAC:       return "aac";
        case AV_CODEC_ID_AC3:       return "ac3";
        case AV_CODEC_ID_VORBIS:    return "vorbis";
        case AV_CODEC_ID_WMAVOICE:
        case AV_CODEC_ID_WMAPRO:
        case AV_CODEC_ID_WMALOSSLESS:
        case AV_CODEC_ID_WMAV1:
        case AV_CODEC_ID_WMAV2:     return "wma";
        case AV_CODEC_ID_FLAC:      return "flac";
        case AV_CODEC_ID_ALAC:      return "alac";
        case AV_CODEC_ID_WAVPACK:   return "wavpack";
        case AV_CODEC_ID_APE:       return "monkey";
        case AV_CODEC_ID_MUSEPACK7:
        case AV_CODEC_ID_MUSEPACK8: return "musepack";
        case AV_CODEC_ID_OPUS:      return "opus";
        default:                    return "unknown";
    }
}

static void ff_info(struct decoder* dec, struct info* info)
{
    struct ffdecoder* d = dec->handle;
    memset(info, 0, sizeof *info);
    info->length        = d->frames / d->codec_context->sample_rate;
    info->codec         = codec_type(d);
    info->bitrate       = d->codec_context->bit_rate / 1000.0;
    info->channels      = d->codec_context->channels;
    info->samplerate    = d->codec_context->sample_rate;
    info->flags         = INFO_SEEKABLE;
}

static char* ff_metadata(struct decoder* dec, const char* key)
{
    struct ffdecoder* d = dec->handle;
    AVDictionaryEntry* entry = av_dict_get(d->format_context->metadata, key, 0, 0);
    if (!entry || !entry->value)
        return NULL;
    return util_trim(strdup(entry->value));
}

static void ff_free(struct decoder* dec)
{
    struct ffdecoder* d = dec->handle;
    stream_free(&d->stream);
    avcodec_close(d->codec_context);
    avformat_close_input(&d->format_context);
    swr_free(&d->swr_context);
    free(d);
    memset(dec, 0, sizeof *dec);
}

static bool ff_load(struct decoder* dec, const char* path, int samplerate, int channels, const char* args)
{
    // TODO reject input files with low score
    static bool initialized = false;
    if (!initialized) {
        initialized = true;
        av_register_all();
        avformat_network_init();
        av_log_set_level(AV_LOG_QUIET);
    }

    log_debug("[ffmpeg] loading %s", path);
    struct ffdecoder* d = calloc(sizeof *d, 1);
    dec->handle = d;

    int err = avformat_open_input(&d->format_context, path, 0, 0);
    if (err)
        goto error;

    err = avformat_find_stream_info(d->format_context, NULL);
    if (err < 0)
        goto error;

    for (unsigned i = 0; i < d->format_context->nb_streams; i++) {
        if (d->format_context->streams[i]->codec->codec_type == AVMEDIA_TYPE_AUDIO) {
            d->stream_index = i;
            break;
        }
    }
    if (d->stream_index == -1)
        goto error;

    d->codec_context = d->format_context->streams[d->stream_index]->codec;
    d->codec = avcodec_find_decoder(d->codec_context->codec_id);
    if (!d->codec)
        goto error;

    if (avcodec_open2(d->codec_context, d->codec, NULL) < 0)
        goto error;

    samplerate = samplerate <= 0 ? d->codec_context->sample_rate : samplerate;
    channels   = channels <= 0 ? d->codec_context->channels : channels;
    if (d->format_context->duration > 0)
        d->frames = d->format_context->duration * samplerate / AV_TIME_BASE;
    d->swr_context = swr_alloc_set_opts(NULL, av_get_default_channel_layout(channels),
                                        AV_SAMPLE_FMT_FLTP, samplerate, d->codec_context->channel_layout,
                                        d->codec_context->sample_fmt, d->codec_context->sample_rate, 0, NULL);
    err = swr_init(d->swr_context);
    if (err) {
        log_debug("[ffmpeg] converter error");
        ff_free(dec);
        return false;
    }

    log_debug("[ffmpeg] loaded %s", path);
    return true;

error:
    ff_free(dec);
    log_debug("[ffmpeg] failed to load %s", path);
    return false;
}

static bool ff_probe(const char* path)
{
    const char* ext[] = {"aac", "ac3", "ape", "flac", "m4a", "mp+", "mp2", "mp3",
                         "mp4", "mpc", "ogg", "opus", "ra", "wav", "wma", "wv", NULL};
    for (int i = 0; ext[i]; i++) {
        const char* tmp = strrchr(path, '.');
        if (tmp && !strcasecmp(tmp + 1, ext[i]))
            return true;
    }
    return false;
}

static void ff_init(void)
{
    av_register_all();
    avformat_network_init();
    av_log_set_level(AV_LOG_QUIET); // remove for debugging
}

const struct decoder ff_class = {
    .name       = "ffmpeg",
    .init       = ff_init,
    .load       = ff_load,
    .decode     = ff_decode,
    .seek       = ff_seek,
    .info       = ff_info,
    .metadata   = ff_metadata,
    .probe      = ff_probe,
    .free       = ff_free
};
