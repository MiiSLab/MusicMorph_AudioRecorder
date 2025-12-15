import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import os
def detect_beats(file_path, hop_length=512):
    """
    Detect main/heavy beats in a wav file and return their timestamps in seconds.
    
    Parameters:
    -----------
    file_path : str
        Path to the wav file
    hop_length : int, optional
        Hop length for onset detection, by default 512
        
    Returns:
    --------
    list
        List of beat timestamps in seconds
    """
    # Load the audio file
    y, sr = librosa.load(file_path)
    
    # Use librosa's beat tracking
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop_length)
    
    # Convert beat frames to time in seconds
    beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=hop_length)
    
    # Return the beat times as a list
    return beat_times.tolist(), y, sr

def visualize_waveform(y, sr, beat_times=None, output_file=None):
    """
    Visualize the audio waveform and optionally mark the beat positions.
    
    Parameters:
    -----------
    y : np.ndarray
        Audio time series
    sr : int
        Sampling rate
    beat_times : list, optional
        List of beat timestamps in seconds
    output_file : str, optional
        Path to save the visualization. If None, the plot is displayed.
    """
    plt.figure(figsize=(12, 4))
    
    # Plot the waveform
    librosa.display.waveshow(y, sr=sr, alpha=0.6)
    
    # If beat times are provided, mark them on the plot
    if beat_times:
        for beat in beat_times:
            plt.axvline(x=beat, color='r', alpha=0.7, linestyle='--')
    
    plt.title('Audio Waveform with Beat Markers')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file)
    else:
        plt.show()

def visualize_spectrogram(y, sr, beat_times=None, output_file=None):
    """
    Visualize the audio spectrogram and optionally mark the beat positions.
    
    Parameters:
    -----------
    y : np.ndarray
        Audio time series
    sr : int
        Sampling rate
    beat_times : list, optional
        List of beat timestamps in seconds
    output_file : str, optional
        Path to save the visualization. If None, the plot is displayed.
    """
    plt.figure(figsize=(12, 6))
    
    # Compute the spectrogram
    D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
    
    # Plot the spectrogram
    librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    
    # If beat times are provided, mark them on the plot
    if beat_times:
        for beat in beat_times:
            plt.axvline(x=beat, color='r', alpha=0.7, linestyle='--')
    
    plt.title('Spectrogram with Beat Markers')
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file)
    else:
        plt.show()
# Example usage
if __name__ == "__main__":
    # relative path to the wav (output)
    file_path = "../outputs/output1.wav"  # Replace with your wav file path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.abspath(os.path.join(script_dir, file_path))
    save_visual_path = os.path.abspath(os.path.join(script_dir, "../Visualization/"))

    # Abs Path Music
    file_path = "C:/Users/Angus/Music/15Dodoro_clip.wav"

    beat_times, y, sr = detect_beats(file_path)
    print(f"Detected {len(beat_times)} beats:")
    print(beat_times)

    # Visualize the waveform with beat markers
    # visualize_waveform(y, sr, beat_times)
    
    # # Visualize the spectrogram with beat markers
    # visualize_spectrogram(y, sr, beat_times)
    
    # Uncomment to save visualizations to files
    w_path = os.path.join(save_visual_path, "waveform.png")
    s_path = os.path.join(save_visual_path, "spectrogram.png")
    visualize_waveform(y, sr, beat_times, w_path)
    # visualize_spectrogram(y, sr, beat_times, s_path)
