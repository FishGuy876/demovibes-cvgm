from math import atan
import logging
L = logging.getLogger("dv.webview.songlock")

# Base horizontal vote bias.  The model is symmetric around a vote average of
# 3 + hBiasBase.  So, if hBiasBase = 0.3, song ratings higher than 3.3 are
# considered good and song ratings lower than 3.3 are considered bad.
hBiasBase = 0.1

# Multiplication factor.  This value controls the strength of the deviation
# from a strictly linear model (the one we had before).  For smaller values
# of m, this model will approximate the linear model.  m cannot be zero.
# Also, m should be positive.  If m is negative, then the model will invert
# its behavior, which is outside its design specifications (i.e. the behavior
# will be unspecified).
m = 0.2

# Default vote value for unvoted songs.  If less than 5, then the model has a
# wedge in the lock time function for unrated songs.  Wedges are not bad, just
# keep that in mind when looking at test results.
unvoted_songs_value = 4

# Vote number de-penalty.  This is a modifier on hBias that applies based on
# the number of votes a song has received.  When a song has few votes, the
# rating could be skewed because of the preference of just a handful of users.
# As the vote count increases, this effect will fade.  Setting this to zero
# disables the vote de-penalty.
vote_bias = 0.2

# Vote bias fade power.  This number should be greater than 1.  With a fade
# power of 2, the vote bias above will be short lived.  By default, we set this
# to 2.
vote_bias_power = 2

# Minimum number of votes before the vote de-penalty starts fading away.  The
# lower this number, the faster the vote de-penalty will fade as votes come in.
# Also, when songs have a number of votes less than this amount, the actual
# rating is put into a weighed average with unvoted_songs_value.  This is so
# that a song with 1 vote of 1 star doesn't receive the maximum penalty, and so
# that a song with 1 vote of 5 stars doesn't receive the minimum penalty.  This
# can be described as the "benefit of the doubt" or "lack of quorum" effect.
# This value must be non-zero, and it must be a floating point value.
vote_min_votes = 7.0

# Song length penalty configuration.  This is also a modifier on hBias.  All
# other things being equal, longer songs must be better to have the same lock
# times.  The values are set in minutes.  The length_bias_minmins specifies
# songs that won't be affected by this setting if they are shorter.  The
# length_bias_worstmins specifies the song length at which the targeted penalty
# is achieved.  Set this last value keeping in mind the maximum hBias you want
# for the longest playable song the code may encounter (e.g. 25 mins).  Setting
# the length_bias to zero disables the length penalty.
length_bias_minmins = 4
length_bias_worstmins = 25
length_bias = 1.5 / ((length_bias_worstmins - length_bias_minmins) * 60)

class TestSong(object):
    """
    Mock class for testing song lock time calculation
    """
    def __init__(self, name, rating, votes, length):
        self.name = name
        self.rating = rating
        self.rating_votes = votes
        self.get_songlength = lambda: length

    def __unicode__(self):
        return self.name

def calc_songlock(song):
    L.debug("Calc called for song : %s", song)

    r = song.rating and song.rating or unvoted_songs_value

    hBiasLength = max(song.get_songlength() - length_bias_minmins * 60, 0) * length_bias
    L.debug("Length bias is %s", hBiasLength)

    voteCount = song.rating_votes
    hBiasVote = ((vote_min_votes / max(vote_min_votes, voteCount)) ** vote_bias_power) * vote_bias
    L.debug("Vote bias is %s", hBiasVote)

    hBias = hBiasBase + hBiasLength - hBiasVote
    L.debug("Total bias is : %s", hBias)

    weighedR = (unvoted_songs_value * max(vote_min_votes - voteCount, 0) + r * min(vote_min_votes, voteCount)) / vote_min_votes
    newLockTimeFactor = (atan((3 - weighedR + hBias) * m) - atan((hBias - 2) * m)) / (atan((hBias + 2) * m) - atan((hBias - 2) * m))
    L.debug("Lock factor for song is : %s", newLockTimeFactor)

    return newLockTimeFactor

def test_calcsongs(songlist):
    """
    Calculate value for songs in list and print to stdout
    """
    print "Song name\t\t\t\t\tRating\tVotes\tLength\tMagic number"
    for x in songlist:
        num = calc_songlock(x)
        d = [unicode(x).ljust(40), x.rating, x.rating_votes, x.get_songlength(), num]
        print "\t".join([unicode(y) for y in d])

