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
import wave
import pyaudio
import tempfile
# Global switches
is_recording = False  # Controls start/pause of recording
start_record = False
end_recording = False  # Ends the recording completely when "Z" is pressed
last_resume_time = 0  
total_paused_time = 0  
unpaused1 = False
unpaused2 = False
mido_ports = []
midi_devicez = []
pygame_ports = []
soundfont_paths = ["./soundfonts/FluidR3_GM.sf2", "./soundfonts/PNSDrumKit.SF2"]
gain = 3.0
midi_path_1 = "C:\\Users\\miisl\\Desktop\\MusicMorph\\MusicMorph_Demo\\AudioRecording\\outputs\\recorded_device1.mid"
midi_path_2 = "C:\\Users\\miisl\\Desktop\\MusicMorph\\MusicMorph_Demo\\AudioRecording\\outputs\\recorded_device2.mid"
wav_path = "C:\\Users\\miisl\\Desktop\\MusicMorph\\MusicMorph_Demo\\AudioRecording\\outputs\\output.wav"

# Define the minimum recording length in milliseconds (15 seconds)
MIN_RECORDING_LENGTH_MS = 16000


import threading

# Add these global variables
recording_thread = None
recording_active = False

def initialize():
    """Initialize the MIDI environment"""
    global mido_ports, pygame_ports
    
    # Initialize pygame
    if not pygame.midi.get_init():
        pygame.midi.init()
    
    # Detect MIDI devices
    mido_ports, pygame_ports = detect_midi_inputs()
    print(f"Available MIDI Input Devices: {mido_ports}")
    
    # Ensure output directories exist
    os.makedirs("C:\\Users\\miisl\\Desktop\\MusicMorph\\MusicMorph_Demo\\AudioRecording\\outputs", exist_ok=True)
    
    return mido_ports, pygame_ports

def single_device_midi_threaded(output_file, gain, output_wav_path, midi_devices, emit_callback=None):
    """Non-blocking version of single_device_midi that checks end_recording flag"""
    global is_recording, end_recording, last_resume_time, total_paused_time, unpaused1
    
    try:
        pygame.midi.init()

        available_ports = [i for i in range(pygame.midi.get_count()) if pygame.midi.get_device_info(i)[2] == 1]
        if not available_ports:
            print("No MIDI input devices found.")
            pygame.midi.quit()
            return

        input_id = midi_devices[0].input_id
        device_info = pygame.midi.get_device_info(input_id)
        print(f"Using Single MIDI Input Device: {device_info[1].decode()} (ID: {input_id})")

        midi_input = pygame.midi.Input(input_id)

        midi_file = MidiFile()
        track = MidiTrack()
        midi_file.tracks.append(track)

        fs = fluidsynth.Synth(gain, samplerate=44100)
        fs.start(driver="dsound")
        sfid = fs.sfload(midi_devices[0].soundfont_path)
        fs.program_select(0, sfid, 0, midi_devices[0].instrument_number)

        print("Recording started in single-device mode")

        start_time = pygame.midi.time()
        last_time = start_time

        # Add a timeout mechanism to check end_recording flag regularly
        max_idle_time = 0.1  # Check every 100ms
        
        while not end_recording:
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
                        pass_playback_info(midi_devices[0].device_name, message.type, time_delta, message.note, message.velocity, emit_callback)

                        track.append(message.copy(time=time_delta))

                        if message.type == "note_on" and message.velocity > 0:
                            fs.noteon(0, message.note, message.velocity)
                        elif message.type == "note_off" or (message.type == "note_on" and message.velocity == 0):
                            fs.noteoff(0, message.note)
                else:
                    # No MIDI events, sleep briefly to avoid CPU hogging
                    time.sleep(max_idle_time)
            else:
                time.sleep(max_idle_time)  # Pause briefly when not recording
                
            # Check if we should exit
            if end_recording:
                print("Detected end_recording flag in single_device_midi")
                break

    except Exception as e:
        print(f"Error in single device recording: {str(e)}")
    finally:
        try:
            print(f"[debug] output_file:",output_file)
            midi_file.save(output_file)
            print(f"MIDI saved to {output_file}")

            print(f"[debug] output_wav_path:",output_wav_path)
            playback2wav(output_file, gain, output_wav_path, midi_devices[0].instrument_number, midi_devices[0].soundfont_path)
            print(f"[debug] playback2wav successed!")
            
            # Ensure the WAV file is at least 15 seconds long
            extend_wav_to_minimum_length(output_wav_path, MIN_RECORDING_LENGTH_MS)
        except Exception as e:
            print(f"Error saving MIDI or converting to WAV: {str(e)}")
        
        try:
            midi_input.close()
            pygame.midi.quit()
            fs.delete()
        except:
            pass

