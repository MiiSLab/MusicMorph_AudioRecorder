import os
import wave
import pyaudio
import tempfile
from pydub import AudioSegment
wav_path = "./outputs/output.wav"
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
        louder_audio = audio + 15  # +10dB increase
        
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

play_wav_file()