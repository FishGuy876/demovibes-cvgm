/*
 * load_j2b.cpp
 * ------------
 * Purpose: RIFF AM and RIFF AMFF (Galaxy Sound System) module loader
 * Notes  : J2B is a compressed variant of RIFF AM and RIFF AMFF files used in Jazz Jackrabbit 2.
 *          It seems like no other game used the AM(FF) format.
 *          RIFF AM is the newer version of the format, generally following the RIFF "standard" closely.
 * Authors: Johannes Schultz (OpenMPT port, reverse engineering + loader implementation of the instrument format)
 *          Chris Moeller (foo_dumb - this is almost a complete port of his code, thanks)
 * The OpenMPT source code is released under the BSD license. Read LICENSE for more details.
 */


#include "stdafx.h"
#include "Loaders.h"
#include "ChunkReader.h"

#if defined(MPT_WITH_ZLIB)
#include <zlib.h>
#elif defined(MPT_WITH_MINIZ)
#include <miniz/miniz.c>
#endif


OPENMPT_NAMESPACE_BEGIN


// First off, a nice vibrato translation LUT.
static const uint8 j2bAutoVibratoTrans[] = 
{
	VIB_SINE, VIB_SQUARE, VIB_RAMP_UP, VIB_RAMP_DOWN, VIB_RANDOM,
};

#ifdef NEEDS_PRAGMA_PACK
#pragma pack(push, 1)
#endif

// header for compressed j2b files
struct PACKED J2BFileHeader
{
	// Magic Bytes
	// 32-Bit J2B header identifiers
	static const uint32 magicDEADBEAF = 0xAFBEADDEu;
	static const uint32 magicDEADBABE = 0xBEBAADDEu;

	char   signature[4];	// MUSE
	uint32 deadbeaf;		// 0xDEADBEAF (AM) or 0xDEADBABE (AMFF)
	uint32 fileLength;		// complete filesize
	uint32 crc32;			// checksum of the compressed data block
	uint32 packedLength;	// length of the compressed data block
	uint32 unpackedLength;	// length of the decompressed module

	// Convert all multi-byte numeric values to current platform's endianness or vice versa.
	void ConvertEndianness()
	{
		SwapBytesLE(deadbeaf);
		SwapBytesLE(fileLength);
		SwapBytesLE(crc32);
		SwapBytesLE(packedLength);
		SwapBytesLE(unpackedLength);
	}
};

STATIC_ASSERT(sizeof(J2BFileHeader) == 24);


// AM(FF) stuff

struct PACKED AMFFRiffChunk
{
	// 32-Bit chunk identifiers
	enum ChunkIdentifiers
	{
		idRIFF	= MAGIC4LE('R','I','F','F'),
		idAMFF	= MAGIC4LE('A','M','F','F'),
		idAM__	= MAGIC4LE('A','M',' ',' '),
		idMAIN	= MAGIC4LE('M','A','I','N'),
		idINIT	= MAGIC4LE('I','N','I','T'),
		idORDR	= MAGIC4LE('O','R','D','R'),
		idPATT	= MAGIC4LE('P','A','T','T'),
		idINST	= MAGIC4LE('I','N','S','T'),
		idSAMP	= MAGIC4LE('S','A','M','P'),
		idAI__	= MAGIC4LE('A','I',' ',' '),
		idAS__	= MAGIC4LE('A','S',' ',' '),
	};

	typedef ChunkIdentifiers id_type;

	uint32 id;		// See ChunkIdentifiers
	uint32 length;	// Chunk size without header

	size_t GetLength() const
	{
		return SwapBytesReturnLE(length);
	}

	id_type GetID() const
	{
		return static_cast<id_type>(SwapBytesReturnLE(id));
	}

	// Convert all multi-byte numeric values to current platform's endianness or vice versa.
	void ConvertEndianness()
	{
		SwapBytesLE(id);
		SwapBytesLE(length);
	}
};

STATIC_ASSERT(sizeof(AMFFRiffChunk) == 8);


// This header is used for both AM's "INIT" as well as AMFF's "MAIN" chunk
struct PACKED AMFFMainChunk
{
	// Main Chunk flags
	enum MainFlags
	{
		amigaSlides = 0x01,
	};

	char   songname[64];
	uint8  flags;
	uint8  channels;
	uint8  speed;
	uint8  tempo;
	uint16 minPeriod;
	uint16 maxPeriod;
	uint8  globalvolume;

	// Convert all multi-byte numeric values to current platform's endianness or vice versa.
	void ConvertEndianness()
	{
		SwapBytesLE(minPeriod);
		SwapBytesLE(maxPeriod);
	}
};

STATIC_ASSERT(sizeof(AMFFMainChunk) == 73);


// AMFF instrument envelope point (old format)
struct PACKED AMFFEnvelopePoint
{
	uint16 tick;
	uint8  value;	// 0...64

	// Convert all multi-byte numeric values to current platform's endianness or vice versa.
	void ConvertEndianness()
	{
		SwapBytesLE(tick);
	}
};

