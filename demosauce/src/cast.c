/*
*   demosauce - fancy icecast source client
*
*   this source is published under the GPLv3 license.
*   http://www.gnu.org/licenses/gpl.txt
*   also, this is beerware! you are strongly encouraged to invite the
*   authors of this software to a beer when you happen to meet them.
*   copyright MMXIII by maep
*/

#include <pthread.h>
#include <unistd.h>
#include <lame/lame.h>
#include <shout/shout.h>
#include "settings.h"
#include "decoder.h"
#include "cast.h"
#include "all.h"

enum {
    RETRY_TIME      = 15,       // seconds to wait before retry
    SILENCE_TIME    = 60,       // seconds to play silence after LOAD_TRIES failed
    BUFFER_SIZE     = 200,      // miliseconds
    FADE_TIME       = 5,        // seconds
    LOAD_TRIES      = 3,
    COMMAND_NOP     = 0,
    COMMAND_SKIP,
    COMMAND_PLAY,
    COMMAND_META,
    COMMAND_QUIT
};
static const double MIX_RATIO = 0.4; // default mix ratio for amiga modules
static const char*  remote_cmd[] = {NULL, "SKIP", "PLAY", "META", "QUIT", NULL};


static lame_t           lame;
static shout_t*         shout;
static struct stream    stream;
static struct buffer    remote_buf;
static struct buffer    config_buf;
static struct buffer    lame_buf;
static struct info      info;
static struct decoder   decoder;
static struct fadefx    fader;
static double           mix_ratio;
static double           gain;
static long             remaining_frames;
static bool             mixer_enabled;
static bool             fader_enabled;
static bool             have_remote;
static sig_atomic_t     decoder_ready;
static sig_atomic_t     remote_command;

static void get_next_song(void)
{
    if (have_remote) {
        have_remote = false; // config_buf already contains info
    } else if (settings_debug_song) {
        buffer_resize(&config_buf, strlen(settings_debug_song) + 1);
        strcpy(config_buf.data, settings_debug_song);
    } else {
        buffer_zero(&config_buf);
        int socket = socket_connect(settings_demovibes_host, settings_demovibes_port);
        if (socket < 0) {
            log_error("[cast] can't connect to demosauce");
            return;
        }
        socket_write(socket, "NEXTSONG", 8);
        socket_read(socket, &config_buf);
        socket_close(socket);
    }
}

static void zero_generator(struct decoder* dec, struct stream* s, int frames)
{
    s->frames = frames;
    s->end_of_stream = false;
    stream_resize(s, frames, settings_encoder_channels);
    stream_zero(s, 0, frames);
}

static void configure_effects(const char* config, double forced_length)
{
    // play length
    remaining_frames = LONG_MAX;
    if (forced_length > 0) {
        remaining_frames = settings_encoder_samplerate * forced_length;
        log_debug("[cast] song length forced to %f seconds", forced_length);
    }

    // channel mixing
    char mix_str[8] = {0};
    keyval_str(mix_str, sizeof mix_str, config, "mix", "auto");
    mixer_enabled = (settings_encoder_channels == 2) && (strcmp(mix_str, "auto") || (info.flags & INFO_AMIGAMOD));
    if (mixer_enabled) {
        mix_ratio = fclamp(0, keyval_real(config, "mix", MIX_RATIO), 1);
        log_debug("[cast] mixing channels with %f ratio", mix_ratio);
    }

    // gain
    gain = keyval_real(config, "gain", 0.0);
    log_debug("[cast] setting gain to %f dB", gain);
    gain = db_to_amp(gain);

    // fade out
    fader_enabled = keyval_bool(config, "fade_out", false);
    if (fader_enabled) {
        double length = forced_length > 0 ? forced_length : info.length;
        int64_t start = fmax(0, (length - FADE_TIME)) * settings_encoder_samplerate;
        int64_t end = length * settings_encoder_samplerate;
        stream_fade_init(&fader, start, end, 1, 0);
        log_debug("[cast] fading out at %f seconds", length);
    }
}

