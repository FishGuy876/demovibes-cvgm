#
# Example showing how to extend or override queue / play logic
#

import sockulf

# queuefetcher have the "which song to play" logic
# Here we subclass that class, and override a function
class MyFetcher(sockulf.queuefetcher.song_finder):

    #This function determines if the randomly selected song is good to play.
    #Here we change the logic to accept all songs
    def isGoodSong(self, song):
        return True # All songs are good songs!


# pyWhisperer contains the tcp server logic that clients can connect to
# and send / receive commands. It then communicates with the queuefetcher
class mySock(sockulf.pyWhisperer):
    
    #Define a new command, that returns the string "Hahey, my custom command! WOO!" to the client.
    def command_mycustomcommand(self): #We need a new, custom command
        return "Hahey, my custom command! WOO!"

    # Need to override init so that we can add the new command to the self.COMMANDS dict
    # We also change the player logic to the new MyFetcher class
    def __init__(self, *args, **kwargs):
        
        #First, run the normal init code
        super(mySock, self).__init__(*args, **kwargs)
        
        #override player with the new one after running the original init
        self.player = MyFetcher() 
        
        # Add custom command "MYCUSTOM" to dict of command -> function mapping
        self.COMMANDS['MYCUSTOM'] = self.command_mycustomcommand 

# Now, let's start the damn thing
# Just as in sockulf - but without the cute option parser part.
# IP, port, timeout (warning.. timeout should be None unless in very special cases
server = mySock("127.0.0.1", 32167, None)
server.listen()
