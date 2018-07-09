/*
*   libReplayGain, based on mp3gain 1.5.1
*   LGPL 2.1
*   http://www.gnu.org/licenses/old-licenses/lgpl-2.1.txt
*/

#ifndef REPLAY_GAIN_H
#define REPLAY_GAIN_H

#ifdef __cplusplus
    extern "C" {
#endif

#define RG_SIGNED16 1
#define RG_SIGNED32 2
#define RG_FLOAT32  3

struct rg_context;

/* samplerate   44100, 48000, etc...
 * sampletype:  RG_SIGNED16, RG_SIGNED32, RG_FLOAT32
 * channels:    1, 2
 * interleaved: 0 (false), 1 (true)
 */
struct rg_context*  rg_new(int samplerate, int sampletype, int channels, int interleaved);
void                rg_free(struct rg_context* ctx);

/* if stereo input is planar (not interleaved) data must point to a 
 * list of two pointers:
 *
 * float* foo[2] = {left, right};
 * rg_analyze(ctx, foo, frames);
 */
void                rg_analyze(struct rg_context* ctx, void* data, int frames);

float               rg_title_gain(struct rg_context* ctx);
float               rg_album_gain(struct rg_context* ctx);

#ifdef __cplusplus
    }
#endif

#endif /* REPLAY_GAIN_H */

