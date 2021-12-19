/*
*   demosauce - fancy icecast source client
*
*   this source is published under the GPLv3 license.
*   http://www.gnu.org/licenses/gpl.txt
*   also, this is beerware! you are strongly encouraged to invite the
*   authors of this software to a beer when you happen to meet them.
*   copyright MMXVIII by maep
*/

// TODO add stream size counter to ffmpeg
// TODO print length seems to depend on samplerate
// TODO loopiness generic
// TODO samplerate for openmpt

#include <libavcodec/avcodec.h>
#include <getopt.h>
#include <chromaprint.h>
#include <replay_gain.h>
#include "decoder.h"
#include "all.h"

enum {
    SAMPLERATE = 44100,
    CHANNELS   = 2,
    MAX_LENGTH = 3600, // abort scan if track is too long, in seconds
    FP_LENGTH  = 120,  // length of fingerprint
};

struct scan {
    int64_t frames;
    int64_t silence;
    double  nrg_l;
    double  nrg_r;
    double  corr;
};

static const char* LOAD_OPTS    = "bass_prescan=true";
static const char* HELP_MESSAGE =
    "demosauce scan tool 0.6.3"ID_STR"\n"
    "syntax: dscan [options] file\n"
    "   -c      acoustic fingerprint\n"
    "   -d      print debug information\n"
    "   -h      print help\n"
    "   -o PATH decode to wav";

// for some formats avcodec fails to provide a bitrate so I just
// make an educated guess. if the file contains large amounts of
// other data besides music, this will be completely wrong.
static double fake_bitrate(const char* path, double duration)
{
    int64_t size = util_filesize(path);
    return (size * 8) / (duration * 1000);
}

static void die_if(bool condition, const char* msg)
{
    if (condition) {
        puts(msg);
        exit(EXIT_FAILURE);
    }
}

static FILE* wav_open(const char* path)
{
    FILE* f = fopen(path, "w");
    uint8_t h[44] = {0};
    die_if(fwrite(h, 1, 44, f) != 44, "wav write error");
    return f;
}

static void wav_close(FILE* f)
{
    long tell = ftell(f);
    die_if(tell == -1, "wav io error");
    int a = imax(0, tell - 8), b = imax(0, tell - 44);
    // header for 44100 Hz stereo 16 bit wav
    uint8_t h[] = {82,73,70,70,  a,a>>8,a>>16,a>>24,  87,65,86,69,  102,109,116,32,  16,0,0,0,  1,0,
                   2,0,  68,172,0,0,  16,177,2,0,  4,0,  16,0,  100,97,116,97,  b,b>>8,b>>16,b>>24};
    die_if(fseek(f, 0, SEEK_SET), "wav io error");
    die_if(fwrite(h, 1, 44, f) != 44, "wav write error");
    fclose(f);
}

// update scan states for silence and channel separation detection
static void update_scan(struct scan* scan, const struct stream* s)
{
    assert(s->channels == 2);
    const float* lbuf = s->buffer[0];
    const float* rbuf = s->buffer[1];

    for (int i = 0; i < s->frames; i++) {
        scan->nrg_l  += lbuf[i] * lbuf[i];
        scan->nrg_r  += rbuf[i] * rbuf[i];
        scan->corr   += lbuf[i] * rbuf[i];
        scan->silence = fabsf(fmaxf(lbuf[i], rbuf[i])) < 0.001 ? scan->silence + 1 : 0;
    }
    scan->frames += s->frames;
}

static double channel_correlation(struct scan* scan)
{
    return scan->corr / sqrt(scan->nrg_l * scan->nrg_r);
}

