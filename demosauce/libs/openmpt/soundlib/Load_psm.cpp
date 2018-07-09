/*
 * Load_psm.cpp
 * ------------
 * Purpose: PSM16 and new PSM (ProTracker Studio) module loader
 * Notes  : This is partly based on http://www.shikadi.net/moddingwiki/ProTracker_Studio_Module
 *          and partly reverse-engineered. Also thanks to the author of foo_dumb, the source code gave me a few clues. :)
 * Authors: Johannes Schultz
 * The OpenMPT source code is released under the BSD license. Read LICENSE for more details.
 */


#include "stdafx.h"
#include "Loaders.h"
#include "ChunkReader.h"

#ifdef LIBOPENMPT_BUILD
#define MPT_PSM_USE_REAL_SUBSONGS
#endif

OPENMPT_NAMESPACE_BEGIN

#ifdef NEEDS_PRAGMA_PACK
#pragma pack(push, 1)
#endif

////////////////////////////////////////////////////////////
//
//  New PSM support starts here. PSM16 structs are below.
//

// PSM File Header
struct PACKED PSMFileHeader
{
	char   formatID[4];		// "PSM " (new format)
	uint32 fileSize;		// Filesize - 12
	char   fileInfoID[4];	// "FILE"

	// Convert all multi-byte numeric values to current platform's endianness or vice versa.
	void ConvertEndianness()
	{
		SwapBytesLE(fileSize);
	}
};

STATIC_ASSERT(sizeof(PSMFileHeader) == 12);

// RIFF-style Chunk
struct PACKED PSMChunk
{
	// 32-Bit chunk identifiers
	enum ChunkIdentifiers
	{
		idTITL	= MAGIC4LE('T','I','T','L'),
		idSDFT	= MAGIC4LE('S','D','F','T'),
		idPBOD	= MAGIC4LE('P','B','O','D'),
		idSONG	= MAGIC4LE('S','O','N','G'),
		idDATE	= MAGIC4LE('D','A','T','E'),
		idOPLH	= MAGIC4LE('O','P','L','H'),
		idPPAN	= MAGIC4LE('P','P','A','N'),
		idPATT	= MAGIC4LE('P','A','T','T'),
		idDSAM	= MAGIC4LE('D','S','A','M'),
		idDSMP	= MAGIC4LE('D','S','M','P'),
	};

	typedef ChunkIdentifiers id_type;

	uint32 id;
	uint32 length;

	size_t GetLength() const
	{
		return SwapBytesReturnLE(length);
	}

	id_type GetID() const
	{
		return static_cast<id_type>(SwapBytesReturnLE(id));
	}
};

STATIC_ASSERT(sizeof(PSMChunk) == 8);

// Song Information
struct PACKED PSMSongHeader
{
	char  songType[9];		// Mostly "MAINSONG " (But not in Extreme Pinball!)
	uint8 compression;		// 1 - uncompressed
	uint8 numChannels;		// Number of channels

};

STATIC_ASSERT(sizeof(PSMSongHeader) == 11);

// Regular sample header
struct PACKED PSMSampleHeader
{
	uint8  flags;
	char   fileName[8];		// Filename of the original module (without extension)
	char   sampleID[4];		// INS0...INS9 (only last digit of sample ID, i.e. sample 1 and sample 11 are equal)
	char   sampleName[33];
	uint8  unknown1[6];		// 00 00 00 00 00 FF
	uint16 sampleNumber;
	uint32 sampleLength;
	uint32 loopStart;
	uint32 loopEnd;			// FF FF FF FF = end of sample
	uint8  unknown3;
	uint8  finetune;		// unused? always 0
	uint8  defaultVolume;
	uint32 unknown4;
	uint32 c5Freq;			// MASI ignores the high 16 bits
	uint8  padding[19];		// 00 ... 00

	// Convert all multi-byte numeric values to current platform's endianness or vice versa.
	void ConvertEndianness()
	{
		SwapBytesLE(sampleNumber);
		SwapBytesLE(sampleLength);
		SwapBytesLE(loopStart);
		SwapBytesLE(loopEnd);
		SwapBytesLE(c5Freq);
	}

	// Convert header data to OpenMPT's internal format
	void ConvertToMPT(ModSample &mptSmp) const
	{
		mptSmp.Initialize();
		mpt::String::Read<mpt::String::maybeNullTerminated>(mptSmp.filename, fileName);

		mptSmp.nC5Speed = c5Freq;
		mptSmp.nLength = sampleLength;
		mptSmp.nLoopStart = loopStart;
		// It is not entirely clear if/when we should add +1 to the loopEnd value.
		// Sample 8 in the medieval table music of Extreme Pinball and CONVERT.EXE v1.36 suggest that we should do so.
		// But for other tunes it's not correct, e.g. the OMF 2097 music!
		mptSmp.nLoopEnd = loopEnd;
		mptSmp.nVolume = (defaultVolume + 1) * 2;
		mptSmp.uFlags.set(CHN_LOOP, (flags & 0x80) != 0);
		LimitMax(mptSmp.nLoopEnd, mptSmp.nLength);
		LimitMax(mptSmp.nLoopStart, mptSmp.nLoopEnd);
	}
};

STATIC_ASSERT(sizeof(PSMSampleHeader) == 96);

// Sinaria sample header (and possibly other games)
struct PACKED PSMSinariaSampleHeader
{
	uint8  flags;
	char   fileName[8];		// Filename of the original module (without extension)
	char   sampleID[8];		// INS0...INS99999
	char   sampleName[33];
	uint8  unknown1[6];		// 00 00 00 00 00 FF
	uint16 sampleNumber;
	uint32 sampleLength;
	uint32 loopStart;
	uint32 loopEnd;
	uint16 unknown3;
	uint8  finetune;		// Possibly finetune like in PSM16, but sounds even worse than just ignoring it
	uint8  defaultVolume;
	uint32 unknown4;
	uint16 c5Freq;
	char   padding[16];		// 00 ... 00

	// Convert all multi-byte numeric values to current platform's endianness or vice versa.
	void ConvertEndianness()
	{
		SwapBytesLE(sampleNumber);
		SwapBytesLE(sampleLength);
		SwapBytesLE(loopStart);
		SwapBytesLE(loopEnd);
		SwapBytesLE(c5Freq);
	}