def multi_device_midi_threaded(output_file_1, output_file_2, gain, output_wav_path, midi_devices, socketio=None):
    """Non-blocking version of multi_device_midi that checks end_recording flag"""
    global is_recording, end_recording, last_resume_time, total_paused_time, unpaused1, unpaused2
    
    try:
        pygame.midi.init()
        
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

        sfid1 = fs1.sfload(soundfont_paths[0])
        sfid2 = fs2.sfload(soundfont_paths[1])

        fs1.program_select(0, sfid1, 0, midi_devices[0].instrument_number)
        fs2.program_select(1, sfid2, 0, midi_devices[1].instrument_number)
        print("Recording started in multi-device mode")

        start_time = pygame.midi.time()
        last_time_1 = start_time
        last_time_2 = start_time

        # Add a timeout mechanism to check end_recording flag regularly
        max_idle_time = 0.1  # Check every 100ms
        
        while not end_recording:
            has_messages = False
            
            if is_recording:  # Only record when `is_recording` is True
                # Process device 1
                for msg in input_port_1.iter_pending():
                    has_messages = True
                    if msg.type in ("note_on", "note_off"):
                        current_time = pygame.midi.time()
                        if unpaused1:
                            time_delta = max(0, (current_time - last_time_1) - total_paused_time)
                            unpaused1 = not unpaused1
                        elif not unpaused1:
                            time_delta = current_time - last_time_1
                        last_time_1 = current_time
                        track_1.append(msg.copy(time=time_delta))
                        
                        # Send notes to Fluidsynth for playback
                        if msg.type == "note_on" and msg.velocity > 0:
                            fs1.noteon(0, msg.note, msg.velocity)
                        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                            fs1.noteoff(0, msg.note)
                        pass_playback_info(midi_devices[0].device_name, msg.type, time_delta, msg.note, msg.velocity, socketio)

                # Process device 2
                for msg in input_port_2.iter_pending():
                    has_messages = True
                    if msg.type in ("note_on", "note_off"):
                        current_time = pygame.midi.time()
                        if unpaused2:
                            time_delta = max(0, (current_time - last_time_2) - total_paused_time)
                            unpaused2 = not unpaused2
                        elif not unpaused2:
                            time_delta = current_time - last_time_2
                        last_time_2 = current_time
                        track_2.append(msg.copy(time=time_delta))
                        
                        # Send notes to Fluidsynth for playback
                        if msg.type == "note_on" and msg.velocity > 0:
                            fs2.noteon(1, msg.note, msg.velocity)
                        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                            fs2.noteoff(1, msg.note)
                        # Send MIDI playback info to frontend via socket
                        pass_playback_info(midi_devices[1].device_name, msg.type, time_delta, msg.note, msg.velocity, socketio)
                
                # If no messages were processed, sleep briefly
                if not has_messages:
                    time.sleep(max_idle_time)
            else:
                time.sleep(max_idle_time)  # Pause briefly when not recording
                
            # Check if we should exit
            if end_recording:
                print("Detected end_recording flag in multi_device_midi")
                break

    except Exception as e:
        print(f"Error in multi-device recording: {str(e)}")
    finally:
        try:
            midi_file_1.save(output_file_1)
            midi_file_2.save(output_file_2)
            print(f"MIDI 1 saved to {output_file_1}")
            print(f"MIDI 2 saved to {output_file_2}")

            # Convert each MIDI file separately to WAV
            device1_wav = output_wav_path.replace(".wav", "_device1.wav")
            device2_wav = output_wav_path.replace(".wav", "_device2.wav")
            
            playback2wav(output_file_1, gain, device1_wav, 
                        midi_devices[0].instrument_number, midi_devices[0].soundfont_path)
            playback2wav(output_file_2, gain, device2_wav, 
                        midi_devices[1].instrument_number, midi_devices[1].soundfont_path)
            
            # Ensure each individual device WAV is at least 15 seconds long
            extend_wav_to_minimum_length(device1_wav, MIN_RECORDING_LENGTH_MS)
            extend_wav_to_minimum_length(device2_wav, MIN_RECORDING_LENGTH_MS)
            
            # Combine the WAV files (they should now be the same length)
            combine_wav_files(device1_wav, device2_wav, output_wav_path)
        except Exception as e:
            print(f"Error saving MIDI or converting to WAV: {str(e)}")
        
        try:
            input_port_1.close()
            input_port_2.close()
        except:
            pass

