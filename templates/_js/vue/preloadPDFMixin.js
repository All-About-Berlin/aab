{% js %}
const preloadPDFMixin = {
	// Preloads PDF generation code when the user starts filling the HTML form
	data: function () {
		return {
			stageIndex: 0,
			pdfUrl: null,
			pdfPreloadPromise: null,
		}
	},
	watch: {
		stageIndex(newStageIndex){
			if(newStageIndex > 0 && this.pdfPreloadPromise === null){
				this.pdfPreloadPromise = pdf.preloadPDF(this.pdfUrl);
			}
		},
	}
}
{% endjs %}