# SGB Music Test ROM

## About

Demonstration of making the Super Game Boy play SNES music. Currently this will
not work on a bog-standard GameBoy emulator (not even BGB)

The SGB reads this music data by reading the screen when prompted by a `SOU_TRN`
packet.

The music data itself is in the SBN format (a very simple, block-based container
for SPC music data basically)

The SPC data itself is just song sequence data in the basic [N-SPC](https://sneslab.net/wiki/N-SPC_Engine) format.

The instruments are all coming from the Super Game Boy itself, in other words,
the Super Game Boy has a "soundfont" built in :p

This ROM has only been tested with SGB1/SGB2 with BSNES.

Included is a **MIDI to SBN** script, which you can use, distribute, modify, whatever.

## Building

What do you need?

* RGBDS
* Python 3
* Python Mido package (just do `pip install mido`)
* GNU Make
* A Super Game Boy (1 or 2) boot ROM, if you're gonna test this in BSNES

How build?

* `make`

How test?

* In BSNES, go to System -> Load Special -> Load Super Game Boy Cartridge
* Load the boot ROM to Base cartridge, and the built ROM to Game Boy cartridge
