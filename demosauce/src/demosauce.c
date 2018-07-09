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
    development started in 2009, originally in c++

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

    pony source: http://www.geocities.com/SoHo/7373/index.htm#home
*/

#include "settings.h"
#include "decoder.h"
#include "cast.h"
#include "all.h"

int main(int argc, char** argv)
{
    decoder_init();
    puts("demosauce 0.6.0"ID_STR);
    settings_init(argc, argv);
    log_set_console_level(settings_log_console_level);
    log_set_file(settings_log_file, settings_log_file_level);
    puts("The spice must flow!");
    cast_run();
    return EXIT_SUCCESS;
}

