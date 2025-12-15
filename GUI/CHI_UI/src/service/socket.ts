import { io } from "socket.io-client";

// Create socket with more options for debugging
const socket = io("127.0.0.1:8000", {
  reconnection: true,
  reconnectionAttempts: 5,
  reconnectionDelay: 1000,
  transports: ['websocket', 'polling']
});

// Add event listeners for connection status
socket.on("connect", () => {
  console.log("Socket connected with ID:", socket.id);
});

socket.on("connect_error", (error) => {
  console.error("Socket connection error:", error);
});

socket.on("disconnect", (reason) => {
  console.log("Socket disconnected:", reason);
});

export default socket;