STATIC_ASSERT(sizeof(AMFFEnvelopePoint) == 3);


// AMFF instrument envelope (old format)
struct PACKED AMFFEnvelope
{
	// Envelope flags (also used for RIFF AM)
	enum EnvelopeFlags
	{
		envEnabled	= 0x01,
		envSustain	= 0x02,
		envLoop		= 0x04,
	};

	uint8  envFlags;			// high nibble = pan env flags, low nibble = vol env flags (both nibbles work the same way)
	uint8  envNumPoints;		// high nibble = pan env length, low nibble = vol env length
	uint8  envSustainPoints;	// you guessed it... high nibble = pan env sustain point, low nibble = vol env sustain point
	uint8  envLoopStarts;		// i guess you know the pattern now.
	uint8  envLoopEnds;			// same here.
	AMFFEnvelopePoint volEnv[10];
	AMFFEnvelopePoint panEnv[10];

	// Convert all multi-byte numeric values to current platform's endianness or vice versa.
	void ConvertEndianness()
	{
		for(size_t i = 0; i < CountOf(volEnv); i++)
		{
			volEnv[i].ConvertEndianness();
			panEnv[i].ConvertEndianness();
		}
	}

	// Convert weird envelope data to OpenMPT's internal format.
	void ConvertEnvelope(uint8 flags, uint8 numPoints, uint8 sustainPoint, uint8 loopStart, uint8 loopEnd, const AMFFEnvelopePoint *points, InstrumentEnvelope &mptEnv) const
	{
		// The buggy mod2j2b converter will actually NOT limit this to 10 points if the envelope is longer.
		mptEnv.resize(std::min(numPoints, static_cast<uint8>(10)));

		mptEnv.nSustainStart = mptEnv.nSustainEnd = sustainPoint;

		mptEnv.nLoopStart = loopStart;
		mptEnv.nLoopEnd = loopEnd;

		for(uint32 i = 0; i < mptEnv.size(); i++)
		{
			mptEnv[i].tick = points[i].tick >> 4;
			if(i == 0)
				mptEnv[0].tick = 0;
			else if(mptEnv[i].tick < mptEnv[i - 1].tick)
				mptEnv[i].tick = mptEnv[i - 1].tick + 1;

			mptEnv[i].value = Clamp(points[i].value, uint8(0), uint8(0x40));
		}

		mptEnv.dwFlags.set(ENV_ENABLED, (flags & AMFFEnvelope::envEnabled) != 0);
		mptEnv.dwFlags.set(ENV_SUSTAIN, (flags & AMFFEnvelope::envSustain) && mptEnv.nSustainStart <= mptEnv.size());
		mptEnv.dwFlags.set(ENV_LOOP, (flags & AMFFEnvelope::envLoop) && mptEnv.nLoopStart <= mptEnv.nLoopEnd && mptEnv.nLoopStart <= mptEnv.size());
	}

	void ConvertToMPT(ModInstrument &mptIns) const
	{
		// interleaved envelope data... meh. gotta split it up here and decode it separately.
		// note: mod2j2b is BUGGY and always writes ($original_num_points & 0x0F) in the header,
		// but just has room for 10 envelope points. That means that long (>= 16 points)
		// envelopes are cut off, and envelopes have to be trimmed to 10 points, even if
		// the header claims that they are longer.
		ConvertEnvelope(envFlags & 0x0F, envNumPoints & 0x0F, envSustainPoints & 0x0F, envLoopStarts & 0x0F, envLoopEnds & 0x0F, volEnv, mptIns.VolEnv);
		ConvertEnvelope(envFlags >> 4, envNumPoints >> 4, envSustainPoints >> 4, envLoopStarts >> 4, envLoopEnds >> 4, panEnv, mptIns.PanEnv);
	}
};

STATIC_ASSERT(sizeof(AMFFEnvelope) == 65);


// AMFF instrument header (old format)
struct PACKED AMFFInstrumentHeader
{
	uint8  unknown;				// 0x00
	uint8  index;				// actual instrument number
	char   name[28];
	uint8  numSamples;
	uint8  sampleMap[120];
	uint8  vibratoType;
	uint16 vibratoSweep;
	uint16 vibratoDepth;
	uint16 vibratoRate;
	AMFFEnvelope envelopes;
	uint16 fadeout;

	// Convert all multi-byte numeric values to current platform's endianness or vice versa.
	void ConvertEndianness()
	{
		SwapBytesLE(vibratoSweep);
		SwapBytesLE(vibratoDepth);
		SwapBytesLE(vibratoRate);
		envelopes.ConvertEndianness();
		SwapBytesLE(fadeout);
	}

	// Convert instrument data to OpenMPT's internal format.
	void ConvertToMPT(ModInstrument &mptIns, SAMPLEINDEX baseSample)
	{
		mpt::String::Read<mpt::String::maybeNullTerminated>(mptIns.name, name);

		STATIC_ASSERT(CountOf(sampleMap) <= CountOf(mptIns.Keyboard));
		for(size_t i = 0; i < CountOf(sampleMap); i++)
		{
			mptIns.Keyboard[i] = sampleMap[i] + baseSample + 1;
		}

		mptIns.nFadeOut = fadeout << 5;
		envelopes.ConvertToMPT(mptIns);
	}

};

