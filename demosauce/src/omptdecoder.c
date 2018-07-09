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
#include <libopenmpt/libopenmpt.h>
#include <libopenmpt/libopenmpt_stream_callbacks_file.h>
#include "decoder.h"

struct omptdecoder {
    openmpt_module* mod;
    int             channels;
    int             samplerate;
    const char*     type;
    int64_t         frames;
    int64_t         force_frames;
};

static void ompt_decode(struct decoder* dec, struct stream* s, int frames)
{
    struct omptdecoder* d = dec->handle;

    stream_resize(s, frames, d->channels);
    if (s->channels == 1) {
        s->frames = openmpt_module_read_float_mono(d->mod, d->samplerate, frames, s->buffer[0]);
    } else if (s->channels == 2) {
        s->frames = openmpt_module_read_float_stereo(d->mod, d->samplerate, frames, s->buffer[0], s->buffer[1]);
    }

    d->frames += s->frames;
    s->end_of_stream = d->force_frames ? d->frames >= d->force_frames : s->frames == 0;
    if(s->end_of_stream)
        log_debug("[openmpt] end of stream");
}

static void ompt_seek(struct decoder* dec, double position)
{
    struct omptdecoder* d = dec->handle;
    openmpt_module_set_position_seconds(d->mod, position);
}

static void ompt_info(struct decoder* dec, struct info* info)
{
    struct omptdecoder* d = dec->handle;
    memset(info, 0, sizeof *info);
    info->codec         = d->type;
    info->channels      = d->channels;
    info->samplerate    = d->samplerate;
    info->length        = openmpt_module_get_duration_seconds(d->mod);
    info->flags         = INFO_SEEKABLE | INFO_MOD;
}

static char* ompt_metadata(struct decoder* dec, const char* key)
{
    struct omptdecoder* d = dec->handle;
    const char* value = openmpt_module_get_metadata(d->mod, key);
    char* dupval = value && value[0] ? strdup(value) : NULL;
    openmpt_free_string(value);
    return util_trim(dupval);
}

static void ompt_free(struct decoder* dec)
{
    struct omptdecoder* d = dec->handle;
    openmpt_free_string(d->type);
    openmpt_module_destroy(d->mod);
    free(d);
}

static bool ompt_load(struct decoder* dec, const char* path, int samplerate, int channels, const char* args)
{
    log_debug("[openmpt] loading %s", path);

    if (channels > 2) {
        log_error("[openmpt] unsupported number of channels: %d", channels);
        return false;
    }

    FILE* file = fopen(path, "r");
    if (!file) {
        log_debug("[openmpt] failed to open %s", path);
        return false;
    }

    openmpt_module* mod = openmpt_module_create(openmpt_stream_get_file_callbacks(),
                                                file, openmpt_log_func_silent, NULL, NULL);
    fclose(file);
    if (!mod) {
        log_debug("[openmpt] failed to load %s", path);
        return false;
    }

    struct omptdecoder* d = calloc(sizeof *d, 1);
    dec->handle     = d;
    d->mod          = mod;
    d->channels     = channels <= 0 ? 2 : channels;
    d->samplerate   = samplerate <= 0 ? 44100 : samplerate;
    d->type         = openmpt_module_get_metadata(mod, "type");
    d->force_frames = keyval_real(args, "length", 0) * d->samplerate;

    if (d->force_frames)
        openmpt_module_set_repeat_count(mod, -1);

    log_info("[openmpt] loaded %s", path);
    return true;
}

static bool ompt_probe(const char* path)
{
    const char* ext = strrchr(path, '.');
    if (ext && openmpt_is_extension_supported(ext + 1))
        return true;
    // extrawurst for AMP, their file extensions are prefixes
    char tmp[8] = {0};
    strncpy(tmp, path, sizeof tmp - 1);
    char* pxt = strchr(tmp, '.');
    if (pxt)
        *pxt = 0;
    return openmpt_is_extension_supported(tmp);
}

const struct decoder ompt_class = {
    .name       = "openmpt",
    .load       = ompt_load,
    .decode     = ompt_decode,
    .seek       = ompt_seek,
    .info       = ompt_info,
    .metadata   = ompt_metadata,
    .probe      = ompt_probe,
    .free       = ompt_free
};
