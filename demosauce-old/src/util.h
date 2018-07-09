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

#include <stddef.h>
#include <stdbool.h>
 
#define MAX_CHANNELS    2

#define INFO_SEEKABLE   1
#define INFO_FFMPEG     (1 << 1)
#define INFO_BASS       (1 << 2)  
#define INFO_MOD        (1 << 16)
#define INFO_AMIGAMOD   (1 << 17)

#define BOOL_STR(x)     ((x) ? "true" : "false") 
#define XSTR_(s)        "-"#s
#define XSTR(s)         XSTR_(s)
#ifdef BUILD_ID
    #define ID_STR      XSTR(BUILD_ID)
#else
    #define ID_STR
#endif
#define DEMOSAUCE_VERSION "demosauce 0.4.1"ID_STR" - C++ sucks edition"

#define COUNT(array)    (sizeof(array) / sizeof(array[0]))
#define MIN(a, b)       ((a) < (b) ? (a) : (b))
#define MAX(a, b)       ((a) > (b) ? (a) : (b))
#define CLAMP(a, b, c)  ((b) < (a) ? (a) : (b) > (c) ? (c) : (b))

enum sampleformat {                 // planar formats must have odd number
    SF_INT16I       = 0,            // interleaved 16 bit int    
    SF_INT16P       = 1,            // planar 16 bit int
    SF_FLOAT32I     = 2,            // interleaved 32 bit float
    SF_FLOAT32P     = 3             // planar 32 bit float
};

struct buffer {
    void*       data;
    long        size;                   // number of valid data in buffer
    long        max_size;               // capacity of allocated buffer
};

struct stream {
    float*      buffer[MAX_CHANNELS];   // buffer[0] left channel, buffer[1] right channel
    long        frames;                 // number of samples in the buffer, same for mono and stereo
    long        max_frames;             // capacity of allocated buffers
    int         channels;               // 1 mono, 2 stereo
    bool        end_of_stream;          // is set when stream ended
};

struct info {
    const char* codec;
    float       bitrate;                // kbps
    long        frames;                 // length of file in frames, devide by samplerate to get seconds
    int         channels;               // 1 mono, 2 stereo
    int         samplerate;
    int         flags;                  // one or more of the INFO_* flags may be set
};

/*  decode(decoder, stream, frames)
 *      This function will decode up to <frames> into <stream>, buy may decode less, even zero.
 *      Any data in stream is overwritten. If the stream.end_of_stream flag is set, no more
 *      data is available. decode must allow subsequent calls even after the end of stream is
 *      reached. In that case steram.frames is set to 0 and stream.end_of_stream is set.
 *
 *  metadata(decoder, key)
 *      This function returns a value for a given <key>. The most common keys are 'title' and 'artist'.
 *      The returned string must be freed with util_free. NULL is returned if no data is available.
 *
 *  seek(decoder, frames)
 *      Seek to position. <frames> is absolute, counting from the beginning of the file.
 */
struct decoder {
    void        (*free)(struct decoder*);
    void        (*seek)(struct decoder*, long);
    void        (*info)(struct decoder*, struct info*);
    char*       (*metadata)(struct decoder*, const char*);
    void        (*decode)(struct decoder*, struct stream*, int);
    void*       handle;
};


// equivalent to stdlib functions, but memory is aligned to 32 byte boundry. 
void*   util_malloc(size_t size);
void*   util_realloc(void* ptr, size_t size);
void    util_free(void* ptr);


/*  misc functions
 *  util_strdup
 *      duplicates string. returned string must be freed with util_free. return NULL on NULL.
 *  util_trim
 *      removes leading an tailing spaces of a string. returned string is same as <str>.
 *  util_isfile
 *      return true if <path> is a regular file
 *  util_filesize
 *      returns size of <path> in bytes
 */
char*   util_strdup(const char* str);
char*   util_trim(char* str);          
bool    util_isfile(const char* path);
long    util_filesize(const char* path);

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
long    keyval_int(const char* str, const char* key, long fallback);
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
void    buffer_resize(struct buffer* b, long size);
void    buffer_free(struct buffer* b);
void    buffer_zero(struct buffer* b);

/*  stream_resize
 *      resize <stream> to hold at least <frames> frames in <channels> channels. if <frames> is
 *      smaller than s->max_frames this function has no effect, unless <channels> changes number
 *      of channels.
 *  stream_free
 *      frees the buffers and set all members of <stram> to zero.
 *      stream_append
 *      append <frames> frames of <source> to <stream>. <source> will not be changed.
 *      <stream> might be increased to hold all data.
 *  stream_append_convert
 *      append <frames> frames of <source> to <stream>. <type> must be one of the formats
 *      in enum sampleformat. source[0] holds the left channel, source[1] the right channel
 *      if applicable. if the data is interleaved only source[0] is set.
 *  stream_drop
 *      remove <frames> frames from the beginning of the <stream>.
 *  stream_zero
 *      set <frames> frames to zero, starting with <offset> frames.
 */
void    stream_resize(struct stream* s, int frames, int channels);
void    stream_free(struct stream* s);
void    stream_append(struct stream* s, struct stream* source, int frames);
void    stream_append_convert(struct stream* s, void** source, int type, int frames, int channels);
void    stream_drop(struct stream* s, int frames);
void    stream_zero(struct stream* s, int offset, int frames);

#endif // UTIL_H
