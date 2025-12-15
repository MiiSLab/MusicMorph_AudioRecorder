import React from 'react';
import ReactDOM from 'react-dom/client';
import { HashRouter as Router } from 'react-router-dom';
import './index.css';
import { useEffect, useRef, useState } from 'react';
import bgImg from './assets/Background_1088_488.png';
// ES modules
import socket from './service/socket';
import { FaMicrophone } from 'react-icons/fa'; // Font Awesome Microphone icon
import { BsPlayFill, BsPauseFill, BsStopFill } from 'react-icons/bs'; // Bootstrap icons
import { FaHeadphones } from "react-icons/fa";
const App = () => {
	const [input, setInput] = useState([]);
	const bottomRef = useRef(null); // 用於滾動到底部的 ref
	const [message, setMessage] = useState('');
	const [instruments, setInstruments] = useState("Piano");
	const [device_name, setDeviceName] = useState('');
	const [deviceCount, setDeviceCount] = useState(0);
	const [hasrecorded, setHasRecorded] = useState(false);
	// available_devices is an object with two keys: devices and devices_id
	const [available_devices, setDevices] = useState<{
		devices: string[];
		devices_id: string[];
	}>({
		devices: [],
		devices_id: []
	});
	const [added_devices, setAddedDevices] = useState<{ [key: string]: string[] }>({});
	const [responseMessage, setResponseMessage] = useState("");
	// Add state for the upload popup
	const [showUploadPopup, setShowUploadPopup] = useState(false);
	const [selectedFile, setSelectedFile] = useState<File | null>(null);
	const fileInputRef = useRef<HTMLInputElement>(null);
	// loading screen
	const [IsUploading, setIsUploading] = useState(false);
	const [uploadOption, setUploadOption] = useState<'recorded' | 'file' | null>(null);

	// SENDING FILE TO SERVER33333
	const [file, setFile] = React.useState<File>(null);

	// Recording timer states
	const [isRecording, setIsRecording] = useState(false);
	const [recordingTime, setRecordingTime] = useState(0);
	const [isPaused, setIsPaused] = useState(false);
	const timerRef = useRef<number | null>(null);

	// Playback timer states
	const [isPlaying, setIsPlaying] = useState(false);
	const [playbackTime, setPlaybackTime] = useState(0);
	const [totalRecordingTime, setTotalRecordingTime] = useState(0);
	const playbackTimerRef = useRef<number | null>(null);

	// Timer Display
	const [showTimer, setShowTimer] = useState(false);
	const [finalTime, setFinalTime] = useState(0);

	// Status Message
	const [statusMessage, setStatusMessage] = useState("");
	// useEffect(() => {
	// 	// Set up the listener for the response_event
	// 	socket.on("response_event", (data) => {
	// 		console.log("📩 Received response:", data);
	// 		setResponseMessage(data.message);
	// 		console.log(data.message);
	// 	});

	// 	// Clean up the listener when the component unmounts
	// 	return () => {
	// 		socket.off("response_event");
	// 	};
	// }, []);

	useEffect(() => {
		// 當 input 更新時滾動到底部
		if (bottomRef.current) {
			bottomRef.current.scrollIntoView({ behavior: 'instant' });
		}
	}, [input]);

	useEffect(() => {
		socket.on("connect", () => {
			console.log("✅ Connected to Flask-SocketIO");
			clearPlaybackInfo();
		});

		socket.on("message", (data) => {
			console.log("📨 Message received:", data);
			setMessage(data);
		});

		socket.on("available_devices", (data) => {
			console.log("Available MIDI devices:", data.devices);
			console.log("device id:", data.devices_id);
			setDevices(data);
			setDeviceName(data.devices[0]);
			setInstruments("Piano");
			console.log("peepee device", available_devices);
			// Now you can populate dropdowns or other UI elements with these options
		});

		return () => {
			socket.disconnect();
		};
	}, []);

	// Timer effect for recording
	useEffect(() => {
		if (isRecording && !isPaused) {
			timerRef.current = window.setInterval(() => {
				setRecordingTime(prevTime => prevTime + 1);
			}, 1000);
		} else if (timerRef.current) {
			clearInterval(timerRef.current);
		}

		return () => {
			if (timerRef.current) {
				clearInterval(timerRef.current);
			}
		};
	}, [isRecording, isPaused]);

	// Format the recording time as "MM:SS"
	const formatTime = (seconds: number) => {
		const minutes = Math.floor(seconds / 60);
		const remainingSeconds = seconds % 60;
		return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
	};

	const pauseRecording = () => {
		if (deviceCount === 0) {
			console.error("No devices added. Please add a device before recording.");
			setStatusMessage("Please add a device before recording.");
			return;
		}
		console.log("Paused Recording Pressed!");
		socket.emit("pause_recording");
		setIsPaused(true);
	};

	const resumeRecording = () => {
		if (deviceCount === 0) {
			console.error("No devices added. Please add a device before recording.");
			setStatusMessage("Please add a device before recording.");
			return;
		}
		console.log("Resume Recording Pressed!");
		socket.emit("resume_recording");
		setIsPaused(false);
	};

	const stopRecording = () => {
		if (deviceCount === 0) {
			console.error("No devices added. Please add a device before recording.");
			setStatusMessage("Please add a device before recording.");
			return;
		}
		console.log("🛑 Sending Stop Recording");
		socket.emit("stop_recording");
		setIsRecording(false);
		setIsPaused(false);
		setTotalRecordingTime(recordingTime); // Save the total recording time
		setFinalTime(recordingTime); // Save the final time to display
		setShowTimer(true); // Keep showing the timer
	};


	// Update the tryagain function to reset everything
	const tryagain = () => {
		console.log("try again!");
		socket.emit("stop_recording");
		clearPlaybackInfo();
		setIsRecording(false);
		setIsPaused(false);
		setRecordingTime(0);
		setIsPlaying(false);
		setPlaybackTime(0);
		setTotalRecordingTime(0);
		setFinalTime(0);
		setShowTimer(false); // Hide the timer when trying again
		if (playbackTimerRef.current) {
			clearInterval(playbackTimerRef.current);
		}
	};

	const startRecording = () => {
		if (deviceCount === 0) {
			console.error("No devices added. Please add a device before recording.");
			setStatusMessage("Please add a device before recording.");
			return;
		}
		setHasRecorded(true);
		setStatusMessage("Recording will be padded to 15 seconds.");
		console.log("Start Recording!");
		socket.emit("start_recording");
		clearPlaybackInfo();
		setIsRecording(true);
		setIsPaused(false);
		setRecordingTime(0);
		setShowTimer(true); // Show the timer when recording starts
	};

	const playRecording = () => {
		if (hasrecorded === false) {
			console.error("No recording available. Please record before playing.");
			setStatusMessage("Please record before playing.");
			return;
		}
		setStatusMessage(" ");
		console.log("Play Recording!");
		socket.emit("replay");
		setIsPlaying(true);
		setPlaybackTime(0);
		setShowTimer(true); // Make sure timer is visible

		// Start the playback timer
		if (playbackTimerRef.current) {
			clearInterval(playbackTimerRef.current);
		}

		playbackTimerRef.current = window.setInterval(() => {
			setPlaybackTime(prevTime => {
				// If we've reached the total recording time, stop the timer but keep displaying it
				if (prevTime >= totalRecordingTime) {
					clearInterval(playbackTimerRef.current);
					setIsPlaying(false);
					setFinalTime(totalRecordingTime); // Save the final time
					return totalRecordingTime;
				}
				return prevTime + 1;
			});
		}, 1000);
	};

	// Add a useEffect to clean up the playback timer
	useEffect(() => {
		return () => {
			if (playbackTimerRef.current) {
				clearInterval(playbackTimerRef.current);
			}
		};
	}, []);

	// Add this state to store playback information
	const [playbackInfo, setPlaybackInfo] = useState<{
		device_name: string;
		message_type: string;
		duration: number;
		note: string;
		velocity: number;
	}[]>([]);

	// Update the useEffect for midi_playback_info with better debugging
	useEffect(() => {
		// Set up the listener for midi playback info
		socket.on("midi_playback_info", (data) => {
			console.log("🎵 Received playback info:", data);

			// Check if data has the expected structure
			if (!data || typeof data !== 'object') {
				console.error("Received invalid playback data:", data);
				return;
			}

			// Create a formatted entry for the table
			const newEntry = {
				'Velocity': data.velocity || '0',
				'Source': data.device_name || 'Unknown device',
				'Message': data.message_type || 'Unknown message',
				'Channel': '0',
				'Note': data.note || 'N/A',
				'Duration': data.duration || 'N/A'
			};

			console.log("Adding new entry to input:", newEntry);

			// Add the new entry to the input array
			setInput(prevInput => {
				const updatedInput = [...prevInput, newEntry];
				console.log("Updated input array length:", updatedInput.length);
				return updatedInput.slice(-50); // Keep only the most recent 50 items
			});

			// Also update the playbackInfo state
			setPlaybackInfo(prevInfo => [...prevInfo, data].slice(-50));
		});

		// console.log("🔌 Set up midi_playback_info listener");

		// Clean up the listener when the component unmounts
		return () => {
			// console.log("🔌 Removing midi_playback_info listener");
			socket.off("midi_playback_info");
		};
	}, []);

	// Function to clear playback info if needed
	const clearPlaybackInfo = () => {
		setPlaybackInfo([]);
		setInput([
		]); // Set a default entry that shows the format of the data
		console.log("cleared playback info and input arrays!");
	};

	const add_device = () => {
		// Check if device_name is empty or not selected
		if (!device_name || device_name === "Select a device") {
			console.error("No device selected");
			return;
		}

		// Check if the selected device is in the available devices list
		const availableDeviceNames = Object.values(available_devices.devices);
		if (!availableDeviceNames.includes(device_name)) {
			console.error("Selected device is not in the available devices list");
			return;
		}

		// Create a copy of the current added_devices
		const updatedDevices = { ...added_devices };

		// Check if this device already exists in the list
		if (updatedDevices[device_name]) {
			// Device already exists - replace the instrument instead of adding to array
			updatedDevices[device_name] = [instruments]; // Replace with new instrument
			// Update the state with the new devices
			setAddedDevices(updatedDevices);

			console.log(`Updated device: ${device_name} with instrument: ${instruments}`);
			// Emit event to the server to save this configuration
			socket.emit("add_device_config", {
				added_devices: updatedDevices
			});
		} else {
			// Create a new entry for this device with the instrument
			updatedDevices[device_name] = [instruments];

			// Update the state with the new devices
			setAddedDevices(updatedDevices);
			console.log(`Added device: ${device_name} with instrument: ${instruments}`);

			// Emit event to the server to save this configuration
			socket.emit("add_device_config", {
				added_devices: updatedDevices
			});
		}

		// Update the device count after adding/updating a device
		const deviceCount = Object.keys(updatedDevices).length;
		setDeviceCount(deviceCount);
		console.log(`Total devices: ${deviceCount}`);
	};

	// New functions for handling the upload popup
	const openUploadPopup = () => {
		setShowUploadPopup(true);
		setUploadOption(null);
	};

	const closeUploadPopup = () => {
		setShowUploadPopup(false);
		setSelectedFile(null);
		setUploadOption(null);
	};

	const handleRecordedUpload = () => {
		// Set the upload option to 'recorded'
		setUploadOption('recorded');

		// Create a File object with a reference to the server-side recorded file
		try {
			// Create a placeholder File object for UI purposes
			const recordedFile = new File(
				[new Blob(['placeholder'])],
				'recorded_output.wav',
				{ type: 'audio/wav' }
			);

			setSelectedFile(recordedFile);
			setFile(recordedFile);

			// Store additional information that this is a server-side file
			// We'll use this flag in the submit function
			recordedFile['isServerFile'] = true;
			recordedFile['serverPath'] = './outputs/output.wav';

			console.log("Using recorded audio file from server");
		} catch (error) {
			console.error("Error setting recorded audio file:", error);
		}
	};

	const handleFileSelect = () => {
		// Set the upload option to 'file'
		setUploadOption('file');
		// Trigger the hidden file input
		if (fileInputRef.current) {
			fileInputRef.current.click();
		}
	};

	const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
		const files = event.target.files;
		if (files && files.length > 0) {
			const selectedFile = files[0];
			setSelectedFile(selectedFile);
			setFile(selectedFile); // Set the file state for the submit function
			console.log("Selected file:", selectedFile.name);
		}
	};

	// Submit function from main.tsx, integrated into App.tsx
	const submitFile = async () => {
		console.log('Submitting file:', file);
		if (!file) {
			console.error('No file selected');
			return;
		}

		setIsUploading(true);

		const formData = new FormData();
		formData.append('file', file);

		try {
			const host = 'http://140.118.162.43:8443'; // Define your host URL here
			const response = await fetch(host + '/generate', { method: 'POST', body: formData });

			if (!response.ok) {
				throw new Error(`HTTP error! Status: ${response.status}`);
			}

			const data = await response.json();
			const { success, id } = data;
			console.log('Success:', data.success);

			// Show success message or update UI
			setStatusMessage(`File uploaded successfully! ID: ${id}`);
		} catch (error) {
			console.error('Error:', error);
			setResponseMessage(`Upload failed: ${error.message}`);
		} finally {
			setIsUploading(false);
			// setStatusMessage("Upload Finished!");
			closeUploadPopup();
		}
	};

	// Function to handle the recorded audio upload
	// Function to handle the recorded audio upload
	const handleRecordedAudioSubmit = async () => {
		setIsUploading(true);

		try {
			// Instead of trying to access the file directly from the frontend,
			// we'll tell the server to process the file that's already on the server
			socket.emit("use_recorded_file_for_upload", {
				filePath: './outputs/output.wav',
				targetUrl: 'http://140.118.162.43:8443/generate'
			});

			// Listen for the response from the server
			socket.on("file_upload_result", (data) => {
				console.log("File upload result:", data);

				if (data.success) {
					setStatusMessage(`File uploaded successfully! ${data.id || ''}`);
				} else {
					setResponseMessage(`Upload failed: ${data.error || 'Unknown error'}`);
				}

				setIsUploading(false);
				// setStatusMessage("Upload Finished!");
				closeUploadPopup();
			});

			// Set a timeout in case the server doesn't respond
			setTimeout(() => {
				if (IsUploading) {
					console.error("Server did not respond to upload request");
					setResponseMessage("Upload timed out. Please try again.");
					setIsUploading(false);
					setStatusMessage("Upload Failed!");
					closeUploadPopup();
				}
			}, 30000); // 30 second timeout for upload

		} catch (error) {
			console.error('Error with recorded file upload:', error);
			setResponseMessage(`Upload failed: ${error.message}`);
			setIsUploading(false);
			setStatusMessage("Upload Failed!");
			closeUploadPopup();
		}
	};

	// Combined submit function that handles both file and recorded audio
	const handleConfirmUpload = () => {
		if (uploadOption === 'file' && file) {
			submitFile();
		} else if (uploadOption === 'recorded') {
			handleRecordedAudioSubmit();
		} else {
			console.error('No upload option selected or no file selected');
		}
	};

	// console.log(socket);

	const handleKeyDown = () => {
	};

	return (
		<div id='app' className=' relative p-5 pb-32' tabIndex={0} onKeyDown={handleKeyDown}>

			<div className='view w-[1088px] h-[488px] relative'>
				<img className='absolute w-[1088px] h-[488px]' src={bgImg} alt='' />

				<div className='absolute z-10 w-[1088px] h-[488px]'>

					<div className='absolute flex flex-col gap-7 w-[225px] top-[140px] left-[80px]'>
						<style>{`
						select {
							background-color: #000000;
							color: #ffffff;
							padding: 4px 8px;
							border-color: #333333;
						}
						
						option {
							background-color: #000000;
							color: #ffffff;
						}
						`}</style>

						<select
							className='text-sm bg-transparent border rounded-md'
							value={device_name}
							onChange={(e) => {
								const selectedName = e.target.value;
								// console.log("Selected Device Name:", selectedName);
								setDeviceName(selectedName);
							}}
						>
							{available_devices.devices &&
								typeof available_devices.devices === 'object' &&
								Object.keys(available_devices.devices).length > 0 ?
								Object.values(available_devices.devices).map((deviceName, index) => {
									// console.log(`Rendering option ${index}: ${deviceName}`);
									return (
										<option key={index} value={deviceName}>
											{deviceName}
										</option>
									);

								})
								:
								<option value="">Select a device</option>
							}
						</select>

						<select
							className='text-sm border rounded-md'
							value={instruments}
							onChange={(e) => setInstruments(e.target.value)}
						>
							<option value="piano">piano</option>
							<option value="e. guitar">electric guitar</option>
							<option value="drums">drums</option>
							<option value="music box">music box</option>
							<option value="a. guitar">acoustic guitar</option>
							<option value="violin">violin</option>
							<option value="trumpet">trumpet</option>
							<option value="gunshot">gunshot</option>
							{/* Add more instruments as needed */}
						</select>
					</div>

					<button
						onClick={add_device}
						className='hover:cursor-pointer active:scale-90 active:opacity-75 transition absolute top-[230px] left-[230px]'
						style={{ border: "none", background: "none", padding: 0 }}
					>

						<div
							className="w-[76px] h-[30px] rounded-md bg-[rgb(147,80,251)] flex items-center justify-center"
							style={{
								borderRadius: '8px',
								letterSpacing: '0.5px' // Adjust letter spacing if needed
							}}
						>
							<span className="text-white font-semibold text-sm">Add</span>
						</div>
					</button>
					<div className='absolute device-list top-[307px] left-[80px] w-[225px] h-[130px] flex flex-col overflow-auto'>
						{/* Header for the device list */}
						<div className='flex bg-[rgb(25,25,25)]'>
							<span className='flex-1 pl-12 text-[11px] text-start font-semibold'>Input Device</span>
							<span className='text-[11px] text-center w-[83px] font-semibold'>Sound</span>
						</div>

						{/* Device list entries */}
						{Object.entries(added_devices).map(([deviceName, instruments], deviceIndex) => (
							instruments.map((instrument, instrumentIndex) => (
								<div className='flex mt-0' key={`${deviceIndex}-${instrumentIndex}`}>
									<span className='flex-1 pl-2 text-[13px] text-start '>{deviceName}</span>
									<span className='text-[13px] text-center w-[83px] '>{instrument}</span>
								</div>
							))
						))}

						{/* Empty state message */}
						{Object.keys(added_devices).length === 0 && (
							<div className='flex justify-center items-center h-full text-xs text-gray-400'>
								No devices added yet
							</div>
						)}

						{/* Divider line */}
						<div className='mt-auto'></div>

						{/* Total devices count */}
						<div className='flex pl-2 text-[11px] text-gray-300 bg-[rgb(48,48,48)] font-semibold'>
							Total Active Devices: {deviceCount}
						</div>
					</div>

					{/* center-section */}
					<section className='absolute top-[135px] left-[370px] w-[445px] h-[30px] flex flex-col gap-2 text-sm bg-[#1E1E1E] overflow-auto'>
						<div className='flex gap-1 bg'>
							<div className='w-[100px] border-r px-1 border-r-stone-600'>Velocity</div>
							<div className='w-[200px] border-r px-1 border-r-stone-600'>Source</div>
							<div className='w-[100px] border-r px-1 border-r-stone-600'>Message</div>
							<div className='w-[100px] border-r px-1 border-r-stone-600'>Channel</div>
							<div className='w-[100px] border-r px-1 border-r-transparent'>Note</div>
						</div>
					</section>
					<section className='absolute top-[160px] left-[370px] w-[455px] h-[270px] flex flex-col gap-1 text-sm bg-[#1E1E1E] overflow-auto'>
						{input.length === 0 ? (
							<div className='flex justify-center items-center h-full text-xs text-gray-400 font-semibold'>
								No playback data yet
							</div>
						) : (
							input.map((item, index) => (
								<div className='flex gap-2' key={index}>
									<div className='w-[100px] border px-1 border-y-none border-l-none border-transparent'>
										{item['Velocity']}
									</div>
									<div className='w-[200px] border px-1 border-y-none border-l-none border-transparent'>
										{item['Source']}
									</div>
									<div className='w-[100px] border px-1 border-y-none border-l-none border-transparent'>
										{item['Message']}
									</div>
									<div className='w-[100px] border px-1 border-y-none border-l-none border-transparent'>
										{item['Channel']}
									</div>
									<div className='w-[100px] border px-1 border-y-none border-l-none border-transparent'>
										{item['Note']}
									</div>
								</div>
							))
						)}
						<div ref={bottomRef}></div>
					</section>

					{/* Status message below the table */}
					<div className='absolute top-[445px] left-[370px] w-[455px] text-center'>
						<p className='text-sm text-gray-300'>{statusMessage}</p>
					</div>

					{/* right-section */}
					<section className='right-section absolute top-[220px] left-[880px]  flex flex-col items-center gap-16'>
						{/* top-section */}
						<section className='flex flex-col items-center justify-center gap-5 top-section'>
							{/* top-group */}
							<div className='flex items-center justify-center gap-4'>
								<button
									onClick={startRecording}
									className="transition hover:cursor-pointer active:scale-90 active:opacity-75"
									style={{ border: "none", background: "none", padding: 0 }}
								>
									<div
										className="w-[74px] h-[74px] rounded-full bg-[rgb(147,80,251)] flex items-center justify-center"
									>
										<FaMicrophone
											size={40}
											color="white"
										/>
									</div>
								</button>
								<button
									onClick={playRecording}
									className="transition hover:cursor-pointer active:scale-90 active:opacity-75"
									style={{ border: "none", background: "none", padding: 0 }}
								>
									<div
										className="w-[74px] h-[74px] rounded-full bg-[rgb(147,80,251)] flex items-center justify-center"
									>
										<FaHeadphones
											size={40}
											color="white"
										/>
									</div>
								</button>
							</div>

							{/* bottom-group */}
							<div className='flex flex-col items-center h-[30px]'>
								<div className='flex items-center justify-center gap-5 bottom-group'>
									<button
										onClick={pauseRecording}
										className="transition hover:cursor-pointer active:scale-90 active:opacity-75"
										style={{ border: "none", background: "none", padding: 0 }}
									>
										<div className="w-[30px] h-[30px] rounded-full bg-[rgb(147,80,251)] flex items-center justify-center">
											<BsPauseFill
												size={20}
												color="white"
											/>
										</div>
									</button>

									<button
										onClick={stopRecording}
										className="transition hover:cursor-pointer active:scale-90 active:opacity-75"
										style={{ border: "none", background: "none", padding: 0 }}
									>
										<div className="w-[30px] h-[30px] rounded-full bg-[rgb(147,80,251)] flex items-center justify-center">
											<BsStopFill
												size={20}
												color="white"
											/>
										</div>
									</button>
									<button
										onClick={resumeRecording}
										className="transition hover:cursor-pointer active:scale-90 active:opacity-75"
										style={{ border: "none", background: "none", padding: 0 }}
									>
										<div
											className="w-[30px] h-[30px] rounded-full bg-[rgb(147,80,251)] flex items-center justify-center"
										>
											<BsPlayFill
												size={20}
												color="white"
												style={{ marginLeft: '2px' }} // Slight adjustment to visually center the triangle
											/>
										</div>
									</button>
								</div>

								{/* Recording/Playback Timer */}
								<div className="h-[20px] mt-2"> {/* Container with fixed height */}
									{showTimer && (
										<div
											className="mt-2 font-mono font-medium"
											style={{
												color: isRecording && recordingTime < 15 ? '#ff4d4d' : '#cccccc',
												fontSize: '14px'
											}}
										>
											{isRecording ? formatTime(recordingTime) :
												isPlaying ? formatTime(playbackTime) :
													formatTime(finalTime)}
										</div>
									)}
								</div>
							</div>
						</section>

						{/* bottom-section */}
						<section className='flex gap-5 bottom-section'>
							<button
								onClick={tryagain}
								className="transition hover:cursor-pointer active:scale-90 active:opacity-75"
								style={{ border: "none", background: "none", padding: 0 }}
							>
								<div
									className="w-[80px] h-[30px] flex items-center justify-center"
									style={{
										backgroundColor: '#4A4A4A',
										borderRadius: '9px',
										letterSpacing: '0.5px'
									}}
								>
									<span
										className="text-white font-semibold text-sm">Try Again</span>
								</div>
							</button>

							<button
								onClick={openUploadPopup}
								className="transition hover:cursor-pointer active:scale-90 active:opacity-75"
								style={{ border: "none", background: "none", padding: 0 }}
							>
								<div
									className="w-[80px] h-[30px] flex items-center justify-center"
									style={{
										backgroundColor: 'rgb(147, 80, 251)',
										borderRadius: '9px'
									}}
								>
									<span
										className="text-white font-semibold text-sm"
										style={{
											letterSpacing: '0.5px'
										}}
									>
										Upload !
									</span>
								</div>
							</button>
						</section>
					</section>

					{/* Upload Popup */}
					{showUploadPopup && (
						<div className="fixed inset-0 flex items-center justify-center z-50">
							{/* Overlay */}
							<div
								className="absolute inset-0 bg-black opacity-70"
								onClick={closeUploadPopup}
							></div>

							{/* Popup Content */}
							<div className="bg-[#1E1E1E] w-[300px] rounded-lg p-6 z-10 border border-[#333] shadow-lg">
								<h3 className="text-white text-[25px] font-semibold mb-4 text-center">Upload Audio</h3>

								<div className="flex flex-col gap-4">
									<button
										onClick={handleRecordedUpload}
										className={`w-full py-2 ${uploadOption === 'recorded' ? 'bg-[rgb(127,60,231)]' : 'bg-[rgb(147,80,251)]'} text-white font-semibold rounded-md hover:bg-[rgb(127,60,231)] transition`}
									>
										Use Recorded Audio
									</button>

									<button
										onClick={handleFileSelect}
										className={`w-full py-2 ${uploadOption === 'file' ? 'bg-[#3A3A3A]' : 'bg-[#4A4A4A]'} text-white font-semibold rounded-md hover:bg-[#5A5A5A] transition`}
									>
										Select Audio File
									</button>

									{selectedFile && (
										<p className="text-sm text-gray-300 text-center mt-2">
											Selected: {selectedFile.name}
										</p>
									)}

									{/* Hidden file input */}
									<input
										ref={fileInputRef}
										type="file"
										accept=".mp3,.wav"
										onChange={handleFileChange}
										className="hidden"
									/>

									<div className="flex gap-2 mt-2">
										<button
											onClick={closeUploadPopup}
											className="flex-1 py-2 bg-transparent text-gray-400 border border-gray-600 rounded-md hover:bg-[#2A2A2A] transition"
										>
											Cancel
										</button>

										{/* New Confirm button */}
										<button
											onClick={handleConfirmUpload}
											disabled={!uploadOption}
											className={`flex-1 py-2 ${!uploadOption ? 'bg-[rgb(100,50,180)] cursor-not-allowed' : 'bg-[rgb(147,80,251)] hover:bg-[rgb(127,60,231)]'} text-white font-semibold rounded-md transition`}
										>
											Confirm
										</button>
									</div>
								</div>
							</div>
						</div>
					)}

					{/* Loading overlay */}
					{IsUploading && (
						<div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-80">
							<div className="text-white text-xl">
								Uploading...
							</div>
						</div>
					)}
				</div>
			</div>
		</div>
	);
};

export default App;
