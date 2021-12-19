/*
*   demosauce - fancy icecast source client
*
*   this source is published under the GPLv3 license.
*   http://www.gnu.org/licenses/gpl.txt
*   also, this is beerware. you are strongly encouraged to invite the
*   author(s) of this software to a beer when you happen to meet them.
*   copyright MMXIII by maep
*/

#define _POSIX_C_SOURCE 200112L // for glibc getaddrinfo
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include "all.h"

enum { SOCKET_BLOCK = 1024 };

double db_to_amp(double db)
{
    return pow(10, db / 20);
}

double amp_to_db(double amp)
{
    return log10(amp) * 20;
}

//-----------------------------------------------------------------------------

void* util_memalign(size_t size, size_t align)
{
    void* ptr = NULL;
    int err = posix_memalign(&ptr, align, size);
    assert(!err);
    return ptr;
}

void* util_realign(void* ptr, size_t size, size_t align)
{
    if (ptr) {
        ptr = realloc(ptr, size);
        if ((size_t)ptr % align != 0) {
            log_debug("[malloc] realloc not aligned");
            void* tmp_ptr = util_memalign(size, align);
            memmove(tmp_ptr, ptr, size);
            free(ptr);
            ptr = tmp_ptr;
        }
    } else {
        ptr = util_memalign(size, align);
    }
    return ptr;
}

//-----------------------------------------------------------------------------

bool util_isfile(const char* path)
{
    struct stat buf = {0};
    int err = stat(path, &buf);
    bool isfile = !err && S_ISREG(buf.st_mode);
    log_debug("[isfile] '%s' %s", path, isfile ? "true" : "false");
    return isfile;
}

int64_t util_filesize(const char* path)
{
    struct stat buf = {0};
    int err = stat(path, &buf);
    int64_t size = err ? -1 : buf.st_size;
    log_debug("[filesize] '%s' %"PRIi64, path, size);
    return size;
}

//-----------------------------------------------------------------------------

char* util_strdup(const char* str)
{
    if (!str)
        return NULL;
    char* s = calloc(strlen(str) + 1, 1);
    strcpy(s, str);
    return s;
}

char* util_trim(char* str)
{
    if (!str)
        return NULL;
    char* tmp = str;
    while (isspace(*tmp))
        tmp++;
    memmove(str, tmp, strlen(tmp) + 1);
    tmp += strlen(tmp);
    while (tmp > str && isspace(tmp[-1]))
        tmp--;
    *tmp = 0;
    return str;
}

static const char* skip_line(const char* str)
{
    str = strchr(str, '\n');
    return str ? str + 1 : NULL;
}

static char* keyval(char* out, int size, const char* heap, const char* key, const char* fallback)
{
    const char* tmp         = heap;
    size_t      span        = 0;
    bool        have_key    = false;

    while (tmp && *tmp) {
        tmp += strspn(tmp, " \t");                  // skip space before key
        if (strncmp(tmp, key, strlen(key))) {       // see if matches key
            tmp = skip_line(tmp);
            continue;
        }
        tmp += strlen(key);
        tmp += strspn(tmp, " \t");                  // skip space after key
        if (!*tmp || *tmp != '=') {                 // check for =
            tmp = skip_line(tmp);
            continue;
        }
        have_key = true;
        tmp += strspn(tmp + 1, " \t") + 1;          // skip space before value
        span = strcspn(tmp, "\r\n");                // find end of line
        while (span && isspace(tmp[span - 1]))      // remove tailing whitespace
            span--;
        break;
    }

    if (have_key) {
        if (!out || span < size) {
            char* value = out ? out : malloc(span + 1);
            sprintf(value, "%.*s", (int)span, tmp);
            log_debug("[keyval] %s = %s", key, value);
            return value;
        } else {
            log_warn("[keyval] output buffer too small %s = %.*s", key, (int)span, tmp);
        }
    }

    log_debug("[keyval] %s = %s (fallback)", key, fallback ? fallback : "NULL");
    if (!out && fallback) {
        return util_strdup(fallback);
    } else if (out && fallback && strlen(fallback) < size) {
        return strcpy(out, fallback);
    } else if (out && fallback && size) {
        log_warn("[keyval] output buffer too small %s = %s (fallback)", key, fallback);
        return strcpy(out, "");
    } else {
        return NULL;
    }
}

void keyval_str(char* out, int outsize, const char* heap, const char* key, const char* fallback)
{
    keyval(out, outsize, heap, key, fallback);
}

char* keyval_str_dup(const char* heap, const char* key, const char* fallback)
{
    return keyval(NULL, 0, heap, key, fallback);
}

int64_t keyval_int(const char* heap, const char* key, int64_t fallback)
{
    char tmp[16] = {0};
    keyval(tmp, sizeof tmp, heap, key, NULL);
    char* str_end = NULL;
    int64_t val = strtoll(tmp, &str_end, 0);
    return str_end != tmp ? val : fallback;
}

