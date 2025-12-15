import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import os

def detect_loud_sounds(file_path, seconds_per_beat=3.0, min_separation=0.5, hop_length=512, initial_percentile=95):
    """
    Detect loud sounds in a wav file based on a time-based threshold.
    Automatically adjusts amplitude threshold to find approximately one loud sound per N seconds.
    Ensures detected sounds are separated by at least min_separation seconds.
    
    Parameters:
    -----------a
    file_path : str
        Path to the wav file
    seconds_per_beat : float, optional
        Target time interval between loud sounds in seconds, by default 3.0
    min_separation : float, optional
        Minimum separation between consecutive loud sounds in seconds, by default 0.05
    hop_length : int, optional
        Hop length for onset detection, by default 512
    initial_percentile : int, optional
        Starting percentile for threshold calculation, by default 95
        
    Returns:
    --------
    tuple
        (loud_times, threshold, y, sr) where:
        - loud_times: List of loud sound timestamps in seconds
        - threshold: The amplitude threshold used
        - y: Audio time series
        - sr: Sample rate
    """
    # Load the audio file
    y, sr = librosa.load(file_path)
    
    # Calculate total duration in seconds
    duration = librosa.get_duration(y=y, sr=sr)
    
    # Calculate target number of loud sounds based on duration and seconds_per_beat
    target_num_sounds = max(1, int(duration / seconds_per_beat))
    print(f"Audio duration: {duration:.2f} seconds")
    print(f"Target: ~1 loud sound per {seconds_per_beat:.1f} seconds = {target_num_sounds} sounds")
    
    # Compute the root mean square energy
    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
    
    # Find frames where loud sounds occur by adjusting threshold
    percentile = initial_percentile
    loud_frames = []
    threshold = 0
    
    # Binary search approach for finding the right threshold
    min_percentile = 50
    max_percentile = initial_percentile
    
    while max_percentile - min_percentile > 1:
        mid_percentile = (min_percentile + max_percentile) / 2
        threshold = np.percentile(rms, mid_percentile)
        loud_frames = np.where(rms > threshold)[0]
        
        # If we have too many loud sounds, increase the threshold
        if len(loud_frames) > target_num_sounds:
            min_percentile = mid_percentile
        # If we have too few loud sounds, decrease the threshold
        else:
            max_percentile = mid_percentile
    
    # Get the final threshold and frames
    threshold = np.percentile(rms, min_percentile)
    loud_frames = np.where(rms > threshold)[0]
    
    # If we still don't have enough loud sounds, use the top N loudest points
    if len(loud_frames) < target_num_sounds:
        sorted_indices = np.argsort(rms)[::-1]  # Sort in descending order
        loud_frames = sorted_indices[:target_num_sounds]
        threshold = rms[loud_frames[-1]]  # Use the amplitude of the last point as threshold
    
    # Convert frames to time in seconds
    loud_times = librosa.frames_to_time(loud_frames, sr=sr, hop_length=hop_length)
    
    # Sort the times (in case we used the top N approach)
    loud_times = np.sort(loud_times)
    
    # Filter out beats that are too close to each other
    filtered_times = []
    if len(loud_times) > 0:
        filtered_times.append(loud_times[0])  # Always include the first beat
        
        for i in range(1, len(loud_times)):
            # Check if this beat is at least min_separation seconds away from the last included beat
            if loud_times[i] - filtered_times[-1] >= min_separation:
                filtered_times.append(loud_times[i])
    
    print(f"Original detections: {len(loud_times)}, After filtering: {len(filtered_times)}")
    
    return filtered_times, threshold, y, sr

