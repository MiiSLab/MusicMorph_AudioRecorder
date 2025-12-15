import pygame.midi
from midi2audio import FluidSynth
import fluidsynth
from mido import Message, MidiFile, MidiTrack

def real_time_midi_playback_and_record(output_file, soundfont_path, instrument_number, gain, output_wav_path):
    # Initialize Pygame MIDI
    pygame.midi.init()

    # Automatically detect the first available MIDI input device
    available_ports = [i for i in range(pygame.midi.get_count()) if pygame.midi.get_device_info(i)[2] == 1]
    if not available_ports:
        print("No MIDI input devices found.")
        pygame.midi.quit()
        return

    input_id = available_ports[0]  # Automatically use the first available MIDI input port
    device_info = pygame.midi.get_device_info(input_id)
    print(f"Using MIDI Input Device: {device_info[1].decode()} (ID: {input_id})")

    midi_input = pygame.midi.Input(input_id)

    # Create a new MIDI file and track
    midi_file = MidiFile()
    track = MidiTrack()
    midi_file.tracks.append(track)

    # Initialize FluidSynth for real-time playback
    fs = fluidsynth.Synth(gain, samplerate=44100)
    fs.start(driver="dsound")  # Use the DirectSound driver
    sfid = fs.sfload(soundfont_path)
    fs.program_select(0, sfid, 0, instrument_number)

    print("Recording and playing MIDI... Press Ctrl+C to stop.")

    # Initialize timing
    start_time = pygame.midi.time()
    last_time = start_time

    try:
        while True:
            if midi_input.poll():
                # Read MIDI input events
                midi_events = midi_input.read(10)
                for event in midi_events:
                    data = event[0]  # MIDI message data
                    timestamp = event[1]  # Timestamp in milliseconds

                    # Calculate time delta
                    current_time = pygame.midi.time()
                    
                    time_delta = current_time - last_time
                    last_time = current_time

                    # Convert MIDI data to a Mido Message
                    message = Message.from_bytes(data[:3])  # Use first 3 bytes for the MIDI message
                    print(f"Source: {device_info[1].decode()}, Message: {message.type}, Channel: {message.channel}, Note: {message.note}, Velocity: {message.velocity}, Time Delta: {time_delta}, Time: {current_time}")

                    # Append the message with time delta to the track
                    track.append(message.copy(time=time_delta))

                    # Real-time playback
                    if message.type == "note_on" and message.velocity > 0:
                        fs.noteon(0, message.note, message.velocity)
                    elif message.type == "note_off" or (message.type == "note_on" and message.velocity == 0):
                        fs.noteoff(0, message.note)
    except KeyboardInterrupt:
        print("Recording stopped.")
    finally:
        # Save the MIDI file
        midi_file.save(output_file)
        print(f"MIDI saved to {output_file}")

        # save to wav
        playback2wav(output_file, gain, output_wav_path, instrument_number)

        # Cleanup
        midi_input.close()
        pygame.midi.quit()
        fs.delete()

def playback2wav(original_midi_path, gain, output_wav_path, instrument_num):
    """
    Modifies a MIDI file to assign specific instruments to tracks.

    :param midi_path: Path to the original MIDI file.
    :param instrument_map: Dictionary mapping track indices to instrument program numbers.
    :return: A modified MIDI file object.
    """
    midi = MidiFile(original_midi_path)
    for track in midi.tracks:
        program = instrument_num
        #the number behind "insert" is the number of notes that ignored the instrument changes
        track.insert(0, Message('program_change', program=program, time=0))

    midi.save(original_midi_path)
    fss = FluidSynth(gain=gain*0.3, sound_font=soundfont_path, sample_rate=44100)
    fss.midi_to_audio(original_midi_path, output_wav_path)

if __name__ == "__main__":
    instrument = 1 #piano
    gain = 1.5
    soundfont_path = "./soundfonts/FluidR3_GM.sf2"  # Path to your SoundFont file
    midi_path = "./outputs/modified.mid"  # Path to save the MIDI file
    wav_path = "./outputs/output.wav" 
    real_time_midi_playback_and_record(midi_path, soundfont_path, instrument, gain, wav_path)