STATIC_ASSERT(sizeof(AMFFInstrumentHeader) == 225);


// AMFF sample header (old format)
struct PACKED AMFFSampleHeader
{
	// Sample flags (also used for RIFF AM)
	enum SampleFlags
	{
		smp16Bit	= 0x04,
		smpLoop		= 0x08,
		smpPingPong	= 0x10,
		smpPanning	= 0x20,
		smpExists	= 0x80,
		// some flags are still missing... what is e.g. 0x8000?
	};

	uint32 id;	// "SAMP"
	uint32 chunkSize;	// header + sample size
	char   name[28];
	uint8  pan;
	uint8  volume;
	uint16 flags;
	uint32 length;
	uint32 loopStart;
	uint32 loopEnd;
	uint32 sampleRate;
	uint32 reserved1;
	uint32 reserved2;

	// Convert all multi-byte numeric values to current platform's endianness or vice versa.
	void ConvertEndianness()
	{
		SwapBytesLE(id);
		SwapBytesLE(chunkSize);
		SwapBytesLE(flags);
		SwapBytesLE(length);
		SwapBytesLE(loopStart);
		SwapBytesLE(loopEnd);
		SwapBytesLE(sampleRate);
	}

	// Convert sample header to OpenMPT's internal format.
	void ConvertToMPT(AMFFInstrumentHeader &instrHeader, ModSample &mptSmp) const
	{
		mptSmp.Initialize();
		mptSmp.nPan = pan * 4;
		mptSmp.nVolume = volume * 4;
		mptSmp.nGlobalVol = 64;
		mptSmp.nLength = length;
		mptSmp.nLoopStart = loopStart;
		mptSmp.nLoopEnd = loopEnd;
		mptSmp.nC5Speed = sampleRate;

		if(instrHeader.vibratoType < CountOf(j2bAutoVibratoTrans))
			mptSmp.nVibType = j2bAutoVibratoTrans[instrHeader.vibratoType];
		mptSmp.nVibSweep = static_cast<uint8>(instrHeader.vibratoSweep);
		mptSmp.nVibRate = static_cast<uint8>(instrHeader.vibratoRate / 16);
		mptSmp.nVibDepth = static_cast<uint8>(instrHeader.vibratoDepth / 4);
		if((mptSmp.nVibRate | mptSmp.nVibDepth) != 0)
		{
			// Convert XM-style vibrato sweep to IT
			mptSmp.nVibSweep = 255 - mptSmp.nVibSweep;
		}

		if(flags & AMFFSampleHeader::smp16Bit)
			mptSmp.uFlags.set(CHN_16BIT);
		if(flags & AMFFSampleHeader::smpLoop)
			mptSmp.uFlags.set(CHN_LOOP);
		if(flags & AMFFSampleHeader::smpPingPong)
			mptSmp.uFlags.set(CHN_PINGPONGLOOP);
		if(flags & AMFFSampleHeader::smpPanning)
			mptSmp.uFlags.set(CHN_PANNING);
	}

	// Retrieve the internal sample format flags for this sample.
	SampleIO GetSampleFormat() const
	{
		return SampleIO(
			(flags & AMFFSampleHeader::smp16Bit) ? SampleIO::_16bit : SampleIO::_8bit,
			SampleIO::mono,
			SampleIO::littleEndian,
			SampleIO::signedPCM);
	}
};

STATIC_ASSERT(sizeof(AMFFSampleHeader) == 64);


// AM instrument envelope point (new format)
struct PACKED AMEnvelopePoint
{
	uint16 tick;
	uint16 value;

	// Convert all multi-byte numeric values to current platform's endianness or vice versa.
	void ConvertEndianness()
	{
		SwapBytesLE(tick);
		SwapBytesLE(value);
	}
};

STATIC_ASSERT(sizeof(AMEnvelopePoint) == 4);


// AM instrument envelope (new format)
struct PACKED AMEnvelope
{
	uint16 flags;
	uint8  numPoints;	// actually, it's num. points - 1, and 0xFF if there is no envelope
	uint8  sustainPoint;
	uint8  loopStart;
	uint8  loopEnd;
	AMEnvelopePoint values[10];
	uint16 fadeout;		// why is this here? it's only needed for the volume envelope...

	// Convert all multi-byte numeric values to current platform's endianness or vice versa.
	void ConvertEndianness()
	{
		SwapBytesLE(flags);
		for(size_t i = 0; i < CountOf(values); i++)
		{
			values[i].ConvertEndianness();
		}
		SwapBytesLE(fadeout);
	}

