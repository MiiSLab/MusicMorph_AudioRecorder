# AudioRecording - MIDI Device Audio Recording & Dance Generation System

An integrated system for MIDI device input, audio recording, and dance motion generation. This project includes a Python backend server and a React frontend UI that can capture MIDI device input, record audio, and upload audio to an external service to generate corresponding dance movements.

## 🎬 Demo

Watch the system in action:

[![Demo Video](https://img.shields.io/badge/▶️_Watch-Demo_Video-blue?style=for-the-badge)](https://github.com/MiiSLab/MusicMorph_AudioRecorder/raw/main/docs/demo.mp4)

> 📥 Click the badge above to download and watch the demo video, or view it directly in the repository: [docs/demo.mp4](docs/demo.mp4)

## 📋 Project Overview

### System Architecture

This project consists of two main components:

1. **Python Backend Server** (`Scripts/` directory)

    - WebSocket server built with Flask-SocketIO
    - Real-time monitoring and processing of MIDI device input
    - Converts MIDI signals to audio files (.wav)
    - Supports single-device and multi-device simultaneous recording

2. **React Frontend UI** (`GUI/CHI_UI/` directory)
    - Built with React + TypeScript + Vite
    - Provides real-time MIDI input monitoring interface
    - Supports recording, pause, stop, playback functions
    - Can upload local music files or recorded audio to dance generation service

### Key Features

-   ✨ **MIDI Device Management**: Auto-detect and configure MIDI input devices
-   🎵 **Real-time Audio Recording**: Convert MIDI input to audio and record in real-time
-   🎹 **Multi-Instrument Support**: Supports Piano, Guitar, Drums, Violin, and more
-   ⏯️ **Recording Control**: Complete recording controls including start, pause, resume, stop
-   🎧 **Audio Playback**: Instant playback of recorded audio
-   📤 **File Upload**: Upload local music files or recorded audio to dance generation service
-   ⏱️ **Auto-Padding**: Recordings shorter than 15 seconds are automatically padded with silence

## 🚀 Quick Start

### System Requirements

-   **Python**: 3.8 or higher
-   **Node.js**: v20.15.1 or higher
-   **Operating System**: Windows (currently optimized for Windows platform)

### Installation

#### 1. Install Python Dependencies

Using conda environment:

```bash
conda env create -f environment.yml
conda activate audiorecording
```

Or using pip:

```bash
pip install -r requirements.txt
```

#### 2. Install Frontend Dependencies

```bash
cd GUI/CHI_UI
npm install
```

### Starting the System

#### 1. Start Python Backend Server

```bash
cd Scripts
python server.py
```

The server will start at `http://0.0.0.0:8000`.

#### 2. Start Frontend Development Server

```bash
cd GUI/CHI_UI
npm run dev
```

The frontend will start at `http://localhost:5173` (default Vite port).

#### 3. Build Frontend for Production (Optional)

```bash
cd GUI/CHI_UI
npm run build
```

Built files will be output to `GUI/CHI_UI/dist/` directory.

## 📖 Usage Guide

### 1. Device Configuration

1. Ensure your MIDI device is connected to the computer
2. Start the backend server, which will auto-detect available MIDI devices
3. Select MIDI device and instrument sound in the frontend UI
4. Click "Add" button to add the device to the recording list

### 2. Recording Audio

1. Click 🎤 (microphone icon) to start recording
2. Play your MIDI device, the system will display MIDI signals in real-time
3. Use pause ⏸️ and resume ▶️ buttons to control recording
4. Click stop ⏹️ to finish recording
5. After recording, click 🎧 (headphone icon) to play the audio

### 3. Upload Music to Generate Dance

Two upload methods available:

**Method 1: Use Recorded Audio**

1. After recording, click "Upload" button
2. Select "Use Recorded Audio"
3. System will automatically upload `outputs/output.wav` to dance generation service

**Method 2: Upload Local Music File**

1. Click "Upload" button
2. Select "Select Audio File"
3. Choose a local .wav or other audio file
4. System will upload the file to dance generation service

> **Note**: Currently the dance generation service URL is set to `http://140.118.162.43:8443/generate`, which can be modified in `GUI/CHI_UI/src/App.tsx`.

## 📁 Project Structure

```
AudioRecording/
├── Scripts/                    # Python backend server
│   ├── server.py              # Flask-SocketIO main server
│   ├── MultiInput.py          # MIDI device input processing
│   ├── MIDIDevice.py          # MIDI device class definition
│   ├── Midi2Wav.py            # MIDI to WAV conversion
│   ├── Loud_Detection.py      # Volume detection
│   └── ...
├── GUI/
│   └── CHI_UI/                # React frontend UI
│       ├── src/
│       │   ├── App.tsx        # Main application component
│       │   ├── service/
│       │   │   └── socket.ts  # SocketIO client
│       │   └── utils/         # Utility functions
│       ├── package.json       # Frontend dependencies
│       └── vite.config.ts     # Vite build configuration
├── soundfonts/                # Sound font files (.sf2)
├── outputs/                   # Output audio files
├── Midi_Files/                # Saved MIDI files
├── environment.yml            # Conda environment config
└── requirements.txt           # Python dependencies
```

## 🔧 Tech Stack

### Backend

-   **Flask** - Web framework
-   **Flask-SocketIO** - WebSocket communication
-   **pygame** - MIDI device control
-   **mido** - MIDI message processing
-   **FluidSynth** - MIDI to audio synthesis
-   **pydub** - Audio processing and editing

### Frontend

-   **React 18** - UI framework
-   **TypeScript** - Type safety
-   **Vite** - Build tool
-   **Socket.IO Client** - Real-time communication
-   **TailwindCSS** - Styling framework
-   **React Icons** - Icon library

## ⚙️ Configuration

### Backend Settings

Edit path settings in `Scripts/MultiInput.py`:

```python
# Output path configuration
midi_path_1 = "path/recorded_device1.mid"
midi_path_2 = "path/recorded_device2.mid"
wav_path = "path/output.wav"

# Minimum recording length (milliseconds)
MIN_RECORDING_LENGTH_MS = 16000  # 16 seconds
```

### Sound Font Files

Sound font files (.sf2) should be placed in `soundfonts/` directory:

-   `FluidR3_GM.sf2` - General MIDI sound bank (piano, guitar, etc.)
-   `PNSDrumKit.SF2` - Drum kit sounds

### Dance Generation Service URL

Edit `GUI/CHI_UI/src/App.tsx`:

```typescript
const host = 'http://your-server-url:port';
const response = await fetch(host + '/generate', { method: 'POST', body: formData });
```

## 🎹 Supported Instruments

| Instrument Name | MIDI Program Number   |
| --------------- | --------------------- |
| Piano           | 0                     |
| Music Box       | 10                    |
| Violin          | 40                    |
| Acoustic Guitar | 24                    |
| Electric Guitar | 27                    |
| Trumpet         | 56                    |
| Flute           | 73                    |
| Drums           | 0 (special soundfont) |