static void update_metadata(const char* config)
{
    char cast_title[1024]   = {0};
    char artist[512]        = {0};
    char title[512]         = {0};

    keyval_str(title, sizeof(title), config, "title", settings_error_title);
    keyval_str(artist, sizeof(artist), config, "artist", "");

    // remove '-' in artist name, players use it for artist-title separation
    for (size_t i = 0; i < strlen(artist); i++)
        if (cast_title[i] == '-')
            cast_title[i] = ' ';

    size_t len = strlen(artist);
    if (len > 0) {
        strcpy(cast_title, artist);
        strcpy(cast_title + len, " - ");
        len += 3;
    }
    strcpy(cast_title + len, title);
    log_debug("[cast] updating metadata to %s", cast_title);

    shout_metadata_t* metadata = shout_metadata_new();
    shout_metadata_add(metadata, "song", cast_title);
    if (shout_set_metadata(shout, metadata) != SHOUTERR_SUCCESS)
        log_warn("[cast] metadat update failed (%s)", shout_get_error(shout));
    shout_metadata_free(metadata);
}

static void remote_handler(void)
{
    switch(remote_command) {
    default:
    case COMMAND_NOP:
        break;
    case COMMAND_SKIP:
        remaining_frames = FADE_TIME * settings_encoder_samplerate;
        fader_enabled = true;
        stream_fade_init(&fader, 0, remaining_frames, 1, 0);
        break;
    case COMMAND_PLAY:
        buffer_resize(&config_buf, remote_buf.size);
        memmove(config_buf.data, remote_buf.data, remote_buf.size + 1);
        config_buf.size = strlen(config_buf.data) + 1;
        have_remote = true;
        break;
    case COMMAND_META:
        update_metadata(remote_buf.data);
        break;
    case COMMAND_QUIT:
        exit(EXIT_SUCCESS);
    }
    remote_command = COMMAND_NOP;
}

static void* remote_control(void* data)
{
    while (true) {
        int socket = socket_listen(settings_remote_port, true);
        log_info("[remote] connected");
        while (socket >= 0) {
            const char* cmd = NULL;
            while (remote_command)
                sleep(1);

            if (!socket_read(socket, &remote_buf))
                break;

            for (int i = 1; !remote_command && remote_cmd[i]; i++) {
                cmd = remote_cmd[i];
                if (!strncmp(cmd, remote_buf.data, strlen(cmd))) {
                    memset(remote_buf.data, ' ', strlen(cmd));
                    remote_command = i;
                }
            }
            if (remote_command)
                log_debug("[remote] got command %s", cmd);
            else
                log_warn("[remote] unknown command");
        }
        log_debug("[remote] disconnected");
        socket_close(socket);
        sleep(RETRY_TIME);
    }
    return NULL;
}

static void* load_next(void* data)
{
    char    path[4096]    = {0};
    double  forced_length = 0;
    int     tries         = 0;
    bool    loaded        = false;

    while (tries++ < LOAD_TRIES && !loaded) {
        get_next_song();
        keyval_str(path, sizeof(path), config_buf.data, "path", "");
        loaded = decoder_open(&decoder, path,
                              settings_encoder_samplerate,
                              settings_encoder_channels,
                              config_buf.data);
        if (!loaded) {
            log_error("[cast] failed to load %s", path);
            sleep(3);
        }
    }

    memset(&info, 0, sizeof info);
    if (loaded) {
        decoder_info(&decoder, &info);
        if (info.length <= 0)
            log_warn("[cast] no length %s", path);
        forced_length = keyval_real(config_buf.data, "length", 0);
    } else {
        log_warn("[cast] load failed three times, sending one minute sound of silence");
        decoder.decode  = zero_generator;
        info.samplerate = settings_encoder_samplerate;
        info.channels   = settings_encoder_channels;
        forced_length   = SILENCE_TIME;
        buffer_zero(&config_buf);
    }

    configure_effects(config_buf.data, forced_length);
    update_metadata(config_buf.data);
    decoder_ready = true;
    return NULL;
}

