/*
 * DLSBank.cpp
 * -----------
 * Purpose: Sound bank loading.
 * Notes  : Supported sound bank types: DLS (including embedded DLS in MSS & RMI), SF2
 * Authors: Olivier Lapicque
 *          OpenMPT Devs
 * The OpenMPT source code is released under the BSD license. Read LICENSE for more details.
 */


#include "stdafx.h"
#include "Sndfile.h"
#ifdef MODPLUG_TRACKER
#include "../mptrack/mptrack.h"
#include "../common/mptFileIO.h"
#endif
#include "Dlsbank.h"
#include "../common/StringFixer.h"
#include "../common/FileReader.h"
#include "../common/Endianness.h"
#include "SampleIO.h"
#include "modsmp_ctrl.h"

#include <math.h>

OPENMPT_NAMESPACE_BEGIN

#ifdef MODPLUG_TRACKER

//#define DLSBANK_LOG
//#define DLSINSTR_LOG

#define F_RGN_OPTION_SELFNONEXCLUSIVE	0x0001

///////////////////////////////////////////////////////////////////////////
// Articulation connection graph definitions

// Generic Sources
#define CONN_SRC_NONE              0x0000
#define CONN_SRC_LFO               0x0001
#define CONN_SRC_KEYONVELOCITY     0x0002
#define CONN_SRC_KEYNUMBER         0x0003
#define CONN_SRC_EG1               0x0004
#define CONN_SRC_EG2               0x0005
#define CONN_SRC_PITCHWHEEL        0x0006

// Midi Controllers 0-127
#define CONN_SRC_CC1               0x0081
#define CONN_SRC_CC7               0x0087
#define CONN_SRC_CC10              0x008a
#define CONN_SRC_CC11              0x008b

// Generic Destinations
#define CONN_DST_NONE              0x0000
#define CONN_DST_ATTENUATION       0x0001
#define CONN_DST_RESERVED          0x0002
#define CONN_DST_PITCH             0x0003
#define CONN_DST_PAN               0x0004

// LFO Destinations
#define CONN_DST_LFO_FREQUENCY     0x0104
#define CONN_DST_LFO_STARTDELAY    0x0105

// EG1 Destinations
#define CONN_DST_EG1_ATTACKTIME    0x0206
#define CONN_DST_EG1_DECAYTIME     0x0207
#define CONN_DST_EG1_RESERVED      0x0208
#define CONN_DST_EG1_RELEASETIME   0x0209
#define CONN_DST_EG1_SUSTAINLEVEL  0x020a

// EG2 Destinations
#define CONN_DST_EG2_ATTACKTIME    0x030a
#define CONN_DST_EG2_DECAYTIME     0x030b
#define CONN_DST_EG2_RESERVED      0x030c
#define CONN_DST_EG2_RELEASETIME   0x030d
#define CONN_DST_EG2_SUSTAINLEVEL  0x030e

#define CONN_TRN_NONE              0x0000
#define CONN_TRN_CONCAVE           0x0001


//////////////////////////////////////////////////////////
// Supported DLS1 Articulations

#define MAKE_ART(src, ctl, dst)	( ((dst)<<16) | ((ctl)<<8) | (src) )

// Vibrato / Tremolo
#define ART_LFO_FREQUENCY	MAKE_ART	(CONN_SRC_NONE,	CONN_SRC_NONE,	CONN_DST_LFO_FREQUENCY)
#define ART_LFO_STARTDELAY	MAKE_ART	(CONN_SRC_NONE,	CONN_SRC_NONE,	CONN_DST_LFO_STARTDELAY)
#define ART_LFO_ATTENUATION	MAKE_ART	(CONN_SRC_LFO,	CONN_SRC_NONE,	CONN_DST_ATTENUATION)
#define ART_LFO_PITCH		MAKE_ART	(CONN_SRC_LFO,	CONN_SRC_NONE,	CONN_DST_PITCH)
#define ART_LFO_MODWTOATTN	MAKE_ART	(CONN_SRC_LFO,	CONN_SRC_CC1,	CONN_DST_ATTENUATION)
#define ART_LFO_MODWTOPITCH	MAKE_ART	(CONN_SRC_LFO,	CONN_SRC_CC1,	CONN_DST_PITCH)

// Volume Envelope
#define ART_VOL_EG_ATTACKTIME	MAKE_ART(CONN_SRC_NONE,	CONN_SRC_NONE,	CONN_DST_EG1_ATTACKTIME)
#define ART_VOL_EG_DECAYTIME	MAKE_ART(CONN_SRC_NONE,	CONN_SRC_NONE,	CONN_DST_EG1_DECAYTIME)
#define ART_VOL_EG_SUSTAINLEVEL	MAKE_ART(CONN_SRC_NONE,	CONN_SRC_NONE,	CONN_DST_EG1_SUSTAINLEVEL)
#define ART_VOL_EG_RELEASETIME	MAKE_ART(CONN_SRC_NONE,	CONN_SRC_NONE,	CONN_DST_EG1_RELEASETIME)
#define ART_VOL_EG_VELTOATTACK	MAKE_ART(CONN_SRC_KEYONVELOCITY,	CONN_SRC_NONE,	CONN_DST_EG1_ATTACKTIME)
#define ART_VOL_EG_KEYTODECAY	MAKE_ART(CONN_SRC_KEYNUMBER,		CONN_SRC_NONE,	CONN_DST_EG1_DECAYTIME)

// Pitch Envelope
#define ART_PITCH_EG_ATTACKTIME		MAKE_ART(CONN_SRC_NONE,	CONN_SRC_NONE,	CONN_DST_EG2_ATTACKTIME)
#define ART_PITCH_EG_DECAYTIME		MAKE_ART(CONN_SRC_NONE,	CONN_SRC_NONE,	CONN_DST_EG2_DECAYTIME)
#define ART_PITCH_EG_SUSTAINLEVEL	MAKE_ART(CONN_SRC_NONE,	CONN_SRC_NONE,	CONN_DST_EG2_SUSTAINLEVEL)
#define ART_PITCH_EG_RELEASETIME	MAKE_ART(CONN_SRC_NONE,	CONN_SRC_NONE,	CONN_DST_EG2_RELEASETIME)
#define ART_PITCH_EG_VELTOATTACK	MAKE_ART(CONN_SRC_KEYONVELOCITY,	CONN_SRC_NONE,	CONN_DST_EG2_ATTACKTIME)
#define ART_PITCH_EG_KEYTODECAY		MAKE_ART(CONN_SRC_KEYNUMBER,		CONN_SRC_NONE,	CONN_DST_EG2_DECAYTIME)

// Default Pan
#define ART_DEFAULTPAN		MAKE_ART	(CONN_SRC_NONE,	CONN_SRC_NONE,	CONN_DST_PAN)


#ifdef NEEDS_PRAGMA_PACK
#pragma pack(push, 1)
#endif

//////////////////////////////////////////////////////////
// DLS IFF Chunk IDs

// Standard IFF chunks IDs
#define IFFID_FORM		0x4d524f46
#define IFFID_RIFF		0x46464952
#define IFFID_LIST		0x5453494C
#define IFFID_INFO		0x4F464E49

// IFF Info fields
#define IFFID_ICOP		0x504F4349
#define IFFID_INAM		0x4D414E49
#define IFFID_ICMT		0x544D4349
#define IFFID_IENG		0x474E4549
#define IFFID_ISFT		0x54465349
#define IFFID_ISBJ		0x4A425349

// Wave IFF chunks IDs
#define IFFID_wave		0x65766177
#define IFFID_wsmp		0x706D7377

#define IFFID_XDLS		0x534c4458
#define IFFID_DLS		0x20534C44
#define IFFID_MLS		0x20534C4D
#define IFFID_RMID		0x44494D52
#define IFFID_colh		0x686C6F63
#define IFFID_ins		0x20736E69
#define IFFID_insh		0x68736E69
#define IFFID_ptbl		0x6C627470
#define IFFID_wvpl		0x6C707677
#define IFFID_rgn		0x206E6772
#define IFFID_rgn2		0x326E6772
#define IFFID_rgnh		0x686E6772
#define IFFID_wlnk		0x6B6E6C77
#define IFFID_art1		0x31747261
#define IFFID_art2		0x32747261

//////////////////////////////////////////////////////////
// DLS Structures definitions

typedef struct PACKED IFFCHUNK
{
	uint32 id;
	uint32 len;
} IFFCHUNK, *LPIFFCHUNK;

STATIC_ASSERT(sizeof(IFFCHUNK) == 8);

typedef struct PACKED RIFFCHUNKID
{
	uint32 id_RIFF;
	uint32 riff_len;
	uint32 id_DLS;
} RIFFCHUNKID;

STATIC_ASSERT(sizeof(RIFFCHUNKID) == 12);

typedef struct PACKED LISTCHUNK
{
	uint32 id;
	uint32 len;
	uint32 listid;
} LISTCHUNK;

STATIC_ASSERT(sizeof(LISTCHUNK) == 12);

typedef struct PACKED DLSRGNRANGE
{
	uint16 usLow;
	uint16 usHigh;
} DLSRGNRANGE;

STATIC_ASSERT(sizeof(DLSRGNRANGE) == 4);

typedef struct PACKED COLHCHUNK
{
	uint32 id;
	uint32 len;
	uint32 ulInstruments;
} COLHCHUNK;

STATIC_ASSERT(sizeof(COLHCHUNK) == 12);

typedef struct PACKED VERSCHUNK
{
	uint32 id;
	uint32 len;
	uint16 version[4];
} VERSCHUNK;

STATIC_ASSERT(sizeof(VERSCHUNK) == 16);

typedef struct PACKED PTBLCHUNK
{
	uint32 id;
	uint32 len;
	uint32 cbSize;
	uint32 cCues;
	uint32 ulOffsets[1];
} PTBLCHUNK;

STATIC_ASSERT(sizeof(PTBLCHUNK) == 20);

typedef struct PACKED INSHCHUNK
{
	uint32 id;
	uint32 len;
	uint32 cRegions;
	uint32 ulBank;
	uint32 ulInstrument;
} INSHCHUNK;

STATIC_ASSERT(sizeof(INSHCHUNK) == 20);

typedef struct PACKED RGNHCHUNK
{
	uint32 id;
	uint32 len;
	DLSRGNRANGE RangeKey;
	DLSRGNRANGE RangeVelocity;
	uint16 fusOptions;
	uint16 usKeyGroup;
} RGNHCHUNK;

STATIC_ASSERT(sizeof(RGNHCHUNK) == 20);

typedef struct PACKED WLNKCHUNK
{
	uint32 id;
	uint32 len;
	uint16 fusOptions;
	uint16 usPhaseGroup;
	uint32 ulChannel;
	uint32 ulTableIndex;
} WLNKCHUNK;

