#!/bin/sh
test $(uname -s) != 'Linux' && echo 'unsupported OS' && exit 1
test $(uname -m) = 'x86_64' && SOFILE='x64/libbass.so' || SOFILE='libbass.so'
rm -f bass24-linux.zip
wget 'http://us.un4seen.com/files/bass24-linux.zip'
unzip -oj bass24-linux.zip bass.h $SOFILE
