# RGBDS variables
# for if you want to get another version

# remove implicit rules
MAKEFLAGS += -rR

.PHONY: clean clean-dist rom
.PRECIOUS: %.sbn

ASM	?= rgbasm
GFX	?= rgbgfx
LNK	?= rgblink
FIX	?= rgbfix

PYTHON ?= python3

ROMNAME  := sgbtest
GAMENAME := "SGB TEST ROM"
RGBFIX_OPTS := -c -k "ZD" -l 0x33 -m 0x01 -p 0x00 -s
RGBASM_OPTS :=

SRCFILES = $(shell find . -name \*.asm)

MUSIC_DIR = music
MUSIC_FILES = $(shell find $(MUSIC_DIR) -name \*.mid)
MUSIC_SBN = $(patsubst $(MUSIC_DIR)/%.mid, $(MUSIC_DIR)/%.sbn, $(MUSIC_FILES))

all: rom

rom: $(ROMNAME).gb

%.gb: %.o
	$(LNK) -m $(patsubst %.gb, %.map, $@) -n $(patsubst %.gb, %.sym, $@) -o $@ -l $(patsubst %.gb, %.link, $@) $<
	$(FIX) $(RGBFIX_OPTS) -t $(GAMENAME) -v $@

%.o: main.asm $(SRCFILES) $(MUSIC_SBN)
	$(ASM) $(RGBASM_OPTS) -o $@ $<

%.sbn: %.mid
	$(PYTHON) scripts/mid2sbn.py -o $@ $<

clean:
ifneq ("$(wildcard *.gb)","")
	rm *.gb
endif
ifneq ("$(wildcard *.sym)","")
	rm *.sym
endif
ifneq ("$(wildcard *.o)","")
	rm *.o
endif
ifneq ("$(wildcard *.map)","")
	rm *.map
endif
ifneq ("$(wildcard */*.sbn)","")
	rm */*.sbn
endif

clean-dist: clean
ifneq ("$(wildcard *.sav)","")
	rm *.sav
endif
ifneq ("$(wildcard *.spc)","")
	rm *.sav
endif