	// Convert header data to OpenMPT's internal format
	void ConvertToMPT(ModSample &mptSmp) const
	{
		mptSmp.Initialize();
		mpt::String::Read<mpt::String::maybeNullTerminated>(mptSmp.filename, fileName);

		mptSmp.nC5Speed = c5Freq;
		mptSmp.nLength = sampleLength;
		mptSmp.nLoopStart = loopStart;
		mptSmp.nLoopEnd = loopEnd;
		mptSmp.nVolume = (defaultVolume + 1) * 2;
		mptSmp.uFlags.set(CHN_LOOP, (flags & 0x80) != 0);
		LimitMax(mptSmp.nLoopEnd, mptSmp.nLength);
		LimitMax(mptSmp.nLoopStart, mptSmp.nLoopEnd);
	}
};

STATIC_ASSERT(sizeof(PSMSinariaSampleHeader) == 96);

#ifdef NEEDS_PRAGMA_PACK
#pragma pack(pop)
#endif


struct PSMSubSong // For internal use (pattern conversion)
{
	std::vector<uint8> channelPanning, channelVolume;
	std::vector<bool> channelSurround;
	uint8 defaultTempo, defaultSpeed;
	char  songName[10];
	ORDERINDEX startOrder, endOrder, restartPos;

	PSMSubSong()
	{
		channelPanning.assign(MAX_BASECHANNELS, 128);
		channelVolume.assign(MAX_BASECHANNELS, 64);
		channelSurround.assign(MAX_BASECHANNELS, false);
		MemsetZero(songName);
		defaultTempo = 125;
		defaultSpeed = 6;
		startOrder = endOrder = ORDERINDEX_INVALID;
		restartPos = 0;
	}
};


// Portamento effect conversion (depending on format version)
static uint8 ConvertPSMPorta(uint8 param, bool sinariaFormat)
//-----------------------------------------------------------
{
	if(sinariaFormat)
		return param;
	if(param < 4)
		return (param | 0xF0);
	else
		return (param >> 2);
}


// Read a Pattern ID (something like "P0  " or "P13 " in the old format, or "PATT0   " in Sinaria)
static PATTERNINDEX ReadPSMPatternIndex(FileReader &file, bool &sinariaFormat)
//----------------------------------------------------------------------------
{
	char patternID[5];
	uint8 offset = 1;
	file.ReadString<mpt::String::spacePadded>(patternID, 4);
	if(!memcmp(patternID, "PATT", 4))
	{
		file.ReadString<mpt::String::spacePadded>(patternID, 4);
		sinariaFormat = true;
		offset = 0;
	}
	return ConvertStrTo<uint16>(&patternID[offset]);

}


