/*
*   demosauce - fancy icecast source client
*
*   this source is published under the GPLv3 license.
*   http://www.gnu.org/licenses/gpl.txt
*   also, this is beerware! you are strongly encouraged to invite the
*   authors of this software to a beer when you happen to meet them.
*   copyright MMXIII by maep
*/

#define _POSIX_C_SOURCE 200112L

#include <string.h>
#include <strings.h>
#include <stdlib.h>
#include <stdio.h>
#include <ctype.h>
#include <assert.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <netdb.h>
#include "util.h"
#include "log.h"
#include "effects.h"

#define MEM_ALIGN       32
#define SOCKET_BLOCK    1024

void* util_malloc(size_t size)
{
    void* ptr = NULL;
    int err = posix_memalign(&ptr, MEM_ALIGN, size);
    return err ? NULL : ptr;
}    

void* util_realloc(void* ptr, size_t size)
{
    if (ptr) {
        ptr = realloc(ptr, size);
        if ((size_t)ptr % MEM_ALIGN != 0) {
            void* tmp_ptr = util_malloc(size);
            memmove(tmp_ptr, ptr, size);
            free(ptr);
            ptr = tmp_ptr;
        }
    } else {
        ptr = util_malloc(size);
    }
    return ptr;
}

void util_free(void* ptr)
{
    free(ptr);
}

//-----------------------------------------------------------------------------

bool util_isfile(const char* path)
{
    struct stat buf = {0};
    int err = stat(path, &buf);
    bool isfile = !err && S_ISREG(buf.st_mode);
    LOG_DEBUG("[isfile] '%s' %s", path, BOOL_STR(isfile));
    return isfile;
}

long util_filesize(const char* path)
{
    struct stat buf = {0};
    int err = stat(path, &buf);
    long size = err ? -1 : buf.st_size;
    LOG_DEBUG("[filesize] '%s' %ld", path, size);
    return size;
}

//-----------------------------------------------------------------------------

char* util_strdup(const char* str)
{
    if (!str)
        return NULL;
    char* s = util_malloc(strlen(str) + 1);
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

static char* keyval_impl(char* out, int size, const char* heap, const char* key, const char* fallback)
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
            char* value = out ? out : util_malloc(span + 1);
            memmove(value, tmp, span);
            value[span] = 0;
            LOG_DEBUG("[keyval] '%s' = '%s'", key, value);
            return value;
        } else {
            LOG_WARN("[keyval] buffer too small for value '%s'", key);
        }
    }

    LOG_DEBUG("[keyval] '%s' = '%s' (fallback)", key, fallback);    
    if (!out && fallback) {
        return util_strdup(fallback);
    } else if (out && fallback && strlen(fallback) < size) {
        return strcpy(out, fallback);
    } else if (out && fallback && size) {
        LOG_WARN("[keyval] buffer too small for fallback (%s, %s)", key, fallback);
        return strcpy(out, "");
    } else {
        return NULL;
    }
}

void keyval_str(char* out, int outsize, const char* heap, const char* key, const char* fallback)
{
    keyval_impl(out, outsize, heap, key, fallback);
}

char* keyval_str_dup(const char* heap, const char* key, const char* fallback)
{
    return keyval_impl(NULL, 0, heap, key, fallback);
}

long keyval_int(const char* heap, const char* key, long fallback)
{
    char tmp[16] = {0};
    keyval_impl(tmp, sizeof(tmp), heap, key, NULL);
    char* str_end = NULL;
    long val = strtol(tmp, &str_end, 0);
    return str_end != tmp ? val : fallback;
}

double keyval_real(const char* heap, const char* key, double fallback)
{
    char tmp[16] = {0};
    keyval_impl(tmp, sizeof(tmp), heap, key, NULL);
    char* str_end = NULL;
    double val = strtod(tmp, &str_end);
    return str_end != tmp ? val : fallback;
}
  
bool keyval_bool(const char* heap, const char* key, bool fallback)
{
    char tmp[8] = {0};
    keyval_impl(tmp, sizeof(tmp), heap, key, NULL);
    return strlen(tmp) ? !strcasecmp(tmp, "true") : fallback;
}

//-----------------------------------------------------------------------------