double keyval_real(const char* heap, const char* key, double fallback)
{
    char tmp[16] = {0};
    keyval(tmp, sizeof tmp, heap, key, NULL);
    char* str_end = NULL;
    double val = strtod(tmp, &str_end);
    return str_end != tmp ? val : fallback;
}

bool keyval_bool(const char* heap, const char* key, bool fallback)
{
    char tmp[8] = {0};
    keyval(tmp, sizeof tmp, heap, key, NULL);
    return strlen(tmp) ? !strcasecmp(tmp, "true") : fallback;
}

//-----------------------------------------------------------------------------

#ifndef MSG_NOSIGNAL
#define MSG_NOSIGNAL 0 // osx extrawurst
#endif

int socket_connect(const char* host, int port)
{
    int                 fd          = -1;
    char                portstr[8]  = {0};
    struct addrinfo*    info        = NULL;
    struct addrinfo     hints       = {0};

    log_debug("[socket] connecting to %s:%i", host, port);
    if (snprintf(portstr, sizeof portstr, "%i", port) < 0)
        goto error;

    hints.ai_family     = AF_UNSPEC;
    hints.ai_socktype   = SOCK_STREAM;
    if (getaddrinfo(host, portstr, &hints, &info) != 0)
        goto error;

    for (struct addrinfo* ai = info; ai; ai = ai->ai_next) {
        fd = socket(ai->ai_family, ai->ai_socktype, ai->ai_protocol);
        if (fd < 0)
            continue;   // error
        if (connect(fd, ai->ai_addr, ai->ai_addrlen) == 0)
            break;      // success
        close(fd);
        fd = -1;
    }

    freeaddrinfo(info);
    if (fd >= 0)
        return fd;

error:
    log_debug("[socket] failed to connect to %s:%i", host, port);
    return -1;
}

int socket_listen(int port, bool local)
{
    int                 fd0         = -1;
    int                 fd1         = -1;
    char                portstr[8]  = {0};
    struct addrinfo*    info        = NULL;
    struct addrinfo     hints       = {0};

    log_debug("[socket] listening on %i", port);
    if (snprintf(portstr, sizeof portstr, "%i", port) < 0)
        goto error;

    hints.ai_family     = AF_UNSPEC;
    hints.ai_socktype   = SOCK_STREAM;
    hints.ai_flags      = AI_PASSIVE;
    if (getaddrinfo(local ? "localhost" : NULL, portstr, &hints, &info) != 0)
        goto error;

    for (struct addrinfo* ai = info; ai; ai = ai->ai_next) {
        fd0 = socket(ai->ai_family, ai->ai_socktype, ai->ai_protocol);
        if (fd0 < 0)
            goto error;
        if (bind(fd0, ai->ai_addr, ai->ai_addrlen) == 0)
            break;
        close(fd0);
    }

    if (listen(fd0, 1) < 0)
        goto error;
    fd1 = accept(fd0, NULL, NULL);
    if (fd1 < 0)
        goto error;

    freeaddrinfo(info);
    close(fd0);
    return fd1;

error:
    freeaddrinfo(info);
    close(fd0);
    close(fd1);
    log_debug("[socket] failed to listen on %i", port);
    return -1;
}

bool socket_write(int socket, const void* buffer, long size)
{
    ssize_t bytes = send(socket, buffer, size, MSG_NOSIGNAL);
    if (bytes < 0) {
        log_debug("[socket] write failed");
    } else {
        log_debug("[socket] write %zi bytes", bytes);
    }
    return bytes >= 0;
}

bool socket_read(int socket, struct buffer* buffer)
{
    ssize_t bytes = 0;
    long    total = 0;
    buffer->size = 0;

    do {
        buffer_resize(buffer, total + SOCKET_BLOCK);
        bytes = recv(socket, (char*)buffer->data + total, SOCKET_BLOCK, 0);
        if (bytes < 0) {
            buffer->size = 0;
            log_debug("[socket] read failed");
            return false;
        }
        total += bytes;
    } while (bytes == SOCKET_BLOCK);

    buffer->size = total;
    ((char*)buffer->data)[total] = 0;
    log_debug("[socket] read %"PRIi64" bytes", buffer->size);
    return bytes > 0;
}

void socket_close(int socket)
{
    close(socket);
}

//-----------------------------------------------------------------------------

void buffer_zero(struct buffer* buf)
{
    memset(buf->data, 0, buf->size);
}

void buffer_resize(struct buffer* buf, int64_t size)
{
    buf->size = imax64(1, size);
    if (buf->max_size < buf->size) {
        buf->data = realloc(buf->data, buf->size);
        buf->max_size = buf->size;
        log_debug("[buffer] %p resize to %"PRIi64" bytes", buf, size);
    }
}

void buffer_free(struct buffer* buf)
{
    free(buf->data);
    memset(buf, 0, sizeof *buf);
    log_debug("[buffer] %p free", buf);
}
