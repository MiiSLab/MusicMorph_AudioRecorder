import React from 'react';
import ReactDOM from 'react-dom/client';
import { HashRouter as Router } from 'react-router-dom';
import App from './App.tsx';
import './index.css';
import { log } from 'console';
const Bang = () => {
	const [file, setFile] = React.useState<File>(null)
	const submit = async () => {
		console.log('!!', file)
		if (!file) return;
		console.log('!! no return')

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
		} catch (error) {
			console.error('Error:', error);
		}
	}

	return (
		<>
			<input type="file" name="" id="" onChange={e => { setFile(e.target.files?.[0]) }} />
			<div onClick={submit}>main</div>
		</>
	)
}

ReactDOM.createRoot(document.getElementById('root')).render(
	<Router>

		<App />
	</Router>
);
// <React.StrictMode>
{/* </React.StrictMode> */ }
