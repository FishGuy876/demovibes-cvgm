#!/usr/bin/liquidsoap

# liquidsoap setup script by FishGuy876/Brainstorm
#
# Set up mountpoints to connect to existing Icecast2 server.
# Be aware, there are known bugs with Opus which will cause Ogg streams to
# Permanantly break. If your Ogg streams fail, uninstall the Opus plugin to fix.

# Logging Path
set("log.stdout",true)
set("log.file",true)
set("log.file.path","/tmp/mp3-streams.log")

CVGM_Genre = "Video Game Music, ChipTune, Atari, Amiga, GameBoy"
CVGM_URL = "http://www.cvgm.net/demovibes"
CVGM_Description = "CVGM.net - Oldschool 8-Bit Video Game And Console Music"

# Input the stream,
# from an Icecast server or any other source
url = "http://localhost/cvgm192"
input = mksafe(input.http(url))


# OGG Vorbis Output
# MP3 streams need title, otherwise only the mountpoint is shown

# Constant OGG bitrate stream, highest quality possible
output.icecast(
  %mp3(bitrate=128),
  mount="/cvgm128",
  genre=CVGM_Genre, url=CVGM_URL, description=CVGM_Description,
  host="localhost", port=80, password="password",
  input, icy_metadata="true")

# Constant OGG bitrate stream, highest quality possible
output.icecast(
  %mp3(bitrate=64),
  mount="/cvgm64",
  genre=CVGM_Genre, url=CVGM_URL, description=CVGM_Description, 
  host="localhost", port=80, password="password",
  input, icy_metadata="true")

# We can also enable the AAC stream here
output.icecast(
  %aac(channels=2, samplerate=44100, bitrate=64, adts=true),
  mount="/cvgm64-aac",
  genre=CVGM_Genre, url=CVGM_URL, description=CVGM_Description,
  host="localhost", port=80, password="password",
  input, icy_metadata="true")

