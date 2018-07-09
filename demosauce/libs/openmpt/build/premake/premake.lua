
-- premake gets a tiny bit confused if the same project appears in multiple
-- solutions in a single run. premake adds a bogus $projectname path to the
-- intermediate objects directory in that case. work-around using multiple
-- invocations of premake and a custom option to distinguish them.

MPT_PREMAKE_VERSION = ""

MPT_WITH_SHARED = true

if _PREMAKE_VERSION == "5.0.0-alpha9" then
 MPT_PREMAKE_VERSION = "5.0"
else
 print "Premake 5.0.0-alpha9 required"
 os.exit(1)
end

newoption {
 trigger     = "group",
 value       = "PROJECTS",
 description = "OpenMPT project group",
 allowed = {
  { "libopenmpt-all", "libopenmpt-all" },
  { "libopenmpt_test", "libopenmpt_test" },
  { "libopenmpt", "libopenmpt" },
  { "libopenmpt-small", "libopenmpt-small" },
  { "foo_openmpt", "foo_openmpt" },
  { "in_openmpt", "in_openmpt" },
  { "xmp-openmpt", "xmp-openmpt" },
  { "openmpt123", "openmpt123" },
  { "PluginBridge", "PluginBridge" },
  { "OpenMPT-VSTi", "OpenMPT-VSTi" },
  { "OpenMPT", "OpenMPT" },
  { "all-externals", "all-externals" }
 }
}

newoption {
	trigger = "xp",
	description = "Generate XP targetting projects",
}

if not _OPTIONS["xp"] then
	mpt_projectpathname = _ACTION;
else
	mpt_projectpathname = _ACTION .. "xp";
end

function replace_in_file (filename, from, to)
	local text
	local infile
	local outfile
	local oldtext
	local newtext
	infile = io.open(filename, "r")
	text = infile:read("*all")
	infile:close()
	oldtext = text
	newtext = string.gsub(oldtext, from, to)
	text = newtext
	if newtext == oldtext then
   print("Failed to postprocess '" .. filename .. "': " .. from .. " -> " .. to)
   os.exit(1)
	end
	outfile = io.open(filename, "w")
	outfile:write(text)
	outfile:close()
end

-- related to issue https://github.com/premake/premake-core/issues/68
function postprocess_vs2008_main (filename)
	replace_in_file(filename, "\t\t\t\tEntryPointSymbol=\"mainCRTStartup\"\n", "")
end

function postprocess_vs2008_nonxcompat (filename)
	replace_in_file(filename, "\t\t\t<Tool\n\t\t\t\tName=\"VCLinkerTool\"\n", "\t\t\t<Tool\n\t\t\t\tName=\"VCLinkerTool\"\n\t\t\t\t\DataExecutionPrevention=\"1\"\n")
end

-- related to issue https://github.com/premake/premake-core/issues/68
function postprocess_vs2010_main (filename)
	replace_in_file(filename, "<EntryPointSymbol>mainCRTStartup</EntryPointSymbol>", "")
end

function postprocess_vs2010_nonxcompat (filename)
	replace_in_file(filename, "    </Link>\n", "      <DataExecutionPrevention>false</DataExecutionPrevention>\n    </Link>\n")
end

function postprocess_vs2010_disabledpiaware (filename)
	replace_in_file(filename, "%%%(AdditionalManifestFiles%)</AdditionalManifestFiles>\n", "%%%(AdditionalManifestFiles%)</AdditionalManifestFiles>\n      <EnableDPIAwareness>false</EnableDPIAwareness>\n")
end

