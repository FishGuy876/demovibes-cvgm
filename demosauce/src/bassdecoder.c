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
#include <bass.h>
#include "decoder.h"

/*  load options:
 *      bass_inter  auto, off, linear, sinc
 *      bass_ramp   auto, off, normal, sensitive
 *      bass_mode   auto, pt1, ft2
 */

struct bassdecoder {
    struct buffer       read_buffer;
    DWORD               channel;
    SwrContext*         swr_context;
    BASS_CHANNELINFO    channel_info;
    double              length;
    int64_t             frames;             // at source samplerate
    int64_t             current_frame;      // at source samplerate
    char*               path;
    int                 flags;              // for prescan flag
    char                control_buf[16];    // stores return value for bass_control
};

static bool is_mod(struct bassdecoder* d)
{
    return d->channel_info.ctype & BASS_CTYPE_MUSIC_MOD;
}

static bool is_amigamod(struct bassdecoder* d)
{
    return d->channel_info.ctype == BASS_CTYPE_MUSIC_MOD;
}

static void bass_decode(struct decoder* dec, struct stream* s, int frames)
{
    struct bassdecoder* d = dec->handle;

    int frames_need = stream_swr_frames(d->swr_context, frames);

    frames_need = iclamp64(0, d->frames - d->current_frame, frames_need);
    int bytes_need = frames_need * d->channel_info.chans * sizeof(float);
    buffer_resize(&d->read_buffer, bytes_need);

    int bytes_read = BASS_ChannelGetData(d->channel, d->read_buffer.data, bytes_need);
    if (bytes_read == -1 && BASS_ErrorGetCode() != BASS_ERROR_ENDED)
        log_error("[bass] failed to read from channel (%d)", BASS_ErrorGetCode());

    int frames_read = (bytes_read != -1) ? bytes_read / (sizeof(float) * d->channel_info.chans) : 0;
    d->current_frame += frames_read;

    s->frames = 0;
    stream_append_convert(s, d->swr_context, (const uint8_t**)&d->read_buffer.data, frames_read);

    s->end_of_stream = (frames_read != frames_need) || (d->current_frame >= d->frames);
    if(s->end_of_stream)
        log_debug("[bass] end of stream %i frames left", s->frames);
}

static void bass_seek(struct decoder* dec, double position)
{
    // TODO implement me!
}

static const char* codec_type(struct bassdecoder* d)
{
    switch (d->channel_info.ctype) {
    case BASS_CTYPE_STREAM_OGG: return "vorbis";
    case BASS_CTYPE_STREAM_MP2: return "mp2";
    case BASS_CTYPE_STREAM_MP3: return "mp3";
    case BASS_CTYPE_STREAM_AIFF:
    case BASS_CTYPE_STREAM_WAV_PCM:
    case BASS_CTYPE_STREAM_WAV_FLOAT:
    case BASS_CTYPE_STREAM_WAV: return "pcm";
    case BASS_CTYPE_MUSIC_MOD:  return "mod";
    case BASS_CTYPE_MUSIC_MTM:  return "mtm";
    case BASS_CTYPE_MUSIC_S3M:  return "s3m";
    case BASS_CTYPE_MUSIC_XM:   return "xm";
    case BASS_CTYPE_MUSIC_IT:   return "it";
    case BASS_CTYPE_MUSIC_MO3:  return "mo3";
    default:                    return "unknown";
    }
}

static void bass_info(struct decoder* dec, struct info* info)
{
    struct bassdecoder* d = dec->handle;
    memset(info, 0, sizeof *info);
    info->codec         = codec_type(d);
    info->channels      = d->channel_info.chans;
    info->samplerate    = d->channel_info.freq;
    info->length        = d->length;
    info->flags         = d->flags;
    if (!is_mod(d))
        info->bitrate = BASS_StreamGetFilePosition(d->channel, BASS_FILEPOS_END) / (125 * d->length);
}