int main(int argc, char** argv)
{
    bool  enable_fp = false;
    FILE* wavfile   = NULL;

    decoder_init();
    die_if(argc < 2, HELP_MESSAGE);

    char c = 0;
    while ((c = getopt(argc, argv, "hrcqo:d")) != -1) {
        switch (c) {
        default:
        case '?':
            die_if(true, HELP_MESSAGE);
        case 'h':
            puts(HELP_MESSAGE);
            return EXIT_SUCCESS;
        case 'c':
            enable_fp = true;
            break;
        case 'o':
            wavfile = wav_open(optarg);
            break;
        case 'd':
            log_set_console_level(LOG_DEBUG);
            break;
        };
    }
    const char* path = argv[optind];
    die_if(!path, HELP_MESSAGE);

    struct decoder decoder = {0};
    die_if(!decoder_open(&decoder, path, SAMPLERATE, CHANNELS, LOAD_OPTS), "unknown format");

    struct info info = {0};
    decoder_info(&decoder, &info);
    die_if(info.samplerate <= 0 || info.channels < 1, "broken input file");

    struct rg_context* rg_ctx = rg_new(SAMPLERATE, RG_FLOAT32, CHANNELS, false);
    die_if(!rg_ctx, "replaygain error");

    SwrContext* swr_ctx = stream_swr_new_dst(CHANNELS, SAMPLERATE, CHANNELS, SAMPLERATE, STREAM_FMT_S16);
    die_if(!swr_ctx, "converter error");

    ChromaprintContext* cp_ctx = chromaprint_new(CHROMAPRINT_ALGORITHM_DEFAULT);
    die_if(!chromaprint_start(cp_ctx, SAMPLERATE, CHANNELS), "chromaprint error");

    struct stream s    = {0};
    struct scan   scan = {0};
    int16_t buf16[SAMPLERATE * CHANNELS]; // for chromaprint / wav output

    // processing loop
    while (!s.end_of_stream) {
        // decode some samples
        decoder_decode(&decoder, &s, SAMPLERATE);
        // silence, channel corr
        update_scan(&scan, &s);
        // replay gain
        rg_analyze(rg_ctx, (float*[]){s.buffer[0], s.buffer[1]}, s.frames);
        // convert to 16 bit for wav / chromaprint
        bool process_fp = enable_fp && scan.frames <= FP_LENGTH * info.samplerate;
        if (process_fp || wavfile)
            stream_read_convert(&s, swr_ctx, (uint8_t*[]){(uint8_t*)buf16}, s.frames);
        // chromaprint
        if (process_fp) {
            bool ok = chromaprint_feed(cp_ctx, buf16, s.frames * CHANNELS);
            die_if(!ok, "chromaprint error");
        }
        // output wav
        if (wavfile) {
            int bw = fwrite(buf16, CHANNELS * 2, s.frames, wavfile);
            die_if(bw != s.frames, "wav write error");
        }
        // exit in case decoder loops or some joker uploads a long file
        die_if(scan.frames > MAX_LENGTH * info.samplerate, "maxium length exceeded");
    }

    if (wavfile)
        wav_close(wavfile);

    char* str = decoder_metadata(&decoder, "artist");
    if (str)
        printf("artist:%s\n", str);
    free(str);

    str = decoder_metadata(&decoder, "title");
    if (str)
        printf("title:%s\n", str);
    free(str);

    printf("decoder:%s\n", decoder.name);
    printf("type:%s\n", info.codec);
    printf("length:%.2f\n", (double)scan.frames / SAMPLERATE); // use measured length, ffmpeg & co can be unreliable
    printf("samplerate:%i\n", info.samplerate);
    printf("silence:%.2f\n", (double)scan.silence / SAMPLERATE);
    printf("correlation:%.2f\n", channel_correlation(&scan));
    printf("replaygain:%.2f\n", rg_title_gain(rg_ctx));

    if (info.bitrate) {
        printf("bitrate:%.2f\n", info.bitrate);
    } else if (!strcmp(decoder.name, "ffmpeg")) {
        printf("bitrate:%.2f\n", fake_bitrate(path, scan.frames / info.samplerate));
    }

    if (!strcmp(decoder.name, "bass") && (info.flags & INFO_MOD))
        printf("loopiness:%s\n", decoder_control(&decoder, "bass_loopiness"));

    if (enable_fp) {
        char* fingerprint = NULL;
        chromaprint_finish(cp_ctx);
        chromaprint_get_fingerprint(cp_ctx, &fingerprint);
        printf("acoustid:%s\n", fingerprint);
        chromaprint_dealloc(fingerprint);
    }

    chromaprint_free(cp_ctx);
    stream_swr_free(swr_ctx);
    rg_free(rg_ctx);
    decoder_free(&decoder);
    stream_free(&s);
    return EXIT_SUCCESS;
}
