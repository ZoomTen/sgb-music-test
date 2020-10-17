INCLUDE "include/hardware.asm"
INCLUDE "sgb.asm"

hVBlankOccured equ $FF80

SECTION "int VBlank", ROM0
	jp VB

SECTION "Entry Point", ROM0
Entry:
	jp Start

SECTION "Main Program", ROM0
Start:
	ld sp, $DFFF

	xor a
	ld [rIF], a	; clear interrupt force
	ldh [hVBlankOccured], a
	ld a, %00000001 ; enable vblank
	ld [rIE], a

; setup screen
	call DisableLCD

; copy audio data to tileset
	di
	ld bc, $1000	 ; how many bytes
	ld hl, AudioData ; where the audio data is
	ld de, $8000	 ; tile set destination (VRAM)
	call CopyData

; data transfer tile map
; generate a tile map of 00 - 14 on the first row
; 14 - 28 on the second, etc.
; matching the tileset layout

; this is because the super game boy literally reads out
; the screen for large data transfers like this
	xor a
	ld hl, $9800	 ; tile map destination (VRAM)
	ld b, $c
.outer
	ld c, $14
.inner
	ld [hli], a
	inc a
	dec c
	jr nz, .inner
	rept 12
	inc hl
	endr
	push af
	ld a, b
	or c
	jr z, .map_done
	dec b
	pop af
	jr .outer
.map_done
; reset scroll registers
	xor a
	ld [rWY], a
	ld [rSCX], a
	ld [rSCY], a
; default palette
	ld a, $E4
	ld [rBGP], a
 ; enable LCD
	ld a, %10010001 ; enable LCD
	ld [rLCDC], a
	ei

; give the SGB enough time to render the screen
; (tested in BSNES :p)
	call DelayFrame
; send two packets
	di
	ld hl, LoadSPC		; send over the N-SPC data from the screen
	call SendSGBPacket
	ld hl, PlaySPC		; tell the SGB to run the audio engine
	call SendSGBPacket
	ei
Loop:
; purgatory
	halt
	nop
	jr Loop

SECTION "Home Functions", ROM0
; From pret/pokered

CopyData::
; Copy bc bytes from hl to de.
	ld a, [hli]
	ld [de], a
	inc de
	dec bc
	ld a, c
	or b
	jr nz, CopyData
	ret

DisableLCD::
	xor a
	ldh [rIF], a
	ldh a, [rIE]
	ld b, a
	res 0, a
	ldh [rIE], a

.wait
	ldh a, [rLY]
	cp 144
	jr nz, .wait

	ldh a, [rLCDC]
	res 7, a
	ldh [rLCDC], a
	ld a, b
	ldh [rIE], a
	ret

EnableLCD::
	ldh a, [rLCDC]
	set 7, a
	ldh [rLCDC], a
	ret

VB:
	push af
	xor a
	ld [hVBlankOccured], a
	pop af
	reti

DelayFrames::
; wait c frames
	call DelayFrame
	dec c
	jr nz, DelayFrames
	ret

Delay3:
	call DelayFrame
	call DelayFrame
	jp DelayFrame

DelayFrame::
; Wait for the next vblank interrupt.
; As a bonus, this saves battery.
	ld a, 1
	ldh [hVBlankOccured], a
.halt
	halt
	ldh a, [hVBlankOccured]
	and a
	jr nz, .halt
	ret
