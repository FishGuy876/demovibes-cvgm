#!/bin/sh
if test `uname -s` != 'Linux'; then
    echo unsupported OS
    exit 1
fi
sofile='libbass.so'
if test `uname -m` = 'x86_64'; then
    sofile="x64/$sofile";
fi
rm -f bass24-linux.zip
wget 'http://us.un4seen.com/files/bass24-linux.zip'
unzip -oj bass24-linux.zip bass.h $sofile