	// Convert envelope data to OpenMPT's internal format.
	void ConvertToMPT(InstrumentEnvelope &mptEnv, EnvelopeType envType) const
	{
		if(numPoints == 0xFF || numPoints == 0)
			return;

		mptEnv.resize(std::min(numPoints + 1, 10));

		mptEnv.nSustainStart = mptEnv.nSustainEnd = sustainPoint;

		mptEnv.nLoopStart = loopStart;
		mptEnv.nLoopEnd = loopEnd;

		for(uint32 i = 0; i < mptEnv.size(); i++)
		{
			mptEnv[i].tick = values[i].tick >> 4;
			if(i == 0)
				mptEnv[i].tick = 0;
			else if(mptEnv[i].tick < mptEnv[i - 1].tick)
				mptEnv[i].tick = mptEnv[i - 1].tick + 1;

			const uint16 val = values[i].value;
			switch(envType)
			{
			case ENV_VOLUME:	// 0....32767
				mptEnv[i].value = (uint8)((val + 1) >> 9);
				break;
			case ENV_PITCH:		// -4096....4096
				mptEnv[i].value = (uint8)((((int16)val) + 0x1001) >> 7);
				break;
			case ENV_PANNING:	// -32768...32767
				mptEnv[i].value = (uint8)((((int16)val) + 0x8001) >> 10);
				break;
			}
			Limit(mptEnv[i].value, uint8(ENVELOPE_MIN), uint8(ENVELOPE_MAX));
		}

		mptEnv.dwFlags.set(ENV_ENABLED, (flags & AMFFEnvelope::envEnabled) != 0);
		mptEnv.dwFlags.set(ENV_SUSTAIN, (flags & AMFFEnvelope::envSustain) && mptEnv.nSustainStart <= mptEnv.size());
		mptEnv.dwFlags.set(ENV_LOOP, (flags & AMFFEnvelope::envLoop) && mptEnv.nLoopStart <= mptEnv.nLoopEnd && mptEnv.nLoopStart <= mptEnv.size());
	}
};

STATIC_ASSERT(sizeof(AMEnvelope) == 48);


// AM instrument header (new format)
struct PACKED AMInstrumentHeader
{
	uint32 headSize;	// Header size (i.e. the size of this struct)
	uint8  unknown1;	// 0x00
	uint8  index;		// Actual instrument number
	char   name[32];
	uint8  sampleMap[128];
	uint8  vibratoType;
	uint16 vibratoSweep;
	uint16 vibratoDepth;
	uint16 vibratoRate;
	uint8  unknown2[7];
	AMEnvelope volEnv;
	AMEnvelope pitchEnv;
	AMEnvelope panEnv;
	uint16 numSamples;

	// Convert all multi-byte numeric values to current platform's endianness or vice versa.
	void ConvertEndianness()
	{
		SwapBytesLE(headSize);
		SwapBytesLE(vibratoSweep);
		SwapBytesLE(vibratoDepth);
		SwapBytesLE(vibratoRate);
		volEnv.ConvertEndianness();
		pitchEnv.ConvertEndianness();
		panEnv.ConvertEndianness();
		SwapBytesLE(numSamples);
	}

	// Convert instrument data to OpenMPT's internal format.
	void ConvertToMPT(ModInstrument &mptIns, SAMPLEINDEX baseSample)
	{
		mpt::String::Read<mpt::String::maybeNullTerminated>(mptIns.name, name);

		STATIC_ASSERT(CountOf(sampleMap) <= CountOf(mptIns.Keyboard));
		for(uint8 i = 0; i < CountOf(sampleMap); i++)
		{
			mptIns.Keyboard[i] = sampleMap[i] + baseSample + 1;
		}

		mptIns.nFadeOut = volEnv.fadeout << 5;

		volEnv.ConvertToMPT(mptIns.VolEnv, ENV_VOLUME);
		pitchEnv.ConvertToMPT(mptIns.PitchEnv, ENV_PITCH);
		panEnv.ConvertToMPT(mptIns.PanEnv, ENV_PANNING);

		if(numSamples == 0)
		{
			MemsetZero(mptIns.Keyboard);
		}
	}
};

STATIC_ASSERT(sizeof(AMInstrumentHeader) == 326);


// AM sample header (new format)
struct PACKED AMSampleHeader
{
	uint32 headSize;	// Header size (i.e. the size of this struct), apparently not including headSize.
	char   name[32];
	uint16 pan;
	uint16 volume;
	uint16 flags;
	uint16 unkown;		// 0x0000 / 0x0080?
	uint32 length;
	uint32 loopStart;
	uint32 loopEnd;
	uint32 sampleRate;

	// Convert all multi-byte numeric values to current platform's endianness or vice versa.
	void ConvertEndianness()
	{
		SwapBytesLE(headSize);
		SwapBytesLE(pan);
		SwapBytesLE(volume);
		SwapBytesLE(flags);
		SwapBytesLE(length);
		SwapBytesLE(loopStart);
		SwapBytesLE(loopEnd);
		SwapBytesLE(sampleRate);
	}

