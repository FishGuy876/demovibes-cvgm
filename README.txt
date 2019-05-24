What Is This?
=============

Demovibes is an engine designed for streaming music over the interwebs. It was created after the fall of the original Nectarine project. demovibes-cvgm is an original fork of the demovibes code tree. Demovibes allows the users to queue up songs which are then played in the order they are queued. Demovibes has many other features including forums, screenshots, sessions, and the infamous oneliner.

What you need
=============

# Linux - At present, the code is tested and ran on Debian 9. Its also compatible with Ubuntu from version 12 upwards.
# Python 2.7 is preferred. 
# Django 1.3+, see the requirements.txt in the contrib folder for the specific versions used in this release.
# A Database + python bindings. MySQL is preferred for production servers.
# It is preferred if you use VirtualEnv to host your site.
# uwsgi 0.9.5.4 is the version used on CVGM. There are other versions that work, some better than others.
# For streaming you will need Icecast2 and LibBoost. Demosauce will set up the streamer requirements for compilation, including BASS.

Installation
============

See contrib/INSTALL

Getting Started
===============

   1. Create the virtual environment using virtualenv. Install packages from contrib/requirements.txt
   2. Syncronize the DB's together and create your Admin user.
   3. Log into the Admin Panel and create your first user - djrandom
   4. Compile the Demosauce streamer and scan tools.
   5 Create a regular user account via the website.
   6. Activate your VirtualEnv and start sockulf with the supplied start_sockulf.sh script. You can then start uploading songs.
   7. Start the streamer with the supplied start_demosauce.sh script.
   8. Sit back and relax!
   9. Start the streamer with the icecaster.sh script 

Contact / updates
=================

The latest version is always avaliable at https://github.com/FishGuy876/demovibes-cvgm See Releases tab for stable releases of code.
The original project authors can be reached at fishguy8765@gmail.com (FishGuy876) or mikael@thelazy.net (Terrasque)

This code is released as GPL. May contain traces of NUTS!