newaction {
 trigger     = "postprocess",
 description = "OpenMPT postprocess the project files to mitigate premake problems",
 execute     = function ()

  postprocess_vs2008_main("build/vs2008/libopenmpt_test.vcproj")
  postprocess_vs2008_main("build/vs2008/openmpt123.vcproj")
  postprocess_vs2008_main("build/vs2008/libopenmpt_example_c_probe.vcproj")
  postprocess_vs2008_main("build/vs2008/libopenmpt_example_c.vcproj")
  postprocess_vs2008_main("build/vs2008/libopenmpt_example_c_mem.vcproj")
  postprocess_vs2008_main("build/vs2008/libopenmpt_example_c_unsafe.vcproj")
  postprocess_vs2008_nonxcompat("build/vs2008/OpenMPT.vcproj")
  postprocess_vs2008_nonxcompat("build/vs2008/PluginBridge.vcproj")

  postprocess_vs2010_main("build/vs2010/libopenmpt_test.vcxproj")
  postprocess_vs2010_main("build/vs2010/openmpt123.vcxproj")
  postprocess_vs2010_main("build/vs2010/libopenmpt_example_c_probe.vcxproj")
  postprocess_vs2010_main("build/vs2010/libopenmpt_example_c.vcxproj")
  postprocess_vs2010_main("build/vs2010/libopenmpt_example_c_mem.vcxproj")
  postprocess_vs2010_main("build/vs2010/libopenmpt_example_c_unsafe.vcxproj")
  postprocess_vs2010_main("build/vs2010/libopenmpt_example_cxx.vcxproj")
  postprocess_vs2010_nonxcompat("build/vs2010/OpenMPT.vcxproj")
  postprocess_vs2010_disabledpiaware("build/vs2010/OpenMPT.vcxproj")
  postprocess_vs2010_nonxcompat("build/vs2010/PluginBridge.vcxproj")
  postprocess_vs2010_disabledpiaware("build/vs2010/PluginBridge.vcxproj")
  
  postprocess_vs2010_main("build/vs2012/libopenmpt_test.vcxproj")
  postprocess_vs2010_main("build/vs2012/openmpt123.vcxproj")
  postprocess_vs2010_main("build/vs2012/libopenmpt_example_c_probe.vcxproj")
  postprocess_vs2010_main("build/vs2012/libopenmpt_example_c.vcxproj")
  postprocess_vs2010_main("build/vs2012/libopenmpt_example_c_mem.vcxproj")
  postprocess_vs2010_main("build/vs2012/libopenmpt_example_c_unsafe.vcxproj")
  postprocess_vs2010_main("build/vs2012/libopenmpt_example_cxx.vcxproj")
  postprocess_vs2010_nonxcompat("build/vs2012/OpenMPT.vcxproj")
  postprocess_vs2010_disabledpiaware("build/vs2012/OpenMPT.vcxproj")
  postprocess_vs2010_nonxcompat("build/vs2012/PluginBridge.vcxproj")
  postprocess_vs2010_disabledpiaware("build/vs2012/PluginBridge.vcxproj")
	
  postprocess_vs2010_main("build/vs2013/libopenmpt_test.vcxproj")
  postprocess_vs2010_main("build/vs2013/openmpt123.vcxproj")
  postprocess_vs2010_main("build/vs2013/libopenmpt_example_c_probe.vcxproj")
  postprocess_vs2010_main("build/vs2013/libopenmpt_example_c.vcxproj")
  postprocess_vs2010_main("build/vs2013/libopenmpt_example_c_mem.vcxproj")
  postprocess_vs2010_main("build/vs2013/libopenmpt_example_c_unsafe.vcxproj")
  postprocess_vs2010_main("build/vs2013/libopenmpt_example_cxx.vcxproj")
  postprocess_vs2010_nonxcompat("build/vs2013/OpenMPT.vcxproj")
  postprocess_vs2010_disabledpiaware("build/vs2013/OpenMPT.vcxproj")
  postprocess_vs2010_nonxcompat("build/vs2013/PluginBridge.vcxproj")
  postprocess_vs2010_disabledpiaware("build/vs2013/PluginBridge.vcxproj")

  postprocess_vs2010_main("build/vs2015/libopenmpt_test.vcxproj")
  postprocess_vs2010_main("build/vs2015/openmpt123.vcxproj")
  postprocess_vs2010_main("build/vs2015/libopenmpt_example_c_probe.vcxproj")
  postprocess_vs2010_main("build/vs2015/libopenmpt_example_c.vcxproj")
  postprocess_vs2010_main("build/vs2015/libopenmpt_example_c_mem.vcxproj")
  postprocess_vs2010_main("build/vs2015/libopenmpt_example_c_unsafe.vcxproj")
  postprocess_vs2010_main("build/vs2015/libopenmpt_example_cxx.vcxproj")
  postprocess_vs2010_nonxcompat("build/vs2015/OpenMPT.vcxproj")
  postprocess_vs2010_disabledpiaware("build/vs2015/OpenMPT.vcxproj")
  postprocess_vs2010_nonxcompat("build/vs2015/PluginBridge.vcxproj")
  postprocess_vs2010_disabledpiaware("build/vs2015/PluginBridge.vcxproj")

  postprocess_vs2010_main("build/vs2010xp/libopenmpt_test.vcxproj")
  postprocess_vs2010_main("build/vs2010xp/openmpt123.vcxproj")
  postprocess_vs2010_main("build/vs2010xp/libopenmpt_example_c_probe.vcxproj")
  postprocess_vs2010_main("build/vs2010xp/libopenmpt_example_c.vcxproj")
  postprocess_vs2010_main("build/vs2010xp/libopenmpt_example_c_mem.vcxproj")
  postprocess_vs2010_main("build/vs2010xp/libopenmpt_example_c_unsafe.vcxproj")
  postprocess_vs2010_main("build/vs2010xp/libopenmpt_example_cxx.vcxproj")
  postprocess_vs2010_nonxcompat("build/vs2010xp/OpenMPT.vcxproj")
  postprocess_vs2010_disabledpiaware("build/vs2010xp/OpenMPT.vcxproj")
  postprocess_vs2010_nonxcompat("build/vs2010xp/PluginBridge.vcxproj")
  postprocess_vs2010_disabledpiaware("build/vs2010xp/PluginBridge.vcxproj")
  
  postprocess_vs2010_main("build/vs2012xp/libopenmpt_test.vcxproj")
  postprocess_vs2010_main("build/vs2012xp/openmpt123.vcxproj")
  postprocess_vs2010_main("build/vs2012xp/libopenmpt_example_c_probe.vcxproj")
  postprocess_vs2010_main("build/vs2012xp/libopenmpt_example_c.vcxproj")
  postprocess_vs2010_main("build/vs2012xp/libopenmpt_example_c_mem.vcxproj")
  postprocess_vs2010_main("build/vs2012xp/libopenmpt_example_c_unsafe.vcxproj")
  postprocess_vs2010_main("build/vs2012xp/libopenmpt_example_cxx.vcxproj")
  postprocess_vs2010_nonxcompat("build/vs2012xp/OpenMPT.vcxproj")
  postprocess_vs2010_disabledpiaware("build/vs2012xp/OpenMPT.vcxproj")
  postprocess_vs2010_nonxcompat("build/vs2012xp/PluginBridge.vcxproj")
  postprocess_vs2010_disabledpiaware("build/vs2012xp/PluginBridge.vcxproj")
	
  postprocess_vs2010_main("build/vs2013xp/libopenmpt_test.vcxproj")
  postprocess_vs2010_main("build/vs2013xp/openmpt123.vcxproj")
  postprocess_vs2010_main("build/vs2013xp/libopenmpt_example_c_probe.vcxproj")
  postprocess_vs2010_main("build/vs2013xp/libopenmpt_example_c.vcxproj")
  postprocess_vs2010_main("build/vs2013xp/libopenmpt_example_c_mem.vcxproj")
  postprocess_vs2010_main("build/vs2013xp/libopenmpt_example_c_unsafe.vcxproj")
  postprocess_vs2010_main("build/vs2013xp/libopenmpt_example_cxx.vcxproj")
  postprocess_vs2010_nonxcompat("build/vs2013xp/OpenMPT.vcxproj")
  postprocess_vs2010_disabledpiaware("build/vs2013xp/OpenMPT.vcxproj")
  postprocess_vs2010_nonxcompat("build/vs2013xp/PluginBridge.vcxproj")
  postprocess_vs2010_disabledpiaware("build/vs2013xp/PluginBridge.vcxproj")

  postprocess_vs2010_main("build/vs2015xp/libopenmpt_test.vcxproj")
  postprocess_vs2010_main("build/vs2015xp/openmpt123.vcxproj")
  postprocess_vs2010_main("build/vs2015xp/libopenmpt_example_c_probe.vcxproj")
  postprocess_vs2010_main("build/vs2015xp/libopenmpt_example_c.vcxproj")
  postprocess_vs2010_main("build/vs2015xp/libopenmpt_example_c_mem.vcxproj")
  postprocess_vs2010_main("build/vs2015xp/libopenmpt_example_c_unsafe.vcxproj")
  postprocess_vs2010_main("build/vs2015xp/libopenmpt_example_cxx.vcxproj")
  postprocess_vs2010_nonxcompat("build/vs2015xp/OpenMPT.vcxproj")
  postprocess_vs2010_disabledpiaware("build/vs2015xp/OpenMPT.vcxproj")
  postprocess_vs2010_nonxcompat("build/vs2015xp/PluginBridge.vcxproj")
  postprocess_vs2010_disabledpiaware("build/vs2015xp/PluginBridge.vcxproj")

 end
}