	// Convert sample header to OpenMPT's internal format.
	void ConvertToMPT(AMInstrumentHeader &instrHeader, ModSample &mptSmp) const
	{
		mptSmp.Initialize();
		mptSmp.nPan = std::min(pan, static_cast<uint16>(32767)) * 256 / 32767;
		mptSmp.nVolume = std::min(volume, static_cast<uint16>(32767)) * 256 / 32767;
		mptSmp.nGlobalVol = 64;
		mptSmp.nLength = length;
		mptSmp.nLoopStart = loopStart;
		mptSmp.nLoopEnd = loopEnd;
		mptSmp.nC5Speed = sampleRate;

		if(instrHeader.vibratoType < CountOf(j2bAutoVibratoTrans))
			mptSmp.nVibType = j2bAutoVibratoTrans[instrHeader.vibratoType];
		mptSmp.nVibSweep = static_cast<uint8>(instrHeader.vibratoSweep);
		mptSmp.nVibRate = static_cast<uint8>(instrHeader.vibratoRate / 16);
		mptSmp.nVibDepth = static_cast<uint8>(instrHeader.vibratoDepth / 4);
		if((mptSmp.nVibRate | mptSmp.nVibDepth) != 0)
		{
			// Convert XM-style vibrato sweep to IT
			mptSmp.nVibSweep = 255 - mptSmp.nVibSweep;
		}

		if(flags & AMFFSampleHeader::smp16Bit)
			mptSmp.uFlags |= CHN_16BIT;
		if(flags & AMFFSampleHeader::smpLoop)
			mptSmp.uFlags |= CHN_LOOP;
		if(flags & AMFFSampleHeader::smpPingPong)
			mptSmp.uFlags |= CHN_PINGPONGLOOP;
		if(flags & AMFFSampleHeader::smpPanning)
			mptSmp.uFlags |= CHN_PANNING;
	}

	// Retrieve the internal sample format flags for this sample.
	SampleIO GetSampleFormat() const
	{
		return SampleIO(
			(flags & AMFFSampleHeader::smp16Bit) ? SampleIO::_16bit : SampleIO::_8bit,
			SampleIO::mono,
			SampleIO::littleEndian,
			SampleIO::signedPCM);
	}
};

STATIC_ASSERT(sizeof(AMSampleHeader) == 60);


#ifdef NEEDS_PRAGMA_PACK
#pragma pack(pop)
#endif


// Convert RIFF AM(FF) pattern data to MPT pattern data.
static bool ConvertAMPattern(FileReader chunk, PATTERNINDEX pat, bool isAM, CSoundFile &sndFile)
//----------------------------------------------------------------------------------------------
{
	// Effect translation LUT
	static const ModCommand::COMMAND amEffTrans[] =
	{
		CMD_ARPEGGIO, CMD_PORTAMENTOUP, CMD_PORTAMENTODOWN, CMD_TONEPORTAMENTO,
		CMD_VIBRATO, CMD_TONEPORTAVOL, CMD_VIBRATOVOL, CMD_TREMOLO,
		CMD_PANNING8, CMD_OFFSET, CMD_VOLUMESLIDE, CMD_POSITIONJUMP,
		CMD_VOLUME, CMD_PATTERNBREAK, CMD_MODCMDEX, CMD_TEMPO,
		CMD_GLOBALVOLUME, CMD_GLOBALVOLSLIDE, CMD_KEYOFF, CMD_SETENVPOSITION,
		CMD_CHANNELVOLUME, CMD_CHANNELVOLSLIDE, CMD_PANNINGSLIDE, CMD_RETRIG,
		CMD_TREMOR, CMD_XFINEPORTAUPDOWN,
	};

	enum
	{
		rowDone		= 0,		// Advance to next row
		channelMask	= 0x1F,		// Mask for retrieving channel information
		volFlag		= 0x20,		// Volume effect present
		noteFlag	= 0x40,		// Note + instr present
		effectFlag	= 0x80,		// Effect information present
		dataFlag	= 0xE0,		// Channel data present
	};

	if(chunk.NoBytesLeft())
	{
		return false;
	}

	ROWINDEX numRows = Clamp(static_cast<ROWINDEX>(chunk.ReadUint8()) + 1, ROWINDEX(1), MAX_PATTERN_ROWS);

	if(!sndFile.Patterns.Insert(pat, numRows))
		return false;

	const CHANNELINDEX channels = sndFile.GetNumChannels();
	if(channels == 0)
		return false;

	PatternRow rowBase = sndFile.Patterns[pat].GetRow(0);
	ROWINDEX row = 0;

	while(row < numRows && chunk.CanRead(1))
	{
		const uint8 flags = chunk.ReadUint8();

		if(flags == rowDone)
		{
			row++;
			rowBase = sndFile.Patterns[pat].GetRow(row);
			continue;
		}

		ModCommand &m = rowBase[std::min<CHANNELINDEX>((flags & channelMask), channels - 1)];

		if(flags & dataFlag)
		{
			if(flags & effectFlag) // effect
			{
				m.param = chunk.ReadUint8();
				m.command = chunk.ReadUint8();

				if(m.command < CountOf(amEffTrans))
				{
					// command translation
					m.command = amEffTrans[m.command];
				} else
				{
#ifdef DEBUG
					Log(mpt::String::Print("J2B: Unknown command: 0x%1, param 0x%2", mpt::fmt::HEX0<2>(m.command), mpt::fmt::HEX0<2>(m.param)));
#endif // DEBUG
					m.command = CMD_NONE;
				}

				// Handling special commands
				switch(m.command)
				{
				case CMD_ARPEGGIO:
					if(m.param == 0) m.command = CMD_NONE;
					break;
				case CMD_VOLUME:
					if(m.volcmd == VOLCMD_NONE)
					{
						m.volcmd = VOLCMD_VOLUME;
						m.vol = Clamp(m.param, uint8(0), uint8(64));
						m.command = CMD_NONE;
						m.param = 0;
					}
					break;
				case CMD_TONEPORTAVOL:
				case CMD_VIBRATOVOL:
				case CMD_VOLUMESLIDE:
				case CMD_GLOBALVOLSLIDE:
				case CMD_PANNINGSLIDE:
					if (m.param & 0xF0) m.param &= 0xF0;
					break;
				case CMD_PANNING8:
					if(m.param <= 0x80) m.param = MIN(m.param << 1, 0xFF);
					else if(m.param == 0xA4) {m.command = CMD_S3MCMDEX; m.param = 0x91;}
					break;
				case CMD_PATTERNBREAK:
					m.param = ((m.param >> 4) * 10) + (m.param & 0x0F);
					break;
				case CMD_MODCMDEX:
					m.ExtendedMODtoS3MEffect();
					break;
				case CMD_TEMPO:
					if(m.param <= 0x1F) m.command = CMD_SPEED;
					break;
				case CMD_XFINEPORTAUPDOWN:
					switch(m.param & 0xF0)
					{
					case 0x10:
						m.command = CMD_PORTAMENTOUP;
						break;
					case 0x20:
						m.command = CMD_PORTAMENTODOWN;
						break;
					}
					m.param = (m.param & 0x0F) | 0xE0;
					break;
				}
			}

			if (flags & noteFlag) // note + ins
			{
				m.instr = chunk.ReadUint8();
				m.note = chunk.ReadUint8();
				if(m.note == 0x80) m.note = NOTE_KEYOFF;
				else if(m.note > 0x80) m.note = NOTE_FADE;	// I guess the support for IT "note fade" notes was not intended in mod2j2b, but hey, it works! :-D
			}

			if (flags & volFlag) // volume
			{
				m.volcmd = VOLCMD_VOLUME;
				m.vol = chunk.ReadUint8();
				if(isAM)
				{
					m.vol = m.vol * 64 / 127;
				}
			}
		}
	}

	return true;
}


