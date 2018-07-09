/*
*   demosauce - fancy icecast source client
*
*   this source is published under the GPLv3 license.
*   http://www.gnu.org/licenses/gpl.txt
*   also, this is beerware! you are strongly encouraged to invite the
*   authors of this software to a beer when you happen to meet them.
*   copyright MMXIII by maep
*/

#ifndef BASSDEC_H
#define BASSDEC_H

#include "util.h"

bool    bass_loadso(void); 
bool    bass_probe(const char* path);
bool    bass_load(struct decoder* dec, const char* path, const char* options, int samplerate);
void    bass_set_loop_duration(struct decoder* dec, double duration);
float   bass_loopiness(const char* path);

#endif

