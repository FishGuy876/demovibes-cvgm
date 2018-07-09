/*
*   demosauce - fancy icecast source client
*
*   this source is published under the GPLv3 license.
*   http://www.gnu.org/licenses/gpl.txt
*   also, this is beerware! you are strongly encouraged to invite the
*   authors of this software to a beer when you happen to meet them.
*   copyright MMXIII by maep
*/

/*
    a fancy source client for scenemusic.net
    slapped together by maep 2009 - 2011
    ported from c++ to c in 2013

    BEHOLD, A FUCKING PONY!

               .,,.
         ,;;*;;;;,
        .-'``;-');;.
       /'  .-.  /;;;
     .'    \d    \;;               .;;;,
    / o      `    \;    ,__.     ,;*;;;*;,
    \__, _.__,'   \_.-') __)--.;;;;;*;;;;,
     `""`;;;\       /-')_) __)  `\' ';;;;;;
        ;*;;;        -') `)_)  |\ |  ;;;;*;
        ;;;;|        `---`    O | | ;;*;;;
        *;*;\|                 O  / ;;;;;*
       ;;;;;/|    .-------\      / ;*;;;;;
      ;;;*;/ \    |        '.   (`. ;;;*;;;
      ;;;;;'. ;   |          )   \ | ;;;;;;
      ,;*;;;;\/   |.        /   /` | ';;;*;
       ;;;;;;/    |/       /   /__/   ';;;
       '*jgs/     |       /    |      ;*;
            `""""`        `""""`     ;'

    pony source (yeah... geocities, haha):
    http://www.geocities.com/SoHo/7373/index.htm#home
*/

#include <stdio.h>
#include <stdlib.h>

#include "settings.h"
#include "cast.h"
#include "bassdecoder.h"

int main(int argc, char** argv)
{
#ifdef ENABLE_BASS
    if (!bass_loadso()) {
        puts("failed to load libbass.so");
        return EXIT_FAILURE;
    }
#endif
    puts(DEMOSAUCE_VERSION);
    settings_init(argc, argv);
    log_set_console_level(settings_log_console_level);
    log_set_file(settings_log_file, settings_log_file_level);
    puts("The spice must flow!");
    cast_run();
    return EXIT_SUCCESS;
}