STATIC_ASSERT(sizeof(WLNKCHUNK) == 20);

typedef struct PACKED ART1CHUNK
{
	uint32 id;
	uint32 len;
	uint32 cbSize;
	uint32 cConnectionBlocks;
} ART1CHUNK;

STATIC_ASSERT(sizeof(ART1CHUNK) == 16);

typedef struct PACKED CONNECTIONBLOCK
{
	uint16 usSource;
	uint16 usControl;
	uint16 usDestination;
	uint16 usTransform;
	LONG lScale;
} CONNECTIONBLOCK;

STATIC_ASSERT(sizeof(CONNECTIONBLOCK) == 12);

typedef struct PACKED WSMPCHUNK
{
	uint32 id;
	uint32 len;
	uint32 cbSize;
	uint16 usUnityNote;
	int16 sFineTune;
	LONG lAttenuation;
	uint32 fulOptions;
	uint32 cSampleLoops;
} WSMPCHUNK;

STATIC_ASSERT(sizeof(WSMPCHUNK) == 28);

typedef struct PACKED WSMPSAMPLELOOP
{
	uint32 cbSize;
	uint32 ulLoopType;
	uint32 ulLoopStart;
	uint32 ulLoopLength;
	void ConvertEndianness()
	{
		SwapBytesLE(cbSize);
		SwapBytesLE(ulLoopType);
		SwapBytesLE(ulLoopStart);
		SwapBytesLE(ulLoopLength);
	}
} WSMPSAMPLELOOP;

STATIC_ASSERT(sizeof(WSMPSAMPLELOOP) == 16);


/////////////////////////////////////////////////////////////////////
// SF2 IFF Chunk IDs

#define IFFID_sfbk		0x6b626673
#define IFFID_sdta		0x61746473
#define IFFID_pdta		0x61746470
#define IFFID_phdr		0x72646870
#define IFFID_pbag		0x67616270
#define IFFID_pgen		0x6E656770
#define IFFID_inst		0x74736E69
#define IFFID_ibag		0x67616269
#define IFFID_igen		0x6E656769
#define IFFID_shdr		0x72646873

///////////////////////////////////////////
// SF2 Generators IDs

#define SF2_GEN_MODENVTOFILTERFC		11
#define SF2_GEN_PAN						17
#define SF2_GEN_DECAYMODENV				28
#define SF2_GEN_DECAYVOLENV				36
#define SF2_GEN_RELEASEVOLENV			38
#define SF2_GEN_INSTRUMENT				41
#define SF2_GEN_KEYRANGE				43
#define SF2_GEN_ATTENUATION				48
#define SF2_GEN_COARSETUNE				51
#define SF2_GEN_FINETUNE				52
#define SF2_GEN_SAMPLEID				53
#define SF2_GEN_SAMPLEMODES				54
#define SF2_GEN_KEYGROUP				57
#define SF2_GEN_UNITYNOTE				58

/////////////////////////////////////////////////////////////////////
// SF2 Structures Definitions

typedef struct PACKED SFPRESETHEADER
{
	char achPresetName[20];
	uint16 wPreset;
	uint16 wBank;
	uint16 wPresetBagNdx;
	uint32 dwLibrary;
	uint32 dwGenre;
	uint32 dwMorphology;
} SFPRESETHEADER;

STATIC_ASSERT(sizeof(SFPRESETHEADER) == 38);

typedef struct PACKED SFPRESETBAG
{
	uint16 wGenNdx;
	uint16 wModNdx;
} SFPRESETBAG;

STATIC_ASSERT(sizeof(SFPRESETBAG) == 4);

typedef struct PACKED SFGENLIST
{
	uint16 sfGenOper;
	uint16 genAmount;
} SFGENLIST;

STATIC_ASSERT(sizeof(SFGENLIST) == 4);

typedef struct PACKED SFINST
{
	char achInstName[20];
	uint16 wInstBagNdx;
} SFINST;

STATIC_ASSERT(sizeof(SFINST) == 22);

typedef struct PACKED SFINSTBAG
{
	uint16 wGenNdx;
	uint16 wModNdx;
} SFINSTBAG;

STATIC_ASSERT(sizeof(SFINSTBAG) == 4);

typedef struct PACKED SFINSTGENLIST
{
	uint16 sfGenOper;
	uint16 genAmount;
} SFINSTGENLIST;

STATIC_ASSERT(sizeof(SFINSTGENLIST) == 4);

typedef struct PACKED SFSAMPLE
{
	char achSampleName[20];
	uint32 dwStart;
	uint32 dwEnd;
	uint32 dwStartloop;
	uint32 dwEndloop;
	uint32 dwSampleRate;
	uint8 byOriginalPitch;
	char chPitchCorrection;
	uint16 wSampleLink;
	uint16 sfSampleType;
} SFSAMPLE;

STATIC_ASSERT(sizeof(SFSAMPLE) == 46);

// End of structures definitions
/////////////////////////////////////////////////////////////////////

#ifdef NEEDS_PRAGMA_PACK
#pragma pack(pop)
#endif


typedef struct SF2LOADERINFO
{
	uint32 nPresetBags;
	SFPRESETBAG *pPresetBags;
	uint32 nPresetGens;
	SFGENLIST *pPresetGens;
	uint32 nInsts;
	SFINST *pInsts;
	uint32 nInstBags;
	SFINSTBAG *pInstBags;
	uint32 nInstGens;
	SFINSTGENLIST *pInstGens;
} SF2LOADERINFO;


/////////////////////////////////////////////////////////////////////
// Unit conversion

LONG CDLSBank::DLS32BitTimeCentsToMilliseconds(LONG lTimeCents)
//-------------------------------------------------------------
{
	// tc = log2(time[secs]) * 1200*65536
	// time[secs] = 2^(tc/(1200*65536))
	if ((uint32)lTimeCents == 0x80000000) return 0;
	double fmsecs = 1000.0 * pow(2.0, ((double)lTimeCents)/(1200.0*65536.0));
	if (fmsecs < -32767) return -32767;
	if (fmsecs > 32767) return 32767;
	return (LONG)fmsecs;
}


// 0dB = 0x10000
LONG CDLSBank::DLS32BitRelativeGainToLinear(LONG lCentibels)
//----------------------------------------------------------
{
	// v = 10^(cb/(200*65536)) * V
	return (LONG)(65536.0 * pow(10.0, ((double)lCentibels)/(200*65536.0)) );
}


LONG CDLSBank::DLS32BitRelativeLinearToGain(LONG lGain)
//-----------------------------------------------------
{
	// cb = log10(v/V) * 200 * 65536
	if (lGain <= 0) return -960 * 65536;
	return (LONG)( 200*65536.0 * log10( ((double)lGain)/65536.0 ) );
}


LONG CDLSBank::DLSMidiVolumeToLinear(uint32 nMidiVolume)
//------------------------------------------------------
{
	return (nMidiVolume * nMidiVolume << 16) / (127*127);
}


/////////////////////////////////////////////////////////////////////
// Implementation

CDLSBank::CDLSBank()
//------------------
{
	m_nInstruments = 0;
	m_nWaveForms = 0;
	m_nEnvelopes = 0;
	m_nSamplesEx = 0;
	m_nMaxWaveLink = 0;
	m_pWaveForms = NULL;
	m_pInstruments = NULL;
	m_pSamplesEx = NULL;
	m_nType = SOUNDBANK_TYPE_INVALID;
	MemsetZero(m_BankInfo);
}


CDLSBank::~CDLSBank()
//-------------------
{
	Destroy();
}


void CDLSBank::Destroy()
//----------------------
{
	if (m_pWaveForms)
	{
		delete[] m_pWaveForms;
		m_pWaveForms = NULL;
		m_nWaveForms = 0;
	}
	if (m_pSamplesEx)
	{
		delete[] m_pSamplesEx;
		m_pSamplesEx = NULL;
		m_nSamplesEx = 0;
	}
	if (m_pInstruments)
	{
		delete[] m_pInstruments;
		m_pInstruments = NULL;
		m_nInstruments = 0;
	}
}


bool CDLSBank::IsDLSBank(const mpt::PathString &filename)
//-------------------------------------------------------
{
	RIFFCHUNKID riff;
	FILE *f;
	if(filename.empty()) return false;
	if((f = mpt_fopen(filename, "rb")) == NULL) return false;
	MemsetZero(riff);
	fread(&riff, sizeof(RIFFCHUNKID), 1, f);
	// Check for embedded DLS sections
	if (riff.id_RIFF == IFFID_FORM)
	{
		do
		{
			int len = BigEndian(riff.riff_len);
			if (len <= 4) break;
			if (riff.id_DLS == IFFID_XDLS)
			{
				fread(&riff, sizeof(RIFFCHUNKID), 1, f);
				break;
			}
			if((len % 2u) != 0)
				len++;
			if (fseek(f, len-4, SEEK_CUR) != 0) break;
		} while (fread(&riff, sizeof(RIFFCHUNKID), 1, f) != 0);
	} else
	if ((riff.id_RIFF == IFFID_RIFF) && (riff.id_DLS == IFFID_RMID))
	{
		for (;;)
		{
			if(!fread(&riff, sizeof(RIFFCHUNKID), 1, f))
				break;
			if (riff.id_DLS == IFFID_DLS) break; // found it
			int len = riff.riff_len;
			if((len % 2u) != 0)
				len++;
			if ((len <= 4) || (fseek(f, len-4, SEEK_CUR) != 0)) break;
		}
	}
	fclose(f);
	return ((riff.id_RIFF == IFFID_RIFF)
		 && ((riff.id_DLS == IFFID_DLS) || (riff.id_DLS == IFFID_MLS) || (riff.id_DLS == IFFID_sfbk))
		 && (riff.riff_len >= 256));
}


///////////////////////////////////////////////////////////////
// Find an instrument based on the given parameters

