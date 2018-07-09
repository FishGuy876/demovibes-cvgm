/*
*   demosauce - fancy icecast source client
*
*   this source is published under the GPLv3 license.
*   http://www.gnu.org/licenses/gpl.txt
*   also, this is beerware! you are strongly encouraged to invite the
*   authors of this software to a beer when you happen to meet them.
*   copyright MMXIII by maep
*/

#ifndef FFDECODER_H
#define FFDECODER_H

#include "util.h"

bool    ff_probe(const char* filename);
bool    ff_load(struct decoder* dec, const char* file_name);

#endif // FFDECODER_H