# New function to extend WAV files to minimum length
def extend_wav_to_minimum_length(wav_path, min_length_ms):
    """
    Extends a WAV file with silence if it's shorter than the minimum length.
    
    Args:
        wav_path: Path to the WAV file
        min_length_ms: Minimum length in milliseconds
    """
    try:
        # Load the audio file
        audio = AudioSegment.from_wav(wav_path)
        
        # Get current length in milliseconds
        current_length_ms = len(audio)
        
        # Check if the audio is shorter than the minimum length
        if current_length_ms < min_length_ms:
            # Calculate how much silence to add
            silence_duration_ms = min_length_ms - current_length_ms
            print(f"Extending {wav_path} with {silence_duration_ms}ms of silence to reach {min_length_ms}ms")
            
            # Create silence segment
            silence = AudioSegment.silent(duration=silence_duration_ms)
            
            # Append silence to the audio
            extended_audio = audio + silence
            
            # Export the extended audio back to the same file
            extended_audio.export(wav_path, format="wav")
            print(f"Successfully extended {wav_path} to {min_length_ms}ms")
        else:
            print(f"No extension needed for {wav_path}, already {current_length_ms}ms (minimum: {min_length_ms}ms)")
            
    except Exception as e:
        print(f"Error extending WAV file {wav_path}: {str(e)}")

# Detect available MIDI input devices
def detect_midi_inputs():
    global mido_ports, pygame_ports
    pygame.midi.init()
    pygame_ports = [i for i in range(pygame.midi.get_count()) if pygame.midi.get_device_info(i)[2] == 1]
    mido_ports = [port for port in mido.get_input_names()]
    # print("available devices: ", mido_ports)
    pygame.midi.quit()
    return mido_ports, pygame_ports

def single_device_midi(output_file, gain, output_wav_path, midi_devices, socketio = None):
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
                        pass_playback_info(midi_devices[0].device_name, message.type, time_delta, message.note, message.velocity, socketio = None)
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
        
        # Ensure the WAV file is at least 15 seconds long
        extend_wav_to_minimum_length(output_wav_path, MIN_RECORDING_LENGTH_MS)

        midi_input.close()
        pygame.midi.quit()
        fs.delete()