bool CSoundFile::ReadPSM(FileReader &file, ModLoadingFlags loadFlags)
//-------------------------------------------------------------------
{
	file.Rewind();
	PSMFileHeader fileHeader;
	if(!file.ReadConvertEndianness(fileHeader))
	{
		return false;
	}

#ifdef MPT_PSM_DECRYPT
	// CONVERT.EXE /K - I don't think any game ever used this.
	std::vector<mpt::byte> decrypted;
	if(!memcmp(fileHeader.formatID, "QUP$", 4)
		&& !memcmp(fileHeader.fileInfoID, "OSWQ", 4))
	{
		if(loadFlags == onlyVerifyHeader)
			return true;
		file.Rewind();
		decrypted.resize(file.GetLength());
		file.ReadRaw(&decrypted[0], decrypted.size());
		uint8 i = 0;
		for(std::vector<mpt::byte>::iterator c = decrypted.begin(); c != decrypted.end(); c++)
		{
			*c -= ++i;
		}
		file = FileReader(mpt::as_span(decrypted));
		file.ReadConvertEndianness(fileHeader);
	}
#endif // MPT_PSM_DECRYPT

	// Check header
	if(memcmp(fileHeader.formatID, "PSM ", 4)
		|| memcmp(fileHeader.fileInfoID, "FILE", 4))
	{
		return false;
	}

	ChunkReader chunkFile(file);
	ChunkReader::ChunkList<PSMChunk> chunks;
	if(loadFlags == onlyVerifyHeader)
		chunks = chunkFile.ReadChunksUntil<PSMChunk>(1, PSMChunk::idSDFT);
	else
		chunks = chunkFile.ReadChunks<PSMChunk>(1);

	// "SDFT" - Format info (song data starts here)
	if(!chunks.GetChunk(PSMChunk::idSDFT).ReadMagic("MAINSONG"))
		return false;
	else if(loadFlags == onlyVerifyHeader)
		return true;

	// Yep, this seems to be a valid file.
	InitializeGlobals(MOD_TYPE_PSM);
	m_SongFlags = SONG_ITOLDEFFECTS | SONG_ITCOMPATGXX;

	// "TITL" - Song Title
	FileReader titleChunk = chunks.GetChunk(PSMChunk::idTITL);
	titleChunk.ReadString<mpt::String::spacePadded>(m_songName, titleChunk.GetLength());

	Order.clear();
	// Subsong setup
	std::vector<PSMSubSong> subsongs;
	bool subsongPanningDiffers = false; // Do we have subsongs with different panning positions?
	bool sinariaFormat = false; // The game "Sinaria" uses a slightly modified PSM structure - in some ways it's more like PSM16 (e.g. effects).

	// "SONG" - Subsong information (channel count etc)
	std::vector<FileReader> songChunks = chunks.GetAllChunks(PSMChunk::idSONG);
	for(std::vector<FileReader>::iterator subsongIter = songChunks.begin(); subsongIter != songChunks.end(); subsongIter++)
	{
		ChunkReader chunk(*subsongIter);
		PSMSongHeader songHeader;
		if(!chunk.ReadStruct(songHeader)
			|| songHeader.compression != 0x01)	// No compression for PSM files
		{
			return false;
		}
		// Subsongs *might* have different channel count
		m_nChannels = Clamp(static_cast<CHANNELINDEX>(songHeader.numChannels), m_nChannels, MAX_BASECHANNELS);

		PSMSubSong subsong;
		mpt::String::Read<mpt::String::nullTerminated>(subsong.songName, songHeader.songType);

#ifdef MPT_PSM_USE_REAL_SUBSONGS
		if(Order.GetLength() != 0)
		{
			// Add a new sequence for this subsong
			if(Order.AddSequence(false) == SEQUENCEINDEX_INVALID)
				break;
			Order.clear();
		}
		Order.SetName(subsong.songName);
#endif // MPT_PSM_USE_REAL_SUBSONGS

		// Read "Sub chunks"
		ChunkReader::ChunkList<PSMChunk> subChunks = chunk.ReadChunks<PSMChunk>(1);
		for(ChunkReader::ChunkList<PSMChunk>::iterator subChunkIter = subChunks.begin(); subChunkIter != subChunks.end(); subChunkIter++)
		{
			FileReader subChunk(subChunkIter->GetData());
			PSMChunk subChunkHead = subChunkIter->GetHeader();
			
			switch(subChunkHead.GetID())
			{
#if 0
			case PSMChunk::idDATE: // "DATE" - Conversion date (YYMMDD)
				if(subChunkHead.GetLength() == 6)
				{
					char cversion[7];
					subChunk.ReadString<mpt::String::maybeNullTerminated>(cversion, 6);
					uint32 version = ConvertStrTo<uint32>(cversion);
					// Sinaria song dates (just to go sure...)
					if(version == 800211 || version == 940902 || version == 940903 ||
						version == 940906 || version == 940914 || version == 941213)
						sinariaFormat = true;
				}
				break;
#endif

			case PSMChunk::idOPLH: // "OPLH" - Order list, channel + module settings
				if(subChunkHead.GetLength() >= 9)
				{
					// First two bytes = Number of chunks that follow
					//uint16 totalChunks = subChunk.ReadUint16LE();
					subChunk.Skip(2);

					// Now, the interesting part begins!
					uint16 chunkCount = 0, firstOrderChunk = uint16_max;

					// "Sub sub chunks" (grrrr, silly format)
					while(subChunk.CanRead(1))
					{
						uint8 opcode = subChunk.ReadUint8();
						if(!opcode)
						{
							// Last chunk was reached.
							break;
						}

						// Note: This is more like a playlist than a collection of global values.
						// In theory, a tempo item inbetween two order items should modify the
						// tempo when switching patterns. No module uses this feature in practice
						// though, so we can keep our loader simple.
						// Unimplemented opcodes do nothing or freeze MASI.
						switch(opcode)
						{
						case 0x01: // Play order list item
							{
								if(subsong.startOrder == ORDERINDEX_INVALID)
									subsong.startOrder = Order.size();
								subsong.endOrder = Order.size();
								PATTERNINDEX pat = ReadPSMPatternIndex(subChunk, sinariaFormat);
								if(pat == 0xFF)
									pat = Order.GetInvalidPatIndex();
								else if(pat == 0xFE)
									pat = Order.GetIgnoreIndex();
								Order.Append(pat);
								// Decide whether this is the first order chunk or not (for finding out the correct restart position)
								if(firstOrderChunk == uint16_max)
									firstOrderChunk = chunkCount;
							}
							break;

						// 0x02: Play Range
						// 0x03: Jump Loop

						case 0x04: // Jump Line (Restart position)
							{
								uint16 restartChunk = subChunk.ReadUint16LE();
								if(restartChunk >= firstOrderChunk)
									subsong.restartPos = static_cast<ORDERINDEX>(restartChunk - firstOrderChunk);	// Close enough - we assume that order list is continuous (like in any real-world PSM)
								Order.SetRestartPos(subsong.restartPos);
							}
							break;

						// 0x05: Channel Flip
						// 0x06: Transpose

						case 0x07: // Default Speed
							subsong.defaultSpeed = subChunk.ReadUint8();
							break;

						case 0x08: // Default Tempo
							subsong.defaultTempo =  subChunk.ReadUint8();
							break;

						case 0x0C: // Sample map table
							// Never seems to be different, so...
							// This is probably a part of the never-implemented "mini programming language" mentioned in the PSM docs.
							// Output of PLAY.EXE: "SMapTabl from pos 0 to pos -1 starting at 0 and adding 1 to it each time"
							// It appears that this maps e.g. what is "I0" in the file to sample 1.
							// If we were being fancy, we could implement this, but in practice it won't matter.
							if (subChunk.ReadUint8() != 0x00 || subChunk.ReadUint8() != 0xFF ||	// "0 to -1" (does not seem to do anything)
								subChunk.ReadUint8() != 0x00 || subChunk.ReadUint8() != 0x00 ||	// "at 0" (actually this appears to be the adding part - changing this to 0x01 0x00 offsets all samples by 1)
								subChunk.ReadUint8() != 0x01 || subChunk.ReadUint8() != 0x00)	// "adding 1" (does not seem to do anything)
							{
								return false;
							}
							break;

						case 0x0D: // Channel panning table - can be set using CONVERT.EXE /E
							{
								uint8 chn = subChunk.ReadUint8();
								uint8 pan = subChunk.ReadUint8();
								uint8 type = subChunk.ReadUint8();
								if(chn < subsong.channelPanning.size())
								{
									switch(type)
									{
									case 0: // use panning
										subsong.channelPanning[chn] = pan ^ 128;
										subsong.channelSurround[chn] = false;
										break;

									case 2: // surround
										subsong.channelPanning[chn] = 128;
										subsong.channelSurround[chn] = true;
										break;

									case 4: // center
										subsong.channelPanning[chn] = 128;
										subsong.channelSurround[chn] = false;
										break;

									}
									if(subsongPanningDiffers == false && subsongs.size() > 0)
									{
										if(subsongs.back().channelPanning[chn] != subsong.channelPanning[chn]
										|| subsongs.back().channelSurround[chn] != subsong.channelSurround[chn])
											subsongPanningDiffers = true;
									}
								}
							}
							break;

						case 0x0E: // Channel volume table (0...255) - can be set using CONVERT.EXE /E, is 255 in all "official" PSMs except for some OMF 2097 tracks
							{
								uint8 chn = subChunk.ReadUint8();
								uint8 vol = subChunk.ReadUint8();
								if(chn < subsong.channelVolume.size())
								{
									subsong.channelVolume[chn] = (vol / 4u) + 1;
								}
							}
							break;

						default:
							// Should never happen in "real" PSM files. But in this case, we have to quit as we don't know how big the chunk really is.
							return false;

						}
						chunkCount++;
					}
				}
				break;

			case PSMChunk::idPPAN: // PPAN - Channel panning table (used in Sinaria)
				// In some Sinaria tunes, this is actually longer than 2 * channels...
				MPT_ASSERT(subChunkHead.GetLength() >= m_nChannels * 2u);
				for(CHANNELINDEX chn = 0; chn < m_nChannels; chn++)
				{
					if(!subChunk.CanRead(2))
						break;

					uint8 type = subChunk.ReadUint8();
					uint8 pan = subChunk.ReadUint8();
					switch(type)
					{
					case 0: // use panning
						subsong.channelPanning[chn] = pan ^ 128;
						subsong.channelSurround[chn] = false;
						break;

					case 2: // surround
						subsong.channelPanning[chn] = 128;
						subsong.channelSurround[chn] = true;
						break;

					case 4: // center
						subsong.channelPanning[chn] = 128;
						subsong.channelSurround[chn] = false;
						break;

					default:
						break;
					}
				}
				break;

			case PSMChunk::idPATT: // PATT - Pattern list
				// We don't really need this.
				break;

			case PSMChunk::idDSAM: // DSAM - Sample list
				// We don't need this either.
				break;

			default:
				break;

			}
		}

		// Attach this subsong to the subsong list - finally, all "sub sub sub ..." chunks are parsed.
		if(subsong.startOrder != ORDERINDEX_INVALID && subsong.endOrder != ORDERINDEX_INVALID)
		{
			// Separate subsongs by "---" patterns
			Order.Append();
			subsongs.push_back(subsong);
		}
	}

#ifdef MPT_PSM_USE_REAL_SUBSONGS
	Order.SetSequence(0);
#endif // MPT_PSM_USE_REAL_SUBSONGS

	if(subsongs.empty())
		return false;

	// DSMP - Samples
	if(loadFlags & loadSampleData)
	{
		std::vector<FileReader> sampleChunks = chunks.GetAllChunks(PSMChunk::idDSMP);
		for(std::vector<FileReader>::iterator sampleIter = sampleChunks.begin(); sampleIter != sampleChunks.end(); sampleIter++)
		{
			FileReader &chunk(*sampleIter);
			SAMPLEINDEX smp;
			if(!sinariaFormat)
			{
				// Original header
				PSMSampleHeader sampleHeader;
				if(!chunk.ReadConvertEndianness(sampleHeader))
				{
					continue;
				}

				smp = static_cast<SAMPLEINDEX>(sampleHeader.sampleNumber + 1);
				if(smp > 0 && smp < MAX_SAMPLES)
				{
					m_nSamples = std::max(m_nSamples, smp);
					mpt::String::Read<mpt::String::nullTerminated>(m_szNames[smp], sampleHeader.sampleName);

					sampleHeader.ConvertToMPT(Samples[smp]);
				}
			} else
			{
				// Sinaria uses a slightly different sample header
				PSMSinariaSampleHeader sampleHeader;
				if(!chunk.ReadConvertEndianness(sampleHeader))
				{
					continue;
				}

				smp = static_cast<SAMPLEINDEX>(sampleHeader.sampleNumber + 1);
				if(smp > 0 && smp < MAX_SAMPLES)
				{
					m_nSamples = std::max(m_nSamples, smp);
					mpt::String::Read<mpt::String::nullTerminated>(m_szNames[smp], sampleHeader.sampleName);

					sampleHeader.ConvertToMPT(Samples[smp]);
				}
			}
			if(smp > 0 && smp < MAX_SAMPLES)
			{
				SampleIO(
					SampleIO::_8bit,
					SampleIO::mono,
					SampleIO::littleEndian,
					SampleIO::deltaPCM).ReadSample(Samples[smp], chunk);
			}
		}
	}

	// Make the default variables of the first subsong global
	m_nDefaultSpeed = subsongs[0].defaultSpeed;
	m_nDefaultTempo.Set(subsongs[0].defaultTempo);
	Order.SetRestartPos(subsongs[0].restartPos);
	for(CHANNELINDEX chn = 0; chn < m_nChannels; chn++)
	{
		ChnSettings[chn].Reset();
		ChnSettings[chn].nVolume = subsongs[0].channelVolume[chn];
		ChnSettings[chn].nPan = subsongs[0].channelPanning[chn];
		ChnSettings[chn].dwFlags.set(CHN_SURROUND, subsongs[0].channelSurround[chn]);
	}

	m_madeWithTracker = sinariaFormat ? "Epic MegaGames MASI (New Version / Sinaria)" : "Epic MegaGames MASI (New Version)";

	if(!(loadFlags & loadPatternData) || m_nChannels == 0)
	{
		return true;
	}

	// "PBOD" - Pattern data of a single pattern
	// Now that we know the number of channels, we can go through all the patterns.
	std::vector<FileReader> pattChunks = chunks.GetAllChunks(PSMChunk::idPBOD);
	for(std::vector<FileReader>::iterator patternIter = pattChunks.begin(); patternIter != pattChunks.end(); patternIter++)
	{
		FileReader &chunk(*patternIter);
		if(chunk.GetLength() != chunk.ReadUint32LE()	// Same value twice
			|| !chunk.LengthIsAtLeast(8))
		{
			continue;
		}

		PATTERNINDEX pat = ReadPSMPatternIndex(chunk, sinariaFormat);
		uint16 numRows = chunk.ReadUint16LE();

		if(!Patterns.Insert(pat, numRows))
		{
			continue;
		}

		enum
		{
			noteFlag	= 0x80,
			instrFlag	= 0x40,
			volFlag		= 0x20,
			effectFlag	= 0x10,
		};

		// Read pattern.
		for(ROWINDEX row = 0; row < numRows; row++)
		{
			PatternRow rowBase = Patterns[pat].GetRow(row);
			uint16 rowSize = chunk.ReadUint16LE();
			if(rowSize <= 2)
			{
				continue;
			}

			FileReader rowChunk = chunk.ReadChunk(rowSize - 2);

			while(rowChunk.CanRead(3))
			{
				uint8 flags = rowChunk.ReadUint8();
				uint8 channel = rowChunk.ReadUint8();
				// Point to the correct channel
				ModCommand &m = rowBase[std::min<CHANNELINDEX>(m_nChannels - 1, channel)];

				if(flags & noteFlag)
				{
					// Note present
					uint8 note = rowChunk.ReadUint8();
					if(!sinariaFormat)
					{
						if(note == 0xFF)	// Can be found in a few files but is apparently not supported by MASI
							note = NOTE_NOTECUT;
						else
							if(note < 129) note = (note & 0x0F) + 12 * (note >> 4) + 13;
					} else
					{
						if(note < 85) note += 36;
					}
					m.note = note;
				}

				if(flags & instrFlag)
				{
					// Instrument present
					m.instr = rowChunk.ReadUint8() + 1;
				}

				if(flags & volFlag)
				{
					// Volume present
					uint8 vol = rowChunk.ReadUint8();
					m.volcmd = VOLCMD_VOLUME;
					m.vol = (MIN(vol, 127) + 1) / 2;
				}

				if(flags & effectFlag)
				{
					// Effect present - convert
					m.command = rowChunk.ReadUint8();
					m.param = rowChunk.ReadUint8();

					// This list is annoyingly similar to PSM16, but not quite identical.
					switch(m.command)
					{
					// Volslides
					case 0x01: // fine volslide up
						m.command = CMD_VOLUMESLIDE;
						if (sinariaFormat) m.param = (m.param << 4) | 0x0F;
						else m.param = ((m.param & 0x1E) << 3) | 0x0F;
						break;
					case 0x02: // volslide up
						m.command = CMD_VOLUMESLIDE;
						if (sinariaFormat) m.param = 0xF0 & (m.param << 4);
						else m.param = 0xF0 & (m.param << 3);
						break;
					case 0x03: // fine volslide down
						m.command = CMD_VOLUMESLIDE;
						if (sinariaFormat) m.param |= 0xF0;
						else m.param = 0xF0 | (m.param >> 1);
						break;
					case 0x04: // volslide down
						m.command = CMD_VOLUMESLIDE;
						if (sinariaFormat) m.param &= 0x0F;
						else if(m.param < 2) m.param |= 0xF0; else m.param = (m.param >> 1) & 0x0F;
						break;

					// Portamento
					case 0x0B: // fine portamento up
						m.command = CMD_PORTAMENTOUP;
						m.param = 0xF0 | ConvertPSMPorta(m.param, sinariaFormat);
						break;
					case 0x0C: // portamento up
						m.command = CMD_PORTAMENTOUP;
						m.param = ConvertPSMPorta(m.param, sinariaFormat);
						break;
					case 0x0D: // fine portamento down
						m.command = CMD_PORTAMENTODOWN;
						m.param = 0xF0 | ConvertPSMPorta(m.param, sinariaFormat);
						break;
					case 0x0E: // portamento down
						m.command = CMD_PORTAMENTODOWN;
						m.param = ConvertPSMPorta(m.param, sinariaFormat);
						break;
					case 0x0F: // tone portamento
						m.command = CMD_TONEPORTAMENTO;
						if(!sinariaFormat) m.param >>= 2;
						break;
					case 0x11: // glissando control
						m.command = CMD_S3MCMDEX;
						m.param = 0x10 | (m.param & 0x01);
						break;
					case 0x10: // tone portamento + volslide up
						m.command = CMD_TONEPORTAVOL;
						m.param = m.param & 0xF0;
						break;
					case 0x12: // tone portamento + volslide down
						m.command = CMD_TONEPORTAVOL;
						m.param = (m.param >> 4) & 0x0F;
						break;

					case 0x13: // ScreamTracker command S - actually hangs / crashes MASI
						m.command = CMD_S3MCMDEX;
						break;

					// Vibrato
					case 0x15: // vibrato
						m.command = CMD_VIBRATO;
						break;
					case 0x16: // vibrato waveform
						m.command = CMD_S3MCMDEX;
						m.param = 0x30 | (m.param & 0x0F);
						break;
					case 0x17: // vibrato + volslide up
						m.command = CMD_VIBRATOVOL;
						m.param = 0xF0 | m.param;
						break;
					case 0x18: // vibrato + volslide down
						m.command = CMD_VIBRATOVOL;
						break;

					// Tremolo
					case 0x1F: // tremolo
						m.command = CMD_TREMOLO;
						break;
					case 0x20: // tremolo waveform
						m.command = CMD_S3MCMDEX;
						m.param = 0x40 | (m.param & 0x0F);
						break;

					// Sample commands
					case 0x29: // 3-byte offset - we only support the middle byte.
						m.command = CMD_OFFSET;
						m.param = rowChunk.ReadUint8();
						rowChunk.Skip(1);
						break;
					case 0x2A: // retrigger
						m.command = CMD_RETRIG;
						break;
					case 0x2B: // note cut
						m.command = CMD_S3MCMDEX;
						m.param = 0xC0 | (m.param & 0x0F);
						break;
					case 0x2C: // note delay
						m.command = CMD_S3MCMDEX;
						m.param = 0xD0 | (m.param & 0x0F);
						break;

					// Position change
					case 0x33: // position jump - MASI seems to ignore this command, and CONVERT.EXE never writes it
						m.command = CMD_POSITIONJUMP;
						m.param /= 2u;	// actually it is probably just an index into the order table
						rowChunk.Skip(1);
						break;
					case 0x34: // pattern break
						m.command = CMD_PATTERNBREAK;
						// When converting from S3M, the parameter is double-BDC-encoded (wtf!)
						// When converting from MOD, it's in binary.
						// MASI ignores the parameter entirely, and so do we.
						m.param = 0;
						break;
					case 0x35: // loop pattern
						m.command = CMD_S3MCMDEX;
						m.param = 0xB0 | (m.param & 0x0F);
						break;
					case 0x36: // pattern delay
						m.command = CMD_S3MCMDEX;
						m.param = 0xE0 | (m.param & 0x0F);
						break;

					// speed change
					case 0x3D: // set speed
						m.command = CMD_SPEED;
						break;
					case 0x3E: // set tempo
						m.command = CMD_TEMPO;
						break;

					// misc commands
					case 0x47: // arpeggio
						m.command = CMD_ARPEGGIO;
						break;
					case 0x48: // set finetune
						m.command = CMD_S3MCMDEX;
						m.param = 0x20 | (m.param & 0x0F);
						break;
					case 0x49: // set balance
						m.command = CMD_S3MCMDEX;
						m.param = 0x80 | (m.param & 0x0F);
						break;

					default:
						m.command = CMD_NONE;
						break;

					}
				}
			}
		}
	}

	if(subsongs.size() > 1)
	{
		// Write subsong "configuration" to patterns (only if there are multiple subsongs)
		for(size_t i = 0; i < subsongs.size(); i++)
		{
#ifdef MPT_PSM_USE_REAL_SUBSONGS
			ModSequence &order = Order.GetSequence(static_cast<SEQUENCEINDEX>(i));
#else
			ModSequence &order = Order;
#endif // MPT_PSM_USE_REAL_SUBSONGS
			const PSMSubSong &subsong = subsongs[i];
			PATTERNINDEX startPattern = order[subsong.startOrder];
			if(Patterns.IsValidPat(startPattern))
			{
				startPattern = order.EnsureUnique(subsong.startOrder);
				// Subsongs with different panning setup -> write to pattern (MUSIC_C.PSM)
				// Don't write channel volume for now, as there is no real-world module which needs it.
				if(subsongPanningDiffers)
				{
					for(CHANNELINDEX chn = 0; chn < m_nChannels; chn++)
					{
						if(subsong.channelSurround[chn])
							Patterns[startPattern].WriteEffect(EffectWriter(CMD_S3MCMDEX, 0x91).Row(0).Channel(chn).Retry(EffectWriter::rmTryNextRow));
						else
							Patterns[startPattern].WriteEffect(EffectWriter(CMD_PANNING8, subsong.channelPanning[chn]).Row(0).Channel(chn).Retry(EffectWriter::rmTryNextRow));
					}
				}
				// Write default tempo/speed to pattern
				Patterns[startPattern].WriteEffect(EffectWriter(CMD_SPEED, subsong.defaultSpeed).Row(0).Retry(EffectWriter::rmTryNextRow));
				Patterns[startPattern].WriteEffect(EffectWriter(CMD_TEMPO, subsong.defaultTempo).Row(0).Retry(EffectWriter::rmTryNextRow));
			}

#ifndef MPT_PSM_USE_REAL_SUBSONGS
			// Add restart position to the last pattern
			PATTERNINDEX endPattern = order[subsong.endOrder];
			if(Patterns.IsValidPat(endPattern))
			{
				endPattern = order.EnsureUnique(subsong.endOrder);
				ROWINDEX lastRow = Patterns[endPattern].GetNumRows() - 1;
				ModCommand *m;
				m = Patterns[endPattern];
				for(uint32 cell = 0; cell < m_nChannels * Patterns[endPattern].GetNumRows(); cell++, m++)
				{
					if(m->command == CMD_PATTERNBREAK || m->command == CMD_POSITIONJUMP)
					{
						lastRow = cell / m_nChannels;
						break;
					}
				}
				Patterns[endPattern].WriteEffect(EffectWriter(CMD_POSITIONJUMP, mpt::saturate_cast<ModCommand::PARAM>(subsong.startOrder + subsong.restartPos)).Row(lastRow).Retry(EffectWriter::rmTryPreviousRow));
			}

			// Set the subsong name to all pattern names
			for(ORDERINDEX ord = subsong.startOrder; ord <= subsong.endOrder; ord++)
			{
				if(Patterns.IsValidIndex(order[ord]))
					Patterns[order[ord]].SetName(subsong.songName);
			}
#endif // MPT_PSM_USE_REAL_SUBSONGS
		}
	}

	return true;
}