def gen_testdata():
    """
    Create a set of test data
    """
    testdata = [
# Songs with no votes but different lengths
        TestSong("No ratings, length bias A", None, 0, 100),
        TestSong("No ratings, length bias B", None, 0, 200),
        TestSong("No ratings, length bias C", None, 0, 350),
        TestSong("No ratings, length bias D", None, 0, 500),
        TestSong("No ratings, length bias E", None, 0, 60 * 20),
        TestSong("No ratings, length bias F", None, 0, 60 * 25),
        TestSong("No ratings, length bias G", None, 0, 60 * 30),
# Songs with high ratings but different vote counts
        TestSong("Benefit of the doubt 1A", None, 0, 312),
        TestSong("Benefit of the doubt 1B", 4.5, 1, 312),
        TestSong("Benefit of the doubt 1C", 4.5, 2, 312),
        TestSong("Benefit of the doubt 1D", 4.5, 3, 312),
        TestSong("Benefit of the doubt 1E", 4.5, 4, 312),
        TestSong("Benefit of the doubt 1F", 4.5, 5, 312),
        TestSong("Benefit of the doubt 1G", 4.5, 6, 312),
        TestSong("Benefit of the doubt 1H", 4.5, 7, 312),
        TestSong("Benefit of the doubt 1I", 4.5, 8, 312),
        TestSong("Benefit of the doubt 1J", 4.5, 9, 312),
        TestSong("Benefit of the doubt 1K", 4.5, 10, 312),
        TestSong("Benefit of the doubt 1L", 4.5, 15, 312),
        TestSong("Benefit of the doubt 1M", 4.5, 20, 312),
        TestSong("Benefit of the doubt 1N", 4.5, 35, 312),
        TestSong("Benefit of the doubt 1O", 4.5, 50, 312),
        TestSong("Benefit of the doubt 1P", 4.5, 75, 312),
        TestSong("Benefit of the doubt 1Q", 4.5, 100, 312),
# Songs with low ratings but different vote counts
        TestSong("Benefit of the doubt 2A", None, 0, 312),
        TestSong("Benefit of the doubt 2B", 1.5, 1, 312),
        TestSong("Benefit of the doubt 2C", 1.5, 2, 312),
        TestSong("Benefit of the doubt 2D", 1.5, 3, 312),
        TestSong("Benefit of the doubt 2E", 1.5, 4, 312),
        TestSong("Benefit of the doubt 2F", 1.5, 5, 312),
        TestSong("Benefit of the doubt 2G", 1.5, 6, 312),
        TestSong("Benefit of the doubt 2H", 1.5, 7, 312),
        TestSong("Benefit of the doubt 2I", 1.5, 8, 312),
        TestSong("Benefit of the doubt 2J", 1.5, 9, 312),
        TestSong("Benefit of the doubt 2K", 1.5, 10, 312),
        TestSong("Benefit of the doubt 2L", 1.5, 15, 312),
        TestSong("Benefit of the doubt 2M", 1.5, 20, 312),
        TestSong("Benefit of the doubt 2N", 1.5, 35, 312),
        TestSong("Benefit of the doubt 2O", 1.5, 50, 312),
        TestSong("Benefit of the doubt 2P", 1.5, 75, 312),
        TestSong("Benefit of the doubt 2Q", 1.5, 100, 312),
# Songs with medium ratings but different vote counts
        TestSong("Benefit of the doubt 3A", None, 0, 312),
        TestSong("Benefit of the doubt 3B", 3.0, 1, 312),
        TestSong("Benefit of the doubt 3C", 3.0, 2, 312),
        TestSong("Benefit of the doubt 3D", 3.0, 3, 312),
        TestSong("Benefit of the doubt 3E", 3.0, 4, 312),
        TestSong("Benefit of the doubt 3F", 3.0, 5, 312),
        TestSong("Benefit of the doubt 3G", 3.0, 6, 312),
        TestSong("Benefit of the doubt 3H", 3.0, 7, 312),
        TestSong("Benefit of the doubt 3I", 3.0, 8, 312),
        TestSong("Benefit of the doubt 3J", 3.0, 9, 312),
        TestSong("Benefit of the doubt 3K", 3.0, 10, 312),
        TestSong("Benefit of the doubt 3L", 3.0, 15, 312),
        TestSong("Benefit of the doubt 3M", 3.0, 20, 312),
        TestSong("Benefit of the doubt 3N", 3.0, 35, 312),
        TestSong("Benefit of the doubt 3O", 3.0, 50, 312),
        TestSong("Benefit of the doubt 3P", 3.0, 75, 312),
        TestSong("Benefit of the doubt 3Q", 3.0, 100, 312),
# Songs with lowest rating but different vote counts
        TestSong("Benefit of the doubt 4A", 1.0, 1, 312),
        TestSong("Benefit of the doubt 4B", 1.0, 2, 312),
        TestSong("Benefit of the doubt 4C", 1.0, 3, 312),
        TestSong("Benefit of the doubt 4D", 1.0, 5, 312),
        TestSong("Benefit of the doubt 4E", 1.0, 8, 312),
        TestSong("Benefit of the doubt 4F", 1.0, 13, 312),
        TestSong("Benefit of the doubt 4G", 1.0, 21, 312),
        TestSong("Benefit of the doubt 4H", 1.0, 34, 312),
# Songs with lowest rating but different vote counts
        TestSong("Benefit of the doubt 5A", 5.0, 1, 312),
        TestSong("Benefit of the doubt 5B", 5.0, 2, 312),
        TestSong("Benefit of the doubt 5C", 5.0, 3, 312),
        TestSong("Benefit of the doubt 5D", 5.0, 5, 312),
        TestSong("Benefit of the doubt 5E", 5.0, 8, 312),
        TestSong("Benefit of the doubt 5F", 5.0, 13, 312),
        TestSong("Benefit of the doubt 5G", 5.0, 21, 312),
        TestSong("Benefit of the doubt 5H", 5.0, 34, 312),
# Songs with many votes but different song ratings
        TestSong("Lock times and ratings go together A", 1.0, 21, 312),
        TestSong("Lock times and ratings go together B", 1.5, 21, 312),
        TestSong("Lock times and ratings go together C", 2.0, 21, 312),
        TestSong("Lock times and ratings go together D", 2.5, 21, 312),
        TestSong("Lock times and ratings go together E", 3.0, 21, 312),
        TestSong("Lock times and ratings go together F", 3.5, 21, 312),
        TestSong("Lock times and ratings go together G", 4.0, 21, 312),
        TestSong("Lock times and ratings go together H", 4.5, 21, 312),
        TestSong("Lock times and ratings go together I", 5.0, 21, 312),
# Extremes
        TestSong("Strong bad A", 1.1, 4, 312),
        TestSong("Strong bad A longer", 1.1, 4, 20 * 60),
        TestSong("Strong bad A more votes", 1.1, 21, 312),
        TestSong("Strong bad A longer and more votes", 1.1, 21, 20 * 60),
    ]
    return testdata

if __name__=="__main__":
    test_calcsongs(gen_testdata())
