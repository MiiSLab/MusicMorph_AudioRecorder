import pygame.midi
import mido
from mido import MidiFile, MidiTrack, Message

def record_midi_with_timing(output_file):
    # Initialize Pygame MIDI
    pygame.midi.init()

    # List all available MIDI input devices
    print("Available MIDI Input Devices:")
    for i in range(pygame.midi.get_count()):
        print(f"{i}: {pygame.midi.get_device_info(i)}")

    # Automatically detect the first available MIDI input device
    available_ports = [i for i in range(pygame.midi.get_count()) if pygame.midi.get_device_info(i)[2] == 1]
    
    if not available_ports:
        print("No MIDI input devices found.")
        pygame.midi.quit()
        return

    input_id = available_ports[0]  # Automatically use the first available MIDI input port
    device_info = pygame.midi.get_device_info(input_id)
    midi_input = pygame.midi.Input(input_id)
    print(f"Using MIDI Input Device: {device_info[1].decode()} (ID: {input_id})")

    # Manually Select MIDI input device
    # input_id = int(input("Enter the ID of the MIDI input device to use: "))
    # midi_input = pygame.midi.Input(input_id)

    # Create a new MIDI file and track
    midi_file = MidiFile()
    track = MidiTrack()
    midi_file.tracks.append(track)

    print("Recording MIDI with timing... Press Ctrl+C to stop.")

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
                    print(f"Received: {message}, Time Delta: {time_delta}")

                    # Append the message with time delta to the track
                    track.append(message.copy(time=time_delta))
    except KeyboardInterrupt:
        print("Recording stopped.")
    finally:
        # Save the MIDI file
        midi_file.save(output_file)
        print(f"MIDI saved to {output_file}")

        # Cleanup
        midi_input.close()
        pygame.midi.quit()

if __name__ == "__main__":
    output_file = "./Midi_Files/recorded_with_timing.mid"  # Path to save the MIDI file
    record_midi_with_timing(output_file)

