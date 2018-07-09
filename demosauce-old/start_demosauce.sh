#!/bin/bash

# A bash script to start Demosauce, and re-start it in the event it stops. Depending on the system, it can take up
# To 60 seconds to restart again and skip several songs in the process. Increase the sleep delay to prevent the
# Number of skipped songs, as the rest of the system catches up and restarts.

while /bin/true
do
        echo "Restarting Demosauce"
        ./demosauce -t

        # Pause briefly before restart
        sleep 5
done


