/*
*   demosauce - fancy icecast source client
*
*   this source is published under the GPLv3 license.
*   http://www.gnu.org/licenses/gpl.txt
*   also, this is beerware! you are strongly encouraged to invite the
*   authors of this software to a beer when you happen to meet them.
*   copyright MMXIII by maep
*/

#ifndef UTIL_H
#define UTIL_H

#include "all.h"

struct buffer {
    void*       data;
    int64_t     size;       // number of valid data in buffer
    int64_t     max_size;   // capacity of allocated buffer
};

// like realloc, but ensures ptr is aligned to <align> bits.
void* util_realign(void* ptr, size_t size, size_t align);

/*  misc functions
 *  util_strdup
 *      duplicates string. same as strdup but doesn't crash NULL.
 *  util_trim
 *      removes leading an tailing spaces of a string. returned string is same as <str>.
 *  util_isfile
 *      return true if <path> is a regular file
 *  util_filesize
 *      returns size of <path> in bytes
 */
//char*   util_strdup(const char* str);
char*   util_trim(char* str);
bool    util_isfile(const char* path);
int64_t util_filesize(const char* path);

/*  socket_connect
 *      opens tcp socket on <host>:<port>. returns -1 on error. close with socket_close.
 *  socket_listen
 *      opens a tcp socket on localhost:<port> and blocks until a connection is made.
 *      return -1 on error. close with socket_close
 *  socket_write
 *      write <buffer> of <size> to <socket>. returns true on success.
 *  socekt_read
 *      reads data into <socket>. <buffer> will be resized if more space is needed.
 *      <buffer>.size is set to the number of read bytes. returns true on success.
 */
int     socket_connect(const char* host, int port);
int     socket_listen(int port, bool local);
bool    socket_write(int socket, const void* buffer, long size);
bool    socket_read(int socket, struct buffer* buffer);
void    socket_close(int socket);

/*  these functions all extract a value from a string in the form of key1=val1\nkey2=val2\n...
 *  any spaces will be removed. it is expected that one line contains exactly one key value pair.
 *  keyval_str
 *      writes the value or <fallback> into <outbuf> if <key> is not found. if the value is
 *      too large to fit in <outbuf> <fallback> will be used instead. if <fallback> is too
 *      big, <outbuf> will be an emty string. <fallback> may be NULL.
 *  keyval_str_dup
 *      same as keyval_str, but the value and the fallback are put into a newly allocated
 *      string that must be freed with util_free.
 */
void    keyval_str(char* outbuf, int outsize, const char* str, const char* key, const char* fallback);
char*   keyval_str_dup(const char* str, const char* key, const char* fallback);
int64_t keyval_int(const char* str, const char* key, int64_t fallback);
double  keyval_real(const char* str, const char* key, double fallback);
bool    keyval_bool(const char* str, const char* key, bool fallback);

/*  buffer_resize
 *      resize <b> to hold at least <size> bytes. if buffer is already large enough
 *      only <b>.size will be set.
 *  buffer_free
 *      free <b> and set all members of <buffer> to zero.
 *  buffer_zero
 *      zeros <b>.size bytes.
 */
void    buffer_resize(struct buffer* b, int64_t size);
void    buffer_free(struct buffer* b);
void    buffer_zero(struct buffer* b);

double  db_to_amp(double db);
double  amp_to_db(double amp);

/* return value if within of min, max. min must be smaller than max */
static inline int     iclamp(int min, int value, int max) { return value < min ? min : value > max ? max : value; }
static inline double  fclamp(double min, double value, double max) { return value < min ? min : value > max ? max : value; }
static inline int64_t iclamp64(int64_t min, int64_t value, int64_t max) { return value < min ? min : value > max ? max : value; }

/* min/max functions */
static inline int     imax(int a, int b) { return a < b ? b : a; }
static inline int     imin(int a, int b) { return a < b ? a : b; }
static inline int64_t imax64(int64_t a, int64_t b) { return a < b ? b : a; }
static inline int64_t imin64(int64_t a, int64_t b) { return a < b ? a : b; }

#endif // UTIL_H
