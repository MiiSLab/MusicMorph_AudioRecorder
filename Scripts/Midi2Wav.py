from midi2audio import FluidSynth
from mido import MidiFile, MidiTrack, Message
import pygame.midi

# Preprocess MIDI to assign instruments (optional)
def set_instrument_for_tracks(midi_path, instrument_map):
    """
    Modifies a MIDI file to assign specific instruments to tracks.

    :param midi_path: Path to the original MIDI file.
    :param instrument_map: Dictionary mapping track indices to instrument program numbers.
    :return: A modified MIDI file object.
    """
    midi = MidiFile(midi_path)
    for i, track in enumerate(midi.tracks):
        if i in instrument_map:
            #change the number in this list to change instrument
            program = instrument_map[56]
            #the number behind "insert" is the number of notes that ignored the instrument changes
            track.insert(0, Message('program_change', program=program, time=0))
    return midi


if __name__ == "__main__":
    # Path to your SoundFont file
    soundfont_path = "FluidR3_GM.sf2"  

    # Initialize FluidSynth
    fs = FluidSynth(soundfont_path, gain = 5.0)

    # Path to your MIDI file and desired output WAV file
    midi_file = "./outputs/recorded.mid"  # Input MIDI file
    output_wav = "output.wav"  # Output WAV file

    # Instrument map: {track_index: instrument_program}
    instrument_map = {
        0: 0,   # Grand Piano
        4: 4,   # Electric Piano 1
        13: 13, # Xylophone
        14: 14, # Tubular Bells
        16: 16, # Drawbar Organ
        18: 18, # Rock Organ
        19: 19, # Church Organ
        22: 22, # Harmonica
        25: 25, # Acoustic Guitar (steel)
        27: 27, # Electric Guitar (clean)
        29: 29, # Overdriven Guitar
        31: 31, # Guitar Harmonics
        33: 33, # Finger Bass
        34: 34, # Picked Bass
        35: 35, # Fretless Bass
        36: 36, # Slap Bass 1
        39: 39, # Synth Bass 2
        40: 40, # Violin
        41: 41, # Viola
        42: 42, # Cello
        46: 46, # Orchestral Harp
        49: 49, # String Ensemble 2
        50: 50, # Synth Strings 1
        51: 51, # Synth Strings 2
        52: 52, # Choir Aahs
        53: 53, # Voice Oohs
        54: 54, # Synth Voice
        55: 55, # Orchestra Hit
        56: 56, # Trumpet
        57: 57, # Trombone
        58: 58, # Tuba
        59: 59, # Muted Trumpet
        60: 60, # French Horn
        61: 61, # Brass Section
        62: 62, # Synth Brass 1
        66: 66, # Tenor Sax
        69: 69, # English Horn
        73: 73, # Flute
        74: 74, # Recorder
        125: 125, # Helicopter
        127: 127  # Gunshot
    }


    # Modify MIDI file with new instruments
    modified_midi = set_instrument_for_tracks(midi_file, instrument_map)

    # Save the modified MIDI (optional)
    modified_midi.save("modified.mid")
    # Convert MIDI to WAV
    fs.midi_to_audio("./modified.mid", output_wav)

    print(f"Successfully saved WAV file: {output_wav}")

