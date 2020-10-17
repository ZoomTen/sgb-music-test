INCLUDE "include/sgb_macros.asm"

SECTION "SGB Data", ROMX
; packets
LoadSPC: SOU_TRN
PlaySPC: SOUND 0, 0, 0, 1

; sgb data
AudioData:	INCBIN "music/intro.sbn"	; Intro battle from Pokemon R/B

SECTION "SGB Functions", ROM0
; from pokered
Wait7000:
	ld de, 7000/9
.loop
	nop
	nop
	nop
	dec de
	ld a, d
	or e
	jr nz, .loop
	ret

SendSGBPacket:
	ld a, [hl]
	and %00000111
	ret z
	ld b, a
.loop2
	push bc
;	ld a, 1
;	ldh [hDisableJoypadPolling], a
	xor a
	ldh [rJOYP], a
	ld a, $30
	ldh [rJOYP], a
	ld b, $10
.nextByte
	ld e, $08
	ld a, [hli]
	ld d, a
.nextBit0
	bit 0, d
	ld a, $10
	jr nz, .next0
	ld a, $20
.next0
	ldh [rJOYP], a
	ld a, $30
	ldh [rJOYP], a
	rr d
	dec e
	jr nz, .nextBit0
	dec b
	jr nz, .nextByte
	ld a, $20
	ldh [rJOYP], a
	ld a, $30
	ldh [rJOYP], a
	;xor a
	;ldh [hDisableJoypadPolling], a
	call Wait7000
	pop bc
	dec b
	ret z
	jr .loop2
