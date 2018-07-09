/*
*   demosauce - fancy icecast source client
*
*   this source is published under the GPLv3 license.
*   http://www.gnu.org/licenses/gpl.txt
*   also, this is beerware! you are strongly encouraged to invite the
*   authors of this software to a beer when you happen to meet them.
*   copyright MMXIII by maep
*/

#include <string.h>
#include <math.h>
#include <strings.h>
#include <limits.h>
#include <id3tag.h>
#include <bass.h>
#include "log.h"
#include "settings.h"
#include "effects.h"
#include "bassdecoder.h"

#define IS_MOD(dec)         (bool)((dec)->channel_info.ctype & BASS_CTYPE_MUSIC_MOD)
#define IS_AMIGAMOD(dec)    (bool)((dec)->channel_info.ctype == BASS_CTYPE_MUSIC_MOD)

struct bassdecoder {
    struct buffer       read_buffer;
    DWORD               channel;
    BASS_CHANNELINFO    channel_info;
    int                 samplerate;
    long                current_frame;
    long                last_frame;
};

static void bass_decode(struct decoder* dec, struct stream* s, int frames)
{
    struct bassdecoder* d = dec->handle;
    int ch = d->channel_info.chans;
    if (ch != 2 && ch != 1) {
        LOG_ERROR("[bassdecoder] unsupported number of channels");
        s->end_of_stream = true;
        s->frames = 0;
        return;
    }

    frames = CLAMP(0, d->last_frame - d->current_frame, frames);
    DWORD bytes_to_read = frames * ch * sizeof(float);
    buffer_resize(&d->read_buffer, bytes_to_read);
    DWORD bytes_read = BASS_ChannelGetData(d->channel, d->read_buffer.data, bytes_to_read);
    if (bytes_read == -1 && BASS_ErrorGetCode() != BASS_ERROR_ENDED) 
        LOG_ERROR("[bassdecoder] failed to read from channel (%d)", BASS_ErrorGetCode());
    
    int frames_read = (bytes_read != -1) ? bytes_read / (sizeof(float) * ch) : 0;
    d->current_frame += frames_read;

    s->frames = 0;
    stream_append_convert(s, &d->read_buffer.data, SF_FLOAT32I, frames_read, ch);
    s->end_of_stream = (frames_read != frames) || (d->current_frame >= d->last_frame);
    if(s->end_of_stream) 
        LOG_DEBUG("[bassdecoder] eos %d frames left", s->frames);
}

static void bass_seek(struct decoder* dec, long position)
{
    // TODO implement me!
}

