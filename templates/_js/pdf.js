{% js %}{% raw %}
const _pdfPromises = {};

const pdf = {
	async fillAndSavePDF(pdfUrl, textFields, checkboxFields, outputFileName, trackAs) {
		await pdf.loadPDFLib();
		const pdfDoc = await PDFLib.PDFDocument.load(await pdf.loadPDF(pdfUrl));
		const pdfForm = pdfDoc.getForm();

		pdfDoc.registerFontkit(fontkit);
		const customFont = await pdfDoc.embedFont(await pdf.loadFont());
		const rawUpdateFieldAppearances = pdfForm.updateFieldAppearances.bind(pdfForm);
		pdfForm.updateFieldAppearances = function () {
		   return rawUpdateFieldAppearances(customFont);
		};

		pdfDoc.getPage(0).drawText('Auf allaboutberlin.com ausgefüllt', { size: 9, x: 40, y: 20 });

		Object.entries(textFields || {}).forEach(([fieldName, value]) => {
			pdfForm.getTextField(fieldName).setText(value);
		});
		Object.entries(checkboxFields || {}).forEach(([fieldName, value]) => {
			if(value){
				pdfForm.getCheckBox(fieldName).check(value);
			}
			else {
				pdfForm.getCheckBox(fieldName).uncheck(value);
			}
		});

		const blob = new Blob(
			[new Uint8Array(await pdfDoc.save())],
			{type: "application/pdf"}
		);
		const link = document.createElement('a');
		link.href = window.URL.createObjectURL(blob);
		link.download = outputFileName;
		link.click();

		plausible(trackAs, { props: { stage: 'download' }});
	},
	async loadFont() {
		// The default font only supports ANSI characters, so we supply a unicode one.

		if(_pdfPromises.font) {
			return _pdfPromises.font;
		}
		_pdfPromises.font = fetch('/fonts/librefranklin-400-full.ttf')
			.then(r => r.arrayBuffer())
			.then(ab => new Uint8Array(ab));
		return _pdfPromises.font;
	},
	loadPDF(pdfUrl) {
		if(_pdfPromises[pdfUrl]) {
			return _pdfPromises[pdfUrl];
		}
		_pdfPromises[pdfUrl] = fetch(pdfUrl)
			.then(r => r.arrayBuffer())
			.then(ab => new Uint8Array(ab));
		return _pdfPromises[pdfUrl];
	},
	async loadPDFLib() {
		if(_pdfPromises.pdflib) {
			return _pdfPromises.pdflib;
		}

		_pdfPromises.pdflib = new Promise(function(resolve, reject) {
			const script = document.createElement('script');
			let resolved = false;
			script.type = 'text/javascript';
			script.src = '/js/pdflib.js';
			script.async = true;
			script.onerror = function(err) {
				reject(err, s);
			};
			script.onload = script.onreadystatechange = function() {
				if (!resolved && (!this.readyState || this.readyState == 'complete')) {
					resolved = true;
					resolve();
				}
			};
			const t = document.getElementsByTagName('script')[0];
			t.parentElement.insertBefore(script, t);
		});
		return _pdfPromises.pdflib;
	},
	async preloadPDF(pdfUrl) {
		// Async load of everything needed to edit a PDF
		return Promise.all([
			pdf.loadPDF(pdfUrl),
			pdf.loadFont(),
			pdf.loadPDFLib(),
		])
	}
};
{% endraw %}{% endjs %}