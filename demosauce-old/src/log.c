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
#include <stdarg.h>
#include <time.h>
#include <stdio.h>
#include <strings.h>
#include "log.h"

static enum log_level   console_level   = log_off;
static enum log_level   file_level      = log_off;
static FILE*            logfile         = NULL;

void log_set_console_level(enum log_level level)
{
    console_level = level;
}

void log_set_file_level(enum log_level level)
{
    file_level = level;
}

void log_set_file(const char* file_name, enum log_level level)
{
    time_t rawtime;
    char buf[4000] = {0};
    if (level == log_off)
        return;
    file_level = level;
    time(&rawtime);
    if (!strftime(buf, sizeof(buf) - 1, file_name, localtime(&rawtime))) {
        puts("WARNING: malformed log file name");
        return;
    }
    logfile = fopen(buf, "w");
    if (!logfile) 
        puts("WARNING: could not open log file");
}

static void fvlog(FILE* f, enum log_level lvl, const char* fmt, va_list args)
{
    const char* levels[] = {"DEBUG", "INFO ", "WARN ", "ERROR", "DOOOM"};
    time_t rawtime;
    char buf[30] = {0};
    time(&rawtime);
    if (!strftime(buf, 30, "%Y-%m-%d %X", localtime(&rawtime)))
        buf[0] = 0;
    fprintf(f, "%s %s ", levels[lvl], buf);
    vfprintf(f, fmt, args);
    fputc('\n', f);
    fflush(f);
}

void log_log(enum log_level lvl, const char* fmt, ...)
{
    if (lvl >= console_level || (lvl >= file_level && logfile)) {
        va_list args;
        va_start(args, fmt);
        
        if (lvl >= console_level) 
            fvlog(stdout, lvl, fmt, args);
        if (lvl >= file_level && logfile)
            fvlog(logfile, lvl, fmt, args);
            
        va_end(args);
    }

    if (lvl == log_fatal) {
        puts("terminated");
        if (logfile) 
            fputs("terminated", logfile);
        exit(EXIT_FAILURE);
    }
}

bool log_string_to_level(const char* name, enum log_level* level)
{
    const char* lstr[] = {"debug", "info", "warn", "error", "fatal", "off"};
    enum log_level llvl[] = {log_debug, log_info, log_warn, log_error, log_fatal, log_off};
    for (int i = 0; i < 7; i++) {
        if (!strcasecmp(name, lstr[i])) {
            *level = llvl[i];
            return true;
        }
    }
    return false;
}

