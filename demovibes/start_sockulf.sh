#!/bin/bash

# A bash script to start Sockulf, and re-start it in the event it stops. AAK

while /bin/true
do
        echo "Restarting Sockulf"
        python sockulf.py

        # Pause briefly before restart
        sleep 60 # Takes a minute for sockulf to release old connection
done
