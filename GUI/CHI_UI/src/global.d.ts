declare module '*.png' {
	const value: string;
	export default value;
}
// declare module '*.json' {
// 	const value: string;
// 	export default value;
// }
declare namespace EagleAPI {
	interface Item {
		id: string;
		name: string;
		ext: string;
		width: number;
		height: number;
		url: string;
		isDeleted: boolean;
		annotation: string;
		tags: string[];
		AItags: string[];
		folders: string[];
		palettes: { [key: string]: string }[];
		size: number;
		star: number;
		importedAt: number;
		noThumbnail: boolean;
		noPreview: boolean;
		filePath: string;
		fileURL: string;
		thumbnailPath: string;
		thumbnailURL: string;
		metadataFilePath: string;
		status: string;

		save(): Promise<boolean>;
		replaceFile(filePath: string): Promise<boolean>;
		refreshThumbnail(): Promise<boolean>;
		setCustomThumbnail(thumbnailPath: string): Promise<boolean>;
		open(): Promise<void>;
	}

	interface ItemOptions {
		id?: string;
		ids?: string[];
		isSelected?: boolean;
		isUntagged?: boolean;
		isUnfiled?: boolean;
		keywords?: string[];
		tags?: string[];
		folders?: string[];
		ext?: string;
		annotation?: string;
		rating?: number;
		url?: string;
		shape?: 'square' | 'portrait' | 'panoramic-portrait' | 'landscape' | 'panoramic-landscape';
	}

	interface AddItemOptions {
		name?: string;
		website?: string;
		tags?: string[];
		folders?: string[];
		annotation?: string;
	}
}

declare namespace AutoTagging {
	type jsonDataObject = {
		version?: string;
		type?: { original?: string; translated?: string };
		tags?: {
			pending: { original?: string[]; translated?: string[] };
			confirmed: { original?: string[]; translated?: string[] };
		};
		status?: 'None' | 'Pending' | 'Confirmed' | 'NeedsUpdate';
		annotation: { original?: string; translated?: string };
	};
	type GenerateTagsRequestBody = {
		image_data: {
			image_path?: string;
			image_base64?: string;
			annotation?: string;
			tags?: string[];
		};
		token?: string;
		fake?: boolean;
	};
	type GenerateTagsResponseData = {
		success: boolean;
		image_data: {
			runTime?: string;
			type?: string;
			annotation?: { original?: string; translated?: string };
			tags?: string[];
		};
	};
}

declare type InspectorItem = {
	eagleItem: EagleAPI.Item;
	dataItem: AutoTagging.jsonDataObject;
	eagleTags: {
		typeTag: string; // "Type:xxx"
		processedTags: string[]; //["中文(english)","標籤(Tag)"]
		unprocessedTags: string[];
		statusTag: '待確認' | '須更新' | '無法標註' | null; //特殊分類標籤
	};
	dataTags: {
		pendingMergeTags: string[];
		confirmedMergeTags: string[];
	};
	tempTags: {
		newEagleTags: string[];
		confirmedEagleTags: string[];
		removedEagleTags: string[];
		newProcessedTags: string[];
		newProcessedOriginalTags: string[];
		newProcessedTranslatedTags: string[];
	};
	dataPath: string;
};