DLSINSTRUMENT *CDLSBank::FindInstrument(bool bDrum, uint32 nBank, uint32 dwProgram, uint32 dwKey, uint32 *pInsNo)
//---------------------------------------------------------------------------------------------------------------
{
	if ((!m_pInstruments) || (!m_nInstruments)) return NULL;
	for (uint32 iIns=0; iIns<m_nInstruments; iIns++)
	{
		DLSINSTRUMENT *pDlsIns = &m_pInstruments[iIns];
		uint32 insbank = ((pDlsIns->ulBank & 0x7F00) >> 1) | (pDlsIns->ulBank & 0x7F);
		if ((nBank >= 0x4000) || (insbank == nBank))
		{
			if (bDrum)
			{
				if (pDlsIns->ulBank & F_INSTRUMENT_DRUMS)
				{
					if ((dwProgram >= 0x80) || (dwProgram == (pDlsIns->ulInstrument & 0x7F)))
					{
						for (uint32 iRgn=0; iRgn<pDlsIns->nRegions; iRgn++)
						{
							if ((!dwKey) || (dwKey >= 0x80)
							 || ((dwKey >= pDlsIns->Regions[iRgn].uKeyMin)
							  && (dwKey <= pDlsIns->Regions[iRgn].uKeyMax)))
							{
								if (pInsNo) *pInsNo = iIns;
								return pDlsIns;
							}
						}
					}
				}
			} else
			{
				if (!(pDlsIns->ulBank & F_INSTRUMENT_DRUMS))
				{
					if ((dwProgram >= 0x80) || (dwProgram == (pDlsIns->ulInstrument & 0x7F)))
					{
						if (pInsNo) *pInsNo = iIns;
						return pDlsIns;
					}
				}
			}
		}
	}
	return NULL;
}


///////////////////////////////////////////////////////////////
// Update DLS instrument definition from an IFF chunk

bool CDLSBank::UpdateInstrumentDefinition(DLSINSTRUMENT *pDlsIns, void *pvchunk, uint32 dwMaxLen)
//-----------------------------------------------------------------------------------------------
{
	IFFCHUNK *pchunk = (IFFCHUNK *)pvchunk;
	if ((!pchunk->len) || (pchunk->len+8 > dwMaxLen)) return false;
	if (pchunk->id == IFFID_LIST)
	{
		LISTCHUNK *plist = (LISTCHUNK *)pchunk;
		uint32 dwPos = 12;
		while (dwPos < plist->len)
		{
			LPIFFCHUNK p = (LPIFFCHUNK)(((uint8 *)plist) + dwPos);
			if (!(p->id & 0xFF))
			{
				p = (LPIFFCHUNK)( ((uint8 *)p)+1  );
				dwPos++;
			}
			if (dwPos + p->len + 8 <= plist->len + 12)
			{
				UpdateInstrumentDefinition(pDlsIns, p, p->len+8);
			}
			dwPos += p->len + 8;
		}
		switch(plist->listid)
		{
		case IFFID_rgn:		// Level 1 region
		case IFFID_rgn2:	// Level 2 region
			if (pDlsIns->nRegions < DLSMAXREGIONS) pDlsIns->nRegions++;
			break;
		}
	} else
	{
		switch(pchunk->id)
		{
		case IFFID_insh:
			pDlsIns->ulBank = ((INSHCHUNK *)pchunk)->ulBank;
			pDlsIns->ulInstrument = ((INSHCHUNK *)pchunk)->ulInstrument;
			//Log("%3d regions, bank 0x%04X instrument %3d\n", ((INSHCHUNK *)pchunk)->cRegions, pDlsIns->ulBank, pDlsIns->ulInstrument);
			break;

		case IFFID_rgnh:
			if (pDlsIns->nRegions < DLSMAXREGIONS)
			{
				RGNHCHUNK *p = (RGNHCHUNK *)pchunk;
				DLSREGION *pregion = &pDlsIns->Regions[pDlsIns->nRegions];
				pregion->uKeyMin = (uint8)p->RangeKey.usLow;
				pregion->uKeyMax = (uint8)p->RangeKey.usHigh;
				pregion->fuOptions = (uint8)(p->usKeyGroup & DLSREGION_KEYGROUPMASK);
				if (p->fusOptions & F_RGN_OPTION_SELFNONEXCLUSIVE) pregion->fuOptions |= DLSREGION_SELFNONEXCLUSIVE;
				//Log("  Region %d: fusOptions=0x%02X usKeyGroup=0x%04X ", pDlsIns->nRegions, p->fusOptions, p->usKeyGroup);
				//Log("KeyRange[%3d,%3d] ", p->RangeKey.usLow, p->RangeKey.usHigh);
			}
			break;

		case IFFID_wlnk:
			if (pDlsIns->nRegions < DLSMAXREGIONS)
			{
				DLSREGION *pregion = &pDlsIns->Regions[pDlsIns->nRegions];
				WLNKCHUNK *p = (WLNKCHUNK *)pchunk;
				pregion->nWaveLink = (uint16)p->ulTableIndex;
				if ((pregion->nWaveLink < 16384) && (pregion->nWaveLink >= m_nMaxWaveLink)) m_nMaxWaveLink = pregion->nWaveLink + 1;
				//Log("  WaveLink %d: fusOptions=0x%02X usPhaseGroup=0x%04X ", pDlsIns->nRegions, p->fusOptions, p->usPhaseGroup);
				//Log("ulChannel=%d ulTableIndex=%4d\n", p->ulChannel, p->ulTableIndex);
			}
			break;

		case IFFID_wsmp:
			if (pDlsIns->nRegions < DLSMAXREGIONS)
			{
				DLSREGION *pregion = &pDlsIns->Regions[pDlsIns->nRegions];
				WSMPCHUNK *p = (WSMPCHUNK *)pchunk;
				pregion->fuOptions |= DLSREGION_OVERRIDEWSMP;
				pregion->uUnityNote = (uint8)p->usUnityNote;
				pregion->sFineTune = p->sFineTune;
				LONG lVolume = DLS32BitRelativeGainToLinear(p->lAttenuation) / 256;
				if (lVolume > 256) lVolume = 256;
				if (lVolume < 4) lVolume = 4;
				pregion->usVolume = (uint16)lVolume;
				//Log("  WaveSample %d: usUnityNote=%2d sFineTune=%3d ", pDlsEnv->nRegions, p->usUnityNote, p->sFineTune);
				//Log("fulOptions=0x%04X loops=%d\n", p->fulOptions, p->cSampleLoops);
				if ((p->cSampleLoops) && (p->cbSize + sizeof(WSMPSAMPLELOOP) <= p->len))
				{
					WSMPSAMPLELOOP *ploop = (WSMPSAMPLELOOP *)(((uint8 *)p)+8+p->cbSize);
					//Log("looptype=%2d loopstart=%5d loopend=%5d\n", ploop->ulLoopType, ploop->ulLoopStart, ploop->ulLoopLength);
					if (ploop->ulLoopLength > 3)
					{
						pregion->fuOptions |= DLSREGION_SAMPLELOOP;
						//if (ploop->ulLoopType) pregion->fuOptions |= DLSREGION_PINGPONGLOOP;
						pregion->ulLoopStart = ploop->ulLoopStart;
						pregion->ulLoopEnd = ploop->ulLoopStart + ploop->ulLoopLength;
					}
				}
			}
			break;

		case IFFID_art1:
		case IFFID_art2:
			if (m_nEnvelopes < DLSMAXENVELOPES)
			{
				ART1CHUNK *p = (ART1CHUNK *)pchunk;
				if (pDlsIns->ulBank & F_INSTRUMENT_DRUMS)
				{
					if (pDlsIns->nRegions >= DLSMAXREGIONS) break;
				} else
				{
					pDlsIns->nMelodicEnv = m_nEnvelopes + 1;
				}
				if (p->cbSize+p->cConnectionBlocks*sizeof(CONNECTIONBLOCK) > p->len) break;
				DLSENVELOPE *pDlsEnv = &m_Envelopes[m_nEnvelopes];
				MemsetZero(*pDlsEnv);
				pDlsEnv->nDefPan = 128;
				pDlsEnv->nVolSustainLevel = 128;
				//Log("  art1 (%3d bytes): cbSize=%d cConnectionBlocks=%d\n", p->len, p->cbSize, p->cConnectionBlocks);
				CONNECTIONBLOCK *pblk = (CONNECTIONBLOCK *)( ((uint8 *)p)+8+p->cbSize );
				for (uint32 iblk=0; iblk<p->cConnectionBlocks; iblk++, pblk++)
				{
					// [4-bit transform][12-bit dest][8-bit control][8-bit source] = 32-bit ID
					uint32 dwArticulation = pblk->usTransform;
					dwArticulation = (dwArticulation << 12) | (pblk->usDestination & 0x0FFF);
					dwArticulation = (dwArticulation << 8) | (pblk->usControl & 0x00FF);
					dwArticulation = (dwArticulation << 8) | (pblk->usSource & 0x00FF);
					switch(dwArticulation)
					{
					case ART_DEFAULTPAN:
						{
							int32 pan = 128 + pblk->lScale / (65536000/128);
							if (pan < 0) pan = 0;
							if (pan > 255) pan = 255;
							pDlsEnv->nDefPan = (uint8)pan;
						}
						break;

					case ART_VOL_EG_ATTACKTIME:
						// 32-bit time cents units. range = [0s, 20s]
						pDlsEnv->wVolAttack = 0;
						if (pblk->lScale > -0x40000000)
						{
							int32 l = pblk->lScale - 78743200; // maximum velocity
							if (l > 0) l = 0;
							int32 attacktime = DLS32BitTimeCentsToMilliseconds(l);
							if (attacktime < 0) attacktime = 0;
							if (attacktime > 20000) attacktime = 20000;
							if (attacktime >= 20) pDlsEnv->wVolAttack = (uint16)(attacktime / 20);
							//Log("%3d: Envelope Attack Time set to %d (%d time cents)\n", (uint32)(pDlsEnv->ulInstrument & 0x7F)|((pDlsEnv->ulBank >> 16) & 0x8000), attacktime, pblk->lScale);
						}
						break;

					case ART_VOL_EG_DECAYTIME:
						// 32-bit time cents units. range = [0s, 20s]
						pDlsEnv->wVolDecay = 0;
						if (pblk->lScale > -0x40000000)
						{
							int32 decaytime = DLS32BitTimeCentsToMilliseconds(pblk->lScale);
							if (decaytime > 20000) decaytime = 20000;
							if (decaytime >= 20) pDlsEnv->wVolDecay = (uint16)(decaytime / 20);
							//Log("%3d: Envelope Decay Time set to %d (%d time cents)\n", (uint32)(pDlsEnv->ulInstrument & 0x7F)|((pDlsEnv->ulBank >> 16) & 0x8000), decaytime, pblk->lScale);
						}
						break;

					case ART_VOL_EG_RELEASETIME:
						// 32-bit time cents units. range = [0s, 20s]
						pDlsEnv->wVolRelease = 0;
						if (pblk->lScale > -0x40000000)
						{
							int32 releasetime = DLS32BitTimeCentsToMilliseconds(pblk->lScale);
							if (releasetime > 20000) releasetime = 20000;
							if (releasetime >= 20) pDlsEnv->wVolRelease = (uint16)(releasetime / 20);
							//Log("%3d: Envelope Release Time set to %d (%d time cents)\n", (uint32)(pDlsEnv->ulInstrument & 0x7F)|((pDlsEnv->ulBank >> 16) & 0x8000), pDlsEnv->wVolRelease, pblk->lScale);
						}
						break;

					case ART_VOL_EG_SUSTAINLEVEL:
						// 0.1% units
						if (pblk->lScale >= 0)
						{
							int32 l = pblk->lScale / (1000*512);
							if ((l >= 0) || (l <= 128)) pDlsEnv->nVolSustainLevel = (uint8)l;
							//Log("%3d: Envelope Sustain Level set to %d (%d)\n", (uint32)(pDlsIns->ulInstrument & 0x7F)|((pDlsIns->ulBank >> 16) & 0x8000), l, pblk->lScale);
						}
						break;

					//default:
					//	Log("    Articulation = 0x%08X value=%d\n", dwArticulation, pblk->lScale);
					}
				}
				m_nEnvelopes++;
			}
			break;

		case IFFID_INAM:
			mpt::String::CopyN(pDlsIns->szName, ((const char *)pchunk) + 8, pchunk->len);
			break;
	#if 0
		default:
			{
				char sid[5];
				memcpy(sid, &pchunk->id, 4);
				sid[4] = 0;
				Log("    \"%s\": %d bytes\n", (uint32)sid, pchunk->len);
			}
	#endif
		}
	}
	return true;
}