////////////////////////////////
//
//  PSM16 support starts here.
//

#ifdef NEEDS_PRAGMA_PACK
#pragma pack(push, 1)
#endif

struct PACKED PSM16FileHeader
{
	// 32-Bit chunk identifiers
	enum PSM16Magic
	{
		idPORD	= MAGIC4LE('P','O','R','D'),
		idPPAN	= MAGIC4LE('P','P','A','N'),
		idPSAH	= MAGIC4LE('P','S','A','H'),
		idPPAT	= MAGIC4LE('P','P','A','T'),
	};

	char   formatID[4];		// "PSM\xFE" (PSM16)
	char   songName[59];	// Song title, padded with nulls
	uint8  lineEnd;			// $1A
	uint8  songType;		// Song Type bitfield
	uint8  formatVersion;	// $10
	uint8  patternVersion;  // 0 or 1
	uint8  songSpeed;		// 1 ... 255
	uint8  songTempo;		// 32 ... 255
	uint8  masterVolume;	// 0 ... 255
	uint16 songLength;		// 0 ... 255 (number of patterns to play in the song)
	uint16 songOrders;		// 0 ... 255 (same as previous value as no subsongs are present)
	uint16 numPatterns;		// 1 ... 255
	uint16 numSamples;		// 1 ... 255
	uint16 numChannelsPlay;	// 0 ... 32 (max. number of channels to play)
	uint16 numChannelsReal;	// 0 ... 32 (max. number of channels to process)
	uint32 orderOffset;		// Pointer to order list
	uint32 panOffset;		// Pointer to pan table
	uint32 patOffset;		// Pointer to pattern data
	uint32 smpOffset;		// Pointer to sample headers
	uint32 commentsOffset;	// Pointer to song comment
	uint32 patSize;			// Size of all patterns
	uint8  filler[40];

