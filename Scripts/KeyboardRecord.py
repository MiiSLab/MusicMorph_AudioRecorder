import sys
import os
import mido
import pygame.midi
import fluidsynth
import time
import keyboard  # Library for detecting key presses
from mido import Message, MidiFile, MidiTrack, open_input
from midi2audio import FluidSynth
from MIDIDevice import MIDIDevice
from pydub import AudioSegment  
from pydub.playback import play


# Global switches
is_recording = False  # Controls start/pause of recording
end_recording = False  # Ends the recording completely when "Z" is pressed
last_resume_time = 0  
total_paused_time = 0  
unpaused1 = False
unpaused2 = False
mido_ports = []
midi_devicez = []
pygame_ports = []
soundfont_paths = ["./soundfonts/FluidR3_GM.sf2", "./soundfonts/PNSDrumKit.SF2"]
# Detect available MIDI input devices
def detect_midi_inputs():
    pygame.midi.init()
    pygame_ports = [i for i in range(pygame.midi.get_count()) if pygame.midi.get_device_info(i)[2] == 1]
    mido_ports = [port for port in mido.get_input_names()]
    pygame.midi.quit()
    return mido_ports, pygame_ports

def single_device_midi(output_file, gain, output_wav_path, midi_devices):
    global is_recording, end_recording, last_resume_time, total_paused_time, unpaused1
    pygame.midi.init()

    available_ports = [i for i in range(pygame.midi.get_count()) if pygame.midi.get_device_info(i)[2] == 1]
    if not available_ports:
        print("No MIDI input devices found.")
        pygame.midi.quit()
        return

    input_id = midi_devicez[0].input_id
    device_info = pygame.midi.get_device_info(input_id)
    print(f"Using Single MIDI Input Device: {device_info[1].decode()} (ID: {input_id})")

    midi_input = pygame.midi.Input(input_id)

    midi_file = MidiFile()
    track = MidiTrack()
    midi_file.tracks.append(track)

    fs = fluidsynth.Synth(gain, samplerate=44100)
    fs.start(driver="dsound")
    sfid = fs.sfload(midi_devicez[0].soundfont_path)
    fs.program_select(0, sfid, 0, midi_devicez[0].instrument_number)

    print("Press 'A' to toggle recording. Press 'Z' to stop completely.")

    start_time = pygame.midi.time()
    last_time = start_time

    # # ✅ Proper Key Listeners for "A" and "Z"
    # keyboard.add_hotkey("a", toggle_recording)  # Toggle recording when "A" is pressed
    # keyboard.add_hotkey("z", stop_recording)

    try:
        while True:
            if end_recording:  # Stops recording when "Z" is pressed
                print("Recording Ended by 'Z' Key Press.")
                break

            if is_recording:  # Only record when `is_recording` is True
                if midi_input.poll():
                    midi_events = midi_input.read(10)
                    for event in midi_events:
                        data = event[0]
                        current_time = pygame.midi.time()

                        if unpaused1:
                            time_delta = max(0, (current_time - last_time) - total_paused_time)
                            unpaused1 = not unpaused1
                        elif not unpaused1:
                            time_delta = current_time - last_time

                        last_time = current_time

                        message = Message.from_bytes(data[:3])
                        pass_playback_info(midi_devices[0].device_name, message.type, time_delta, message.note, message.velocity)
                        # print(f"Recording | {message.type}, Note: {message.note}, Velocity: {message.velocity}, Time Delta: {time_delta}")

                        track.append(message.copy(time=time_delta))

                        if message.type == "note_on" and message.velocity > 0:
                            fs.noteon(0, message.note, message.velocity)
                        elif message.type == "note_off" or (message.type == "note_on" and message.velocity == 0):
                            fs.noteoff(0, message.note)
            else:
                time.sleep(0.1)  # Pause briefly when not recording

    except KeyboardInterrupt:
        print("Recording stopped manually.")
    finally:
        midi_file.save(output_file)
        print(f"MIDI saved to {output_file}")
        playback2wav(output_file, gain, output_wav_path, midi_devicez[0].instrument_number, midi_devicez[0].soundfont_path)

        midi_input.close()
        pygame.midi.quit()
        fs.delete()