static void cast_free(void)
{
    shout_free(shout);
    shout = NULL;
    lame_close(lame);
    lame = 0;
    decoder_free(&decoder);
    stream_free(&stream);
    buffer_free(&remote_buf);
    buffer_free(&config_buf);
    buffer_free(&lame_buf);
}

static void cast_init(void)
{
    shout_init();
    shout = shout_new();
    lame = lame_init();
    lame_set_quality(lame, 2);
    lame_set_brate(lame, settings_encoder_bitrate);
    lame_set_num_channels(lame, settings_encoder_channels);
    lame_set_in_samplerate(lame, settings_encoder_samplerate);
    lame_init_params(lame);
    buffer_resize(&lame_buf, BUFFER_SIZE * settings_encoder_bitrate);
}

static void process(int frames)
{
    decoder.decode(&decoder, &stream, frames);
    if (mixer_enabled)
        stream_mix(&stream, mix_ratio);
    stream_gain(&stream, gain);
    if (fader_enabled)
        stream_fade(&stream, &fader);
}

static bool cast_connect(void)
{
    char bitrate[8]     = {0};
    char samplerate[8]  = {0};
    char channels[4]    = {0};
    snprintf(bitrate, sizeof bitrate, "%d", settings_encoder_bitrate);
    snprintf(samplerate, sizeof samplerate, "%d", settings_encoder_samplerate);
    snprintf(channels, sizeof channels, "%d", settings_encoder_channels);

    shout_set_host(shout, settings_cast_host);
    shout_set_port(shout, settings_cast_port);
    shout_set_user(shout, settings_cast_user);
    shout_set_password(shout, settings_cast_password);
    shout_set_format(shout, SHOUT_FORMAT_MP3);
    shout_set_mount(shout, settings_cast_mount);
    shout_set_public(shout, 1);
    shout_set_name(shout, settings_cast_name);
    shout_set_url(shout, settings_cast_url);
    shout_set_genre(shout, settings_cast_genre);
    shout_set_description(shout, settings_cast_description);
    shout_set_audio_info(shout, SHOUT_AI_BITRATE, bitrate);
    shout_set_audio_info(shout, SHOUT_AI_SAMPLERATE, samplerate);
    shout_set_audio_info(shout, SHOUT_AI_CHANNELS, channels);

    int err = shout_open(shout);
    if (err != SHOUTERR_SUCCESS) {
        log_error("[cast] can't connect to icecast (%s)", shout_get_error(shout));
    } else {
        log_info("[cast] connected to icecast");
    }
    return err == SHOUTERR_SUCCESS;
}

static void launch_pthread(void* (*func)(void*), void* arg)
{
    pthread_t thread = 0;
    pthread_create(&thread, NULL, func, arg);
    pthread_detach(thread);
}

static void main_loop(void)
{
    int decode_frames = (settings_encoder_samplerate * BUFFER_SIZE) / 1000;
    struct stream* s = &stream;

    while (true) {
        remote_handler();
        if (!decoder_ready) {
            stream_resize(s, decode_frames, s->channels);
            stream_zero(s, 0, decode_frames);
        } else {
            process(decode_frames);
            remaining_frames -= s->frames;
            if (s->end_of_stream || remaining_frames < 0) {
                log_debug("[cast] end of stream");
                decoder_ready = false;
                launch_pthread(load_next, NULL);
            }
        }

        int siz = lame_encode_buffer_ieee_float(lame, s->buffer[0], s->buffer[1], s->frames, lame_buf.data, lame_buf.size);
        if (siz < 0) {
           log_error("[cast] lame error (%d)", siz);
           return;
        }
        shout_sync(shout);
        int err = shout_send(shout, lame_buf.data, siz);
        if (err != SHOUTERR_SUCCESS) {
            log_error("[cast] disconnect (%s)", shout_get_error(shout));
            return;
        }
    }
}

void cast_run(void)
{
    if (settings_remote_enable)
        launch_pthread(remote_control, NULL);
    atexit(cast_free);
    while (true) {
        cast_init();
        if (cast_connect()) {
            if (!decoder.handle)
                load_next(NULL);
            main_loop();
        }
        cast_free();
        sleep(RETRY_TIME);
    }
}
