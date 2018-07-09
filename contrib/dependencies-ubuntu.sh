#!/bin/bash
# Basic script to set up & install basic dependencies on a Ubuntu 12+ System
# Written by FishGuy876/Brainstorm
#
# This script uses some bits originally written by Terrasque, and modified for this install

# This is a condition that ensures we are running in the correct folder
cd ..
if [ ! -f "demovibes/urls.py" ]
then
  echo "This script is ran from the wrong folder. Call from the root of the repo. Quitting."
  exit 1
fi

# Package Variables

# Fluff Packages - Stuff thats a dependant of another install further down the road, or 
# Needed to fix specific issues/problems/build lameness on the site
#
# python-imaging - Replaces PIL and is required to allow any kind of image processing when uploading images on the site
#  Same with libjpeg62-dev zlib1g-dev libpng-dev (to support those images)
# yasm - Needed to build the libavcodec stuff on demosauce
# python-pip - Not always installed automatically on some systems, so we make sure its here for virtual environment
# libxml2-dev & python-dev - Both are needed by uWsgi to build properly from source
fluff="build-essential pkg-config python-software-properties python-setuptools python-imaging libjpeg62-dev zlib1g-dev libpng-dev python-pip gawk yasm bc libxml2-dev python-dev git subversion"

# MySQL Objects & Dependencies
database="mysql-server libmysqlclient-dev"

# Installs Cherokee & its additional modules (which can be used for testing/logging/reporting)
cherokee="cherokee rrdtool libcherokee-mod-rrd libcherokee-mod-libssl"

icecast="icecast2"

demosauce_build="libmad0 libid3tag0-dev libboost-dev libboost-system-dev libboost-date-time-dev libboost-thread-dev libboost-filesystem-dev libboost-program-options-dev libsamplerate0-dev libshout3-dev libmp3lame-dev lame libicu-dev"

# Forcibly update the package lists to the most recent ones, to ensure we don't miss something!
echo -e "\nUpdating Current Package Lists\n"
apt-get update

# Each section is installed indivisually. If something b0rks, we can detect it a little easier

# Install the fluff stuff first, so we can get to work on installing!
echo -e "\n\nInstalling Fluff Packages: $fluff\n\n"
apt-get install -y $fluff
read waittil

# Icecast2 Streamer
echo -e "\n\nInstalling Icecast2 Streamer Packages\n\n"
apt-get install -y $icecast

# Install the Cherokee components
echo -e "\n\nInstalling Cherokee & It's Modules\n\n"
apt-get install -y $cherokee

# Install the stuff needed for MySQL
echo -e "\n\nInstalling MySQL & Related Dependencies. You will be asked to create a master password if there is no current install. Write it down!!\n"
apt-get install -y $database

# Install uWsgi. This particular version seems to work quite well on most installs, so we stick to it. The newer
# Builds tend to have issues with green threads, and don't always build correctly. If you do suffer issues with this
# Version, you can refer back to v0.9.5.4 (but it is quite a lot slower)

echo -e "\nDownloading & Installing uWsgi v0.9.9.2\n";
wget http://projects.unbit.it/downloads/old/uwsgi-0.9.9.2.tar.gz
tar -zxvf uwsgi-0.9.9.2.tar.gz
cd uwsgi-0.9.9.2
python setup.py install
cd ..
rm -Rf uwsgi-0.9.9.2
rm -Rf uwsgi-0.9.9.2.tar.gz

# Now we are done with that, we should attempt to build the streamer. This is where things can get messy
echo "\n\nInstalling packages needed to build demosauce\n\n"
apt-get install -y $demosauce_build

# Notify user about build options
echo -e "\n\nIf this is the first time you have built the demosauce tool suite, you will be prompted about building a custom version of the libavcodec library. Select Y at the prompt to build it. Some distros don't have the best support for the library, and its always a good idea to build it yourself. Demosauce will automatically download and build all needed pieces by itself. No errors (but some warnings) will appear during building. Press ENTER to continue.\n\n"
read PressEnter

# CD into the folder
chmod -R 0755 demosauce  # Change permissions of this folder so its all OK
cd "demosauce"
./configure.sh
./makebelieve.sh
cd ..
