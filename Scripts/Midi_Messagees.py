import mido

# Load the MIDI file
midi_file = mido.MidiFile('./modified.mid')

# Ensure all messages are valid
for track in midi_file.tracks:
    for msg in track:
        print(msg)