if _OPTIONS["group"] == "libopenmpt-all" then

solution "libopenmpt-all"
 location ( "../../build/" .. mpt_projectpathname )
 configurations { "Debug", "Release" }
 platforms { "x86", "x86_64" }

 dofile "../../build/premake/mpt-libopenmpt_test.lua"
 dofile "../../build/premake/mpt-libopenmpt.lua"
 dofile "../../build/premake/mpt-libopenmpt_examples.lua"
 dofile "../../build/premake/mpt-libopenmpt-small.lua"
 dofile "../../build/premake/mpt-libopenmpt_modplug.lua"
 dofile "../../build/premake/mpt-foo_openmpt.lua"
 dofile "../../build/premake/mpt-in_openmpt.lua"
 dofile "../../build/premake/mpt-xmp-openmpt.lua"
 dofile "../../build/premake/mpt-openmpt123.lua"
 dofile "../../build/premake/ext-flac.lua"
 dofile "../../build/premake/ext-miniz.lua"
 dofile "../../build/premake/ext-ogg.lua"
 dofile "../../build/premake/ext-portaudio.lua"
 dofile "../../build/premake/ext-portaudiocpp.lua"
 dofile "../../build/premake/ext-vorbis.lua"
 dofile "../../build/premake/ext-zlib.lua"

