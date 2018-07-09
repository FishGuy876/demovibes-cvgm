/*
*   demosauce - fancy icecast source client
*
*   this source is published under the GPLv3 license.
*   http://www.gnu.org/licenses/gpl.txt
*   also, this is beerware! you are strongly encouraged to invite the
*   authors of this software to a beer when you happen to meet them.
*   copyright MMXIII by maep
*
*   logging and "error handling" stuff. to log use macros:
*   LOG_DEBUG, LOG_INFO, LOG_WARNING, LOG_ERROR, LOG_FATAL
*   LOG_DEBUG will only be compiled with DEBUG macro
*
*   you can use it like printf:
*   LOG_INFO("foo"); // logs "INFO  <time> foo"
*   int foo = 10; const char* bar = "mongo-moose";
*   LOG_DEBUG("i see %1% %2%!", foo, bar);
*   // logs "DEBUG <time> i see 10 mongo-moose!"
*   LOG_FATAL will exit immediateloy after logging
*
*   functions for changing logging behaviour:
*   void log_set_console_level(Level level);
*   void log_set_file_level(Level level);
*   void log_set_file(string file_name, Level level);
*   function for converting a string to log level
*   bool log_string_to_level(string level_string, Level* level);
*/

#ifndef LOG_H
#define LOG_H

#include <stdbool.h>

enum log_level {
    log_debug = 0,
    log_info,
    log_warn,
    log_error,
    log_fatal,
    log_off
};

#ifdef DEBUG
    #define LOG_DEBUG(...) log_log(log_debug, __VA_ARGS__)
#else
    #define LOG_DEBUG(...)
#endif

#define LOG_INFO(...) log_log(log_info, __VA_ARGS__) 
#define LOG_WARN(...) log_log(log_warn, __VA_ARGS__) 
#define LOG_ERROR(...) log_log(log_error, __VA_ARGS__) 
#define LOG_FATAL(...) log_log(log_fatal, __VA_ARGS__) 

void log_log(enum log_level level, const char* fmt, ...);
void log_set_console_level(enum log_level level);
void log_set_file_level(enum log_level level);
void log_set_file(const char* file, enum log_level level);
bool log_string_to_level(const char* name, enum log_level* level);

#endif // LOG_H
