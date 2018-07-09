
/* convenience header to include commonly used headers in this project */

#ifndef ALL_H
#define ALL_H

// standard c libs
#include <assert.h>
#include <ctype.h>
#include <limits.h>
#include <math.h>
#include <signal.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <time.h>

// project headers
#include "log.h"
#include "util.h"

// git id
#define XSTR_(s)        "-"#s
#define XSTR(s)         XSTR_(s)
#ifdef BUILD_ID
    #define ID_STR      XSTR(BUILD_ID)
#else
    #define ID_STR
#endif

#endif
