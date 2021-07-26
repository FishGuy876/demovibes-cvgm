/*
*   demosauce - fancy icecast source client
*
*   this source is published under the GPLv3 license.
*   http://www.gnu.org/licenses/gpl.txt
*   also, this is beerware! you are strongly encouraged to invite the
*   authors of this software to a beer when you happen to meet them.
*   copyright MMXV by maep
*/

// TODO add stream size counter to ffmpeg
// TODO replcae info flags with control calls?
// TODO print length seems to depend on samplerate

// 07-26-2021 - Changed length of MAX_LENGTH to something very very high to prevent sticking on long upload scans.
//              Ideally, this should be re-coded to pull the value from the settings file.

#include <libavcodec/avcodec.h>
#include <getopt.h>
#include <chromaprint.h>
#include <replay_gain.h>
#include "decoder.h"
#include "all.h"

enum {
    SAMPLERATE  = 44100,
    CHANNELS    = 2,
	// MAX_LENGTH  = 3600, // abort scan if track is too long, in seconds (Old Default)
	MAX_LENGTH  = 500000, // Nice long scan time, for really long sets. AAK
    FP_LENGTH   = 120,  // length of fingerprint
};

static const char* LOAD_OPTS    = "bass_prescan=true";
static const char* HELP_MESSAGE =
    "demosauce scan tool 0.6.0"ID_STR"\n"
    "syntax: dscan [options] file\n"
    "   -h          print help\n"
    "   -r          replaygain analysis\n"
    "   -c          acoustic fingerprint\n"
    "   -o file.wav decode to wav\n"
    "   -d          print debug information";

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

int main(int argc, char** argv)
{
    bool    enable_rg   = false;
    bool    enable_fp   = false;
    FILE*   wavfile     = NULL;

    decoder_init();
    die_if(argc < 2, HELP_MESSAGE);

    char c = 0;
    while ((c = getopt(argc, argv, "hrco:d")) != -1) {
        switch (c) {
        default:
        case '?':
            die_if(true, HELP_MESSAGE);
        case 'h':
            puts(HELP_MESSAGE);
            return EXIT_SUCCESS;
        case 'r':
            enable_rg = true;
            break;
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

    // ffmpeg length is unreliable, get accurate length, full decode is needed
    bool decode_audio = enable_rg || enable_fp || wavfile || !(info.flags & INFO_EXACTLEN);
    struct stream s   = {0};
    int64_t frames    = 0;
    int16_t buf[SAMPLERATE * CHANNELS]; // for chromaprint / wav output

    while (decode_audio && !s.end_of_stream) {
        decoder_decode(&decoder, &s, SAMPLERATE);
        frames += s.frames;
        die_if(frames > MAX_LENGTH * info.samplerate, "maxium length exceeded");
        if (enable_rg)
            rg_analyze(rg_ctx, (float*[]){s.buffer[0], s.buffer[1]}, s.frames);
        if ((enable_fp && frames <= FP_LENGTH * info.samplerate) || wavfile)
            stream_read_convert(&s, swr_ctx, (uint8_t*[]){(uint8_t*)buf}, s.frames);
        if (enable_fp && frames <= FP_LENGTH * info.samplerate)
            die_if(!chromaprint_feed(cp_ctx, buf, s.frames * CHANNELS), "chromaprint error");
        if (wavfile)
            die_if(fwrite(buf, CHANNELS * 2, s.frames, wavfile) != s.frames, "wav write error");
    }

    if (wavfile)
        wav_close(wavfile);

    printf("decoder:%s\n", decoder.name);

    char* str = decoder_metadata(&decoder, "artist");
    if (str)
        printf("artist:%s\n", str);
    free(str);

    str = decoder_metadata(&decoder, "title");
    if (str)
        printf("title:%s\n", str);
    free(str);

    printf("type:%s\n", info.codec);

    // use measured length, ffmpeg & co can be unreliable
    double length = decode_audio ? ((double)frames / SAMPLERATE) : info.length;
    printf("length:%.2f\n", length);

    if (enable_rg)
        printf("replaygain:%f\n", rg_title_gain(rg_ctx));

    if (!strcmp(decoder.name, "bass") && (info.flags & INFO_MOD))
        printf("loopiness:%s\n", decoder_control(&decoder, "bass_loopiness"));

    if (info.bitrate) {
        printf("bitrate:%.2f\n", info.bitrate);
    } else if (!strcmp(decoder.name, "ffmpeg")) {
        printf("bitrate:%.2f\n", fake_bitrate(path, frames / info.samplerate));
    }

    if (info.samplerate > 0)
        printf("samplerate:%d\n", info.samplerate);

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
