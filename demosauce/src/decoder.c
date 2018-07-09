#include "decoder.h"
#include "all.h"

static const struct decoder* classes[] = {
    &hvl_class,
#ifdef ENABLE_BASS
    &bass_class,
#endif
    &ompt_class,
    &ff_class,
    NULL
};

void decoder_init(void)
{
    static bool initialized = false;
    if (initialized)
        return;
    for (int i = 0; classes[i]; i++) {
        if (classes[i]->init)
            classes[i]->init();
    }
    initialized = true;
}

bool decoder_open(struct decoder* d, const char* path, int samplerate, int channels, const char* args)
{
    decoder_free(d);
    for (int i = 0; classes[i]; i++) {
        *d = *classes[i];
        if (decoder_probe(d, path) && decoder_load(d, path, samplerate, channels, args))
            return true;
    }
    log_debug("[decoder] unknown extension %s", path);
    for (int i = 0; classes[i]; i++) {
        *d = *classes[i];
        if (decoder_load(d, path, samplerate, channels, args))
            return true;
    }
    return false;
}

void decoder_free(struct decoder* d)
{
    if (d && d->free)
        d->free(d);
    if (d)
        memset(d, 0, sizeof *d);
}

bool decoder_load(struct decoder* d, const char* file, int samplerate, int channels, const char* args)
{
    return d->load(d, file, samplerate, channels, args);
}

void decoder_decode(struct decoder* d, struct stream* s, int frames)
{
    d->decode(d, s, frames);
}

void decoder_seek(struct decoder* d, double position)
{
    d->seek(d, position);
}

void decoder_info(struct decoder* d, struct info* info)
{
    d->info(d, info);
}

char* decoder_metadata(struct decoder* d, const char* key)
{
    return d->metadata(d, key);
}

const char* decoder_control(struct decoder* d, const char* arg)
{
    return d->control ? d->control(d, arg) : NULL;
}

bool decoder_probe(const struct decoder* d, const char* path)
{
    return d->probe(path);
}
