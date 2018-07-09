#!/bin/sh
# a small script to install required dependencies

# Check the distribution and install dependencies
if [ `whoami` != "root" ] ; then
	echo "To run installDependencies.sh you have to be root (install packages)"
	exit
fi

# Debian (and Ubuntu obviously)
if [ -f /etc/debian_version ] ; then
	aptitude -y install g++ yasm lame ladspa-sdk libsamplerate-dev libshout-dev libid3tag0-dev libicu-dev libboost-dev libboost-system-dev libboost-thread-dev libboost-filesystem-dev libboost-program-options-dev
        echo 'note: older debian distros have ancient boost packages. usually there is a newer package available, like libboost1.40-dev'
	exit
fi

# RedHat (and Fedora)
if [ -f /etc/redhat-release ] ; then
	yum -y install gcc-c++ yasm lame ladspa-sdk libsamplerate-devel libshout3-devel libid3tag-devel libicu-devel boost-devel
	exit
fi

# openSUSE
if [ -d /etc/YaST2 ] ; then
	echo "you need to enable the Pacman repository"
	zypper install gcc-c++ make yasm lame ladspa ladspa-devel libsamplerate-devel libshout-devel libid3tag-devel libicu-devel boost-devel
	exit
fi

# Slackware
if [ -f /etc/slackware-version ] ; then
        echo "I don't even know if Slackware has a package manager...  pls fix"
	exit
fi

# Gentoo
# G++ is assumed already installed
if [ -f /etc/gentoo-release ] ; then
	emerge -avuDN yasm lame libshout libsamplerate libid3tag 
	exit
fi

# FreeBSD
if [ `uname -s` = 'FreeBSD' ] ; then
	pkg_add -r gcc yasm libshout2 libsamplerate ffmpeg
        make -C /usr/ports/audio/lame install clean
fi