int socket_connect(const char* host, int port)
{
    int                 fd          = -1;
    char                portstr[8]  = {0};
    struct addrinfo*    info        = NULL;
    struct addrinfo     hints       = {0};
    
    LOG_DEBUG("[socket] connecting to %s:%d", host, port);
    if (snprintf(portstr, sizeof(portstr), "%d", port) < 0)
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
    LOG_DEBUG("[socket] failed to connect to %s:%d", host, port);
    return -1;
}

int socket_listen(int port, bool local)
{
    int                 fd0         = -1;
    int                 fd1         = -1;
    char                portstr[8]  = {0};
    struct addrinfo*    info        = NULL;
    struct addrinfo     hints       = {0};
    
    LOG_DEBUG("[socket] listening on %d", port);
    if (snprintf(portstr, sizeof(portstr), "%d", port) < 0)
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
    LOG_DEBUG("[socket] failed to listen on %d", port);
    return -1;
}

bool socket_write(int socket, const void* buffer, long size)
{
    ssize_t bytes = send(socket, buffer, size, 0);
    if (bytes < 0)
        LOG_DEBUG("[socket] write failed");
    else
        LOG_DEBUG("[socket] write %d bytes", bytes);
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
            LOG_DEBUG("[socket] read failed");
            return false;
        }
        total += bytes;
    } while (bytes == SOCKET_BLOCK);

    buffer->size = total;
    ((char*)buffer->data)[total] = 0;
    LOG_DEBUG("[socket] read %d bytes", buffer->size);
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

void buffer_resize(struct buffer* buf, long size) 
{
    buf->size = MAX(0, size);
    if (buf->max_size < buf->size) {
        buf->data = util_realloc(buf->data, buf->size);
        buf->max_size = buf->size;
        LOG_DEBUG("[buffer] %p resize to %ld bytes", buf, size);
    }
}

void buffer_free(struct buffer* buf)
{
    util_free(buf->data);
    memset(buf, 0, sizeof(struct buffer));
    LOG_DEBUG("[buffer] %p free", buf);
}

//-----------------------------------------------------------------------------

void stream_resize(struct stream* s, int frames, int channels)
{
    assert(channels >= 1 && channels <= MAX_CHANNELS);
    if (frames <= s->max_frames && channels == s->channels)
        return;
    if (frames > s->max_frames)
        LOG_DEBUG("[stream] %p resize to %d frames", s, frames);
    s->channels = channels;
    s->max_frames = MAX(frames, s->max_frames);
    for (int ch = 0; ch < channels; ch++)
        s->buffer[ch] = util_realloc(s->buffer[ch], s->max_frames * sizeof (float));
}

void stream_free(struct stream* s)
{
    for (int i = 0; i < MAX_CHANNELS; i++)
        util_free(s->buffer[i]);
    memset(s, 0, sizeof(struct stream));
}

void stream_append(struct stream* s, struct stream* source, int frames)
{
    assert(source->channels >= 1 && source->channels <= MAX_CHANNELS);
    frames = CLAMP(0, frames, source->frames);
    s->frames += frames;
    stream_resize(s, s->frames, source->channels);
    for (int ch = 0; ch < s->channels; ch++)
        memmove(s->buffer[ch], source->buffer[ch], frames * sizeof (float));
}

void stream_append_convert(struct stream* s, void** source, int type, int frames, int channels)
{
    assert(channels >= 1 && channels <= MAX_CHANNELS);
    float* buffs[MAX_CHANNELS] = {0};
    stream_resize(s, s->frames + frames, channels);
    for (int ch = 0; ch < MAX_CHANNELS; ch++)
        buffs[ch] = s->buffer[ch] + s->frames;
    fx_convert_to_float(source, buffs, type, frames, channels);
    s->frames += frames;
}

void stream_drop(struct stream* s, int frames)
{
    frames = CLAMP(0, frames, s->frames);
    s->frames -= frames;
    if (s->frames > 0)
        for (int ch = 0; ch < s->channels; ch++)
            memmove(s->buffer[ch], s->buffer[ch] + frames, s->frames * sizeof (float));
}

void stream_zero(struct stream* s, int offset, int frames)
{
    frames = CLAMP(0, s->max_frames - (offset + frames), frames);
    for (int ch = 0; ch < s->channels; ch++)
        memset(s->buffer[ch] + offset, 0, frames * sizeof (float));
    s->frames = offset + frames;
}