# Multi-device MIDI recording
def multi_device_midi(output_file_1, output_file_2, gain, output_wav_path, midi_devices,socket):
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
        print("Recording stopped.")
    finally:
        midi_file_1.save(output_file_1)
        midi_file_2.save(output_file_2)
        print(f"MIDI 1 saved to {output_file_1}")
        print(f"MIDI 2 saved to {output_file_2}")

        # Convert each MIDI file separately to WAV
        device1_wav = output_wav_path.replace(".wav", "_device1.wav")
        device2_wav = output_wav_path.replace(".wav", "_device2.wav")
        
        playback2wav(output_file_1, gain, device1_wav, midi_devices[0].instrument_number, midi_devices[0].soundfont_path)
        playback2wav(output_file_2, gain, device2_wav, midi_devices[0].instrument_number, midi_devices[1].soundfont_path)
        
        # Ensure each individual device WAV is at least 15 seconds long
        extend_wav_to_minimum_length(device1_wav, MIN_RECORDING_LENGTH_MS)
        extend_wav_to_minimum_length(device2_wav, MIN_RECORDING_LENGTH_MS)
        
        # Combine the WAV files
        combine_wav_files(device1_wav, device2_wav, output_wav_path)
        
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
    print("你好")
    print("gain",gain)
    # Convert modified MIDI to WAV
    fss = FluidSynth(sound_font=soundfont_path, sample_rate=44100)
    # fss = FluidSynth(gain=gain * 0.3, sound_font=soundfont_path, sample_rate=44100)
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

def pass_playback_info(Name, Message, Duration, Note, Velocity, emit_callback=None):
    """
    Process MIDI playback information and optionally emit it through socketio.
    
    Args:
        Name: Device name
        Message: MIDI message type (note_on, note_off)
        Duration: Time delta
        Note: MIDI note number
        Velocity: Note velocity
        emit_callback: Optional callback function to send data back to the server
    """
    Info = []
    Info.append(Name)
    Info.append(Message)
    Info.append(Duration)
    Info.append(Note)
    Info.append(Velocity)
    # print(f"info: {Info}")
    
    # If emit_callback is provided, send the data back to the server
    if emit_callback:
        # Create a structured data object for the frontend
        playback_data = {
            "device_name": Name,
            "message_type": Message,
            "duration": Duration,
            "note": Note,
            "velocity": Velocity
        }
        # Call the callback with the playback data
        emit_callback(playback_data)
    
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

def start_recording(send_recording_status, emit_playback_info=None):
    """Start recording in a separate thread"""
    global is_recording, recording_thread, recording_active, end_recording
    
    # Reset the end_recording flag
    end_recording = False
    
    if recording_active:
        print("Recording is already active")
        return
    
    # Set recording flag
    is_recording = True
    
    # Create and start the recording thread with the callback
    recording_thread = threading.Thread(target=lambda: recording_thread_function(emit_playback_info))
    recording_thread.daemon = True  # Make thread exit when main program exits
    recording_thread.start()
    
    print("Recording started in background thread")

def stop_recording():
    """Stop the recording process"""
    global end_recording, recording_active, is_recording
    
    print("Stopping recording...")
    end_recording = True
    is_recording = False
    
    # Wait for the recording thread to finish (with timeout)
    if recording_thread and recording_thread.is_alive():
        # Don't join here - it could block the socket server
        # Just set the flags and let the thread exit on its own
        pass
        
    print("Recording stop signal sent")