///////////////////////////////////////////////////////////////
// Converts SF2 chunks to DLS

bool CDLSBank::UpdateSF2PresetData(void *pvsf2, void *pvchunk, uint32 dwMaxLen)
//-----------------------------------------------------------------------------
{
	SF2LOADERINFO *psf2 = (SF2LOADERINFO *)pvsf2;
	IFFCHUNK *pchunk = (IFFCHUNK *)pvchunk;
	if ((!pchunk->len) || (pchunk->len+8 > dwMaxLen)) return false;
	switch(pchunk->id)
	{
	case IFFID_phdr:
		if (m_nInstruments) break;
		m_nInstruments = pchunk->len / sizeof(SFPRESETHEADER);
		if (m_nInstruments) m_nInstruments--; // Disgard EOP
		if (!m_nInstruments) break;
		m_pInstruments = new DLSINSTRUMENT[m_nInstruments];
		if (m_pInstruments)
		{
			memset(m_pInstruments, 0, m_nInstruments * sizeof(DLSINSTRUMENT));
		#ifdef DLSBANK_LOG
			Log("phdr: %d instruments\n", m_nInstruments);
		#endif
			SFPRESETHEADER *psfh = (SFPRESETHEADER *)(pchunk+1);
			DLSINSTRUMENT *pDlsIns = m_pInstruments;
			for (uint32 i=0; i<m_nInstruments; i++, psfh++, pDlsIns++)
			{
				mpt::String::Copy(pDlsIns->szName, psfh->achPresetName);
				pDlsIns->szName[20] = 0;
				pDlsIns->ulInstrument = psfh->wPreset & 0x7F;
				pDlsIns->ulBank = (psfh->wBank >= 128) ? F_INSTRUMENT_DRUMS : (psfh->wBank << 8);
				pDlsIns->wPresetBagNdx = psfh->wPresetBagNdx;
				pDlsIns->wPresetBagNum = 1;
				if (psfh[1].wPresetBagNdx > pDlsIns->wPresetBagNdx) pDlsIns->wPresetBagNum = (uint16)(psfh[1].wPresetBagNdx - pDlsIns->wPresetBagNdx);
			}
		}
		break;

	case IFFID_pbag:
		if (m_pInstruments)
		{
			uint32 nBags = pchunk->len / sizeof(SFPRESETBAG);
			if (nBags)
			{
				psf2->nPresetBags = nBags;
				psf2->pPresetBags = (SFPRESETBAG *)(pchunk+1);
			}
		}
	#ifdef DLSINSTR_LOG
		else Log("pbag: no instruments!\n");
	#endif
		break;

	case IFFID_pgen:
		if (m_pInstruments)
		{
			uint32 nGens = pchunk->len / sizeof(SFGENLIST);
			if (nGens)
			{
				psf2->nPresetGens = nGens;
				psf2->pPresetGens = (SFGENLIST *)(pchunk+1);
			}
		}
	#ifdef DLSINSTR_LOG
		else Log("pgen: no instruments!\n");
	#endif
		break;

	case IFFID_inst:
		if (m_pInstruments)
		{
			uint32 nIns = pchunk->len / sizeof(SFINST);
			psf2->nInsts = nIns;
			psf2->pInsts = (SFINST *)(pchunk+1);
		}
		break;

	case IFFID_ibag:
		if (m_pInstruments)
		{
			uint32 nBags = pchunk->len / sizeof(SFINSTBAG);
			if (nBags)
			{
				psf2->nInstBags = nBags;
				psf2->pInstBags = (SFINSTBAG *)(pchunk+1);
			}
		}
		break;

	case IFFID_igen:
		if (m_pInstruments)
		{
			uint32 nGens = pchunk->len / sizeof(SFINSTGENLIST);
			if (nGens)
			{
				psf2->nInstGens = nGens;
				psf2->pInstGens = (SFINSTGENLIST *)(pchunk+1);
			}
		}
		break;

	case IFFID_shdr:
		if (m_pSamplesEx) break;
		m_nSamplesEx = pchunk->len / sizeof(SFSAMPLE);
	#ifdef DLSINSTR_LOG
		Log("shdr: %d samples\n", m_nSamplesEx);
	#endif
		if (m_nSamplesEx < 1) break;
		m_nWaveForms = m_nSamplesEx;
		m_pSamplesEx = new DLSSAMPLEEX[m_nSamplesEx];
		m_pWaveForms = new uint32[m_nWaveForms];
		if ((m_pSamplesEx) && (m_pWaveForms))
		{
			memset(m_pSamplesEx, 0, sizeof(DLSSAMPLEEX)*m_nSamplesEx);
			memset(m_pWaveForms, 0, sizeof(uint32)*m_nWaveForms);
			DLSSAMPLEEX *pDlsSmp = m_pSamplesEx;
			SFSAMPLE *p = (SFSAMPLE *)(pchunk+1);
			for (uint32 i=0; i<m_nSamplesEx; i++, pDlsSmp++, p++)
			{
				mpt::String::Copy(pDlsSmp->szName, p->achSampleName);
				pDlsSmp->dwLen = 0;
				pDlsSmp->dwSampleRate = p->dwSampleRate;
				pDlsSmp->byOriginalPitch = p->byOriginalPitch;
				pDlsSmp->chPitchCorrection = p->chPitchCorrection;
				if (((p->sfSampleType & 0x7FFF) <= 4) && (p->dwStart < 0x08000000) && (p->dwEnd >= p->dwStart+8))
				{
					pDlsSmp->dwLen = (p->dwEnd - p->dwStart) * 2;
					if ((p->dwEndloop > p->dwStartloop + 7) && (p->dwStartloop >= p->dwStart))
					{
						pDlsSmp->dwStartloop = p->dwStartloop - p->dwStart;
						pDlsSmp->dwEndloop = p->dwEndloop - p->dwStart;
					}
					m_pWaveForms[i] = p->dwStart * 2;
					//Log("  offset[%d]=%d len=%d\n", i, p->dwStart*2, psmp->dwLen);
				}
			}
		}
		break;

	#ifdef DLSINSTR_LOG
	default:
		{
			char sdbg[5];
			memcpy(sdbg, &pchunk->id, 4);
			sdbg[4] = 0;
			Log("Unsupported SF2 chunk: %s (%d bytes)\n", sdbg, pchunk->len);
		}
	#endif
	}
	return true;
}