# instrument_map = {
#         0: 0,   # Grand Piano
#         1: 1,   # Bright Piano
#         2: 2,   # Electric Grand Piano
#         3: 3,   # Honky-tonk Piano
#         4: 4,   # Electric Piano 1
#         5: 5,   # Electric Piano 2
#         6: 6,   # Harpsichord
#         7: 7,   # Clavi
#         8: 8,   # Celesta
#         9: 9,   # Glockenspiel
#         10: 10, # Music Box
#         11: 11, # Vibraphone
#         12: 12, # Marimba
#         13: 13, # Xylophone
#         14: 14, # Tubular Bells
#         15: 15, # Dulcimer
#         16: 16, # Drawbar Organ
#         17: 17, # Percussive Organ
#         18: 18, # Rock Organ
#         19: 19, # Church Organ
#         20: 20, # Reed Organ
#         21: 21, # Accordion
#         22: 22, # Harmonica
#         23: 23, # Tango Accordion
#         24: 24, # Acoustic Guitar (nylon)
#         25: 25, # Acoustic Guitar (steel)
#         26: 26, # Electric Guitar (jazz)
#         27: 27, # Electric Guitar (clean)
#         28: 28, # Electric Guitar (muted)
#         29: 29, # Overdriven Guitar
#         30: 30, # Distortion Guitar
#         31: 31, # Guitar Harmonics
#         32: 32, # Acoustic Bass
#         33: 33, # Finger Bass
#         34: 34, # Picked Bass
#         35: 35, # Fretless Bass
#         36: 36, # Slap Bass 1
#         37: 37, # Slap Bass 2
#         38: 38, # Synth Bass 1
#         39: 39, # Synth Bass 2
#         40: 40, # Violin
#         41: 41, # Viola
#         42: 42, # Cello
#         43: 43, # Contrabass
#         44: 44, # Tremolo Strings
#         45: 45, # Pizzicato Strings
#         46: 46, # Orchestral Harp
#         47: 47, # Timpani
#         48: 48, # String Ensemble 1
#         49: 49, # String Ensemble 2
#         50: 50, # Synth Strings 1
#         51: 51, # Synth Strings 2
#         52: 52, # Choir Aahs
#         53: 53, # Voice Oohs
#         54: 54, # Synth Voice
#         55: 55, # Orchestra Hit
#         56: 56, # Trumpet
#         57: 57, # Trombone
#         58: 58, # Tuba
#         59: 59, # Muted Trumpet
#         60: 60, # French Horn
#         61: 61, # Brass Section
#         62: 62, # Synth Brass 1
#         63: 63, # Synth Brass 2
#         64: 64, # Soprano Sax
#         65: 65, # Alto Sax
#         66: 66, # Tenor Sax
#         67: 67, # Baritone Sax
#         68: 68, # Oboe
#         69: 69, # English Horn
#         70: 70, # Bassoon
#         71: 71, # Clarinet
#         72: 72, # Piccolo
#         73: 73, # Flute
#         74: 74, # Recorder
#         75: 75, # Pan Flute
#         76: 76, # Blown Bottle
#         77: 77, # Shakuhachi
#         78: 78, # Whistle
#         79: 79, # Ocarina
#         80: 80, # Lead 1 (square)
#         81: 81, # Lead 2 (sawtooth)
#         82: 82, # Lead 3 (calliope)
#         83: 83, # Lead 4 (chiff)
#         84: 84, # Lead 5 (charang)
#         85: 85, # Lead 6 (voice)
#         86: 86, # Lead 7 (fifths)
#         87: 87, # Lead 8 (bass + lead)
#         88: 88, # Pad 1 (new age)
#         89: 89, # Pad 2 (warm)
#         90: 90, # Pad 3 (polysynth)
#         91: 91, # Pad 4 (choir)
#         92: 92, # Pad 5 (bowed)
#         93: 93, # Pad 6 (metallic)
#         94: 94, # Pad 7 (halo)
#         95: 95, # Pad 8 (sweep)
#         96: 96, # FX 1 (rain)
#         97: 97, # FX 2 (soundtrack)
#         98: 98, # FX 3 (crystal)
#         99: 99, # FX 4 (atmosphere)
#         100: 100, # FX 5 (brightness)
#         101: 101, # FX 6 (goblins)
#         102: 102, # FX 7 (echoes)
#         103: 103, # FX 8 (sci-fi)
#         104: 104, # Sitar
#         105: 105, # Banjo
#         106: 106, # Shamisen
#         107: 107, # Koto
#         108: 108, # Kalimba
#         109: 109, # Bagpipe
#         110: 110, # Fiddle
#         111: 111, # Shanai
#         112: 112, # Tinkle Bell
#         113: 113, # Agogo
#         114: 114, # Steel Drums
#         115: 115, # Woodblock
#         116: 116, # Taiko Drum
#         117: 117, # Melodic Tom
#         118: 118, # Synth Drum
#         119: 119, # Reverse Cymbal
#         120: 120, # Guitar Fret Noise
#         121: 121, # Breath Noise
#         122: 122, # Seashore
#         123: 123, # Bird Tweet
#         124: 124, # Telephone Ring
#         125: 125, # Helicopter
#         126: 126, # Applause
#         127: 127  # Gunshot
#     }