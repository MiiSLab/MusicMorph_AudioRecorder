import axios from 'axios';
import icon from '../assets/icon';
import { recordErrorAndPrint } from './error-handler';
import { encodeImageToBase64, resizeImage } from './image-utils';

class APIHandler {
	host: string;
	openAI_token: string | null = null;
	fakeGenerate: boolean = false;
	constructor(host: string) {
		this.host = host;
		axios.defaults.baseURL = host;
	}

	setHost(host: string) {
		this.host = host;
		axios.defaults.baseURL = host;
	}

	setAIToken(token: string) {
		this.openAI_token = token;
	}
	setFakeGenerate(fakeGenerate: boolean) {
		this.fakeGenerate = fakeGenerate;
	}

	async showErrorBox(title: string, message: string, detail: string) {
		console.log(' [debug] detail: ', detail);
		if (detail === 'Network Error') detail = ': 請確認IP是否正確或Server是否開啟';
		if (detail === "Failed to construct 'URL': Invalid URL") detail = ': IP格式錯誤，請確認IP是否正確';
		await eagle.notification.show({
			title: title,
			body: `${message ?? ``}\n${detail ?? ``}`,
			mute: false,
			duration: 5000,
			icon: icon,
		});
		// await eagle.dialog.showErrorBox(title, `${message}\n${detail}`);
	}
	async generateTags(
		imagePath: string,
		annotation: string = '',
		tags: string[] = []
	): Promise<AutoTagging.GenerateTagsResponseData['image_data']> {
		const url = `/api/tagging/generate-tags`;
		try {
			const resizedBuffer = await resizeImage(imagePath);
			if (!resizedBuffer) {
				throw new Error('Failed to resize image.');
			}

			const imageBase64 = await encodeImageToBase64(resizedBuffer);
			if (!imageBase64) {
				throw new Error('Failed to encode image to Base64.');
			}

			const requestBody: AutoTagging.GenerateTagsRequestBody = {
				image_data: { image_base64: imageBase64, annotation, tags },
				token: this.openAI_token,
				fake: this.fakeGenerate,
			};

			const response = await axios.post(url, requestBody);
			await eagle.log.info(`POST request to ${url}`);
			return response.data.image_data as AutoTagging.GenerateTagsResponseData['image_data'];
		} catch (error) {
			recordErrorAndPrint(error);
			await this.showErrorBox(`錯誤 ${error.status ?? ''}`, '生成標籤時發生錯誤', error.response?.data?.message ?? error.message);
		}
	}

	async translateTags(tags: string[]): Promise<{ original: string[]; translated: string[] }> {
		const url = `/api/tagging/translate-tags`;
		try {
			const response = await axios.post(url, { tags });
			const { original, translated } = response.data;
			await eagle.log.info(`POST request to ${url}`);
			return { original, translated };
		} catch (error) {
			recordErrorAndPrint(error);
			await this.showErrorBox(`錯誤 ${error.status ?? ''}`, '翻譯標籤時發生錯誤', error.response?.data?.message ?? error.message);
		}
	}

	async confirmTagsAndCreateEmbedding(
		imagePath: string,
		annotation: string = '',
		tags: string[] = [],
		image_id: string
	): Promise<boolean> {
		const url = `/api/tagging/generate-embedding`;
		try {
			const resizedBuffer = await resizeImage(imagePath);
			if (!resizedBuffer) {
				throw new Error('Failed to resize image.');
			}

			const imageBase64 = await encodeImageToBase64(resizedBuffer);
			if (!imageBase64) {
				throw new Error('Failed to encode image to Base64.');
			}

			const requestBody = { image_data: { image_base64: imageBase64, annotation, tags, image_id } };
			const response = await axios.post(url, requestBody);
			await eagle.log.info(`POST request to ${url}`);
			return response.data.success;
		} catch (error) {
			recordErrorAndPrint(error);
			console.log(' [debug] error.message: ', error.message);
			await this.showErrorBox(`錯誤 ${error.status ?? ''}`, '確認標籤時發生錯誤', error.response?.data?.message ?? error.message);
		}
	}

	async translateAnnotation(annotation: string, mode: 'en2zh' | 'zh2en'): Promise<{ original: string; translated: string }> {
		const url = `/api/tagging/translate-annotation`;
		try {
			const response = await axios.post(url, { annotation, mode });
			const {
				annotation: { original, translated },
			} = response.data;
			await eagle.log.info(`POST request to ${url}`);
			return { original, translated };
		} catch (error) {
			recordErrorAndPrint(error);
			await this.showErrorBox(`錯誤 ${error.status ?? ''}`, '翻譯標籤時發生錯誤', error.response?.data?.message ?? error.message);
		}
	}
}

const apiHandler = new APIHandler('http://localhost:8080');
export default apiHandler;
