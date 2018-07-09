/*
*   demosauce - fancy icecast source client
*
*   this source is published under the GPLv3 license.
*   http://www.gnu.org/licenses/gpl.txt
*   also, this is beerware! you are strongly encouraged to invite the
*   authors of this software to a beer when you happen to meet them.
*   copyright MMXIII by maep
*/

#ifndef LOG_H
#define LOG_H

#include <stdbool.h>

enum log_level {
    LOG_DEBUG = 1,
    LOG_INFO,
    LOG_WARN,
    LOG_ERROR,
    LOG_FATAL,
    LOG_OFF
};

#define log_debug(...) log_log(LOG_DEBUG, __VA_ARGS__)
#define log_info(...)  log_log(LOG_INFO, __VA_ARGS__)
#define log_warn(...)  log_log(LOG_WARN, __VA_ARGS__)
#define log_error(...) log_log(LOG_ERROR, __VA_ARGS__)
#define log_fatal(...) log_log(LOG_FATAL, __VA_ARGS__)

void log_log(enum log_level level, const char* fmt, ...) __attribute__((format(printf, 2, 3)));
void log_set_console_level(enum log_level level);
void log_set_file_level(enum log_level level);
void log_set_file(const char* file, enum log_level level);
bool log_string_to_level(const char* name, enum log_level* level);

#endif