declare const eagle: {
	onPluginCreate: (callback: (plugin: { manifest: { name: string; version: string; logo: string }; path: string }) => void) => void;
	onPluginRun: (callback: () => void) => void;
	onThemeChanged: (callback: (theme: 'Auto' | 'LIGHT' | 'LIGHTGRAY' | 'GRAY' | 'DARK' | 'BLUE' | 'PURPLE') => void) => void;
	onPluginShow: (callback: () => void) => void;
	onPluginHide: (callback: () => void) => void;
	onLibraryChanged: (callback: (libraryPath: string) => void) => void;

	item: {
		get(options: EagleAPI.ItemOptions): Promise<EagleAPI.Item[]>;
		getAll(): Promise<EagleAPI.Item[]>;
		getById(itemId: string): Promise<EagleAPI.Item>;
		getByIds(itemIds: string[]): Promise<EagleAPI.Item[]>;
		getSelected(): Promise<EagleAPI.Item[]>;
		addFromURL(url: string, options: EagleAPI.AddItemOptions): Promise<string>;
		addFromBase64(base64: string, options: EagleAPI.AddItemOptions): Promise<string>;
		addFromPath(path: string, options: EagleAPI.AddItemOptions): Promise<string>;
		addBookmark(url: string, options: EagleAPI.AddItemOptions): Promise<string>;
		open(itemId: string): Promise<boolean>;
	};
	folder: {
		get(options: EagleAPI.ItemOptions): Promise<EagleAPI.Item[]>;
		getSelected(): Promise<EagleAPI.Item[]>;
	};
	dialog: {
		showOpenDialog(options: {
			title?: string;
			defaultPath?: string;
			buttonLabel?: string;
			filters?: { name: string; extensions: string[] }[];
			properties?: ('openFile' | 'openDirectory' | 'multiSelections' | 'showHiddenFiles' | 'createDirectory' | 'promptToCreate')[];
			message?: string;
		}): Promise<{ canceled: boolean; filePaths: string[] }>;

		showSaveDialog(options: {
			title?: string;
			defaultPath?: string;
			buttonLabel?: string;
			filters?: { name: string; extensions: string[] }[];
			properties?: ('openDirectory' | 'showHiddenFiles' | 'createDirectory')[];
		}): Promise<{ canceled: boolean; filePath?: string }>;

		showMessageBox(options: {
			message: string;
			title?: string;
			detail?: string;
			buttons?: string[];
			type?: 'none' | 'info' | 'error' | 'question' | 'warning';
		}): Promise<{ response: number }>;

		showErrorBox(title: string, content: string): Promise<void>;
	};
	notification: {
		show(options: {
			title: string;
			body?: string;
			description?: string;
			icon?: string;
			mute?: boolean;
			duration?: number;
		}): Promise<void>;
	};
	log: {
		debug(obj: any): void;
		info(obj: any): void;
		warn(obj: any): void;
		error(obj: any): void;
	};
	window: {
		show(): Promise<void>;
		showInactive(): Promise<void>;
		hide(): Promise<void>;
		focus(): Promise<void>;
		minimize(): Promise<void>;
		isMinimized(): Promise<boolean>;
		restore(): Promise<void>;
		maximize(): Promise<void>;
		unmaximize(): Promise<void>;
		isMaximized(): Promise<boolean>;
		setFullScreen(flag: boolean): Promise<void>;
		isFullScreen(): Promise<boolean>;
		setAspectRatio(aspectRatio: number): Promise<void>;
		setBackgroundColor(backgroundColor: string): Promise<void>;
		setSize(width: number, height: number): Promise<void>;
		setResizable(resizable: boolean): Promise<void>;
		isResizable(): Promise<boolean>;
		setAlwaysOnTop(flag: boolean): Promise<void>;
		isAlwaysOnTop(): Promise<boolean>;
		setPosition(x: number, y: number): Promise<void>;
		getPosition(): Promise<number[]>;
		setOpacity(opacity: number): Promise<void>;
		getOpacity(): Promise<number>;
		flashFrame(flag: boolean): Promise<void>;
		setIgnoreMouseEvents(ignore: boolean): Promise<void>;
		capturePage(rect?: { x: number; y: number; width: number; height: number }): Promise<Electron.NativeImage>;
		setReferer(url: string): void;
	};
	screen: {
		getCursorScreenPoint(): Promise<{ x: number; y: number }>;
		getPrimaryDisplay(): Promise<Display>;
		getAllDisplays(): Promise<Display[]>;
		getDisplayNearestPoint(point: { x: number; y: number }): Promise<Display>;
	};
};