// Convert all instruments to the DLS format
bool CDLSBank::ConvertSF2ToDLS(void *pvsf2info)
//---------------------------------------------
{
	SF2LOADERINFO *psf2;
	DLSINSTRUMENT *pDlsIns;

	if ((!m_pInstruments) || (!m_pSamplesEx)) return false;
	psf2 = (SF2LOADERINFO *)pvsf2info;
	pDlsIns = m_pInstruments;
	for (uint32 nIns=0; nIns<m_nInstruments; nIns++, pDlsIns++)
	{
		DLSENVELOPE dlsEnv;
		uint32 nInstrNdx = 0;
		LONG lAttenuation = 0;
		// Default Envelope Values
		dlsEnv.wVolAttack = 0;
		dlsEnv.wVolDecay = 0;
		dlsEnv.wVolRelease = 0;
		dlsEnv.nVolSustainLevel = 128;
		dlsEnv.nDefPan = 128;
		// Load Preset Bags
		for (uint32 ipbagcnt=0; ipbagcnt<(uint32)pDlsIns->wPresetBagNum; ipbagcnt++)
		{
			uint32 ipbagndx = pDlsIns->wPresetBagNdx + ipbagcnt;
			if ((ipbagndx+1 >= psf2->nPresetBags) || (!psf2->pPresetBags)) break;
			// Load generators for each preset bag
			SFPRESETBAG *pbag = psf2->pPresetBags + ipbagndx;
			for (uint32 ipgenndx=pbag[0].wGenNdx; ipgenndx<pbag[1].wGenNdx; ipgenndx++)
			{
				if ((!psf2->pPresetGens) || (ipgenndx+1 >= psf2->nPresetGens)) break;
				SFGENLIST *pgen = psf2->pPresetGens + ipgenndx;
				switch(pgen->sfGenOper)
				{
				case SF2_GEN_DECAYVOLENV:
					{
						LONG decaytime = DLS32BitTimeCentsToMilliseconds(((LONG)(short int)pgen->genAmount)<<16);
						if (decaytime > 20000) decaytime = 20000;
						if (decaytime >= 20) dlsEnv.wVolDecay = (uint16)(decaytime / 20);
						//Log("  vol decay time set to %d\n", decaytime);
					}
					break;
				case SF2_GEN_RELEASEVOLENV:
					{
						LONG releasetime = DLS32BitTimeCentsToMilliseconds(((LONG)(short int)pgen->genAmount)<<16);
						if (releasetime > 20000) releasetime = 20000;
						if (releasetime >= 20) dlsEnv.wVolRelease = (uint16)(releasetime / 20);
						//Log("  vol release time set to %d\n", releasetime);
					}
					break;
				case SF2_GEN_INSTRUMENT:
					nInstrNdx = pgen->genAmount + 1;
					break;
				case SF2_GEN_ATTENUATION:
					lAttenuation = - (int)(uint16)(pgen->genAmount);
					break;
#if 0
				default:
					Log("Ins %3d: bag %3d gen %3d: ", nIns, ipbagndx, ipgenndx);
					Log("genoper=%d amount=0x%04X ", pgen->sfGenOper, pgen->genAmount);
					Log((pSmp->ulBank & F_INSTRUMENT_DRUMS) ? "(drum)\n" : "\n");
#endif
				}
			}
		}
		// Envelope
		if ((m_nEnvelopes < DLSMAXENVELOPES) && (!(pDlsIns->ulBank & F_INSTRUMENT_DRUMS)))
		{
			m_Envelopes[m_nEnvelopes] = dlsEnv;
			m_nEnvelopes++;
			pDlsIns->nMelodicEnv = m_nEnvelopes;
		}
		// Load Instrument Bags
		if ((!nInstrNdx) || (nInstrNdx >= psf2->nInsts) || (!psf2->pInsts)) continue;
		nInstrNdx--;
		pDlsIns->nRegions = psf2->pInsts[nInstrNdx+1].wInstBagNdx - psf2->pInsts[nInstrNdx].wInstBagNdx;
		//Log("\nIns %3d, %2d regions:\n", nIns, pSmp->nRegions);
		if (pDlsIns->nRegions > DLSMAXREGIONS) pDlsIns->nRegions = DLSMAXREGIONS;
		DLSREGION *pRgn = pDlsIns->Regions;
		for (uint32 nRgn=0; nRgn<pDlsIns->nRegions; nRgn++, pRgn++)
		{
			uint32 ibagcnt = psf2->pInsts[nInstrNdx].wInstBagNdx + nRgn;
			if ((ibagcnt >= psf2->nInstBags) || (!psf2->pInstBags)) break;
			// Create a new envelope for drums
			DLSENVELOPE *pDlsEnv = &dlsEnv;
			if (pDlsIns->ulBank & F_INSTRUMENT_DRUMS)
			{
				if ((m_nEnvelopes < DLSMAXENVELOPES) && (!(pDlsIns->ulBank & F_INSTRUMENT_DRUMS)))
				{
					m_Envelopes[m_nEnvelopes] = dlsEnv;
					pDlsEnv = &m_Envelopes[m_nEnvelopes];
					m_nEnvelopes++;
					pRgn->uPercEnv = (uint16)m_nEnvelopes;
				}
			} else
			if (pDlsIns->nMelodicEnv)
			{
				pDlsEnv = &m_Envelopes[pDlsIns->nMelodicEnv-1];
			}
			// Region Default Values
			LONG lAttn = lAttenuation;
			pRgn->uUnityNote = 0xFF;	// 0xFF means undefined -> use sample
			pRgn->sFineTune = 0;
			pRgn->nWaveLink = Util::MaxValueOfType(pRgn->nWaveLink);
			// Load Generators
			SFINSTBAG *pbag = psf2->pInstBags + ibagcnt;
			for (uint32 igenndx=pbag[0].wGenNdx; igenndx<pbag[1].wGenNdx; igenndx++)
			{
				if ((igenndx >= psf2->nInstGens) || (!psf2->pInstGens)) break;
				SFINSTGENLIST *pgen = psf2->pInstGens + igenndx;
				uint16 value = pgen->genAmount;
				switch(pgen->sfGenOper)
				{
				case SF2_GEN_KEYRANGE:
					pRgn->uKeyMin = (uint8)(value & 0xFF);
					pRgn->uKeyMax = (uint8)(value >> 8);
					if (pRgn->uKeyMin > pRgn->uKeyMax)
					{
						uint8 b = pRgn->uKeyMax;
						pRgn->uKeyMax = pRgn->uKeyMin;
						pRgn->uKeyMin = b;
					}
					//if (nIns == 9) Log("  keyrange: %d-%d\n", pRgn->uKeyMin, pRgn->uKeyMax);
					break;
				case SF2_GEN_UNITYNOTE:
					if (value < 128) pRgn->uUnityNote = (uint8)value;
					break;
				case SF2_GEN_RELEASEVOLENV:
					{
						LONG releasetime = DLS32BitTimeCentsToMilliseconds(((LONG)(short int)pgen->genAmount)<<16);
						if (releasetime > 20000) releasetime = 20000;
						if (releasetime >= 20) pDlsEnv->wVolRelease = (uint16)(releasetime / 20);
						//Log("  vol release time set to %d\n", releasetime);
					}
					break;
				case SF2_GEN_PAN:
					{
						int pan = (short int)value;
						pan = (((pan + 500) * 127) / 500) + 128;
						if (pan < 0) pan = 0;
						if (pan > 255) pan = 255;
						pDlsEnv->nDefPan = (uint8)pan;
					}
					break;
				case SF2_GEN_ATTENUATION:
					lAttn = -(int)value;
					break;
				case SF2_GEN_SAMPLEID:
					if ((m_pSamplesEx) && ((uint32)value < m_nSamplesEx))
					{
						pRgn->nWaveLink = value;
						pRgn->ulLoopStart = m_pSamplesEx[value].dwStartloop;
						pRgn->ulLoopEnd = m_pSamplesEx[value].dwEndloop;
					}
					break;
				case SF2_GEN_SAMPLEMODES:
					value &= 3;
					pRgn->fuOptions &= ~(DLSREGION_SAMPLELOOP|DLSREGION_PINGPONGLOOP|DLSREGION_SUSTAINLOOP);
					if (value == 1) pRgn->fuOptions |= DLSREGION_SAMPLELOOP; else
					if (value == 2) pRgn->fuOptions |= DLSREGION_SAMPLELOOP|DLSREGION_PINGPONGLOOP; else
					if (value == 3) pRgn->fuOptions |= DLSREGION_SAMPLELOOP|DLSREGION_SUSTAINLOOP;
					pRgn->fuOptions |= DLSREGION_OVERRIDEWSMP;
					break;
				case SF2_GEN_KEYGROUP:
					pRgn->fuOptions |= (uint8)(value & DLSREGION_KEYGROUPMASK);
					break;
				case SF2_GEN_COARSETUNE:
					pRgn->sFineTune += static_cast<int16>(value) * 128;
					break;
				case SF2_GEN_FINETUNE:
					pRgn->sFineTune += static_cast<int16>(Util::muldiv(static_cast<int8>(value), 128, 100));
					break;
				//default:
				//	Log("    gen=%d value=%04X\n", pgen->sfGenOper, pgen->genAmount);
				}
			}
			LONG lVolume = DLS32BitRelativeGainToLinear((lAttn/10) << 16) / 256;
			if (lVolume < 16) lVolume = 16;
			if (lVolume > 256) lVolume = 256;
			pRgn->usVolume = (uint16)lVolume;
			//Log("\n");
		}
	}
	return true;
}


///////////////////////////////////////////////////////////////
// Open: opens a DLS bank

bool CDLSBank::Open(const mpt::PathString &filename)
//--------------------------------------------------
{
	if(filename.empty()) return false;
	m_szFileName = filename;
	InputFile f(filename);
	if(!f.IsValid()) return false;
	return Open(GetFileReader(f));
}