end

if _OPTIONS["group"] == "libopenmpt_test" then

solution "libopenmpt_test"
 location ( "../../build/" .. mpt_projectpathname )
 configurations { "Debug", "Release" }
 platforms { "x86", "x86_64" }

 dofile "../../build/premake/mpt-libopenmpt_test.lua"
 dofile "../../build/premake/ext-ogg.lua"
 dofile "../../build/premake/ext-vorbis.lua"
 dofile "../../build/premake/ext-zlib.lua"

end

if _OPTIONS["group"] == "foo_openmpt" then

solution "foo_openmpt"
 location ( "../../build/" .. mpt_projectpathname )
 configurations { "Debug", "Release" }
 platforms { "x86" }

 dofile "../../build/premake/mpt-foo_openmpt.lua"
 dofile "../../build/premake/mpt-libopenmpt.lua"
 dofile "../../build/premake/ext-ogg.lua"
 dofile "../../build/premake/ext-vorbis.lua"
 dofile "../../build/premake/ext-zlib.lua"

end

if _OPTIONS["group"] == "in_openmpt" then

solution "in_openmpt"
 location ( "../../build/" .. mpt_projectpathname )
 configurations { "Debug", "Release" }
 platforms { "x86" }

 dofile "../../build/premake/mpt-in_openmpt.lua"
 dofile "../../build/premake/mpt-libopenmpt.lua"
 dofile "../../build/premake/ext-ogg.lua"
 dofile "../../build/premake/ext-vorbis.lua"
 dofile "../../build/premake/ext-zlib.lua"

