#!/bin/sh
# a small script to install required dependencies

# Check the distribution and install dependencies
test $(whoami) != "root" && echo "must run as root" && exit

# Arch
test -e /usr/bin/packman && pacman -Sy gcc make pkg-config libshout lame ffmpeg chromaprint

# Debian, Ubuntu
# requires deb-multimedia repo
test -e /usr/bin/aptitude &&  echo aptitude -y install build-essential libshout-dev libmp3lame-dev libavformat-dev libchromaprint-dev

# RedHat, Fedora, CentOS
# requires rpm fusinon repo
test -e /usr/bin/yum && yum -y install gcc libshout3-devel lame-devel ffmpeg-devel chromaprint-devel

# openSUSE
test -e /usr/bin/zypper && zypper install gcc make libshout-devel lame-devel ffmpeg-devel chromaprint-devel

# Gentoo
test -e /usr/bin/emerge && emerge -avuDN libshout lame ffmpeg libchromaprint

# FreeBSD
test -e /usr_bin/pkg_add && pkg_add -r gcc libshout2 ffmpeg libchromaprint && make -C /usr/ports/audio/lame install clean