# Multi-device MIDI recording
def multi_device_midi(output_file_1, output_file_2, gain, output_wav_path, midi_devices):
    global is_recording, end_recording, last_resume_time, total_paused_time, unpaused1 ,unpaused2
    pygame.midi.init() #initialize Pygame, although in multi mode, pygame is only used for time calculation, not midi processing
    
    input_port_1 = open_input(midi_devices[0].device_name)
    input_port_2 = open_input(midi_devices[1].device_name)
    print(f"Multi Mode | Using MIDI Input Device 1: {midi_devices[0].device_name}")
    print(f"Multi Mode | Using MIDI Input Device 2: {midi_devices[1].device_name}")

    midi_file_1 = MidiFile()
    midi_file_2 = MidiFile()
    track_1 = MidiTrack()
    track_2 = MidiTrack()
    midi_file_1.tracks.append(track_1)
    midi_file_2.tracks.append(track_2)

    # Initialize Fluidsynth for real-time playback
    fs1 = fluidsynth.Synth(gain=gain, samplerate=44100)
    fs2 = fluidsynth.Synth(gain=gain*3, samplerate=44100)
    fs1.start(driver="dsound")
    fs2.start(driver="dsound")

    sfid1 = fs1.sfload(soundfont_paths[0])  # SoundFont for Device 1
    sfid2 = fs2.sfload(soundfont_paths[1])  # SoundFont for Device 2

    fs1.program_select(0, sfid1, 0, midi_devices[0].instrument_number)
    fs2.program_select(1, sfid2, 0, midi_devices[1].instrument_number)
    print("MultiMode, Press 'A' to toggle recording. Press 'Z' to stop completely.")

    start_time = pygame.midi.time()
    last_time_1 = start_time
    last_time_2 = start_time

    # keyboard.add_hotkey("a", toggle_recording)  # Toggle recording when "A" is pressed
    # keyboard.add_hotkey("z", stop_recording)

    try:
        while True:
            if end_recording:  # Stops recording when "Z" is pressed
                print("Recording Ended by 'Z' Key Press.")
                break

            if is_recording:  # Only record when `is_recording` is True
                for msg in input_port_1.iter_pending():
                    if msg.type in ("note_on", "note_off"):
                        current_time = pygame.midi.time()
                        if unpaused1:
                            time_delta = max(0, (current_time - last_time_1) - total_paused_time)
                            unpaused1 = not unpaused1
                        elif not unpaused1:
                            time_delta = current_time - last_time_1
                        last_time_1 = current_time
                        track_1.append(msg.copy(time=time_delta))
                        # print(f"{midi_devices[0].device_name} | {msg.type}, Note: {msg.note}, Velocity: {msg.velocity}, Time Delta: {time_delta}")
                        # Send notes to Fluidsynth for playback
                        if msg.type == "note_on" and msg.velocity > 0:
                            fs1.noteon(0, msg.note, msg.velocity)
                        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                            fs1.noteoff(0, msg.note)
                        pass_playback_info(midi_devices[0].device_name, msg.type, time_delta, msg.note, msg.velocity)

                for msg in input_port_2.iter_pending():
                    if msg.type in ("note_on", "note_off"):
                        current_time = pygame.midi.time()
                        if unpaused2:
                            time_delta = max(0, (current_time - last_time_2) - total_paused_time)
                            unpaused2 = not unpaused2
                        elif not unpaused2:
                            time_delta = current_time - last_time_2
                        last_time_2 = current_time
                        track_2.append(msg.copy(time=time_delta))
                        # print(f"{midi_devices[1].device_name} | {msg.type}, Note: {msg.note}, Velocity: {msg.velocity}, Time Delta: {time_delta}")
                        # Send notes to Fluidsynth for playback
                        if msg.type == "note_on" and msg.velocity > 0:
                            fs2.noteon(1, msg.note, msg.velocity)
                        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                            fs2.noteoff(1, msg.note)
                        pass_playback_info(midi_devices[1].device_name, msg.type, time_delta, msg.note, msg.velocity)

    except KeyboardInterrupt: 
        print("Recording stopped via keyboard interruption.")
    finally:
        midi_file_1.save(output_file_1)
        midi_file_2.save(output_file_2)
        print(f"MIDI 1 saved to {output_file_1}")
        print(f"MIDI 2 saved to {output_file_2}")

        # Convert each MIDI file separately to WAV
        playback2wav(output_file_1, gain, output_wav_path.replace(".wav", "_device1.wav"), midi_devices[0].instrument_number, midi_devices[0].soundfont_path)
        playback2wav(output_file_2, gain, output_wav_path.replace(".wav", "_device2.wav"), midi_devices[0].instrument_number, midi_devices[1].soundfont_path)
        
        combine_wav_files(output_wav_path.replace(".wav", "_device1.wav"), output_wav_path.replace(".wav", "_device2.wav"), output_wav_path)
        
        input_port_1.close()
        input_port_2.close()