end

if _OPTIONS["group"] == "xmp-openmpt" then

solution "xmp-openmpt"
 location ( "../../build/" .. mpt_projectpathname )
 configurations { "Debug", "Release" }
 platforms { "x86" }

 dofile "../../build/premake/mpt-xmp-openmpt.lua"
 dofile "../../build/premake/mpt-libopenmpt.lua"
 dofile "../../build/premake/ext-ogg.lua"
 dofile "../../build/premake/ext-pugixml.lua"
 dofile "../../build/premake/ext-vorbis.lua"
 dofile "../../build/premake/ext-zlib.lua"

end

if _OPTIONS["group"] == "libopenmpt-small" then

solution "libopenmpt-small"
 location ( "../../build/" .. mpt_projectpathname )
if MPT_WITH_SHARED then
 configurations { "Debug", "Release", "DebugShared", "ReleaseShared" }
else
 configurations { "Debug", "Release" }
end
 platforms { "x86", "x86_64" }

 dofile "../../build/premake/mpt-libopenmpt-small.lua"
 dofile "../../build/premake/ext-miniz.lua"
 dofile "../../build/premake/ext-stb_vorbis.lua"

end

-- should stay the last libopenmpt solution in order to overwrite the libopenmpt base project with all possible configurations
if _OPTIONS["group"] == "libopenmpt" then

solution "libopenmpt"
 location ( "../../build/" .. mpt_projectpathname )
if MPT_WITH_SHARED then
 configurations { "Debug", "Release", "DebugShared", "ReleaseShared" }
else
 configurations { "Debug", "Release" }
end
 platforms { "x86", "x86_64" }

 dofile "../../build/premake/mpt-libopenmpt.lua"
 dofile "../../build/premake/mpt-libopenmpt_examples.lua"
 dofile "../../build/premake/mpt-libopenmpt_modplug.lua"
 dofile "../../build/premake/ext-ogg.lua"
 dofile "../../build/premake/ext-portaudio.lua"
 dofile "../../build/premake/ext-portaudiocpp.lua"
 dofile "../../build/premake/ext-vorbis.lua"
 dofile "../../build/premake/ext-zlib.lua"

end

if _OPTIONS["group"] == "openmpt123" then

solution "openmpt123"
 location ( "../../build/" .. mpt_projectpathname )
if MPT_WITH_SHARED then
 configurations { "Debug", "Release", "DebugShared", "ReleaseShared" }
else
 configurations { "Debug", "Release" }
end
 platforms { "x86", "x86_64" }

 dofile "../../build/premake/mpt-openmpt123.lua"
 dofile "../../build/premake/mpt-libopenmpt.lua"
 dofile "../../build/premake/ext-flac.lua"
 dofile "../../build/premake/ext-ogg.lua"
 dofile "../../build/premake/ext-portaudio.lua"
 dofile "../../build/premake/ext-vorbis.lua"
 dofile "../../build/premake/ext-zlib.lua"

end

if _OPTIONS["group"] == "PluginBridge" then

solution "PluginBridge"
 location ( "../../build/" .. mpt_projectpathname )
 configurations { "Debug", "Release", "DebugMDd", "ReleaseLTCG" }
 platforms { "x86", "x86_64" }

 dofile "../../build/premake/mpt-PluginBridge.lua"

end

if 1 == 0 then
-- disabled
if _OPTIONS["group"] == "OpenMPT-VSTi" then