def visualize_waveform_with_loudness(y, sr, loud_times=None, threshold=None, output_file=None, seconds_per_beat=3.0):
    """
    Visualize the audio waveform with RMS energy and mark loud sound positions.
    
    Parameters:
    -----------
    y : np.ndarray
        Audio time series
    sr : int
        Sampling rate
    loud_times : list, optional
        List of loud sound timestamps in seconds
    threshold : float, optional
        The amplitude threshold used for detection
    output_file : str, optional
        Path to save the visualization. If None, the plot is displayed.
    seconds_per_beat : float, optional
        The target time interval between loud sounds in seconds
    """
    plt.figure(figsize=(12, 8))
    
    # Plot the waveform
    plt.subplot(2, 1, 1)
    librosa.display.waveshow(y, sr=sr, alpha=0.6)
    
    # If loud times are provided, mark them on the plot
    if loud_times:
        for time in loud_times:
            plt.axvline(x=time, color='r', alpha=0.7, linestyle='--')
    
    plt.title(f'Audio Waveform with Loud Sound Markers (1 per ~{seconds_per_beat} sec)')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    
    # Plot the RMS energy
    plt.subplot(2, 1, 2)
    hop_length = 512
    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
    times = librosa.times_like(rms, sr=sr, hop_length=hop_length)
    plt.plot(times, rms)
    
    # If threshold is provided, draw a horizontal line
    if threshold is not None:
        plt.axhline(y=threshold, color='r', linestyle='-', label=f'Threshold: {threshold:.4f}')
        plt.legend()
    
    # If loud times are provided, mark them on the plot
    if loud_times:
        for time in loud_times:
            plt.axvline(x=time, color='r', alpha=0.7, linestyle='--')
    
    plt.title('RMS Energy with Threshold')
    plt.xlabel('Time (s)')
    plt.ylabel('RMS Energy')
    
    plt.tight_layout()
    
    if output_file:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        plt.savefig(output_file)
    else:
        plt.show()

def get_segment_rms_values(y, sr, num_segments=50, hop_length=512):
    """
    Split the audio into n segments and get the RMS energy at the start of each segment.
    
    Parameters:
    -----------
    y : np.ndarray
        Audio time series
    sr : int
        Sampling rate
    num_segments : int, optional
        Number of segments to split the audio into, by default 50
    hop_length : int, optional
        Hop length for RMS calculation, by default 512
        
    Returns:
    --------
    tuple
        (segment_times, segment_rms_values) where:
        - segment_times: List of timestamps for the start of each segment in seconds
        - segment_rms_values: List of RMS values at the start of each segment
    """
    # Calculate total duration in seconds
    duration = librosa.get_duration(y=y, sr=sr)
    
    # Calculate segment length in seconds
    segment_length = duration / num_segments
    
    # Compute the RMS energy for the entire audio
    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
    
    # Calculate the times corresponding to each RMS value
    rms_times = librosa.times_like(rms, sr=sr, hop_length=hop_length)
    
    # Initialize lists to store results
    segment_times = []
    segment_rms_values = []
    
    # For each segment, find the closest RMS value to the segment start time
    for i in range(num_segments):
        segment_start_time = i * segment_length
        segment_times.append(segment_start_time)
        
        # Find the index of the RMS value closest to this time
        closest_idx = np.argmin(np.abs(rms_times - segment_start_time))
        segment_rms_values.append(rms[closest_idx])
    
    return segment_times, segment_rms_values

def analyze_audio_file(file_path, seconds_per_beat=3.0, min_separation=0.5, num_segments=100):
    '''
    seconds_per_beat = 幾秒內希望有一個beat 
    min_separation = 兩個beat之間最少要有幾秒
    num_segments = rms值分成幾個節點 
    '''
    # Ensure the file path is absolute
    file_path = os.path.abspath(file_path)
    
    # Detect loud sounds (beats)
    beat_times, threshold, y, sr = detect_loud_sounds(
        file_path, 
        seconds_per_beat=seconds_per_beat,
        min_separation=min_separation
    )
    
    # Get RMS values at the start of each segment
    segment_times, segment_rms_values = get_segment_rms_values(y, sr, num_segments)
    
    # Convert numpy arrays to lists for better JSON serialization if needed
    if isinstance(beat_times, np.ndarray):
        beat_times = beat_times.tolist()
    if isinstance(segment_times, np.ndarray):
        segment_times = segment_times.tolist()
    if isinstance(segment_rms_values, np.ndarray):
        segment_rms_values = segment_rms_values.tolist()
    
    # Create and return the result object
    result = {
        'beat_times': beat_times,
        # 'segment_times': segment_times,
        'rms_values': segment_rms_values
    }
    return result

# Example usage
if __name__ == "__main__":
    # Example file path
    file_path = "../outputs/output.wav"
    
    # Get the absolute path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.abspath(os.path.join(script_dir, file_path))
    
    # Analyze the audio file
    result = analyze_audio_file(file_path)
    
    # Print the results
    print(f"Beat times: {result['beat_times']}")
    print(f"First few RMS values: {result['rms_values'][:5]}")