	// Convert all multi-byte numeric values to current platform's endianness or vice versa.
	void ConvertEndianness()
	{
		SwapBytesLE(songLength);
		SwapBytesLE(songOrders);
		SwapBytesLE(numPatterns);
		SwapBytesLE(numSamples);
		SwapBytesLE(numChannelsPlay);
		SwapBytesLE(numChannelsReal);
		SwapBytesLE(orderOffset);
		SwapBytesLE(panOffset);
		SwapBytesLE(patOffset);
		SwapBytesLE(smpOffset);
		SwapBytesLE(commentsOffset);
		SwapBytesLE(patSize);
	}
};

STATIC_ASSERT(sizeof(PSM16FileHeader) == 146);

struct PACKED PSM16SampleHeader
{
	enum SampleFlags
	{
		smpMask		= 0x7F,
		smp16Bit	= 0x04,
		smpUnsigned	= 0x08,
		smpDelta	= 0x10,
		smpPingPong	= 0x20,
		smpLoop		= 0x80,
	};

	char   filename[13];	// null-terminated
	char   name[24];		// ditto
	uint32 offset;			// in file
	uint32 memoffset;		// not used
	uint16 sampleNumber;	// 1 ... 255
	uint8  flags;			// sample flag bitfield
	uint32 length;			// in bytes
	uint32 loopStart;		// in samples?
	uint32 loopEnd;			// in samples?
	uint8  finetune;		// Low nibble = MOD finetune, high nibble = transpose (7 = center)
	uint8  volume;			// default volume
	uint16 c2freq;			// Middle-C frequency, which has to be combined with the finetune and transpose.