solution "OpenMPT-VSTi"
 location ( "../../build/" .. mpt_projectpathname )
 configurations { "Debug", "Release" }
 platforms { "x86", "x86_64" }
 
 dofile "../../build/premake/mpt-OpenMPT-VSTi.lua"
 dofile "../../build/premake/ext-flac.lua"
 dofile "../../build/premake/ext-lhasa.lua"
 dofile "../../build/premake/ext-minizip.lua"
 dofile "../../build/premake/ext-ogg.lua"
 dofile "../../build/premake/ext-opus.lua"
 dofile "../../build/premake/ext-opusfile.lua"
 dofile "../../build/premake/ext-portaudio.lua"
 dofile "../../build/premake/ext-portmidi.lua"
 dofile "../../build/premake/ext-r8brain.lua"
 dofile "../../build/premake/ext-smbPitchShift.lua"
 dofile "../../build/premake/ext-soundtouch.lua"
 dofile "../../build/premake/ext-UnRAR.lua"
 dofile "../../build/premake/ext-vorbis.lua"
 dofile "../../build/premake/ext-zlib.lua"

end
end

if _OPTIONS["group"] == "OpenMPT" then

solution "OpenMPT"
 location ( "../../build/" .. mpt_projectpathname )
if MPT_WITH_SHARED then
 configurations { "Debug", "Release", "DebugMDd", "ReleaseLTCG", "DebugShared", "ReleaseShared" }
else
 configurations { "Debug", "Release", "DebugMDd", "ReleaseLTCG" }
end
 platforms { "x86", "x86_64" }
 
 dofile "../../build/premake/mpt-OpenMPT.lua"
 dofile "../../build/premake/mpt-PluginBridge.lua"
 dofile "../../build/premake/ext-flac.lua"
 dofile "../../build/premake/ext-lhasa.lua"
 dofile "../../build/premake/ext-minizip.lua"
 dofile "../../build/premake/ext-ogg.lua"
 dofile "../../build/premake/ext-opus.lua"
 dofile "../../build/premake/ext-opusfile.lua"
 dofile "../../build/premake/ext-portaudio.lua"
 dofile "../../build/premake/ext-portmidi.lua"
 dofile "../../build/premake/ext-r8brain.lua"
 dofile "../../build/premake/ext-smbPitchShift.lua"
 dofile "../../build/premake/ext-soundtouch.lua"
 dofile "../../build/premake/ext-UnRAR.lua"
 dofile "../../build/premake/ext-vorbis.lua"
 dofile "../../build/premake/ext-zlib.lua"

end

-- overwrite all external projects once again with the full matrix of possible build config combinations
if _OPTIONS["group"] == "all-externals" then

solution "all-externals"
 location ( "../../build/" .. mpt_projectpathname .. "-ext" )
if MPT_WITH_SHARED then
 configurations { "Debug", "Release", "DebugMDd", "ReleaseLTCG", "DebugShared", "ReleaseShared" }
else
 configurations { "Debug", "Release", "DebugMDd", "ReleaseLTCG" }
end
 platforms { "x86", "x86_64" }

 dofile "../../build/premake/ext-flac.lua"
 dofile "../../build/premake/ext-lhasa.lua"
 dofile "../../build/premake/ext-miniz.lua"
 dofile "../../build/premake/ext-minizip.lua"
 dofile "../../build/premake/ext-ogg.lua"
 dofile "../../build/premake/ext-opus.lua"
 dofile "../../build/premake/ext-opusfile.lua"
 dofile "../../build/premake/ext-portaudio.lua"
 dofile "../../build/premake/ext-portmidi.lua"
 dofile "../../build/premake/ext-pugixml.lua"
 dofile "../../build/premake/ext-r8brain.lua"
 dofile "../../build/premake/ext-smbPitchShift.lua"
 dofile "../../build/premake/ext-soundtouch.lua"
 dofile "../../build/premake/ext-stb_vorbis.lua"
 dofile "../../build/premake/ext-UnRAR.lua"
 dofile "../../build/premake/ext-vorbis.lua"
 dofile "../../build/premake/ext-zlib.lua"

end
