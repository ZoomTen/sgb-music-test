ATTR_BLK: MACRO
; This is a command macro.
; Use ATTR_BLK_DATA for data sets.
	db ($4 << 3) + ((\1 * 6) / 16 + 1)
	db \1
ENDM
ATTR_BLK_DATA: MACRO
	db \1 ; which regions are affected
	db \2 + (\3 << 2) + (\4 << 4) ; palette for each region
	db \5, \6, \7, \8 ; x1, y1, x2, y2
ENDM

PAL_SET: MACRO
	db ($a << 3) + 1
	dw \1, \2, \3, \4
	ds 7, 0
ENDM

PAL_TRN: MACRO
	db ($b << 3) + 1
	ds 15, 0
ENDM

MLT_REQ: MACRO
	db ($11 << 3) + 1
	db \1 - 1
	ds 14, 0
ENDM

CHR_TRN: MACRO
	db ($13 << 3) + 1
	db \1 + (\2 << 1)
	ds 14, 0
ENDM

PCT_TRN: MACRO
	db ($14 << 3) + 1
	ds 15, 0
ENDM

MASK_EN: MACRO
	db ($17 << 3) + 1
	db \1
	ds 14, 0
ENDM

SOU_TRN: MACRO
	db ($9 << 3) + 1
	ds 15, 0
ENDM

DATA_SND: MACRO
	db ($f << 3) + 1
	dw \1 ; address
	db \2 ; bank
	db \3 ; length (1-11)
ENDM

SOUND: MACRO
	db ($8 << 3) + 1
	db \1 ; Sound Effect A (Port 1) Decrescendo 8bit Sound Code
	db \2 ; Sound Effect B (Port 2) Sustain     8bit Sound Code
	db \3 ; Sound Effect Attributes
	db \4 ; Music Score Code
	ds 11, 0
ENDM
