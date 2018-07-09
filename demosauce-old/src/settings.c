/*
*   demosauce - fancy icecast source client
*
*   this source is published under the GPLv3 license.
*   http://www.gnu.org/licenses/gpl.txt
*   also, this is beerware! you are strongly encouraged to invite the
*   authors of this software to a beer when you happen to meet them.
*   copyright MMXIII by maep
*/

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdbool.h>
#include <getopt.h>
#ifdef __GLIBC__
    #include <mcheck.h>
#endif
#include "util.h"
#include "settings.h"

static const char* HELP_MESSAGE =
    "syntax: demosauce [options]\n"
    "   -V                      print version\n"
    "   -h                      print help\n"
    "   -c file.conf            config file\n"
    "\n"
    "debug options\n"       
#ifdef __GLIBC__                
    "   -t                      trace malloc, see 'man 3 mtrace'\n"
#endif
    "   -d kv-set               debug song, set of key-value pairs";

#define X(type, key, value) SETTINGS_##type settings_##key = value;
SETTINGS_LIST
#undef X

static const char* config_file_name = "demosauce.conf";

static void die(const char* msg)
{
    puts(msg);
    exit(EXIT_FAILURE);
}

static void strip_comments(char* str)
{
    while (str && *str) {
        while (*str && *str != '#')
            str++;
        while (*str && *str != '\n')
            *str++ = ' ';
    }
}

static void read_config(void)
{
    FILE* f = fopen(config_file_name, "r"); 
    if (!f) 
        die("cat't read config file");

    fseek(f, 0, SEEK_END);
    size_t bsize = ftell(f);
    rewind(f);
    char* buf = util_malloc(bsize + 1);
    fread(buf, 1, bsize, f);
    buf[bsize] = 0;
    fclose(f);
    strip_comments(buf);
    
    char tmpstr[8] = {0};
    #define GET_int(key, value) settings_##key = keyval_int(buf, #key, settings_##key);
    #define GET_str(key, value) settings_##key = keyval_str_dup(buf, #key, settings_##key);
    #define GET_log(key, value) settings_##key = value;                                 \
                                keyval_str(tmpstr, sizeof(tmpstr), buf, #key, NULL);    \
                                log_string_to_level(tmpstr, &settings_##key);
    #define X(type, key, value) GET_##type(key, value)
    SETTINGS_LIST
    #undef X

    util_free(buf);
}

static void check_sanity(void)
{
    if (settings_config_version != 34)
        die("config file seems to be outdated, need config_version 34");

    if (settings_demovibes_port < 1 || settings_demovibes_port > 65535) 
        die("setting demovibes_port out of range (1-65535)");

    if (settings_encoder_samplerate <  8000 || settings_encoder_samplerate > 192000) 
        die("setting encoder_samplerate out of range (8000-192000)");

    if (settings_encoder_bitrate > 10000)
        die("setting encoder_bitrate too high >10000");

    if (settings_encoder_channels < 1 || settings_encoder_channels > 2)
        die("setting encoder_channels out of range (1-2)");

    if (settings_cast_port < 1 || settings_cast_port > 65535) 
        die("setting cast_port out of range (1-65535)");

    if (settings_remote_port < 1 || settings_remote_port > 65535)
        die("setting rempte_port out of range (1-65535)");
}

static void settings_free(void)
{
    #define FREE_int(key) 
    #define FREE_str(key) util_free(settings_##key);
    #define FREE_log(key) 
    #define X(type, key, value) FREE_##type(key)
    SETTINGS_LIST
    #undef X
}

void settings_init(int argc, char** argv)
{
    char c = 0;
    while ((c = getopt(argc, argv, "hc:td:V")) != -1) {
        switch (c) {
        default:
        case '?':
            if (strchr("cd", optopt))
                puts("expecting argument");
            puts(HELP_MESSAGE);
            exit(EXIT_FAILURE);
        case 'h':
            puts(HELP_MESSAGE);
            exit(EXIT_SUCCESS);
        case 'c':
            config_file_name = optarg;
            break;
        case 'd':
            settings_debug_song = optarg;
            break;
#ifdef __GLIBC__
        case 't':
            mtrace();
            break;
#endif
        case 'V':
            exit(EXIT_SUCCESS);
        }
    }
    read_config();
    check_sanity();
    atexit(settings_free);
}