bool CDLSBank::Open(FileReader file)
//----------------------------------
{
	SF2LOADERINFO sf2info;
	const uint8 *lpMemFile;	// Pointer to memory-mapped file
	RIFFCHUNKID *priff;
	uint32 dwMemPos, dwMemLength;
	uint32 nInsDef;

	file.Rewind();
	m_szFileName = file.GetFileName();
	lpMemFile = file.GetRawData<uint8>();
	dwMemLength = file.GetLength();
	if (!lpMemFile || dwMemLength < 256)
	{
		return false;
	}

#ifdef DLSBANK_LOG
	Log("\nOpening DLS bank: %s\n", m_szFileName);
#endif

	priff = (RIFFCHUNKID *)lpMemFile;
	dwMemPos = 0;

	// Check DLS sections embedded in RMI midi files
	if ((priff->id_RIFF == IFFID_RIFF) && (priff->id_DLS == IFFID_RMID))
	{
		dwMemPos = 12;
		while (dwMemPos + 12 <= dwMemLength)
		{
			priff = (RIFFCHUNKID *)(lpMemFile + dwMemPos);
			if ((priff->id_RIFF == IFFID_RIFF) && (priff->id_DLS == IFFID_DLS)) break;
			uint32 len = priff->riff_len;
			if((len % 2u) != 0)
				len++;
			dwMemPos += len + 8;
		}
	}

	// Check XDLS sections embedded in big endian IFF files
	if (priff->id_RIFF == IFFID_FORM)
	{
		do {
			priff = (RIFFCHUNKID *)(lpMemFile + dwMemPos);
			int len = BigEndian(priff->riff_len);
			if((len % 2u) != 0)
				len++;
			if ((len <= 4) || ((uint32)len >= dwMemLength - dwMemPos)) break;
			if (priff->id_DLS == IFFID_XDLS)
			{
				dwMemPos += 12;
				priff = (RIFFCHUNKID *)(lpMemFile + dwMemPos);
				break;
			}
			dwMemPos += len + 8;
		} while (dwMemPos + 24 < dwMemLength);
	}
	if ((priff->id_RIFF != IFFID_RIFF)
	 || ((priff->id_DLS != IFFID_DLS) && (priff->id_DLS != IFFID_MLS) && (priff->id_DLS != IFFID_sfbk))
	 || (dwMemPos + priff->riff_len > dwMemLength-8))
	{
	#ifdef DLSBANK_LOG
		Log("Invalid DLS bank!\n");
	#endif
		return false;
	}
	MemsetZero(sf2info);
	m_nType = (priff->id_DLS == IFFID_sfbk) ? SOUNDBANK_TYPE_SF2 : SOUNDBANK_TYPE_DLS;
	m_dwWavePoolOffset = 0;
	m_nInstruments = 0;
	m_nWaveForms = 0;
	m_nEnvelopes = 0;
	m_pInstruments = NULL;
	m_pWaveForms = NULL;
	nInsDef = 0;
	if (dwMemLength > 8 + priff->riff_len + dwMemPos) dwMemLength = 8 + priff->riff_len + dwMemPos;
	dwMemPos += sizeof(RIFFCHUNKID);
	while (dwMemPos + sizeof(IFFCHUNK) < dwMemLength)
	{
		IFFCHUNK *pchunk = (IFFCHUNK *)(lpMemFile + dwMemPos);

		if (dwMemPos + 8 + pchunk->len > dwMemLength) break;
		switch(pchunk->id)
		{
		// DLS 1.0: Instruments Collection Header
		case IFFID_colh:
		#ifdef DLSBANK_LOG
			Log("colh (%d bytes)\n", pchunk->len);
		#endif
			if (!m_pInstruments)
			{
				m_nInstruments = ((COLHCHUNK *)pchunk)->ulInstruments;
				if (m_nInstruments)
				{
					m_pInstruments = new DLSINSTRUMENT[m_nInstruments];
					if (m_pInstruments) memset(m_pInstruments, 0, m_nInstruments * sizeof(DLSINSTRUMENT));
				}
			#ifdef DLSBANK_LOG
				Log("  %d instruments\n", m_nInstruments);
			#endif
			}
			break;

		// DLS 1.0: Instruments Pointers Table
		case IFFID_ptbl:
		#ifdef DLSBANK_LOG
			Log("ptbl (%d bytes)\n", pchunk->len);
		#endif
			if (!m_pWaveForms)
			{
				m_nWaveForms = ((PTBLCHUNK *)pchunk)->cCues;
				if (m_nWaveForms)
				{
					m_pWaveForms = new uint32[m_nWaveForms];
					if (m_pWaveForms)
					{
						memcpy(m_pWaveForms, (lpMemFile + dwMemPos + 8 + ((PTBLCHUNK *)pchunk)->cbSize), m_nWaveForms * sizeof(uint32));
					}
				}
			#ifdef DLSBANK_LOG
				Log("  %d waveforms\n", m_nWaveForms);
			#endif
			}
			break;

		// DLS 1.0: LIST section
		case IFFID_LIST:
		#ifdef DLSBANK_LOG
			Log("LIST\n");
		#endif
			{
				LISTCHUNK *plist = (LISTCHUNK *)pchunk;
				uint32 dwPos = dwMemPos + sizeof(LISTCHUNK);
				uint32 dwMaxPos = dwMemPos + 8 + plist->len;
				if (dwMaxPos > dwMemLength) dwMaxPos = dwMemLength;
				if (((plist->listid == IFFID_wvpl) && (m_nType & SOUNDBANK_TYPE_DLS))
				 || ((plist->listid == IFFID_sdta) && (m_nType & SOUNDBANK_TYPE_SF2)))
				{
					m_dwWavePoolOffset = dwPos;
				#ifdef DLSBANK_LOG
					Log("Wave Pool offset: %d\n", m_dwWavePoolOffset);
				#endif
					break;
				}
				while (dwPos + 12 < dwMaxPos)
				{
					if (!(lpMemFile[dwPos])) dwPos++;
					LISTCHUNK *psublist = (LISTCHUNK *)(lpMemFile+dwPos);
					if (dwPos + psublist->len + 8 > dwMemLength) break;
					// DLS Instrument Headers
					if ((psublist->id == IFFID_LIST) && (m_nType & SOUNDBANK_TYPE_DLS))
					{
						if ((psublist->listid == IFFID_ins) && (nInsDef < m_nInstruments) && (m_pInstruments))
						{
							DLSINSTRUMENT *pDlsIns = &m_pInstruments[nInsDef];
							//Log("Instrument %d:\n", nInsDef);
							UpdateInstrumentDefinition(pDlsIns, (IFFCHUNK *)psublist, psublist->len + 8);
							nInsDef++;
						}
					} else
					// DLS/SF2 Bank Information
					if ((plist->listid == IFFID_INFO) && (psublist->len))
					{
						uint32 len = (psublist->len < 255) ? psublist->len : 255;
						const char *pszInfo = (const char *)(lpMemFile+dwPos+8);
						switch(psublist->id)
						{
						case IFFID_INAM:
							lstrcpynA(m_BankInfo.szBankName, pszInfo, len);
							break;
						case IFFID_IENG:
							lstrcpynA(m_BankInfo.szEngineer, pszInfo, len);
							break;
						case IFFID_ICOP:
							lstrcpynA(m_BankInfo.szCopyRight, pszInfo, len);
							break;
						case IFFID_ICMT:
							len = psublist->len;
							if (len > sizeof(m_BankInfo.szComments)-1) len = sizeof(m_BankInfo.szComments)-1;
							lstrcpynA(m_BankInfo.szComments, pszInfo, len);
							break;
						case IFFID_ISFT:
							lstrcpynA(m_BankInfo.szSoftware, pszInfo, len);
							break;
						case IFFID_ISBJ:
							lstrcpynA(m_BankInfo.szDescription, pszInfo, len);
							break;
						}
					} else
					if ((plist->listid == IFFID_pdta) && (m_nType & SOUNDBANK_TYPE_SF2))
					{
						UpdateSF2PresetData(&sf2info, (IFFCHUNK *)psublist, psublist->len + 8);
					}
					dwPos += 8 + psublist->len;
				}
			}
			break;

		#ifdef DLSBANK_LOG
		default:
			{
				char sdbg[5];
				memcpy(sdbg, &pchunk->id, 4);
				sdbg[4] = 0;
				Log("Unsupported chunk: %s (%d bytes)\n", sdbg, pchunk->len);
			}
			break;
		#endif
		}
		dwMemPos += 8 + pchunk->len;
	}
	// Build the ptbl is not present in file
	if ((!m_pWaveForms) && (m_dwWavePoolOffset) && (m_nType & SOUNDBANK_TYPE_DLS) && (m_nMaxWaveLink > 0))
	{
	#ifdef DLSBANK_LOG
		Log("ptbl not present: building table (%d wavelinks)...\n", m_nMaxWaveLink);
	#endif
		m_pWaveForms = new uint32[m_nMaxWaveLink];
		if (m_pWaveForms)
		{
			memset(m_pWaveForms, 0, m_nMaxWaveLink * sizeof(uint32));
			dwMemPos = m_dwWavePoolOffset;
			while (dwMemPos + sizeof(IFFCHUNK) < dwMemLength)
			{
				IFFCHUNK *pchunk = (IFFCHUNK *)(lpMemFile + dwMemPos);
				if (pchunk->id == IFFID_LIST) m_pWaveForms[m_nWaveForms++] = dwMemPos - m_dwWavePoolOffset;
				dwMemPos += 8 + pchunk->len;
				if (m_nWaveForms >= m_nMaxWaveLink) break;
			}
		#ifdef DLSBANK_LOG
			Log("Found %d waveforms\n", m_nWaveForms);
		#endif
		}
	}
	// Convert the SF2 data to DLS
	if ((m_nType & SOUNDBANK_TYPE_SF2) && (m_pSamplesEx) && (m_pInstruments))
	{
		ConvertSF2ToDLS(&sf2info);
	}
#ifdef DLSBANK_LOG
	Log("DLS bank closed\n");
#endif
	return true;
}

////////////////////////////////////////////////////////////////////////////////////////
// Extracts the WaveForms from a DLS bank

uint32 CDLSBank::GetRegionFromKey(uint32 nIns, uint32 nKey)
//---------------------------------------------------------
{
	DLSINSTRUMENT *pDlsIns;

	if ((!m_pInstruments) || (nIns >= m_nInstruments)) return 0;
	pDlsIns = &m_pInstruments[nIns];
	for (uint32 rgn=0; rgn<pDlsIns->nRegions; rgn++)
	{
		if ((nKey >= pDlsIns->Regions[rgn].uKeyMin) && (nKey <= pDlsIns->Regions[rgn].uKeyMax))
		{
			return rgn;
		}
	}
	return 0;
}


bool CDLSBank::ExtractWaveForm(uint32 nIns, uint32 nRgn, std::vector<uint8> &waveData, uint32 &length)
//----------------------------------------------------------------------------------------------------
{
	DLSINSTRUMENT *pDlsIns;
	uint32 dwOffset;
	uint32 nWaveLink;
	FILE *f;

	if ((!m_pInstruments) || (nIns >= m_nInstruments)
	 || (!m_dwWavePoolOffset) || (!m_pWaveForms))
	{
	#ifdef DLSBANK_LOG
		Log("ExtractWaveForm(%d) failed: m_nInstruments=%d m_dwWavePoolOffset=%d m_pWaveForms=0x%08X\n", nIns, m_nInstruments, m_dwWavePoolOffset, m_pWaveForms);
	#endif
		return false;
	}
	waveData.clear();
	length = 0;
	pDlsIns = &m_pInstruments[nIns];
	if (nRgn >= pDlsIns->nRegions)
	{
	#ifdef DLSBANK_LOG
		Log("invalid waveform region: nIns=%d nRgn=%d pSmp->nRegions=%d\n", nIns, nRgn, pSmp->nRegions);
	#endif
		return false;
	}
	nWaveLink = pDlsIns->Regions[nRgn].nWaveLink;
	if (nWaveLink >= m_nWaveForms)
	{
	#ifdef DLSBANK_LOG
		Log("Invalid wavelink id: nWaveLink=%d nWaveForms=%d\n", nWaveLink, m_nWaveForms);
	#endif
		return false;
	}
	dwOffset = m_pWaveForms[nWaveLink] + m_dwWavePoolOffset;
	if((f = mpt_fopen(m_szFileName, "rb")) == NULL) return false;
	if (fseek(f, dwOffset, SEEK_SET) == 0)
	{
		if (m_nType & SOUNDBANK_TYPE_SF2)
		{
			if ((m_pSamplesEx) && (m_pSamplesEx[nWaveLink].dwLen))
			{
				if (fseek(f, 8, SEEK_CUR) == 0)
				{
					length = m_pSamplesEx[nWaveLink].dwLen;
					try
					{
						waveData.assign(length + 8, 0);
						fread(&waveData[0], 1, length, f);
					} catch(MPTMemoryException)
					{
					}
				}
			}
		} else
		{
			LISTCHUNK chunk;
			if (fread(&chunk, 1, 12, f) == 12)
			{
				if ((chunk.id == IFFID_LIST) && (chunk.listid == IFFID_wave) && (chunk.len > 4))
				{
					length = chunk.len + 8;
					try
					{
						waveData.assign(chunk.len + 8, 0);
						memcpy(&waveData[0], &chunk, 12);
						fread(&waveData[12], 1, length - 12, f);
					} catch(MPTMemoryException)
					{
					}
				}
			}
		}
	}
	fclose(f);
	return !waveData.empty();
}