static double bass_loopiness(const char* path)
{
    // what I'm doing here is find the last 50 ms of a track and return the average positive value
    // i got a bit lazy here, but this part isn't so crucial anyways
    // flags to make decoding as fast as possible. still use 44100 hz, because lower setting might
    // remove upper frequencies that could indicate a loop
    double loopiness        = 0;
    const int flags         = BASS_MUSIC_DECODE | BASS_SAMPLE_MONO | BASS_MUSIC_NONINTER | BASS_MUSIC_PRESCAN;
    const int samplerate    = 44100;
    const int check_frames  = samplerate / 20;
    int16_t buf[check_frames];

    HMUSIC channel = BASS_MusicLoad(FALSE, path, 0, 0 , flags, samplerate);

    BASS_CHANNELINFO channel_info = {};
    BASS_ChannelGetInfo(channel, &channel_info);
    if (!(channel_info.ctype & BASS_CTYPE_MUSIC_MOD))
        goto error;

    QWORD length = BASS_ChannelGetLength(channel, BASS_POS_BYTE);
    if (!BASS_ChannelSetPosition(channel, length - sizeof buf, BASS_POS_BYTE))
        goto error;

    memset(buf, 0, sizeof buf);
    for (int i = 0; i < sizeof buf && BASS_ErrorGetCode() == BASS_OK;) {
        DWORD r = BASS_ChannelGetData(channel, (char*)buf + i, sizeof buf - i);
        i += r;
    }

    double accu = 0;
    for (int i = 0; i < check_frames; i++)
        accu += abs(buf[i]);
    loopiness = (accu / check_frames) / -INT16_MIN;

error:
    BASS_MusicFree(channel);
    return loopiness;
}

static char* bass_metadata(struct decoder* dec, const char* key)
{
    struct bassdecoder* d = dec->handle;
    char* value = NULL;
    if (is_mod(d) && !strcmp(key, "title")) {
        const char* tags = BASS_ChannelGetTags(d->channel, BASS_TAG_MUSIC_NAME);
        value = tags ? strdup(tags) : NULL;
    } else {
        // use libavformat, the bass tag api sucks
        AVFormatContext* ctx = NULL;
        if (!avformat_open_input(&ctx, d->path, 0, 0)) {
            AVDictionaryEntry* entry = av_dict_get(ctx->metadata, key, 0, 0);
            value = entry && entry->value ? strdup(entry->value) : NULL;
        }
        avformat_close_input(&ctx);
    }
    return util_trim(value);
}

static void bass_free(struct decoder* dec)
{
    struct bassdecoder* d = dec->handle;
    free(d->path);
    buffer_free(&d->read_buffer);
    stream_swr_free(d->swr_context);
    if (d->channel && is_mod(d)) {
        BASS_MusicFree(d->channel);
    } else if (d->channel) {
        BASS_StreamFree(d->channel);
    }
    free(d);
}