	// Convert all multi-byte numeric values to current platform's endianness or vice versa.
	void ConvertEndianness()
	{
		SwapBytesLE(offset);
		SwapBytesLE(memoffset);
		SwapBytesLE(sampleNumber);
		SwapBytesLE(length);
		SwapBytesLE(loopStart);
		SwapBytesLE(loopEnd);
		SwapBytesLE(c2freq);
	}

	// Convert sample header to OpenMPT's internal format
	void ConvertToMPT(ModSample &mptSmp) const
	{
		mpt::String::Read<mpt::String::nullTerminated>(mptSmp.filename, filename);

		mptSmp.nLength = length;
		mptSmp.nLoopStart = loopStart;
		mptSmp.nLoopEnd = loopEnd;
		// It seems like that finetune and transpose are added to the already given c2freq... That's a double WTF!
		// Why on earth would you want to use both systems at the same time?
		mptSmp.nC5Speed = Util::Round<uint32>(c2freq * std::pow(2.0, ((finetune ^ 0x08) - 0x78) / (12.0 * 16.0))); // ModSample::TransposeToFrequency(mptSmp.RelativeTone + (finetune >> 4) - 7, MOD2XMFineTune(finetune & 0x0F));

		mptSmp.nVolume = volume << 2;

		mptSmp.uFlags.reset();
		if(flags & PSM16SampleHeader::smp16Bit)
		{
			mptSmp.uFlags.set(CHN_16BIT);
			mptSmp.nLength /= 2;
		}
		if(flags & PSM16SampleHeader::smpPingPong)
		{
			mptSmp.uFlags.set(CHN_PINGPONGLOOP);
		}
		if(flags & PSM16SampleHeader::smpLoop)
		{
			mptSmp.uFlags.set(CHN_LOOP);
		}
	}