bool CDLSBank::ExtractSample(CSoundFile &sndFile, SAMPLEINDEX nSample, uint32 nIns, uint32 nRgn, int transpose)
//-------------------------------------------------------------------------------------------------------------
{
	DLSINSTRUMENT *pDlsIns;
	std::vector<uint8> pWaveForm;
	uint32 dwLen = 0;
	bool bOk, bWaveForm;

	if ((!m_pInstruments) || (nIns >= m_nInstruments)) return false;
	pDlsIns = &m_pInstruments[nIns];
	if (nRgn >= pDlsIns->nRegions) return false;
	if (!ExtractWaveForm(nIns, nRgn, pWaveForm, dwLen)) return false;
	if (dwLen < 16) return false;
	bOk = false;

	FileReader wsmpChunk;
	if (m_nType & SOUNDBANK_TYPE_SF2)
	{
		sndFile.DestroySample(nSample);
		uint32 nWaveLink = pDlsIns->Regions[nRgn].nWaveLink;
		ModSample &sample = sndFile.GetSample(nSample);
		if (sndFile.m_nSamples < nSample) sndFile.m_nSamples = nSample;
		if ((nWaveLink < m_nSamplesEx) && (m_pSamplesEx))
		{
			DLSSAMPLEEX *p = &m_pSamplesEx[nWaveLink];
		#ifdef DLSINSTR_LOG
			Log("  SF2 WaveLink #%3d: %5dHz\n", nWaveLink, p->dwSampleRate);
		#endif
			sample.Initialize();
			sample.nLength = dwLen / 2;
			sample.nLoopStart = pDlsIns->Regions[nRgn].ulLoopStart;
			sample.nLoopEnd = pDlsIns->Regions[nRgn].ulLoopEnd;
			sample.nC5Speed = p->dwSampleRate;
			sample.RelativeTone = p->byOriginalPitch;
			sample.nFineTune = p->chPitchCorrection;
			if (p->szName[0])
				mpt::String::Copy(sndFile.m_szNames[nSample], p->szName);
			else if(pDlsIns->szName[0])
				mpt::String::Copy(sndFile.m_szNames[nSample], pDlsIns->szName);

			FileReader chunk(&pWaveForm[0], dwLen);
			SampleIO(
				SampleIO::_16bit,
				SampleIO::mono,
				SampleIO::littleEndian,
				SampleIO::signedPCM)
				.ReadSample(sample, chunk);
		}
		bWaveForm = sample.pSample != nullptr;
	} else
	{
		FileReader file(&pWaveForm[0], dwLen);
		bWaveForm = sndFile.ReadWAVSample(nSample, file, false, &wsmpChunk);
		if(pDlsIns->szName[0])
			mpt::String::Copy(sndFile.m_szNames[nSample], pDlsIns->szName);
	}
	if (bWaveForm)
	{
		ModSample &sample = sndFile.GetSample(nSample);
		DLSREGION *pRgn = &pDlsIns->Regions[nRgn];
		sample.uFlags.reset(CHN_LOOP | CHN_PINGPONGLOOP | CHN_SUSTAINLOOP | CHN_PINGPONGSUSTAIN);
		if (pRgn->fuOptions & DLSREGION_SAMPLELOOP) sample.uFlags.set(CHN_LOOP);
		if (pRgn->fuOptions & DLSREGION_SUSTAINLOOP) sample.uFlags.set(CHN_SUSTAINLOOP);
		if (pRgn->fuOptions & DLSREGION_PINGPONGLOOP) sample.uFlags.set(CHN_PINGPONGLOOP);
		if (sample.uFlags[CHN_LOOP | CHN_SUSTAINLOOP])
		{
			if (pRgn->ulLoopEnd > pRgn->ulLoopStart)
			{
				if (sample.uFlags[CHN_SUSTAINLOOP])
				{
					sample.nSustainStart = pRgn->ulLoopStart;
					sample.nSustainEnd = pRgn->ulLoopEnd;
				} else
				{
					sample.nLoopStart = pRgn->ulLoopStart;
					sample.nLoopEnd = pRgn->ulLoopEnd;
				}
			} else
			{
				sample.uFlags.reset(CHN_LOOP|CHN_SUSTAINLOOP);
			}
		}
		// WSMP chunk
		{
			uint32 usUnityNote = pRgn->uUnityNote;
			int sFineTune = pRgn->sFineTune;
			int lVolume = pRgn->usVolume;

			WSMPCHUNK wsmp;
			if(!(pRgn->fuOptions & DLSREGION_OVERRIDEWSMP) && wsmpChunk.IsValid() && wsmpChunk.ReadStructPartial(wsmp))
			{
				usUnityNote = wsmp.usUnityNote;
				sFineTune = wsmp.sFineTune;
				lVolume = DLS32BitRelativeGainToLinear(wsmp.lAttenuation) / 256;
				if(wsmp.cSampleLoops)
				{
					WSMPSAMPLELOOP loop;
					wsmpChunk.Skip(8 + wsmp.cbSize);
					wsmpChunk.ReadConvertEndianness(loop);
					if(loop.ulLoopLength > 3)
					{
						sample.uFlags.set(CHN_LOOP);
						//if (loop.ulLoopType) sample.uFlags |= CHN_PINGPONGLOOP;
						sample.nLoopStart = loop.ulLoopStart;
						sample.nLoopEnd = loop.ulLoopStart + loop.ulLoopLength;
					}
				}
			} else if (m_nType & SOUNDBANK_TYPE_SF2)
			{
				usUnityNote = (usUnityNote < 0x80) ? usUnityNote : sample.RelativeTone;
				sFineTune += sample.nFineTune;
			}
		#ifdef DLSINSTR_LOG
			Log("WSMP: usUnityNote=%d.%d, %dHz (transp=%d)\n", usUnityNote, sFineTune, sample.nC5Speed, transpose);
		#endif
			if (usUnityNote > 0x7F) usUnityNote = 60;
			int steps = (60 + transpose - usUnityNote) * 128 + sFineTune;
			sample.nC5Speed = Util::Round<uint32>(std::pow(2.0, steps * (1.0 / (12.0 * 128.0))) * sample.nC5Speed);

			Limit(lVolume, 16, 256);
			sample.nGlobalVol = (uint8)(lVolume / 4);	// 0-64
		}
		sample.nPan = GetPanning(nIns, nRgn);

		sample.Convert(MOD_TYPE_IT, sndFile.GetType());
		sample.PrecomputeLoops(sndFile, false);
		bOk = true;
	}
	return bOk;
}