static const char* codec_type(struct bassdecoder* d)
{
    switch (d->channel_info.ctype) {
    case BASS_CTYPE_STREAM_OGG: return "vorbis";
    case BASS_CTYPE_STREAM_MP1:
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
    memset(info, 0, sizeof(struct info)); 
    info->channels      = d->channel_info.chans;
    info->samplerate    = d->channel_info.freq;
    info->frames        = d->last_frame;
    info->flags         = INFO_BASS;
    info->codec         = codec_type(d); 
    if (IS_MOD(d)) 
        info->flags |= INFO_MOD;
    if (IS_AMIGAMOD(d))
        info->flags |= INFO_AMIGAMOD;
    if (!IS_MOD(d)) {
        float size = BASS_StreamGetFilePosition(d->channel, BASS_FILEPOS_END);
        float duration = (float)d->last_frame / d->channel_info.freq;
        info->bitrate = size / (125 * duration);
    }
}

static char* get_id3_tag(const TAG_ID3* tags, const char* key)
{
    char* value = NULL;
    if (!strcmp(key, "artist")) {
        value = util_malloc(31);
        memmove(value, tags->artist, 30);
        value[30] = 0;
    } else if (!strcmp(key, "title")) {
        value = util_malloc(31);
        memmove(value, tags->title, 30);
        value[30] = 0;
    }
    return value;
}

// and the award to the bestesd documented lib goes to libid3tag! the closest
// thing i could find to a documentation was a mailing list entry from 2002
// http://www.mars.org/pipermail/mad-dev/2002-January/000439.html
static char* get_id3v2_tag(const id3_byte_t* tags, const char* key)
{
    const char* frame_id = NULL;
    id3_utf8_t* utf_str = NULL;
    if (!strcmp(key, "artist")) 
        frame_id = ID3_FRAME_ARTIST;
    else if (!strcmp(key, "title"))
        frame_id = ID3_FRAME_TITLE;
    else
        goto id3_quit;

    long length = id3_tag_query(tags, ID3_TAG_QUERYSIZE);
    if (!length) 
        goto id3_quit;

    struct id3_tag* tag = id3_tag_parse(tags, length);
    if (!tag)
        goto id3_quit;

    struct id3_frame* frame = id3_tag_findframe(tag, frame_id, 0);
    if (!frame) 
        goto id3_quit_tag;

    union id3_field* field = id3_frame_field(frame, 1);
    const id3_ucs4_t* ucs_str = id3_field_getstrings(field, 0);
    if (!ucs_str)
        goto id3_quit_frame;

    utf_str = id3_ucs4_utf8duplicate(ucs_str);
    // TODO free ucs string?

id3_quit_frame:
    id3_frame_delete(frame);
id3_quit_tag:
    id3_tag_delete(tag);
id3_quit:
    return (char*)utf_str;
}

static char* get_ogg_tag(const char* tags, const char* key)
{
    return keyval_str_dup(tags, key, NULL);
}

static char* get_tag(DWORD channel, const char* key)
{
    const void* tags = NULL;
    tags = BASS_ChannelGetTags(channel, BASS_TAG_ID3V2);
    if (tags) 
        return get_id3v2_tag(tags, key);
    tags = BASS_ChannelGetTags(channel, BASS_TAG_ID3);
    if (tags)
        return get_id3_tag(tags, key);
    tags = BASS_ChannelGetTags(channel, BASS_TAG_OGG);
    if (tags)
        return get_ogg_tag(tags, key);
    tags = BASS_ChannelGetTags(channel, BASS_TAG_APE);
    if (tags)
        return get_ogg_tag(tags, key);
    tags = BASS_ChannelGetTags(channel, BASS_TAG_MUSIC_NAME);
    if (tags && !strcmp(key, "title"))
        return util_strdup(tags);
    return NULL;
}

static char* bass_metadata(struct decoder* dec, const char* key)
{
    struct bassdecoder* d = dec->handle;
    return util_trim(get_tag(d->channel, key));
}

static void bass_free(struct decoder* dec)
{
    struct bassdecoder* d = dec->handle;
    buffer_free(&d->read_buffer);
    if (d->channel) {
        if (IS_MOD(d)) 
            BASS_MusicFree(d->channel);
        else 
            BASS_StreamFree(d->channel);
        if (BASS_ErrorGetCode() != BASS_OK)
             LOG_WARN("[bassdecoder] failed to free channel (%d)", BASS_ErrorGetCode());
    }
    util_free(d);
}

void bass_set_loop_duration(struct decoder* dec, double duration)
{
    struct bassdecoder* d = dec->handle;
    d->last_frame = duration * d->channel_info.freq;
    BASS_ChannelFlags(d->channel, BASS_SAMPLE_LOOP, BASS_SAMPLE_LOOP);
}

bool bass_load(struct decoder* dec, const char* path, const char* options, int samplerate)
{
    static bool initialized = false;
    if (!initialized) {
        BASS_SetConfig(BASS_CONFIG_UPDATEPERIOD, 0);
        if (!BASS_Init(0, samplerate, 0, 0, NULL)) {
            LOG_ERROR("[bassdecoder] BASS_Init failed");
            return false; 
        }
        initialized = true;
    }

    LOG_DEBUG("[bassdecoder] loading %s", path);

    // always prescan music or it may loop forever, BASS_MUSIC_STOPBACK would fix that
    // but might also break some mods from playing correctly
    bool prescan = keyval_bool(options, "bass_prescan", false);    
    DWORD stream_flags = BASS_STREAM_DECODE | (prescan ? BASS_STREAM_PRESCAN : 0) | BASS_SAMPLE_FLOAT;
    DWORD music_flags = BASS_MUSIC_DECODE | BASS_MUSIC_PRESCAN | BASS_MUSIC_FLOAT;

    DWORD channel = BASS_StreamCreateFile(FALSE, path, 0, 0, stream_flags);
    if (!channel) 
        channel = BASS_MusicLoad(FALSE, path, 0, 0 , music_flags, samplerate);
    if (!channel) {
        LOG_DEBUG("[bassdecoder] failed to load %s", path);
        return false;
    }

    struct bassdecoder* d = util_malloc(sizeof(struct bassdecoder));
    memset(d, 0, sizeof(struct bassdecoder));
    d->channel = channel;

    BASS_ChannelGetInfo(channel, &d->channel_info);
    long len_bytes = (long)BASS_ChannelGetLength(channel, BASS_POS_BYTE);
    d->last_frame = (len_bytes < 0) ? LONG_MAX : len_bytes / (sizeof(float) * d->channel_info.chans);

    if (IS_MOD(d)) {
        // interpolation, values: auto, auto, off, linear, sinc (bass uses linear as default)
        char inter_str[8] = {0};
        keyval_str(inter_str, 8, options, "bass_inter", "auto");
        if ((IS_AMIGAMOD(d) && !strcmp(inter_str, "auto")) || !strcmp(inter_str, "off")) 
            BASS_ChannelFlags(channel, BASS_MUSIC_NONINTER, BASS_MUSIC_NONINTER);
        else if (!strcmp(inter_str, "sinc"))
            BASS_ChannelFlags(channel, BASS_MUSIC_SINCINTER, BASS_MUSIC_SINCINTER);

        // ramping, values: auto, normal, sensitive
        char ramp_str[12] = {0};
        keyval_str(ramp_str, 12, options, "bass_ramp", "auto");
        if ((!IS_AMIGAMOD(d) && !strcmp(ramp_str, "auto")) || !strcmp(inter_str, "normal"))
            BASS_ChannelFlags(channel, BASS_MUSIC_RAMP, BASS_MUSIC_RAMP);
        else if (!strcmp(ramp_str, "sensitive"))
            BASS_ChannelFlags(channel, BASS_MUSIC_RAMPS, BASS_MUSIC_RAMPS);

        // playback mode, values: auto, bass, pt1, ft2 (bass is default)
        char mode_str[8] = {0};
        keyval_str(mode_str, 8, options, "bass_mode", "auto");
        if ((IS_AMIGAMOD(d) && !strcmp(mode_str, "auto")) || !strcmp(mode_str, "pt1"))
            BASS_ChannelFlags(channel, BASS_MUSIC_PT1MOD, BASS_MUSIC_PT1MOD);
        else if (!strcmp(mode_str, "ft2"))
            BASS_ChannelFlags(channel, BASS_MUSIC_FT2MOD, BASS_MUSIC_FT2MOD);
    } 

    dec->free       = bass_free;
    dec->seek       = bass_seek;
    dec->info       = bass_info;
    dec->metadata   = bass_metadata;
    dec->decode     = bass_decode;
    dec->handle     = d;

    LOG_INFO("[bassdecoder] loaded %s", path);
    return true;
}

float bass_loopiness(const char* path)
{
    // what I'm doing here is find the last 50 ms of a track and return the average positive value
    // i got a bit lazy here, but this part isn't so crucial anyways
    // flags to make decoding as fast as possible. still use 44100 hz, because lower setting might
    // remove upper frequencies that could indicate a loop
    float loopiness     = 0;
    int flags           = BASS_MUSIC_DECODE | BASS_SAMPLE_MONO | BASS_MUSIC_NONINTER | BASS_MUSIC_PRESCAN;
    int samplerate      = 44100;
    int check_frames    = samplerate / 20;
    int check_bytes     = check_frames * sizeof(int16_t);
    int16_t* buf        = NULL;

    HMUSIC channel = BASS_MusicLoad(FALSE, path, 0, 0 , flags, samplerate);

    BASS_CHANNELINFO channel_info = {0};
    BASS_ChannelGetInfo(channel, &channel_info);
    if (!(channel_info.ctype & BASS_CTYPE_MUSIC_MOD))
        goto error;

    QWORD length = BASS_ChannelGetLength(channel, BASS_POS_BYTE);
    if (!BASS_ChannelSetPosition(channel, length - check_bytes, BASS_POS_BYTE)) 
        goto error;

    buf = util_malloc(check_bytes);
    memset(buf, 0, check_bytes);
    for (int i = 0; i < check_bytes && BASS_ErrorGetCode() == BASS_OK;) {
        DWORD r = BASS_ChannelGetData(channel, (char*)buf + i, check_bytes - i);
        i += r;
    }

    long accu = 0;
    for (int i = 0; i < check_frames; i++) 
        accu += fabs(buf[i]);
    loopiness = (float)accu / check_frames / -INT16_MIN;

error:
    BASS_MusicFree(channel);
    util_free(buf);
    return loopiness;
}

bool bass_probe(const char* path)
{
    const char* ext[] = {".mp3", ".mp2", ".wav", ".aiff", ".xm", ".mod", ".s3m", ".it", ".mtm", ".umx", ".mo3", ".fst"};
    for (int i = 0; i < COUNT(ext); i++) {
        const char* tmp = strrchr(path, '.');
        if (tmp && !strcasecmp(tmp, ext[i])) 
            return true;
    }

    // extrawurst for AMP :)
    const char* ext2[] = {"xm.", "mod.", "s3m.", "it.", "mtm.", "umx.", "mo3.", "fst."};
    for (int i = 0; i < COUNT(ext2); i++) {
        if (!strncasecmp(path, ext2[i], strlen(ext2[i])))
            return true;
    }

    return false;
}