# Convert MIDI to WAV
def playback2wav(midi_path, gain, output_wav_path, instrument_number, soundfont_path):
    midi = MidiFile(midi_path)
    if instrument_number != 0:
        midi.tracks[0].insert(0, Message('program_change', program=instrument_number, time=0))

        # Save the modified MIDI file
        midi.save(midi_path)
        print(f"Modified MIDI with program change saved: {midi_path}")

    # Convert modified MIDI to WAV
    fss = FluidSynth(gain=gain * 0.3, sound_font=soundfont_path, sample_rate=44100)
    fss.midi_to_audio(midi_path, output_wav_path)
    print(f"Generated WAV: {output_wav_path}")

def combine_wav_files(wav_1_path, wav_2_path, output_wav_path):
    sound1 = AudioSegment.from_wav(wav_1_path)
    sound2 = AudioSegment.from_wav(wav_2_path)

    # Ensure both audio tracks are the same length
    max_length = max(len(sound1), len(sound2))
    sound1 = sound1 + AudioSegment.silent(duration=max_length - len(sound1))
    sound2 = sound2 + AudioSegment.silent(duration=max_length - len(sound2))

    # Mix the two tracks
    combined = sound1.overlay(sound2)

    # Export to final output file
    combined.export(output_wav_path, format="wav")
    print(f"Final combined WAV file saved to: {output_wav_path}")

def pass_playback_info(Name, Message, Duration, Note, Velocity):
    Info = []
    Info.append(Name)
    Info.append(Message)
    Info.append(Duration)
    Info.append(Note)
    Info.append(Velocity)
    print(f"info: {Info}")
    return Info

# Toggle recording function (Start/Pause)
def pause_recording():
    """Pauses the recording and adjusts timing."""
    global is_recording, last_resume_time, total_paused_time, unpaused1, unpaused2

    
    if is_recording:
        is_recording = not is_recording
        # Resume: Record the time when we resume
        last_resume_time = pygame.midi.time()
        print(f"🎤 Recording: {is_recording}")
        # print(f"⏯️ last Resume Time: {last_resume_time} ms; ⏯️ Total Paused Time: {total_paused_time} ms")

def resume_recording():
    """Resumes the recording and adjusts timing."""
    global is_recording, last_resume_time, total_paused_time, unpaused1, unpaused2
    
    if not is_recording and last_resume_time > 0:
        is_recording = not is_recording
        # Pause: Calculate and store the total pause duration
        total_paused_time = pygame.midi.time() - last_resume_time
        unpaused1 = not unpaused1
        unpaused2 = not unpaused2
        print(f"🎤 Recording: {is_recording}")
    else: print("Start recording first!")
        # print(f"⏯️ last Resume Time: {last_resume_time} ms; ⏯️ Total Paused Time: {total_paused_time} ms")