bool CSoundFile::ReadAM(FileReader &file, ModLoadingFlags loadFlags)
//------------------------------------------------------------------
{
	file.Rewind();
	AMFFRiffChunk fileHeader;
	if(!file.ReadConvertEndianness(fileHeader))
	{
		return false;
	}

	if(fileHeader.id != AMFFRiffChunk::idRIFF)
	{
		return false;
	}

	bool isAM; // false: AMFF, true: AM

	uint32 format = file.ReadUint32LE();
	if(format == AMFFRiffChunk::idAMFF)
		isAM = false; // "AMFF"
	else if(format == AMFFRiffChunk::idAM__)
		isAM = true; // "AM  "
	else
		return false;

	ChunkReader chunkFile(file);

	// The main chunk is almost identical in both formats but uses different chunk IDs.
	// "MAIN" - Song info (AMFF)
	// "INIT" - Song info (AM)
	AMFFRiffChunk::ChunkIdentifiers mainChunkID = isAM ? AMFFRiffChunk::idINIT : AMFFRiffChunk::idMAIN;

	// RIFF AM has a padding byte so that all chunks have an even size.
	ChunkReader::ChunkList<AMFFRiffChunk> chunks;
	if(loadFlags == onlyVerifyHeader)
		chunks = chunkFile.ReadChunksUntil<AMFFRiffChunk>(isAM ? 2 : 1, mainChunkID);
	else
		chunks = chunkFile.ReadChunks<AMFFRiffChunk>(isAM ? 2 : 1);

	FileReader chunk(chunks.GetChunk(mainChunkID));
	AMFFMainChunk mainChunk;
	if(!chunk.IsValid() 
		|| !chunk.ReadConvertEndianness(mainChunk)
		|| mainChunk.channels < 1
		|| !chunk.CanRead(mainChunk.channels))
	{
		return false;
	} else if(loadFlags == onlyVerifyHeader)
	{
		return true;
	}

	InitializeGlobals(MOD_TYPE_J2B);
	m_SongFlags = SONG_ITOLDEFFECTS | SONG_ITCOMPATGXX;
	m_SongFlags.set(SONG_LINEARSLIDES, !(mainChunk.flags & AMFFMainChunk::amigaSlides));

	m_nChannels = MIN(mainChunk.channels, MAX_BASECHANNELS);
	m_nDefaultSpeed = mainChunk.speed;
	m_nDefaultTempo.Set(mainChunk.tempo);
	m_nDefaultGlobalVolume = mainChunk.globalvolume * 2;

	m_madeWithTracker = "Galaxy Sound System (";
	if(isAM)
		m_madeWithTracker += "new version)";
	else
		m_madeWithTracker += "old version)";

	if(mainChunk.minPeriod < mainChunk.maxPeriod)
	{
		m_nMinPeriod = mainChunk.minPeriod / 4u;
		m_nMaxPeriod = mainChunk.maxPeriod / 4u;
	}

	mpt::String::Read<mpt::String::maybeNullTerminated>(m_songName, mainChunk.songname);

	// It seems like there's no way to differentiate between
	// Muted and Surround channels (they're all 0xA0) - might
	// be a limitation in mod2j2b.
	for(CHANNELINDEX nChn = 0; nChn < m_nChannels; nChn++)
	{
		ChnSettings[nChn].Reset();

		uint8 pan = chunk.ReadUint8();
		if(isAM)
		{
			if(pan > 128)
				ChnSettings[nChn].dwFlags = CHN_MUTE;
			else
				ChnSettings[nChn].nPan = pan * 2;
		} else
		{
			if(pan >= 128)
				ChnSettings[nChn].dwFlags = CHN_MUTE;
			else
				ChnSettings[nChn].nPan = static_cast<uint16>(std::min(pan * 4, 256));
		}
	}

	if(chunks.ChunkExists(AMFFRiffChunk::idORDR))
	{
		// "ORDR" - Order list
		FileReader chunk(chunks.GetChunk(AMFFRiffChunk::idORDR));
		uint8 numOrders = chunk.ReadUint8() + 1;
		Order.ReadAsByte(chunk, numOrders, numOrders, 0xFF, 0xFE);
	}

	// "PATT" - Pattern data for one pattern
	if(loadFlags & loadPatternData)
	{
		PATTERNINDEX maxPattern = 0;
		std::vector<FileReader> pattChunks = chunks.GetAllChunks(AMFFRiffChunk::idPATT);
		for(std::vector<FileReader>::iterator patternIter = pattChunks.begin(); patternIter != pattChunks.end(); patternIter++)
		{
			FileReader chunk(*patternIter);
			PATTERNINDEX pat = chunk.ReadUint8();
			size_t patternSize = chunk.ReadUint32LE();
			ConvertAMPattern(chunk.ReadChunk(patternSize), pat, isAM, *this);
			maxPattern = std::max(maxPattern, pat);
		}
		for(PATTERNINDEX pat = 0; pat < maxPattern; pat++)
		{
			if(!Patterns.IsValidPat(pat))
				Patterns.Insert(pat, 64);
		}
	}

	if(!isAM)
	{
		// "INST" - Instrument (only in RIFF AMFF)
		std::vector<FileReader> instChunks = chunks.GetAllChunks(AMFFRiffChunk::idINST);
		for(std::vector<FileReader>::iterator instIter = instChunks.begin(); instIter != instChunks.end(); instIter++)
		{
			FileReader chunk(*instIter);
			AMFFInstrumentHeader instrHeader;
			if(!chunk.ReadConvertEndianness(instrHeader))
			{
				continue;
			}

			const INSTRUMENTINDEX instr = instrHeader.index + 1;
			if(instr >= MAX_INSTRUMENTS)
				continue;

			ModInstrument *pIns = AllocateInstrument(instr);
			if(pIns == nullptr)
			{
				continue;
			}

			m_nInstruments = std::max(m_nInstruments, instr);

			instrHeader.ConvertToMPT(*pIns, m_nSamples);

			// read sample sub-chunks - this is a rather "flat" format compared to RIFF AM and has no nested RIFF chunks.
			for(size_t samples = 0; samples < instrHeader.numSamples; samples++)
			{
				AMFFSampleHeader sampleHeader;

				if(m_nSamples + 1 >= MAX_SAMPLES || !chunk.ReadConvertEndianness(sampleHeader))
				{
					continue;
				}

				const SAMPLEINDEX smp = ++m_nSamples;

				if(sampleHeader.id != AMFFRiffChunk::idSAMP)
				{
					continue;
				}

				mpt::String::Read<mpt::String::maybeNullTerminated>(m_szNames[smp], sampleHeader.name);
				sampleHeader.ConvertToMPT(instrHeader, Samples[smp]);
				if(loadFlags & loadSampleData)
					sampleHeader.GetSampleFormat().ReadSample(Samples[smp], chunk);
				else
					chunk.Skip(Samples[smp].GetSampleSizeInBytes());
			}
		}
	} else
	{
		// "RIFF" - Instrument (only in RIFF AM)
		std::vector<FileReader> instChunks = chunks.GetAllChunks(AMFFRiffChunk::idRIFF);
		for(std::vector<FileReader>::iterator instIter = instChunks.begin(); instIter != instChunks.end(); instIter++)
		{
			ChunkReader chunk(*instIter);
			if(chunk.ReadUint32LE() != AMFFRiffChunk::idAI__)
			{
				continue;
			}

			AMFFRiffChunk instChunk;
			if(!chunk.ReadConvertEndianness(instChunk) || instChunk.id != AMFFRiffChunk::idINST)
			{
				continue;
			}

			AMInstrumentHeader instrHeader;
			if(!chunk.ReadConvertEndianness(instrHeader))
			{
				continue;
			}
			MPT_ASSERT(instrHeader.headSize + 4 == sizeof(instrHeader));

			const INSTRUMENTINDEX instr = instrHeader.index + 1;
			if(instr >= MAX_INSTRUMENTS)
				continue;

			ModInstrument *pIns = AllocateInstrument(instr);
			if(pIns == nullptr)
			{
				continue;
			}
			m_nInstruments = std::max(m_nInstruments, instr);

			instrHeader.ConvertToMPT(*pIns, m_nSamples);

			// Read sample sub-chunks (RIFF nesting ftw)
			ChunkReader::ChunkList<AMFFRiffChunk> sampleChunkFile = chunk.ReadChunks<AMFFRiffChunk>(2);
			std::vector<FileReader> sampleChunks = sampleChunkFile.GetAllChunks(AMFFRiffChunk::idRIFF);
			MPT_ASSERT(sampleChunks.size() == instrHeader.numSamples);

			for(std::vector<FileReader>::iterator smpIter = sampleChunks.begin(); smpIter != sampleChunks.end(); smpIter++)
			{
				ChunkReader sampleChunk(*smpIter);

				if(sampleChunk.ReadUint32LE() != AMFFRiffChunk::idAS__ || m_nSamples + 1 >= MAX_SAMPLES)
				{
					continue;
				}

				// Don't read more samples than the instrument header claims to have.
				if((instrHeader.numSamples--) == 0)
				{
					break;
				}

				const SAMPLEINDEX smp = ++m_nSamples;

				// Aaand even more nested chunks! Great, innit?
				AMFFRiffChunk sampleHeaderChunk;
				if(!sampleChunk.ReadConvertEndianness(sampleHeaderChunk) || sampleHeaderChunk.id != AMFFRiffChunk::idSAMP)
				{
					break;
				}

				FileReader sampleFileChunk = sampleChunk.ReadChunk(sampleHeaderChunk.length);

				AMSampleHeader sampleHeader;
				if(!sampleFileChunk.ReadConvertEndianness(sampleHeader))
				{
					break;
				}

				mpt::String::Read<mpt::String::maybeNullTerminated>(m_szNames[smp], sampleHeader.name);

				sampleHeader.ConvertToMPT(instrHeader, Samples[smp]);

				if(loadFlags & loadSampleData)
				{
					sampleFileChunk.Seek(sampleHeader.headSize + 4);
					sampleHeader.GetSampleFormat().ReadSample(Samples[smp], sampleFileChunk);
				}
			}
		
		}
	}

	return true;
}

