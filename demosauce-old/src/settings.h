/*
*   demosauce - fancy icecast source client
*
*   this source is published under the GPLv3 license.
*   http://www.gnu.org/licenses/gpl.txt
*   also, this is beerware! you are strongly encouraged to invite the
*   authors of this software to a beer when you happen to meet them.
*   copyright MMXIII by maep
*/

#ifndef SETTINGS_H
#define SETTINGS_H

#include "log.h"

void settings_init(int argc, char** argv);

#define SETTINGS_LIST                           \
    X(int, config_version,      0)              \
    X(str, demovibes_host,      "localhost")    \
    X(int, demovibes_port,      32167)          \
    X(int, encoder_samplerate,  44100)          \
    X(int, encoder_bitrate,     192)            \
    X(int, encoder_channels,    2)              \
    X(str, cast_host,           "localhost")    \
    X(int, cast_port,           8000)           \
    X(str, cast_mount,          "stream")       \
    X(str, cast_user,           "source")       \
    X(str, cast_password,       NULL)           \
    X(str, cast_name,           NULL)           \
    X(str, cast_url,            NULL)           \
    X(str, cast_genre,          NULL)           \
    X(str, cast_description,    NULL)           \
    X(int, remote_enable,       1)              \
    X(int, remote_port,         1911)           \
    X(str, error_title,         "server error") \
    X(str, log_file,            "demosauce.log")\
    X(log, log_file_level,      log_info)       \
    X(log, log_console_level,   log_warn)       \
    X(str, debug_song,          NULL)

#define SETTINGS_int    int
#define SETTINGS_str    char*
#define SETTINGS_log    enum log_level

#define X(type, key, value) extern SETTINGS_##type settings_##key;
SETTINGS_LIST
#undef X

#endif