static bool bass_load(struct decoder* dec, const char* path, int samplerate, int channels, const char* args)
{
    log_debug("[bass] loading %s", path);

    samplerate   = samplerate <= 0 ? 44100 : samplerate;
    channels     = channels <= 0 ? 2 : channels;
    bool prescan = keyval_bool(args, "bass_prescan", false);
    // always prescan music or it may loop forever
    DWORD music_flags = BASS_MUSIC_DECODE | BASS_MUSIC_PRESCAN | BASS_MUSIC_FLOAT;
    DWORD stream_flags = BASS_STREAM_DECODE | (prescan ? BASS_STREAM_PRESCAN : 0) | BASS_SAMPLE_FLOAT;

    DWORD channel = BASS_StreamCreateFile(FALSE, path, 0, 0, stream_flags);
    if (!channel)
        channel = BASS_MusicLoad(FALSE, path, 0, 0 , music_flags, samplerate);
    if (!channel) {
        log_debug("[bass] failed to load %s", path);
        return false;
    }

    struct bassdecoder* d = calloc(sizeof *d, 1);

    BASS_ChannelGetInfo(channel, &d->channel_info);
    QWORD chbytes = BASS_ChannelGetLength(channel, BASS_POS_BYTE);

    dec->handle     = d;
    d->path         = strdup(path);
    d->channel      = channel;
    d->length       = fmax(0, BASS_ChannelBytes2Seconds(channel, chbytes));
    d->frames       = d->length > 0 ? llround(d->length * d->channel_info.freq) : INT64_MAX;
    d->swr_context  = stream_swr_new_src(d->channel_info.chans, d->channel_info.freq,
                                         STREAM_FMT_FLT, channels, samplerate);
    d->flags        = prescan ? INFO_EXACTLEN : 0;

    if (!d->swr_context) {
        log_warn("[bass] resampler error");
        bass_free(dec);
        return false;
    }

    double forced_length = keyval_real(args, "length", 0);
    if (forced_length > d->length) {
        d->frames = forced_length * d->channel_info.freq;
        BASS_ChannelFlags(d->channel, BASS_SAMPLE_LOOP, BASS_SAMPLE_LOOP);
    }

    if (is_mod(d)) {
        d->flags |= INFO_MOD | is_amigamod(d) ? INFO_AMIGAMOD : 0;

        // interpolation, values: auto, off, linear, sinc (bass uses linear as default)
        char inter_str[8] = {0};
        keyval_str(inter_str, sizeof inter_str, args, "bass_inter", "auto");
        if ((is_amigamod(d) && !strcmp(inter_str, "auto")) || !strcmp(inter_str, "off")) {
            BASS_ChannelFlags(channel, BASS_MUSIC_NONINTER, BASS_MUSIC_NONINTER);
        } else if (!strcmp(inter_str, "sinc")) {
            BASS_ChannelFlags(channel, BASS_MUSIC_SINCINTER, BASS_MUSIC_SINCINTER);
        }

        // ramping, values: auto, normal, sensitive
        char ramp_str[12] = {0};
        keyval_str(ramp_str, sizeof ramp_str, args, "bass_ramp", "auto");
        if ((!is_amigamod(d) && !strcmp(ramp_str, "auto")) || !strcmp(inter_str, "normal")) {
            BASS_ChannelFlags(channel, BASS_MUSIC_RAMP, BASS_MUSIC_RAMP);
        } else if (!strcmp(ramp_str, "sensitive")) {
            BASS_ChannelFlags(channel, BASS_MUSIC_RAMPS, BASS_MUSIC_RAMPS);
        }

        // playback mode, values: auto, pt1, ft2
        char mode_str[8] = {0};
        keyval_str(mode_str, sizeof mode_str, args, "bass_mode", "auto");
        if (!strcmp(mode_str, "pt1")) {
            BASS_ChannelFlags(channel, BASS_MUSIC_PT1MOD, BASS_MUSIC_PT1MOD);
        } else if (!strcmp(mode_str, "ft2")) {
            BASS_ChannelFlags(channel, BASS_MUSIC_FT2MOD, BASS_MUSIC_FT2MOD);
        }
    }

    log_info("[bass] loaded %s", path);
    return true;
}

static const char* bass_control(struct decoder* dec, const char* args)
{
    struct bassdecoder* d = dec->handle;
    const int bufsize = sizeof d->control_buf;
    memset(d->control_buf, 0, bufsize);
    if (strcmp(args, "bass_loopiness") == 0) {
        int rs = snprintf(d->control_buf, bufsize - 1, "%.2f", bass_loopiness(d->path));
        assert(rs >= 0 && rs < bufsize);
        return d->control_buf;
    }
    return NULL;
}

static bool bass_probe(const char* path)
{
    const char* ext[] = {"aiff", "dms", "fst", "ft", "it", "mo3", "mod", "mp2", "mp3",
                         "mtm", "s3m", "umx", "vorbis", "wav", "xm", NULL};
    for (int i = 0; ext[i]; i++) {
        const char* tmp = strrchr(path, '.');
        if (tmp && !strcasecmp(tmp + 1, ext[i]))
            return true;
    }
    // extrawurst for AMP, their file extensions are prefixes
    const char* rxt[] = {"dms.", "fst.", "ft.", "it.", "mo3.", "mod.", "mtm.", "s3m.",
                         "umx.", "xm.", NULL};
    for (int i = 0; rxt[i]; i++) {
        if (!strncasecmp(path, rxt[i], strlen(rxt[i])))
            return true;
    }
    return false;
}

static void bass_init(void)
{
    BASS_SetConfig(BASS_CONFIG_UPDATEPERIOD, 0);
    if (!BASS_Init(0, 44100, 0, 0, NULL)) {
        log_fatal("[bass] BASS_Init failed");
        exit(EXIT_FAILURE);
    }
}

const struct decoder bass_class = {
    .name       = "bass",
    .init       = bass_init,
    .load       = bass_load,
    .decode     = bass_decode,
    .seek       = bass_seek,
    .info       = bass_info,
    .metadata   = bass_metadata,
    .control    = bass_control,
    .probe      = bass_probe,
    .free       = bass_free
};
