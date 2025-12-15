// import fs from 'fs';
import { copyFile } from 'fs';
import { version } from '../../manifest.json';
import { recordErrorAndPrint } from './error-handler';
const fs = require('fs');
const emptyJson: AutoTagging.jsonDataObject = {
	version,
	type: { original: '', translated: '' },
	tags: { pending: { original: [], translated: [] }, confirmed: { original: [], translated: [] } },
	status: 'None',
	annotation: { original: '', translated: '' },
};
class JsonFileHandler {
	static readJsonFile(filePath: string): AutoTagging.jsonDataObject {
		try {
			if (!fs.existsSync(filePath)) return emptyJson;
			const fileContent = fs.readFileSync(filePath, 'utf-8');
			let data = JSON.parse(fileContent) as AutoTagging.jsonDataObject;
			const { version } = data;
			if (version === 'v1.1.0-alpha') data = this.parse_v1_1_0(data) as AutoTagging.jsonDataObject;

			const { type, tags, status } = data;
			// validate data
			if (typeof type !== 'object' || typeof tags !== 'object' || typeof status !== 'string') return emptyJson;
			const { pending, confirmed } = tags;
			if (
				typeof pending !== 'object' ||
				typeof confirmed !== 'object' ||
				typeof type.original !== 'string'
				// ||typeof type.translated !== 'string'
			)
				return emptyJson;
			const { original, translated } = pending;
			const { original: confirmedOriginal, translated: confirmedTranslated } = confirmed;
			if (
				!Array.isArray(original) ||
				!Array.isArray(translated) ||
				!Array.isArray(confirmedOriginal) ||
				!Array.isArray(confirmedTranslated)
			)
				return emptyJson;
			return data;
		} catch (error) {
			recordErrorAndPrint(error);
			const copyFile = filePath.replace('.json', `_${new Date().getTime()}.json`);
			fs.copyFile(filePath, copyFile, (err) => {
				if (err) console.error('Error Found:', err);
			});
			return emptyJson;
		}
	}

	static parse_v1_1_0(data): any {
		try {
		} catch (error) {
			throw new Error('解析data.json時發生錯誤: 無法轉換v1.1.0-alpha版本檔案至目前版本, ' + error.message);
		}
		return data;
	}

	static writeJsonFile(filePath: string, data: object): void {
		try {
			const jsonData = JSON.stringify(data);
			fs.writeFileSync(filePath, jsonData, 'utf-8');
		} catch (error) {
			recordErrorAndPrint(error);
		}
	}
}

export default JsonFileHandler;
