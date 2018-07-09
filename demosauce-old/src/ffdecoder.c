/*
*   demosauce - fancy icecast source client
*
*   this source is published under the GPLv3 license.
*   http://www.gnu.org/licenses/gpl.txt
*   also, this is beerware! you are strongly encouraged to invite the
*   authors of this software to a beer when you happen to meet them.
*   copyright MMXIII by maep
*/

// on a general not, ffmpeg is a pain in the ass to work with because they change
// their api a couple of times a year, sometimes for no good reason. they just
// change a define or function name so it looks more pretty. and then i have
// to go try and figure out in which version that happend. this is why this file
// is full of #ifdefs which might be off by a few revisions. sorry.
// a good place to look, but it doesn't have all the information:
// http://git.videolan.org/?p=ffmpeg.git;a=blob_plain;f=doc/APIchanges;hb=HEAD

// fixes missing UINT64_C macro on some distros
#define __STDC_CONSTANT_MACROS

#include <string.h>
#include <strings.h>
#ifdef FFMPEG_OLD_HEADER
    #include <avcodec.h>
    #include <avformat.h>
#else
    #include <libavcodec/avcodec.h>
    #include <libavformat/avformat.h>
#endif
#include "log.h"
#include "effects.h"
#include "ffdecoder.h"

#ifndef AV_VERSION_INT 
    #define AV_VERSION_INT(a, b, c) (a << 16 | b << 8 | c)
#endif

#define BUFFER_SIZE (AVCODEC_MAX_AUDIO_FRAME_SIZE)

struct ffdecoder {
    AVFormatContext*    format_context;
    AVCodecContext*     codec_context;
    AVCodec*            codec;
    AVPacket            packet;
    AVPacket            tmp_packet;
#if LIBAVCODEC_VERSION_INT < AV_VERSION_INT(53, 25, 0)
    struct buffer       buffer;
#endif
    struct stream       stream;
    int                 stream_index;
    int                 format;
    long                frames;
};

static int get_format(AVCodecContext* codec_context)
{
    switch (codec_context->sample_fmt) {
#if LIBAVCODEC_VERSION_INT < AV_VERSION_INT(52, 95, 0)
    case SAMPLE_FMT_S16:        return SF_INT16I;
    case SAMPLE_FMT_FLT:        return SF_FLOAT32I;
#else
    case AV_SAMPLE_FMT_S16:     return SF_INT16I;
    case AV_SAMPLE_FMT_FLT:     return SF_FLOAT32I;
#endif
#if LIBAVUTIL_VERSION_INT > AV_VERSION_INT(51, 26, 0)
    case AV_SAMPLE_FMT_S16P:    return SF_INT16P;
    case AV_SAMPLE_FMT_FLTP:    return SF_FLOAT32P;
#endif
    default:                    return -1;
    };
}

static void decode_frame(struct ffdecoder* d, AVPacket* p)
{
    void* packet_data = p->data;
    int   packet_size = p->size;
    
    while (p->size > 0) {
        int ret = 0;
#if LIBAVCODEC_VERSION_INT < AV_VERSION_INT(53, 25, 0)
        int data_size = BUFFER_SIZE;
        int16_t* buf = d->buffer.data;
#if LIBAVCODEC_VERSION_INT < AV_VERSION_INT(52, 23, 0)
        ret = avcodec_decode_audio2(d->codec_context, buf, &data_size, p->data, p->size);
#else
        ret = avcodec_decode_audio3(d->codec_context, buf, &data_size, p);
#endif
        if (ret < 0)
            goto error;
        // TODO check format
        int frames = data_size / (d->codec_context->channels * sizeof(int16_t));
        void* buffs[MAX_CHANNELS] = {buf, buf + frames};
        stream_append_convert(&d->stream, buffs, d->format, frames, d->codec_context->channels);
#else
        int got_frame = 0;
        AVFrame frame = {{0}};
        ret = avcodec_decode_audio4(d->codec_context, &frame, &got_frame, p);
        if (ret < 0 || !got_frame)
            goto error;
        int frames = frame.nb_samples;
        void** buffs = (void**)frame.extended_data;
        stream_append_convert(&d->stream, buffs, d->format, frames, d->codec_context->channels);
#endif
        p->data += ret;
        p->size -= ret;
    }

error:    
    p->data = packet_data;
    p->size = packet_size;
}

