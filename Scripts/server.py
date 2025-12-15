from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
import MultiInput as MI
import Loud_Detection as LD
from pydub import AudioSegment  
import os 
import base64
from werkzeug.utils import secure_filename  # Import secure_filename
# Set the log level to ERROR or higher to suppress most logs
import logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")  # Allow frontend to connect
# Add these global variables at the top of server.py
latest_midi_event = None
midi_event_ready = False

@app.route('/')
def index():
    return "Flask-SocketIO Server Running!"


MI.initialize()

@socketio.on("start_recording")
def start_recording_event():
    print("🎤 Starting Recording via WebSocket")
    

    def send_recording_status(status):
        emit("recording_status", {"status": status})
    

    def emit_playback_info(data):
        print("Storing MIDI playback info:", data)
        global latest_midi_event, midi_event_ready
        print(f"latest midi event = {latest_midi_event}")
        latest_midi_event = data
        midi_event_ready = True

    # Pass the callback to start_recording
    MI.start_recording(send_recording_status, emit_playback_info)
    # Inform client about minimum recording length
    emit("recording_info", {"message": "Recording will be extended to 15 seconds if shorter"})

@socketio.on("pause_recording")
def pause_recording_event():
    print("⏸️ Pausing Recording via WebSocket")
    MI.pause_recording()
    emit("recording_status", {"status": "paused"})

@socketio.on("resume_recording")
def resume_recording_event():
    print("▶️ Resume Recording via WebSocket")
    MI.resume_recording()
    emit("recording_status", {"status": "resumed"})

@socketio.on("stop_recording")
def stop_recording_event():
    print("🛑 Stopping Recording via WebSocket")
    MI.stop_recording()
    # Inform client that recording will be extended if needed
    emit("processing_info", {"message": "Processing recording (ensuring minimum 15-second length)..."})

# Handle client connection
@socketio.on("connect")
def handle_connect():
    print(f"🔌 Client connected! SID: {request.sid}")
    available_devices, devices_id = MI.detect_midi_inputs()
    emit("available_devices", {"devices": available_devices, "devices_id": devices_id})
    # Start the event processing thread if it's not already running
    socketio.start_background_task(check_and_emit_midi_events)

def check_and_emit_midi_events():
    # print("Starting MIDI event checker background task")
    while True:
        global latest_midi_event, midi_event_ready
        if midi_event_ready:
            # print("Found new MIDI event to emit:", latest_midi_event)
            socketio.emit("midi_playback_info", latest_midi_event)
            midi_event_ready = False  # Reset the flag
        socketio.sleep(0.01)  # Use socketio.sleep for compatibility

# Handle client disconnection
@socketio.on("disconnect")
def handle_disconnect():
    print(f"❌ Client disconnected! SID: {request.sid}")

@socketio.on("replay")
def handle_replay():
    print(f"Replaying recording")
    MI.play_wav_file()

# Handle custom message
@socketio.on("message")
def handle_message(msg):
    print(f"📩 Received message: {msg}")
    send(f"🔁 Echo: {msg}", broadcast=True)  # Broadcast message back to all clients

# 上傳Recorded File from local to http, then http wills send to server
@socketio.on('use_recorded_file_for_upload')
def handle_use_recorded_file_for_upload(data):
    import requests  # Add this import at the top of the function
    try:
        file_path = data.get('filePath')
        target_url = data.get('targetUrl')
        
        # Convert relative path to absolute path if needed
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.abspath(os.path.join(script_dir, file_path))
        # absolute_path = "c:/Users/Angus/Angus_Stuff/Programming/AudioRecording/outputs/output.wav"
        absolute_path = "C:/Users/miisl/Desktop/MusicMorph/MusicMorph_Demo/AudioRecording/outputs/output.wav"
        
        print(f"Uploading file from {absolute_path} to {target_url}")
        
        if os.path.exists(absolute_path):
            # Create a multipart form with the file
            with open(absolute_path, 'rb') as file:
                files = {'file': (os.path.basename(absolute_path), file, 'audio/wav')}
                
                # Send the request to the target URL
                response = requests.post(target_url, files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"File successfully uploaded: {result}")
                    socketio.emit('file_upload_result', {
                        'success': True,
                        'message': f"File uploaded successfully. ID: {result.get('id', 'unknown')}",
                        'data': result
                    })
                else:
                    print(f"Error uploading file: {response.status_code}, {response.text}")
                    socketio.emit('file_upload_result', {
                        'success': False,
                        'error': f"HTTP error {response.status_code}"
                    })
        else:
            socketio.emit('file_upload_result', {
                'success': False,
                'error': 'File not found'
            })
    except Exception as e:
        print(f"Exception when uploading file: {str(e)}")
        socketio.emit('file_upload_result', {
            'success': False,
            'error': str(e)
        })

@socketio.on("add_device_config")
def add_device_event(data):
    print(f"➕ Adding Device via WebSocket: {data['added_devices']}")
    added_devices = data['added_devices']
    MI.create_midi_device(added_devices)


@socketio.on('upload_audio_file')
def handle_upload(data):
    try:
        filename = data['filename']
        filetype = data['filetype']
        file_data = data['data']
        
        # The data comes as a data URL, so we need to extract the base64 part
        # Format is: data:audio/wav;base64,<actual base64 data>
        header, encoded = file_data.split(",", 1)
        
        # Decode the base64 data
        file_bytes = base64.b64decode(encoded)
        
        # Save the file
        upload_dir = os.path.join(app.root_path, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, secure_filename(filename))
        
        with open(file_path, 'wb') as f:
            f.write(file_bytes)
        
        # Process the file (e.g., convert to MIDI)
        # This would depend on your specific backend processing needs
        
        # Send a success response
        emit('upload_response', {
            'status': 'success',
            'message': f'File {filename} uploaded successfully',
            'path': file_path
        })
        
        # You might want to trigger further processing here
        # For example, start converting the audio to MIDI
        
    except Exception as e:
        print(f"Error handling upload: {str(e)}")
        emit('upload_response', {
            'status': 'error',
            'message': f'Upload failed: {str(e)}'
        })


if __name__ == "__main__":
    # if debug = True it will print a bunch of logs
    socketio.run(app, host="0.0.0.0", port=8000, debug=False)
    print("🎉 Server started!")