	// Retrieve the internal sample format flags for this sample.
	SampleIO GetSampleFormat() const
	{
		SampleIO sampleIO(
			(flags & PSM16SampleHeader::smp16Bit) ? SampleIO::_16bit : SampleIO::_8bit,
			SampleIO::mono,
			SampleIO::littleEndian,
			SampleIO::signedPCM);

		if(flags & PSM16SampleHeader::smpUnsigned)
		{
			sampleIO |= SampleIO::unsignedPCM;
		} else if((flags & PSM16SampleHeader::smpDelta) || (flags & PSM16SampleHeader::smpMask) == 0)
		{
			sampleIO |= SampleIO::deltaPCM;
		}

		return sampleIO;
	}
};

STATIC_ASSERT(sizeof(PSM16SampleHeader) == 64);

struct PACKED PSM16PatternHeader
{
	uint16 size;		// includes header bytes
	uint8  numRows;		// 1 ... 64
	uint8  numChans;	// 1 ... 32

	void ConvertEndianness()
	{
		SwapBytesLE(size);
	}
};

STATIC_ASSERT(sizeof(PSM16PatternHeader) == 4);

#ifdef NEEDS_PRAGMA_PACK
#pragma pack(pop)
#endif


bool CSoundFile::ReadPSM16(FileReader &file, ModLoadingFlags loadFlags)
//---------------------------------------------------------------------
{
	file.Rewind();

	// Is it a valid PSM16 file?
	PSM16FileHeader fileHeader;
	if(!file.ReadConvertEndianness(fileHeader)
		|| memcmp(fileHeader.formatID, "PSM\xFE", 4)
		|| fileHeader.lineEnd != 0x1A
		|| (fileHeader.formatVersion != 0x10 && fileHeader.formatVersion != 0x01) // why is this sometimes 0x01?
		|| fileHeader.patternVersion != 0 // 255ch pattern version not supported (did anyone use this?)
		|| (fileHeader.songType & 3) != 0
		|| fileHeader.numChannelsPlay > MAX_BASECHANNELS
		|| fileHeader.numChannelsReal > MAX_BASECHANNELS
		|| std::max(fileHeader.numChannelsPlay, fileHeader.numChannelsReal) == 0)
	{
		return false;
	} else if(loadFlags == onlyVerifyHeader)
	{
		return true;
	}

	// Seems to be valid!
	InitializeGlobals(MOD_TYPE_PSM);
	m_madeWithTracker = "Epic MegaGames MASI (Old Version)";
	m_nChannels = Clamp(CHANNELINDEX(fileHeader.numChannelsPlay), CHANNELINDEX(fileHeader.numChannelsReal), MAX_BASECHANNELS);
	m_nSamplePreAmp = fileHeader.masterVolume;
	if(m_nSamplePreAmp == 255)
	{
		// Most of the time, the master volume value makes sense... Just not when it's 255.
		m_nSamplePreAmp = 48;
	}
	m_nDefaultSpeed = fileHeader.songSpeed;
	m_nDefaultTempo.Set(fileHeader.songTempo);

	mpt::String::Read<mpt::String::spacePadded>(m_songName, fileHeader.songName);

	// Read orders
	if(fileHeader.orderOffset > 4 && file.Seek(fileHeader.orderOffset - 4) && file.ReadUint32LE() == PSM16FileHeader::idPORD)
	{
		Order.ReadAsByte(file, fileHeader.songOrders);
	}

	// Read pan positions
	if(fileHeader.panOffset > 4 && file.Seek(fileHeader.panOffset - 4) && file.ReadUint32LE() == PSM16FileHeader::idPPAN)
	{
		for(CHANNELINDEX i = 0; i < 32; i++)
		{
			ChnSettings[i].Reset();
			ChnSettings[i].nPan = ((15 - (file.ReadUint8() & 0x0F)) * 256 + 8) / 15;	// 15 seems to be left and 0 seems to be right...
			// ChnSettings[i].dwFlags = (i >= fileHeader.numChannelsPlay) ? CHN_MUTE : 0; // don't mute channels, as muted channels are completely ignored in S3M
		}
	}

	// Read samples
	if(fileHeader.smpOffset > 4 && file.Seek(fileHeader.smpOffset - 4) && file.ReadUint32LE() == PSM16FileHeader::idPSAH)
	{
		FileReader sampleChunk = file.ReadChunk(fileHeader.numSamples * sizeof(PSM16SampleHeader));

		for(SAMPLEINDEX fileSample = 0; fileSample < fileHeader.numSamples; fileSample++)
		{
			PSM16SampleHeader sampleHeader;
			if(!sampleChunk.ReadConvertEndianness(sampleHeader))
			{
				break;
			}

			SAMPLEINDEX smp = sampleHeader.sampleNumber;
			if(smp < MAX_SAMPLES)
			{
				m_nSamples = std::max(m_nSamples, smp);

				mpt::String::Read<mpt::String::nullTerminated>(m_szNames[smp], sampleHeader.name);
				sampleHeader.ConvertToMPT(Samples[smp]);

				if((loadFlags & loadSampleData) && file.Seek(sampleHeader.offset))
				{
					sampleHeader.GetSampleFormat().ReadSample(Samples[smp], file);
				}
			}
		}
	}

	// Read patterns
	if(!(loadFlags & loadPatternData))
	{
		return true;
	}
	if(fileHeader.patOffset > 4 && file.Seek(fileHeader.patOffset - 4) && file.ReadUint32LE() == PSM16FileHeader::idPPAT)
	{
		for(PATTERNINDEX pat = 0; pat < fileHeader.numPatterns; pat++)
		{
			PSM16PatternHeader patternHeader;
			if(!file.ReadConvertEndianness(patternHeader))
			{
				break;
			}

			if(patternHeader.size < sizeof(PSM16PatternHeader))
			{
				continue;
			}

			// Patterns are padded to 16 Bytes
			FileReader patternChunk = file.ReadChunk(((patternHeader.size + 15) & ~15) - sizeof(PSM16PatternHeader));

			if(!Patterns.Insert(pat, patternHeader.numRows))
			{
				continue;
			}

			enum
			{
				channelMask	= 0x1F,
				noteFlag	= 0x80,
				volFlag		= 0x40,
				effectFlag	= 0x20,
			};

			ROWINDEX curRow = 0;

			while(patternChunk.CanRead(1) && curRow < patternHeader.numRows)
			{
				uint8 chnFlag = patternChunk.ReadUint8();
				if(chnFlag == 0)
				{
					curRow++;
					continue;
				}

				ModCommand &m = *Patterns[pat].GetpModCommand(curRow, std::min<CHANNELINDEX>(chnFlag & channelMask, m_nChannels - 1));

				if(chnFlag & noteFlag)
				{
					// note + instr present
					m.note = patternChunk.ReadUint8() + 36;
					m.instr = patternChunk.ReadUint8();
				}
				if(chnFlag & volFlag)
				{
					// volume present
					m.volcmd = VOLCMD_VOLUME;
					m.vol = std::min(patternChunk.ReadUint8(), uint8(64));
				}
				if(chnFlag & effectFlag)
				{
					// effect present - convert
					m.command = patternChunk.ReadUint8();
					m.param = patternChunk.ReadUint8();

					switch(m.command)
					{
					// Volslides
					case 0x01: // fine volslide up
						m.command = CMD_VOLUMESLIDE;
						m.param = (m.param << 4) | 0x0F;
						break;
					case 0x02: // volslide up
						m.command = CMD_VOLUMESLIDE;
						m.param = (m.param << 4) & 0xF0;
						break;
					case 0x03: // fine voslide down
						m.command = CMD_VOLUMESLIDE;
						m.param = 0xF0 | m.param;
						break;
					case 0x04: // volslide down
						m.command = CMD_VOLUMESLIDE;
						m.param = m.param & 0x0F;
						break;

					// Portamento
					case 0x0A: // fine portamento up
						m.command = CMD_PORTAMENTOUP;
						m.param |= 0xF0;
						break;
					case 0x0B: // portamento down
						m.command = CMD_PORTAMENTOUP;
						break;
					case 0x0C: // fine portamento down
						m.command = CMD_PORTAMENTODOWN;
						m.param |= 0xF0;
						break;
					case 0x0D: // portamento down
						m.command = CMD_PORTAMENTODOWN;
						break;
					case 0x0E: // tone portamento
						m.command = CMD_TONEPORTAMENTO;
						break;
					case 0x0F: // glissando control
						m.command = CMD_S3MCMDEX;
						m.param |= 0x10;
						break;
					case 0x10: // tone portamento + volslide up
						m.command = CMD_TONEPORTAVOL;
						m.param <<= 4;
						break;
					case 0x11: // tone portamento + volslide down
						m.command = CMD_TONEPORTAVOL;
						m.param &= 0x0F;
						break;

					// Vibrato
					case 0x14: // vibrato
						m.command = CMD_VIBRATO;
						break;
					case 0x15: // vibrato waveform
						m.command = CMD_S3MCMDEX;
						m.param |= 0x30;
						break;
					case 0x16: // vibrato + volslide up
						m.command = CMD_VIBRATOVOL;
						m.param <<= 4;
						break;
					case 0x17: // vibrato + volslide down
						m.command = CMD_VIBRATOVOL;
						m.param &= 0x0F;
						break;

					// Tremolo
					case 0x1E: // tremolo
						m.command = CMD_TREMOLO;
						break;
					case 0x1F: // tremolo waveform
						m.command = CMD_S3MCMDEX;
						m.param |= 0x40;
						break;

					// Sample commands
					case 0x28: // 3-byte offset - we only support the middle byte.
						m.command = CMD_OFFSET;
						m.param = patternChunk.ReadUint8();
						patternChunk.Skip(1);
						break;
					case 0x29: // retrigger
						m.command = CMD_RETRIG;
						m.param &= 0x0F;
						break;
					case 0x2A: // note cut
						m.command = CMD_S3MCMDEX;
#ifdef MODPLUG_TRACKER
						if(m.param == 0)	// in S3M mode, SC0 is ignored, so we convert it to a note cut.
						{
							if(m.note == NOTE_NONE)
							{
								m.note = NOTE_NOTECUT;
								m.command = CMD_NONE;
							} else
							{
								m.param = 1;
							}
						}
#endif // MODPLUG_TRACKER
						m.param |= 0xC0;
						break;
					case 0x2B: // note delay
						m.command = CMD_S3MCMDEX;
						m.param |= 0xD0;
						break;

					// Position change
					case 0x32: // position jump
						m.command = CMD_POSITIONJUMP;
						break;
					case 0x33: // pattern break
						m.command = CMD_PATTERNBREAK;
						break;
					case 0x34: // loop pattern
						m.command = CMD_S3MCMDEX;
						m.param |= 0xB0;
						break;
					case 0x35: // pattern delay
						m.command = CMD_S3MCMDEX;
						m.param |= 0xE0;
						break;

					// speed change
					case 0x3C: // set speed
						m.command = CMD_SPEED;
						break;
					case 0x3D: // set tempo
						m.command = CMD_TEMPO;
						break;

					// misc commands
					case 0x46: // arpeggio
						m.command = CMD_ARPEGGIO;
						break;
					case 0x47: // set finetune
						m.command = CMD_S3MCMDEX;
						m.param = 0x20 | (m.param & 0x0F);
						break;
					case 0x48: // set balance (panning?)
						m.command = CMD_S3MCMDEX;
						m.param = 0x80 | (m.param & 0x0F);
						break;

					default:
						m.command = CMD_NONE;
						break;
					}
				}
			}
			// Pattern break for short patterns (so saving the modules as S3M won't break it)
			if(patternHeader.numRows != 64)
			{
				Patterns[pat].WriteEffect(EffectWriter(CMD_PATTERNBREAK, 0).Row(patternHeader.numRows - 1).Retry(EffectWriter::rmTryNextRow));
			}
		}
	}

	if(fileHeader.commentsOffset != 0)
	{
		file.Seek(fileHeader.commentsOffset);
		m_songMessage.Read(file, file.ReadUint16LE(), SongMessage::leAutodetect);
	}

	return true;
}


OPENMPT_NAMESPACE_END