static void ff_decode(struct decoder* dec, struct stream* s, int frames)
{
    struct ffdecoder* d = dec->handle;
    
    // preallocate stream to avoid a bunch of incremental resizes
    stream_resize(&d->stream, frames * 2, d->codec_context->channels);
    
    while (d->stream.frames < frames) {
        AVPacket packet = {0};
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
        LOG_DEBUG("[ffdecoder] eos avcodec %d frames left", s->frames);
}

static void ff_seek(struct decoder* dec, long frame)
{
    struct ffdecoder* d = dec->handle;
    int sr = d->codec_context->sample_rate;
    int64_t timestamp = frame / sr * AV_TIME_BASE;
    if (av_seek_frame(d->format_context, -1, timestamp, 0) < 0)
        LOG_WARN("[ffdecoder] seek failed");
}

static const char* codec_type(struct ffdecoder* d)
{
#if LIBAVCODEC_VERSION_INT < AV_VERSION_INT(54, 25, 0)
    enum CodecID codec_type = d->codec->id;
#else
    enum AVCodecID codec_type = d->codec->id;
#endif
    if (codec_type >= CODEC_ID_PCM_S16LE && codec_type < CODEC_ID_ADPCM_IMA_QT) 
        return "pcm";
    if (codec_type >= CODEC_ID_ADPCM_IMA_QT && codec_type < CODEC_ID_AMR_NB) 
        return "adpcm";
    switch (codec_type) {
        case CODEC_ID_RA_144:
        case CODEC_ID_RA_288:   return "real";
        case CODEC_ID_MP2:      return "mp2";
        case CODEC_ID_MP3:      return "mp3";
        case CODEC_ID_AAC:      return "aac";
        case CODEC_ID_AC3:      return "ac3";
        case CODEC_ID_VORBIS:   return "vorbis";
#if LIBAVCODEC_VERSION_INT > AV_VERSION_INT(51, 50, 0)
        case CODEC_ID_WMAVOICE:
        case CODEC_ID_WMAPRO:
        case CODEC_ID_WMALOSSLESS: 
#endif
        case CODEC_ID_WMAV1:
        case CODEC_ID_WMAV2:    return "wma";
        case CODEC_ID_FLAC:     return "flac";
        case CODEC_ID_WAVPACK:  return "wavpack";
        case CODEC_ID_APE:      return "monkey";
        case CODEC_ID_MUSEPACK7:
        case CODEC_ID_MUSEPACK8:return "musepack";
#if LIBAVCODEC_VERSION_INT > AV_VERSION_INT(54, 24, 0)
        case CODEC_ID_OPUS:     return "opus";
#endif
        default:                return "unknown";
    }
}

static void ff_info(struct decoder* dec, struct info* info)
{
    struct ffdecoder* d = dec->handle;
    memset(info, 0, sizeof(struct info));
    info->frames        = d->frames;
    info->codec         = codec_type(d);
    info->bitrate       = d->codec_context->bit_rate / 1000.0f;
    info->channels      = d->codec_context->channels;
    info->samplerate    = d->codec_context->sample_rate;
    info->flags         = INFO_FFMPEG | INFO_SEEKABLE;
}

static char* ff_metadata(struct decoder* dec, const char* key)
{
    struct ffdecoder* d = dec->handle;
    const char* value = NULL;
#if LIBAVFORMAT_VERSION_INT < AV_VERSION_INT(52, 83, 0)
    if (!strcmp(key, "artist"))
        value = d->format_context->author;
    else if (!strcmp(key, "title"))
        value = d->format_context->title;
#else
    AVDictionaryEntry* entry = av_dict_get(d->format_context->metadata, key, 0, 0);;
    value = entry ? entry->value : NULL;
#endif
    char* v = util_strdup(value);
    util_trim(v);
    return v;
}

static void ff_free2(struct ffdecoder* d)
{
#if LIBAVCODEC_VERSION_INT < AV_VERSION_INT(53, 8, 0)
    buffer_free(&d->buffer);
#endif
    stream_free(&d->stream);
    if (d->codec_context)
        avcodec_close(d->codec_context);
    if (d->format_context)
#if LIBAVFORMAT_VERSION_INT < AV_VERSION_INT(53, 17, 0)
        av_close_input_file(d->format_context);
#else
        avformat_close_input(&d->format_context);
#endif
}

static void ff_free(struct decoder* dec)
{
    struct ffdecoder* d = dec->handle;
    ff_free2(d);
    util_free(d);
}

bool ff_load(struct decoder* dec, const char* path)
{
    // TODO reject input files with low score
    static bool initialized = false;
    if (!initialized) {
        initialized = true;
        av_register_all();
#if LIBAVFORMAT_VERSION_INT > AV_VERSION_INT(53, 18, 0)
        avformat_network_init();
#endif
#ifndef DEBUG
        av_log_set_level(AV_LOG_QUIET);
#endif
    }

    LOG_DEBUG("[ffdecoder] loading %s", path);
    
    int err = 0;
    struct ffdecoder d = {0};
#if LIBAVFORMAT_VERSION_INT < AV_VERSION_INT(52, 111, 0)
    err = av_open_input_file(&d.format_context, path, 0, 0, 0);
#else
    err = avformat_open_input(&d.format_context, path, 0, 0);
#endif
    if (err) 
        goto error;
#if LIBAVFORMAT_VERSION_INT < AV_VERSION_INT(53, 6, 0)
    err = av_find_stream_info(d.format_context);
#else
    err = avformat_find_stream_info(d.format_context, NULL);
#endif
    if (err < 0) 
        goto error;

    for (unsigned i = 0; i < d.format_context->nb_streams; i++) {
#if LIBAVCODEC_VERSION_INT < AV_VERSION_INT(52, 64, 0)
        if (d.format_context->streams[i]->codec->codec_type == CODEC_TYPE_AUDIO)
#else
        if (d.format_context->streams[i]->codec->codec_type == AVMEDIA_TYPE_AUDIO)
#endif
            d.stream_index = i;
            break;
    }
    if (d.stream_index == -1)
        goto error;

    d.codec_context = d.format_context->streams[d.stream_index]->codec;
    d.codec = avcodec_find_decoder(d.codec_context->codec_id);
    if (!d.codec) 
        goto error;

    d.format = get_format(d.codec_context);
    if (d.format < 0)
        goto error;

#if LIBAVCODEC_VERSION_INT < AV_VERSION_INT(53, 8, 0)
    if (avcodec_open(d.codec_context, d.codec) < 0)
#else
    if (avcodec_open2(d.codec_context, d.codec, NULL) < 0)
#endif
        goto error;
    
    if (d.format_context->duration > 0) 
        d.frames = d.format_context->duration * d.codec_context->sample_rate / AV_TIME_BASE;
    
#if LIBAVCODEC_VERSION_INT < AV_VERSION_INT(53, 25, 0)
    buffer_resize(&d.buffer, BUFFER_SIZE);
#endif
    
    dec->free       = ff_free;
    dec->seek       = ff_seek;
    dec->info       = ff_info;
    dec->metadata   = ff_metadata;
    dec->decode     = ff_decode;
    dec->handle     = util_malloc(sizeof(struct ffdecoder));
    memmove(dec->handle, &d, sizeof(struct ffdecoder));
    
    LOG_INFO("[ffdecoder] loaded %s", path);
    return true;

error:
    ff_free2(&d);
    LOG_DEBUG("[ffdecoder] failed to open %s", path);
    return false;
}

bool ff_probe_name(const char* file_name)
{
    const char* ext[] = {".mp3", ".ogg", ".mp4", ".m4a" ".aac", ".wma", ".acc", ".flac", 
        ".ac3", ".wav", ".ape", ".wv", ".mpc", ".mp+", ".mpp", ".ra", ".mp2"
#if LIBAVCODEC_VERSION_INT > AV_VERSION_INT(54, 24, 0)
        , ".opus"
#endif
    }; 
    for (int i = 0; i < COUNT(ext); i++) {
        const char* tmp = strrchr(file_name, '.');
        if (tmp && !strcasecmp(tmp, ext[i])) 
            return true;
    }
    return false;
}
