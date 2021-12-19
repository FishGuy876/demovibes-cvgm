#!/bin/sh
test $(uname -m) != x86_64 && echo 'unsupported architecture' && exit 1

if test $(uname) = Linux; then
    rm -f bass24-linux.zip
    curl -O http://us.un4seen.com/files/bass24-linux.zip
    unzip -oj bass24-linux.zip bass.h x64/libbass.so
elif test $(uname) = Darwin; then
    rm -f bass24-osx.zip
    curl -O https://www.un4seen.com/files/bass24-osx.zip
    unzip -oj bass24-osx.zip bass.h libbass.dylib
    # unfuck apple's dynamic linker
    mv libbass.dylib libbass.so
    install_name_tool -id @loader_path/libs/libbass.so libbass.so
else
    echo 'usupported OS'
    exit 1
fi