bool CDLSBank::ExtractInstrument(CSoundFile &sndFile, INSTRUMENTINDEX nInstr, uint32 nIns, uint32 nDrumRgn)
//---------------------------------------------------------------------------------------------------------
{
	SAMPLEINDEX RgnToSmp[DLSMAXREGIONS];
	DLSINSTRUMENT *pDlsIns;
	ModInstrument *pIns;
	uint32 nRgnMin, nRgnMax, nEnv;

	if ((!m_pInstruments) || (nIns >= m_nInstruments)) return false;
	pDlsIns = &m_pInstruments[nIns];
	if (pDlsIns->ulBank & F_INSTRUMENT_DRUMS)
	{
		if (nDrumRgn >= pDlsIns->nRegions) return false;
		nRgnMin = nDrumRgn;
		nRgnMax = nDrumRgn+1;
		nEnv = pDlsIns->Regions[nDrumRgn].uPercEnv;
	} else
	{
		if (!pDlsIns->nRegions) return false;
		nRgnMin = 0;
		nRgnMax = pDlsIns->nRegions;
		nEnv = pDlsIns->nMelodicEnv;
	}
#ifdef DLSINSTR_LOG
	Log("DLS Instrument #%d: %s\n", nIns, pDlsIns->szName);
	Log("  Bank=0x%04X Instrument=0x%04X\n", pDlsIns->ulBank, pDlsIns->ulInstrument);
	Log("  %2d regions, nMelodicEnv=%d\n", pDlsIns->nRegions, pDlsIns->nMelodicEnv);
	for (uint32 iDbg=0; iDbg<pDlsIns->nRegions; iDbg++)
	{
		DLSREGION *prgn = &pDlsIns->Regions[iDbg];
		Log(" Region %d:\n", iDbg);
		Log("  WaveLink = %d (loop [%5d, %5d])\n", prgn->nWaveLink, prgn->ulLoopStart, prgn->ulLoopEnd);
		Log("  Key Range: [%2d, %2d]\n", prgn->uKeyMin, prgn->uKeyMax);
		Log("  fuOptions = 0x%04X\n", prgn->fuOptions);
		Log("  usVolume = %3d, Unity Note = %d\n", prgn->usVolume, prgn->uUnityNote);
	}
#endif

	pIns = new (std::nothrow) ModInstrument();
	if(pIns == nullptr)
	{
		return false;
	}

	if (sndFile.Instruments[nInstr])
	{
		sndFile.DestroyInstrument(nInstr, deleteAssociatedSamples);
	}
	// Initializes Instrument
	if (pDlsIns->ulBank & F_INSTRUMENT_DRUMS)
	{
		char s[64] = "";
		uint32 key = pDlsIns->Regions[nDrumRgn].uKeyMin;
		if ((key >= 24) && (key <= 84)) lstrcpyA(s, szMidiPercussionNames[key-24]);
		if (pDlsIns->szName[0])
		{
			sprintf(&s[strlen(s)], " (%s", pDlsIns->szName);
			size_t n = strlen(s);
			while ((n) && (s[n-1] == ' '))
			{
				n--;
				s[n] = 0;
			}
			lstrcatA(s, ")");
		}
		mpt::String::Copy(pIns->name, s);
	} else
	{
		mpt::String::Copy(pIns->name, pDlsIns->szName);
	}
	int nTranspose = 0;
	if (pDlsIns->ulBank & F_INSTRUMENT_DRUMS)
	{
		for (uint32 iNoteMap=0; iNoteMap<NOTE_MAX; iNoteMap++)
		{
			if(sndFile.GetType() & (MOD_TYPE_IT|MOD_TYPE_MID|MOD_TYPE_MPT))
			{
				// Formate has instrument note mapping
				if (iNoteMap < pDlsIns->Regions[nDrumRgn].uKeyMin) pIns->NoteMap[iNoteMap] = (uint8)(pDlsIns->Regions[nDrumRgn].uKeyMin + 1);
				if (iNoteMap > pDlsIns->Regions[nDrumRgn].uKeyMax) pIns->NoteMap[iNoteMap] = (uint8)(pDlsIns->Regions[nDrumRgn].uKeyMax + 1);
			} else
			{
				if (iNoteMap == pDlsIns->Regions[nDrumRgn].uKeyMin)
				{
					nTranspose = (pDlsIns->Regions[nDrumRgn].uKeyMin + (pDlsIns->Regions[nDrumRgn].uKeyMax - pDlsIns->Regions[nDrumRgn].uKeyMin) / 2) - 60;
				}
			}
		}
	}
	pIns->nFadeOut = 1024;
	pIns->nMidiProgram = (uint8)(pDlsIns->ulInstrument & 0x7F) + 1;
	pIns->nMidiChannel = (uint8)((pDlsIns->ulBank & F_INSTRUMENT_DRUMS) ? 10 : 0);
	pIns->wMidiBank = (uint16)(((pDlsIns->ulBank & 0x7F00) >> 1) | (pDlsIns->ulBank & 0x7F));
	pIns->nNNA = NNA_NOTEOFF;
	pIns->nDCT = DCT_NOTE;
	pIns->nDNA = DNA_NOTEFADE;
	sndFile.Instruments[nInstr] = pIns;
	uint32 nLoadedSmp = 0;
	SAMPLEINDEX nextSample = 0;
	// Extract Samples
	for (uint32 nRgn=nRgnMin; nRgn<nRgnMax; nRgn++)
	{
		bool bDupRgn = false;
		SAMPLEINDEX nSmp = 0;
		DLSREGION *pRgn = &pDlsIns->Regions[nRgn];
		// Elimitate Duplicate Regions
		uint32 iDup;
		for (iDup=nRgnMin; iDup<nRgn; iDup++)
		{
			DLSREGION *pRgn2 = &pDlsIns->Regions[iDup];
			if (((pRgn2->nWaveLink == pRgn->nWaveLink)
			  && (pRgn2->ulLoopEnd == pRgn->ulLoopEnd)
			  && (pRgn2->ulLoopStart == pRgn->ulLoopStart))
			 || ((pRgn2->uKeyMin == pRgn->uKeyMin)
			  && (pRgn2->uKeyMax == pRgn->uKeyMax)))
			{
				bDupRgn = true;
				nSmp = RgnToSmp[iDup];
				break;
			}
		}
		// Create a new sample
		if (!bDupRgn)
		{
			uint32 nmaxsmp = (m_nType & MOD_TYPE_XM) ? 16 : 32;
			if (nLoadedSmp >= nmaxsmp)
			{
				nSmp = RgnToSmp[nRgn-1];
			} else
			{
				nextSample = sndFile.GetNextFreeSample(nInstr, nextSample + 1);
				if (nextSample == SAMPLEINDEX_INVALID) break;
				if (nextSample > sndFile.GetNumSamples()) sndFile.m_nSamples = nextSample;
				nSmp = nextSample;
				nLoadedSmp++;
			}
		}

		RgnToSmp[nRgn] = nSmp;
		// Map all notes to the right sample
		if (nSmp)
		{
			for (uint32 iKey=0; iKey<NOTE_MAX; iKey++)
			{
				if ((nRgn == nRgnMin) || ((iKey >= pRgn->uKeyMin) && (iKey <= pRgn->uKeyMax)))
				{
					pIns->Keyboard[iKey] = nSmp;
				}
			}
			// Load the sample
			if(!bDupRgn || sndFile.GetSample(nSmp).pSample == nullptr)
			{
				ExtractSample(sndFile, nSmp, nIns, nRgn, nTranspose);
			} else if(sndFile.GetSample(nSmp).GetNumChannels() == 1)
			{
				// Try to combine stereo samples
				uint8 pan1 = GetPanning(nIns, nRgn), pan2 = GetPanning(nIns, iDup);
				if((pan1 == 0 || pan1 == 255) && (pan2 == 0 || pan2 == 255))
				{
					ModSample &sample = sndFile.GetSample(nSmp);
					ctrlSmp::ConvertToStereo(sample, sndFile);
					std::vector<uint8> pWaveForm;
					uint32 dwLen = 0;
					if(ExtractWaveForm(nIns, nRgn, pWaveForm, dwLen) && dwLen >= sample.GetSampleSizeInBytes() / 2)
					{
						SmpLength len = sample.nLength;
						const int16 *src = reinterpret_cast<int16 *>(&pWaveForm[0]);
						int16 *dst = sample.pSample16 + ((pan1 == 0) ? 0 : 1);
						while(len--)
						{
							*dst = *src;
							src++;
							dst += 2;
						}
					}
				}
			}
		}
	}
	// Initializes Envelope
	if ((nEnv) && (nEnv <= m_nEnvelopes))
	{
		DLSENVELOPE *part = &m_Envelopes[nEnv-1];
		// Volume Envelope
		if ((part->wVolAttack) || (part->wVolDecay < 20*50) || (part->nVolSustainLevel) || (part->wVolRelease < 20*50))
		{
			pIns->VolEnv.dwFlags.set(ENV_ENABLED);
			// Delay section
			// -> DLS level 2
			// Attack section
			pIns->VolEnv.assign(2, EnvelopeNode());
			if (part->wVolAttack)
			{
				pIns->VolEnv[0].value = (uint8)(ENVELOPE_MAX / (part->wVolAttack / 2 + 2) + 8);   //	/-----
				pIns->VolEnv[1].tick = part->wVolAttack;                                          //	|
			} else
			{
				pIns->VolEnv[0].value = ENVELOPE_MAX;  //	|-----
				pIns->VolEnv[1].tick = 1;              //	|
			}
			pIns->VolEnv[1].value = ENVELOPE_MAX;
			// Hold section
			// -> DLS Level 2
			// Sustain Level
			if (part->nVolSustainLevel > 0)
			{
				if (part->nVolSustainLevel < 128)
				{
					LONG lStartTime = pIns->VolEnv.back().tick;
					LONG lSusLevel = - DLS32BitRelativeLinearToGain(part->nVolSustainLevel << 9) / 65536;
					LONG lDecayTime = 1;
					if (lSusLevel > 0)
					{
						lDecayTime = (lSusLevel * (LONG)part->wVolDecay) / 960;
						for (uint32 i=0; i<7; i++)
						{
							LONG lFactor = 128 - (1 << i);
							if (lFactor <= part->nVolSustainLevel) break;
							LONG lev = - DLS32BitRelativeLinearToGain(lFactor << 9) / 65536;
							if (lev > 0)
							{
								LONG ltime = (lev * (LONG)part->wVolDecay) / 960;
								if ((ltime > 1) && (ltime < lDecayTime))
								{
									ltime += lStartTime;
									if (ltime > pIns->VolEnv.back().tick)
									{
										pIns->VolEnv.push_back(EnvelopeNode((uint16)ltime, (uint8)(lFactor / 2)));
									}
								}
							}
						}
					}

					if (lStartTime + lDecayTime > (LONG)pIns->VolEnv.back().tick)
					{
						pIns->VolEnv.push_back(EnvelopeNode((uint16)(lStartTime+lDecayTime), (uint8)((part->nVolSustainLevel+1) / 2)));
					}
				}
				pIns->VolEnv.dwFlags.set(ENV_SUSTAIN);
			} else
			{
				pIns->VolEnv.dwFlags.set(ENV_SUSTAIN);
				pIns->VolEnv.push_back(EnvelopeNode((uint16)(pIns->VolEnv.back().tick + 1), pIns->VolEnv.back().value));
			}
			pIns->VolEnv.nSustainStart = pIns->VolEnv.nSustainEnd = (uint8)(pIns->VolEnv.size() - 1);
			// Release section
			if ((part->wVolRelease) && (pIns->VolEnv.back().value > 1))
			{
				LONG lReleaseTime = part->wVolRelease;
				LONG lStartTime = pIns->VolEnv.back().tick;
				LONG lStartFactor = pIns->VolEnv.back().value;
				LONG lSusLevel = - DLS32BitRelativeLinearToGain(lStartFactor << 10) / 65536;
				LONG lDecayEndTime = (lReleaseTime * lSusLevel) / 960;
				lReleaseTime -= lDecayEndTime;
				for (uint32 i=0; i<5; i++)
				{
					LONG lFactor = 1 + ((lStartFactor * 3) >> (i+2));
					if ((lFactor <= 1) || (lFactor >= lStartFactor)) continue;
					LONG lev = - DLS32BitRelativeLinearToGain(lFactor << 10) / 65536;
					if (lev > 0)
					{
						LONG ltime = (((LONG)part->wVolRelease * lev) / 960) - lDecayEndTime;
						if ((ltime > 1) && (ltime < lReleaseTime))
						{
							ltime += lStartTime;
							if (ltime > pIns->VolEnv.back().tick)
							{
								pIns->VolEnv.push_back(EnvelopeNode((uint16)ltime, (uint8)lFactor));
							}
						}
					}
				}
				if (lReleaseTime < 1) lReleaseTime = 1;
				pIns->VolEnv.push_back(EnvelopeNode((uint16)(lStartTime + lReleaseTime), ENVELOPE_MIN));
			} else
			{
				pIns->VolEnv.push_back(EnvelopeNode((uint16)(pIns->VolEnv.back().tick + 1), ENVELOPE_MIN));
			}
		}
	}
	if (pDlsIns->ulBank & F_INSTRUMENT_DRUMS)
	{
		// Create a default envelope for drums
		pIns->VolEnv.dwFlags.reset(ENV_SUSTAIN);
		if(!pIns->VolEnv.dwFlags[ENV_ENABLED])
		{
			pIns->VolEnv.dwFlags.set(ENV_ENABLED);
			pIns->VolEnv.resize(4);
			pIns->VolEnv[0].tick = 0;
			pIns->VolEnv[0].value = ENVELOPE_MAX;
			pIns->VolEnv[1].tick = 5;
			pIns->VolEnv[1].value = ENVELOPE_MAX;
			pIns->VolEnv[2].tick = 10;
			pIns->VolEnv[2].value = ENVELOPE_MID;
			pIns->VolEnv[3].tick = 20;	// 1 second max. for drums
			pIns->VolEnv[3].value = ENVELOPE_MIN;
		}
	}
	return true;
}


const char *CDLSBank::GetRegionName(uint32 nIns, uint32 nRgn) const
//-----------------------------------------------------------------
{
	DLSINSTRUMENT *pDlsIns;

	if ((!m_pInstruments) || (nIns >= m_nInstruments)) return nullptr;
	pDlsIns = &m_pInstruments[nIns];
	if (nRgn >= pDlsIns->nRegions) return nullptr;

	if (m_nType & SOUNDBANK_TYPE_SF2)
	{
		uint32 nWaveLink = pDlsIns->Regions[nRgn].nWaveLink;
		if ((nWaveLink < m_nSamplesEx) && (m_pSamplesEx))
		{
			DLSSAMPLEEX *p = &m_pSamplesEx[nWaveLink];
			return p->szName;
		}
	}
	return nullptr;
}


uint8 CDLSBank::GetPanning(uint32 ins, uint32 region) const
//---------------------------------------------------------
{
	const DLSINSTRUMENT &dlsIns = m_pInstruments[ins];
	if(region >= CountOf(dlsIns.Regions))
		return 128;
	const DLSREGION &rgn = dlsIns.Regions[region];
	if(dlsIns.ulBank & F_INSTRUMENT_DRUMS)
	{
		if(rgn.uPercEnv > 0 && rgn.uPercEnv <= m_nEnvelopes)
		{
			return m_Envelopes[rgn.uPercEnv - 1].nDefPan;
		}
	} else
	{
		if(dlsIns.nMelodicEnv > 0 && dlsIns.nMelodicEnv <= m_nEnvelopes)
		{
			return m_Envelopes[dlsIns.nMelodicEnv - 1].nDefPan;
		}
	}
	return 128;
}


#else // !MODPLUG_TRACKER

MPT_MSVC_WORKAROUND_LNK4221(Dlsbank)

#endif // MODPLUG_TRACKER


OPENMPT_NAMESPACE_END
