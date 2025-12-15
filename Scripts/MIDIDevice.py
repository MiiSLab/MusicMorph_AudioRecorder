# midi_device.py
class MIDIDevice:
    def __init__(self, device_name, soundfont_path, instrument_number, input_id):
        """
        Initializes a MIDI device configuration.
        
        :param device_name: Name of the MIDI device
        :param soundfont_path: Path to the soundfont file (.sf2)
        :param instrument_number: The program/instrument number (0-127)
        :param gain: Sound volume gain (default: 1.0)
        :param channel: MIDI channel (default: 0)
        """
        self.device_name = device_name
        self.soundfont_path = soundfont_path
        self.instrument_number = instrument_number
        self.input_id = input_id

    def change_instrument(self, new_instrument):
        """Change the instrument number (program change)."""
        if 0 <= new_instrument <= 127:
            self.instrument_number = new_instrument
            print(f"✅ Instrument changed to {new_instrument}")
        else:
            print("⚠️ Invalid instrument number! Must be between 0-127.")

    def set_soundfont(self, new_soundfont_path):
        """Change the soundfont file."""
        self.soundfont_path = new_soundfont_path
        print(f"✅ Soundfont changed to {new_soundfont_path}")

    def set_instrument_number(self, new_instrument_number):
        """Change the instrument number."""
        self.instrument_number = new_instrument_number
        print(f"✅ Instrument number changed to {new_instrument_number}")

    def set_device_name(self, name):
        """Change the instrument number."""
        self.device_name = __name__
        print(f"✅ Instrument number changed to {name}")

    def set_input_number(self, input_id):
        """Change the instrument number."""
        self.input_number = input_id
        print(f"✅ input id changed to {input_id}")
    
    def print_stuff(self):
        print(f"Device Name: {self.device_name}")
        print(f"Soundfont Path: {self.soundfont_path}")
        print(f"Instrument Number: {self.instrument_number}")
        print(f"Input ID: {self.input_id}")
