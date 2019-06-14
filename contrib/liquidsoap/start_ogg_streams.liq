#!/usr/bin/liquidsoap

# liquidsoap setup script by FishGuy876/Brainstorm
#
# Set up mountpoints to connect to existing Icecast2 server.
# Be aware, there are known bugs with Opus which will cause Ogg streams to
# Permanantly break. If your Ogg streams fail, uninstall the Opus plugin to fix.

# Logging Path
set("log.stdout",true)
set("log.file",true)
set("log.file.path","/tmp/ogg-vorbis-streams.log")

CVGM_Genre = "Video Game Music, ChipTune, Atari, Amiga, GameBoy"
CVGM_URL = "http://www.cvgm.net/demovibes"
CVGM_Description = "CVGM.net - Oldschool 8-Bit Video Game And Console Music"

# Input the stream,
# from an Icecast server or any other source
url = "http://localhost/cvgm192"
input = mksafe(input.http(url))

# OGG Vorbis Output

# Constant OGG bitrate stream, highest quality possible
output.icecast(
  %vorbis.cbr(samplerate=44100, channels=2, bitrate=192),
  mount="/cvgm192.ogg",
  genre=CVGM_Genre, url=CVGM_URL, description=CVGM_Description,
  host="localhost", port=80, password="password",
  input)

# Constant OGG bitrate stream, highest quality possible
output.icecast(
  %vorbis.cbr(samplerate=44100, channels=2, bitrate=128),
  mount="/cvgm128.ogg",
  genre=CVGM_Genre, url=CVGM_URL, description=CVGM_Description,
  host="localhost", port=80, password="password",
  input)

# Constant OGG bitrate stream, highest quality possible
output.icecast(
  %vorbis.cbr(samplerate=44100, channels=2, bitrate=64),
  mount="/cvgm64.ogg",
  genre=CVGM_Genre, url=CVGM_URL, description=CVGM_Description,
  host="localhost", port=80, password="password",
  input)


