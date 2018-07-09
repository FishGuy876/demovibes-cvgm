import queuefetcher
player = queuefetcher.song_finder()

def ices_init ():
    return 1
def ices_shutdown ():
    return 1
def ices_get_next ():
    return player.get_next_song()
def ices_get_metadata ():
    return player.get_metadata()
