const recordErrorAndPrint = async (error: any) => {
	console.error(error);
	await eagle.log.error(error);
};
export { recordErrorAndPrint };