def create_midi_device(added_devices):
    """Create a MIDI device from socket data and add it to midi_devicez"""
    global midi_devicez, mido_ports, pygame_ports, soundfont_paths
    midi_devicez = []
    print(f"\n--- Creating a New MIDI Device from Socket Data ---")
    for device_name, instruments in added_devices.items():
        instrument = instruments[0] if instruments else 'piano'
        print(f"Device Name: {device_name}")
        print(f"Instrument: {instrument}")

        try:
            print(f"Received device_name: {device_name}")
            print(f"Received instrument_name: {instrument}")
            
            # Find the device in mido_ports and get its index
            device_index = -1
            for i, port in enumerate(mido_ports):
                if port == device_name:
                    device_index = i
                    break
            
            if device_index == -1:
                print(f"❌ Error: Device '{device_name}' not found in available MIDI devices")
                return None
            
            # Set input_id based on the device's position in mido_ports
            input_id = pygame_ports[device_index]
            
            # Determine soundfont path and instrument number based on instrument_name
            if instrument.lower() == "drums":
                soundfont_path = soundfont_paths[1]  # PNSDrumKit.SF2
                instrument_number = 0
            else:
                soundfont_path = soundfont_paths[0]  # FluidR3_GM.sf2
                
                # Map instrument names to General MIDI program numbers
                # This is a basic mapping - you may need to expand it
                instrument_map = {
                    "piano": 0,
                    "music box": 10,
                    "violin": 40,
                    "a. guitar": 24,
                    "e. guitar": 27,
                    "trumpet": 56,
                    "flute": 73,
                    "gunshot": 127
                }
                # Get instrument number from map or default to piano (0)
                instrument_number = instrument_map.get(instrument.lower(), 0)
            
            # Create the MIDI device
            midi_device = MIDIDevice(
                device_name=device_name,
                soundfont_path=soundfont_path,
                instrument_number=instrument_number,
                input_id=input_id
            )
            
            # Add to the global list
            midi_devicez.append(midi_device)
            print(f"✅ Created MIDI Device: {device_name}")
            print(f"   - Input ID: {input_id}")
            print(f"   - Instrument: {instrument} (number: {instrument_number})")
            print(f"   - SoundFont: {soundfont_path}")
            print(f"midi_devices = {midi_devicez}")

        except Exception as e:
            print(f"❌ Error creating MIDI device: {str(e)}")
            return None

def recording_thread_function(emit_playback_info=None):
    """Function to run in a separate thread for recording"""
    global is_recording, midi_devicez, midi_path_1, midi_path_2, wav_path, gain, end_recording, recording_active
    
    print("Recording thread started")
    recording_active = True
    
    try:
        # Set recording flag
        is_recording = True
        
        number_of_device = len(midi_devicez)
        print(f"Number of devices: {number_of_device}")
        
        if number_of_device > 1:
            print(f"Starting multi-device recording")
            multi_device_midi_threaded(midi_path_1, midi_path_2, gain, wav_path, midi_devicez, emit_playback_info)
        elif number_of_device == 1:
            print(f"Starting single-device recording")
            single_device_midi_threaded(midi_path_1, gain, wav_path, midi_devicez, emit_playback_info)
        else:
            print("No MIDI device detected")
    except Exception as e:
        print(f"Error in recording thread: {str(e)}")
    finally:
        recording_active = False
        print("Recording thread stopped")

def play_wav_file():
    """
    Play a WAV file from the given path using PyAudio with increased volume
    """
    global wav_path
    file_path = wav_path
    try:
        if not os.path.exists(file_path):
            print(f"Error: WAV file not found at {file_path}")
            return
            
        print(f"Playing audio file: {file_path}")
        
        # Load the audio with pydub to adjust volume
        audio = AudioSegment.from_wav(file_path)
        
        # Increase volume by 10dB (adjust this value as needed)
        louder_audio = audio + 11  # +10dB increase
        
        # Create a temporary file with the louder audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_path = temp_file.name
        
        # Export the louder audio to the temporary file
        louder_audio.export(temp_path, format="wav")
        # Open the WAV file
        wf = wave.open(temp_path, 'rb')
        
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        
        # Open a stream
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        
        # Read data in chunks and play
        chunk_size = 1024
        data = wf.readframes(chunk_size)
        
        while data:
            stream.write(data)
            data = wf.readframes(chunk_size)
        
        # Close everything
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf.close()
        
        # Clean up the temporary file
        try:
            os.unlink(temp_path)
        except:
            pass
        print("Audio playback completed")
    except Exception as e:
        print(f"Error playing WAV file: {str(e)}")