def start_recording():
    global is_recording
    if not is_recording and last_resume_time > 0:
        pass
    else:
        is_recording = True

def stop_recording():
    global end_recording
    end_recording = True

def create_midi_device(mido_ports, soundfont_paths, midi_devices):
    print("\n--- Create a New MIDI Device ---")
    
    device_name = int(input("🎵 Device Name? "))
    soundfont_path = int(input("🎼 SoundFont Path? (e.g., ./soundfonts/FluidR3_GM.sf2) "))
    instrument_number = int(input("🎹 Instrument Number? (0-127) "))
    
    # Create and store the MIDI device
    midi_device = MIDIDevice(device_name=mido_ports[device_name], soundfont_path=soundfont_paths[soundfont_path], instrument_number=instrument_number, input_id=len(midi_devicez)+1)
    midi_devices.append(midi_device)

    print(f"✅ Created MIDI Device: {device_name} with Instrument {instrument_number} and SoundFont {soundfont_path} and Input ID {midi_devices[len(midi_devices)-1].input_id}")
    midi_device.print_stuff()  # Print the device details
    return midi_devices

# import os
# import tempfile
# from pydub import AudioSegment
# from pydub.playback import play

# # Force pydub to use a custom temp directory
# custom_temp_dir = os.path.join(os.getcwd(), "temp_audio")
# os.makedirs(custom_temp_dir, exist_ok=True)  # Ensure the directory exists
# tempfile.tempdir = custom_temp_dir  # Set pydub's temp directory

# def play_wav():
#     wav_path = "./outputs/output.wav"
#     audio = AudioSegment.from_wav(wav_path)
    
#     # Save the temp file in our controlled temp directory
#     temp_wav_path = os.path.join(custom_temp_dir, "temp_playback.wav")
    
#     audio.export(temp_wav_path, format="wav")  # Export manually
#     play(AudioSegment.from_wav(temp_wav_path))  # Play the exported file

#     os.remove(temp_wav_path)  # Cleanup after playing

if __name__ == "__main__":
    mido_ports, pygame_ports = detect_midi_inputs()
    # mido ports = name of midi device; pygame ports = input id (start from 1)

    midi_devicez = []

    # Create Midi Devices Automatically 
    '''
    midi_devices = []
    for i, port in enumerate(mido_ports):
        device_name = f"Device{i+1}"
        midi_device = MIDIDevice(device_name=mido_ports[i], soundfont_path=soundfont_paths[i], instrument_number=0, input_id=pygame_ports[i])
        midi_devices.append(midi_device)
        print(f"Created {device_name} with port {port}")
        midi_device.print_stuff()
    '''

    gain = 3.0
    midi_path_1 = "./outputs/recorded_device1.mid"
    midi_path_2 = "./outputs/recorded_device2.mid"
    wav_path = "./outputs/output.wav"
    number_of_device = len(midi_devicez)
    keyboard.add_hotkey("c", lambda: create_midi_device(mido_ports, soundfont_paths, midi_devicez))
    keyboard.add_hotkey("a", start_recording)  # Toggle recording when "A" is pressed
    keyboard.add_hotkey("s", pause_recording)
    keyboard.add_hotkey("r", resume_recording)
    keyboard.add_hotkey("z", stop_recording)
    # keyboard.add_hotkey("p", play_wav)

    # Start recording session, toggle using "A", stop with "Z"
    while end_recording == False:
        if is_recording:
            number_of_device = len(midi_devicez)
            if(number_of_device > 1):
                mode = "Multiple"
                multi_device_midi(midi_path_1, midi_path_2, gain, wav_path, midi_devicez)
            elif(number_of_device == 1):
                mode = "Single"
                single_device_midi(midi_path_1, gain, wav_path, midi_devicez)
            elif(number_of_device == 0):
                print("No MIDI device detected")
                break
        if end_recording:
            break