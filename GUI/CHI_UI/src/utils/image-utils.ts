// const sharp = require('sharp');
// import sharp from 'sharp';

async function resizeImage(inputPath: string, shortEdge: number = 512): Promise<Buffer | null> {
	/**
	 * Resize an image maintaining the aspect ratio by specifying the short edge resolution.
	 *
	 * @param inputPath: string, path to the input image
	 * @param shortEdge: number, the target resolution for the short edge
	 * @return: Promise<Buffer | null>, Buffer of the resized image
	 */
	try {
		const sharp = await require('sharp');
		// Load image metadata
		const metadata = await sharp(inputPath).metadata();

		if (!metadata.width || !metadata.height) {
			throw new Error('Unable to retrieve image dimensions.');
		}

		const width = metadata.width;
		const height = metadata.height;

		// Determine scaling factor
		const scale = width < height ? shortEdge / width : shortEdge / height;

		// Calculate new dimensions
		const newWidth = Math.round(width * scale);
		const newHeight = Math.round(height * scale);

		// Resize the image while preserving alpha channel
		const buffer = await sharp(inputPath)
			.resize(newWidth, newHeight)
			.toFormat(metadata.format === 'png' || metadata.hasAlpha ? 'png' : 'jpeg')
			.toBuffer();

		return buffer;
	} catch (error) {
		console.error(`Error resizing image: ${error}`);
		return null;
	}
}

async function encodeImageToBase64(buffer: Buffer): Promise<string | null> {
	/**
	 * Encode an image buffer to Base64.
	 *
	 * @param buffer: Buffer, image buffer
	 * @return: Promise<string | null>, Base64 encoded string of the image
	 */
	try {
		const image_base64 = `data:image/jpeg;base64,${buffer.toString('base64')}`;
		return image_base64;
	} catch (error) {
		console.error(`Error encoding image to Base64: ${error}`);
		return null;
	}
}

export { encodeImageToBase64, resizeImage };
