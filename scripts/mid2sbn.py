'''
Basic MIDI to N-SPC SBN converter
ZoomTen, 2020-10-17

Designed for Super Game Boy music sequence insertion, although it can be
modified to work with other N-SPC games.

License: WTFPL
'''

import mido
import argparse
from io import BytesIO
import os

if __name__ == '__main__':
	ap = argparse.ArgumentParser(
			description="Convert a standard MIDI file to the SBN format commonly used with the N-SPC engine. Currently does not support looping. MIDI channels 1-8 correspond to SNES tracks, while MIDI channel 10, if available, is added to the song if not using all 8 tracks.",
			epilog='example: mid2sbn.py intro.mid'
		)

	ap.add_argument('midi_file', help="The MIDI file to convert.")
	ap.add_argument('--timebase', '-t', type=int, default=6, help="Minimum ticks to interpolate.")
	ap.add_argument('--base', '-b', default='0x2b00', help='Base address in hexadecimal (prefixed with 0x). Defaults to 0x2b00, the SGB music score entry point')
	ap.add_argument('--raw', '-r', action='store_true', help="Only output the raw data.")
	ap.add_argument('--debug', '-d', action='store_true', help="Show MIDI events and the converted N-SPC data.")
	ap.add_argument('--output', '-o', help="Output file name. If not set, the default is *.sbn.")

	args = ap.parse_args()

	# @helper functions
	single_byte = lambda x: x.to_bytes(1, byteorder='little')
	vel2index = lambda x: int(x/127*15)

	########################## options #############################################

	# Map MIDI instrument to N-SPC instrument
	ins_mappings = {
	# midi  n-spc
		56: 45,	# trumpet
		34: 13,	# bass
		48: 29, # string
	}

	# Transpose for each instrument
	ins_transpose = {
	# midi
		56: -12,	# trumpet
		48: -12,	# string
	}

	# Map drums to drum notes (this doesn't use the percussion stuff yet)
	drum_mappings = {
		#     which instrument to use     which note to play when the drum hits
		38: {'patch': single_byte(0x35), 'note':single_byte(0xaa)}
	}

	################################################################################

	# Minimum timebase to use
	tbase = args.timebase

	# Track bins
	tracks = {
		'midi':{
			0: [],
			1: [],
			2: [],
			3: [],
			4: [],
			5: [],
			6: [],
			7: [],
			9: []
		},
		'snes':{
			0: [],
			1: [],
			2: [],
			3: [],
			4: [],
			5: [],
			6: [],
			7: [],
			9: []
		}
	}

	midi_file = mido.MidiFile(args.midi_file)

	tempo = 0
	for i in midi_file:
		if hasattr(i, 'tempo'):
			# THIS WILL NOT WORK FOR DYNAMIC TEMPO
			tempo = (int(mido.tempo2bpm(i.tempo) / 3 * 24 / 60))

	# set global tempo
	tracks['snes'][0].append(b'\xe7'+single_byte(tempo))
	
	# set global volume
	tracks['snes'][0].append(b'\xe5'+b'\xff')

	# (hardcoded) global SNES echo/reverb
	tracks['snes'][0].append(b'\xf7\x03\x07\x03\xf5\x07\xc0\xc0')

	# (hardcoded) vibrato test
	# tracks['snes'][0].append(b'\xe3\x0c\x15\x18')
	
	# enumerate all the events -> midi track bin
	last_msg = mido.Message('reset')	# dummy message... where's the null message?
	for track in midi_file.tracks:
		for event in track:
			for channel in range(10):
				if channel in tracks['midi'].keys():
					if hasattr(event, 'channel'):
						if event.channel == channel:
							if event == last_msg:
								pass
							else:
								# exclude certain events, this is still rough
								if event.dict()['type'] == 'control_change':
									pass
								elif event.dict()['type'] == 'pitchwheel':
									pass
								else:
									tracks['midi'][channel].append(event)
									last_msg = event
	
	# process the midi events -> snes track bin
	for track_number, pattern in tracks['midi'].items():
		if args.debug:
			if (len(pattern) > 0):
				print('Track {}'.format(track_number+1))
		if track_number == 9:
		# drum
			vel = -1
			program = 0
			add_velocity_byte = False
			
			for e in pattern:
				midi_note = e.dict()
				drum_note = midi_note['note']
				command = b''
				
				if midi_note['type'] == 'note_on':
				# for delays.
				# this also sets the velocity of the next note
					if e.time > 0:
						div = int(e.time/tbase)
						command += single_byte(div % 0x7F)	# note length
						if vel < 0:
							# if song just started (beginning delay)
							# set velocity at 100% quantization (0x70)
							vel = e.velocity
							command += single_byte(0x70 + vel2index(vel))
						command += b'\xc9' # rest
					if vel != e.velocity:
						# change the velocity on note_off event
						vel = e.velocity
						add_velocity_byte = True
				
				
				elif midi_note['type'] == 'note_off':
				# actual note plays here
					div = int(e.time/tbase)
					command += single_byte(div)
					
					if add_velocity_byte:
						# change the velocity at 100% quantization (0x70)
						command += single_byte(0x70 + vel2index(vel))
						add_velocity_byte = False
					
					if drum_note in drum_mappings.keys():
						command += b'\xe0'
						command += drum_mappings[drum_note]['patch']
						command += drum_mappings[drum_note]['note']
					else:
						command += b'\xc9'
				
				if args.debug: print('[{}] => {}'.format(e, command.hex()))
				tracks['snes'][track_number].append(command)
		else:
			# melody
			vel = -1
			program = 0
			add_velocity_byte = False
			for e in pattern:
				midi_note = e.dict()
				command = b''
				
				if midi_note['type'] == 'program_change':
					command += b'\xE0'
					if midi_note['program'] in ins_mappings.keys():
						command += single_byte(ins_mappings[e.program])
						program = midi_note['program']
					else:
						command += b'\x14'	# DEFAULT
				
				
				elif midi_note['type'] == 'note_on':
				# for delays.
				# this also sets the velocity of the next note
					if e.time > 0:
						div = int(e.time/tbase)
						
						# rests can be very long, so adjust accordingly
						rests = []
						if div > 0x7f:
							for add in range(int(div/0x7f)):
								rests.append(0x7f)
							rests.append(div % 0x7f)
						else:
							rests.append(div % 0x7f)
						
						for rest in rests:
							command += single_byte(rest)	# note length
							if vel < 0:
								# if song just started (beginning delay)
								# set velocity at 100% quantization (0x70)
								vel = e.velocity
								command += single_byte(0x70 + vel2index(vel))
							command += b'\xc9' # rest
					
					if vel != e.velocity:
						# change the velocity on note_off event
						vel = e.velocity
						add_velocity_byte = True
				
				
				elif midi_note['type'] == 'note_off':
				# actual note plays here
					div = int(e.time/tbase)
					
					# adjust for instrument
					hardcoded_transpose = 0
					if program in ins_transpose.keys():
						hardcoded_transpose = ins_transpose[program]
					
					note = (midi_note['note'] + 104 + hardcoded_transpose) % 0xc7
					
					command += single_byte(div)
					
					if add_velocity_byte:
						# change the velocity at 100% quantization (0x70)
						command += single_byte(0x70 + vel2index(vel))
						add_velocity_byte = False
					
					command += single_byte(note)
				
				if args.debug: print('[{}] => {}'.format(e, command.hex()))
				tracks['snes'][track_number].append(command)
		
		# remove last event if it isn't a note_on or note_off
		# to prevent the n-spc engine crashing
		if (len(pattern) > 0):
			last_event = tracks['midi'][track_number][-1].dict()['type']
			if last_event == 'note_on':
				pass
			elif last_event == 'note_off':
				pass
			else:
				tracks['snes'][track_number].pop()
		

	# create SBN file
	out = BytesIO()
	
	# pad the file so that it'll work with file tell
	out.write(b'\x00'* int(args.base, 16))
	
	# save some space for the necessary headers
	base_location = out.tell()	# beginning of data
	out.write(b'\x00' * 2) # song pointer
	
	song_location = out.tell()	# beginning of song
	out.write(b'\x00' * 2) # 'frame' pointers
	out.write(b'\x00' * 2) # 00 bytes mark end of whole song
	
	frame_location = out.tell()	# beginning of frame
	out.write(b'\x00' * 2 * 8) # eight channels header
	
	channel_locations = [] # locations of channels
	for channel_num, channel_data in tracks['snes'].items():
		if len(channel_data) > 0:
			channel_locations.append(out.tell())
			out.write(b''.join(channel_data))
			out.write(b'\x00') # mark end of track
	
	# write the headers
	out.seek(frame_location)
	out.write(b''.join([x.to_bytes(2, 'little') for x in channel_locations]))
	
	out.seek(song_location)
	out.write(frame_location.to_bytes(2, 'little'))
	
	out.seek(base_location)
	out.write(song_location.to_bytes(2, 'little'))
	
	if args.output:
		out_name = args.output
	else:
		out_name = os.path.splitext(args.midi_file)[0]+'.sbn'
	
	if args.raw:
		with open(out_name, 'wb') as out_file:
			out.seek(int(args.base, 16))
			out_file.write(out.read())
	else:
		with open(out_name, 'wb') as out_file:
			SIZE = 0x1000 - 8
			
			# block size
			out_file.write(SIZE.to_bytes(2,'little'))
			# block destination
			out_file.write(int(args.base, 16).to_bytes(2,'little'))
			
			# data
			out.seek(int(args.base, 16))
			out_file.write(out.read(0xff8))
			if out_file.tell() < (0x1000-4):
				out_file.write(b'\x00' * (0x1000-4-out_file.tell()))
			# spc entry point
			out_file.write(b'\x00\x00\x00\x04')