bool CSoundFile::ReadJ2B(FileReader &file, ModLoadingFlags loadFlags)
//-------------------------------------------------------------------
{

#if !defined(MPT_WITH_ZLIB) && !defined(MPT_WITH_MINIZ)

	MPT_UNREFERENCED_PARAMETER(file);
	MPT_UNREFERENCED_PARAMETER(loadFlags);
	return false;

#else

	file.Rewind();
	J2BFileHeader fileHeader;
	if(!file.ReadConvertEndianness(fileHeader))
	{
		return false;
	}

	if(memcmp(fileHeader.signature, "MUSE", 4)
		|| (fileHeader.deadbeaf != J2BFileHeader::magicDEADBEAF // 0xDEADBEAF (RIFF AM)
			&& fileHeader.deadbeaf != J2BFileHeader::magicDEADBABE) // 0xDEADBABE (RIFF AMFF)
		|| fileHeader.fileLength != file.GetLength()
		|| fileHeader.packedLength != file.BytesLeft()
		|| fileHeader.packedLength == 0
		)
	{
		return false;
	} else if(loadFlags == onlyVerifyHeader)
	{
		return true;
	}

	FileReader::PinnedRawDataView filePackedView = file.GetPinnedRawDataView(fileHeader.packedLength);

#ifndef MPT_BUILD_FUZZER
	if(fileHeader.crc32 != crc32(0, mpt::byte_cast<const Bytef*>(filePackedView.data()), filePackedView.size()))
	{
		return false;
	}
#endif

	// Header is valid, now unpack the RIFF AM file using inflate
	uLongf destSize = fileHeader.unpackedLength;
	std::vector<Bytef> amFileData(destSize);
	int retVal = uncompress(&amFileData[0], &destSize, mpt::byte_cast<const Bytef*>(filePackedView.data()), filePackedView.size());

	bool result = false;

#ifndef MPT_BUILD_FUZZER
	if(destSize == fileHeader.unpackedLength && retVal == Z_OK)
#endif
	{
		// Success, now load the RIFF AM(FF) module.
		FileReader amFile(mpt::as_span(amFileData));
		result = ReadAM(amFile, loadFlags);
	}

	return result;

#endif

}


OPENMPT_NAMESPACE_END
