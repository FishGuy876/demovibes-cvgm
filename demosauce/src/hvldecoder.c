/*
*   demosauce - fancy icecast source client
*
*   this source is published under the GPLv3 license.
*   http://www.gnu.org/licenses/gpl.txt
*   also, this is beerware! you are strongly encouraged to invite the
*   authors of this software to a beer when you happen to meet them.
*   copyright MMXIII by maep
*/

// TODO: support looping
// length on load

#define _POSIX_C_SOURCE 200809L // for strdup
#include <hvl_replay.h>
#include "decoder.h"

struct hvldecoder {
    struct hvl_tune* tune;
    struct stream    stream;
    int64_t          frames;
    int64_t          force_frames;
};

static void i16tofloat(const int16_t* src, float* dst, int n)
{
    const double c = 1. / -INT16_MIN;
    for (int i = 0; i < n; i++)
        dst[i] = src[i] * c;
}

static void hvl_decode(struct decoder* dec, struct stream* s, int frames)
{
    struct hvldecoder* d = dec->handle;
    int samplerate = d->tune->ht_Frequency;
    int channels   = d->tune->ht_defstereo;
    int subframes  = samplerate / 50;

    stream_resize(&d->stream, frames + subframes, channels);
    stream_resize(s, frames, channels);

    while (d->stream.frames < frames) {
        int16_t buf[2][subframes];
        hvl_DecodeFrame(d->tune, (char*)buf[0], (char*)buf[1], 2);
        for (int ch = 0; ch < channels; ch++)
            i16tofloat(buf[ch], d->stream.buffer[ch] + d->stream.frames, subframes);
        d->stream.frames += subframes;
    }

    d->frames += frames;
    s->frames  = 0;
    stream_append(s, &d->stream, frames);
    stream_drop(&d->stream, frames);
    s->end_of_stream = d->force_frames ? (d->frames >= d->force_frames) : d->tune->ht_SongEndReached;
    if(s->end_of_stream)
        log_debug("[hively] end of stream");
}

static void hvl_info(struct decoder* dec, struct info* info)
{
    struct hvldecoder* d = dec->handle;
    memset(info, 0, sizeof *info);
    // todo: this might also be exposed through ht_Version
    info->codec         = d->tune->ht_Type;
    info->channels      = d->tune->ht_defstereo;
    info->samplerate    = d->tune->ht_Frequency;
    info->length        = -1;
    info->flags         = INFO_MOD;
}

static char* hvl_metadata(struct decoder* dec, const char* key)
{
    struct hvldecoder* d = dec->handle;
    if (!strcmp(key, "title"))
        return util_trim(strdup(d->tune->ht_Name));
    return NULL;
}

static void hvl_free(struct decoder* dec)
{
    struct hvldecoder* d = dec->handle;
    hvl_FreeTune(d->tune);
    stream_free(&d->stream);
    free(d);
}

static bool hvl_load(struct decoder* dec, const char* path, int samplerate, int channels, const char* args)
{
    log_debug("[hively] loading %s", path);

    samplerate = samplerate <= 0 ? 44100 : samplerate;
    channels   = channels <= 0 ? 2 : channels;

    if (channels > 2) {
        log_error("[hively] unsupported number of channels: %d", channels);
        return false;
    }

    struct hvl_tune* tune = hvl_LoadTune(path, samplerate, channels);
    if (!tune) {
        log_debug("[hively] failed to load %s", path);
        return false;
    }

    struct hvldecoder* d = calloc(1, sizeof *d);
    dec->handle     = d;
    d->tune         = tune;
    d->force_frames = keyval_real(args, "length", 0) * samplerate;

    log_info("[hively] loaded %s", path);
    return true;
}

static bool hvl_probe(const char* path)
{
    const char* ext[] = {"ahx", "hvl", NULL};
    for (int i = 0; ext[i]; i++) {
        const char* tmp = strrchr(path, '.');
        if (tmp && !strcasecmp(tmp + 1, ext[i]))
            return true;
    }
    // extrawurst for AMP, their file extensions are prefixes
    const char* rxt[] = {"ahx.", "hvl.", NULL};
    for (int i = 0; rxt[i]; i++) {
        if (!strncasecmp(path, rxt[i], strlen(rxt[i])))
            return true;
    }
    return false;
}

const struct decoder hvl_class = {
    .name       = "hively",
    .init       = hvl_InitReplayer,
    .load       = hvl_load,
    .decode     = hvl_decode,
    .info       = hvl_info,
    .metadata   = hvl_metadata,
    .probe      = hvl_probe,
    .free       = hvl_free
};
