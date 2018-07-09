from django.core.management import setup_environ
import settings
setup_environ(settings)
from webview.models import *

from string import *

def move(linktype, field, url, name, rx, icon=None):
    if name in ("World of Spectrum"): #Text field(s)
        kwargs = {field: ""}
    else:
        fname = "%s__isnull" % field
        kwargs = {fname : True}
    songs = Song.objects.exclude(**kwargs)
    if songs:
        print "Doing", name
        gbl = GenericBaseLink.objects.create(name=name, link=url, regex=rx, linktype=linktype)
        for s in songs:
            val = getattr(s, field)
            if val:
                print " Song", s, val
                GenericLink.objects.create(content_object=s, value=val, link=gbl)

def forwards():

    "Write your forwards methods here."
    u = [
        ("S", "al_id", "http://www.atarilegend.com/games/games_detail.php?game_id=%linkval%", "Atari Legends", "\d+"),
        ("S", "cvgm_id", "http://www.cvgm.net/demovibes/song/%linkval%/", "CVGM SongID", "\d+"),
        ("S", "dtv_id", "http://www.demoscene.tv/prod.php?id_prod=%linkval%", "Demoscene.TV", "\d+"),
        ("S", "hol_id", "http://hol.abime.net/%linkval%", "Hall Of Light", "\d+"),
        ("S", "lemon_id", "http://www.lemon64.com/games/details.php?ID=%linkval%", "Lemon 64", "\d+"),
        ("S", "projecttwosix_id", "http://project2612.org/details.php?id=%linkval%", "Project2612", "\d+"),
        ("S", "wos_id", "http://www.worldofspectrum.org/infoseekid.cgi?id=%linkval%", "World of Spectrum", "\d+"),
        ("S", "zxdemo_id", "http://zxdemo.org/item.php?id=%linkval%", "ZXDemo", "\d+"),
        #("S", "pouetid", "http://pouet.net/prod.php?which=%linkval%", "Pouet", "\d+"), -- no move, used for other stuff...
        ("S", "necta_id", "http://www.scenemusic.net/demovibes/song/%linkval%/", "Nectarine", "\d+"),
        #("S", "_id", "%linkval%", "", "\d+"),
    ]
    for e in u:
        move(*e)

#print "This is unfinished. Exiting"
print "Migrating song links"
forwards()
