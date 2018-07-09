#ifndef DECODER_H
#define DECODER_H

#include "stream.h"
#include "all.h"

enum {
    INFO_SEEKABLE   = 1,        // file can be seeked
    INFO_EXACTLEN   = 1 << 1,   // length field in info is accurate
    INFO_MOD        = 1 << 16,  // file is a module
    INFO_AMIGAMOD   = 1 << 17   // file is a amiga module
};

struct info {
    const char* codec;
    double      bitrate;    // kbps
    double      length;     // length of file in seconds
    int         channels;   // 1 mono, 2 stereo
    int         samplerate;
    int         flags;      // INFO_* flags are stored here
};

/*  decode(decoder, stream, frames)
 *      This function will decode up to <frames> into <stream>, buy may decode less, even zero.
 *      Any data in stream is overwritten. If the stream.end_of_stream flag is set, no more
 *      data is available. decode must allow subsequent calls even after the end of stream is
 *      reached. In that case steram.frames is set to 0 and stream.end_of_stream is set.
 *
 *  metadata(decoder, key)
 *      This function returns a value for a given <key>. The most common keys are 'title' and 'artist'.
 *      The returned string must be freed with free. NULL is returned if no data is available.
 *
 *  seek(decoder, frames)
 *      Seek to position. <frames> is absolute, counting from the beginning of the file.
 *
 *  conttrol(decoder, name)
 *      Allows decoders to implement custom control functions. Arguments should be passed as
 *      key-vlaue pairs.
 *
 *  free(decoder)
 *      Frees the decoder, all it's resources and sets all struct members to zero.
 */
struct decoder {
    void        (*init)(void);                                              // optional
    void        (*free)(struct decoder*);
    bool        (*load)(struct decoder*, const char*, int, int, const char*);
    void        (*decode)(struct decoder*, struct stream*, int);
    void        (*seek)(struct decoder*, double);                           // optional
    void        (*info)(struct decoder*, struct info*);
    char*       (*metadata)(struct decoder*, const char*);
    const char* (*control)(struct decoder*, const char*);                   // optional
    bool        (*probe)(const char*);
    const char* name;
    void*       handle;
};

void        decoder_init();
bool        decoder_open(struct decoder* d, const char* path, int samplerate, int channels, const char* args);
void        decoder_free(struct decoder* d);
bool        decoder_load(struct decoder* d, const char* path, int samplerate, int channels, const char* args);
void        decoder_decode(struct decoder* d, struct stream* s, int frames);
void        decoder_info(struct decoder* d, struct info* info);
char*       decoder_metadata(struct decoder* d, const char* key);
const char* decoder_control(struct decoder* d, const char* arg);
bool        decoder_probe(const struct decoder* d, const char* file);

#ifdef ENABLE_BASS
extern const struct decoder bass_class; // bass, for popular module formats
#endif
extern const struct decoder ompt_class; // openmpt, for most module formats
extern const struct decoder hvl_class;  // hively replayer, for ahx and hvl
extern const struct decoder ff_class;   // ffmpeg, anything else
//extern const struct deocder fpsid_class;
//extern const struct decoder dumb_decoder;
#endif
