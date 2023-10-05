{% include '_js/vue.js' %}
{% include "_js/signaturePad.js" %}
{% js %}{% raw %}
Vue.component('signature', {
	props: {
		paddingX: Number,
		paddingY: Number,
		width: Number,
		height: Number,
	},
	data() {
		return {
			isEmpty: true,
			signaturePad: null,
		};
	},
	methods: {
		async addSignature() {
			const pdfResponse = await fetch('/documents/abmeldung-original.pdf');;
			const pdfBytes = new Uint8Array(await pdfResponse.arrayBuffer());

			const pdfDoc = await PDFLib.PDFDocument.load(pdfBytes);

			pdfDoc.getPage(0).drawText('Auf allaboutberlin.com ausgefüllt', { size: 9, x: 40, y: 20 });

			this.$refs.canvas.toBlob(async (pngBlob) => {
				const arrayBuffer = await pngBlob.arrayBuffer();
				const pngImage = await pdfDoc.embedPng(arrayBuffer);
				const pngDims = await pngImage.scale(0.5)
				const page = pdfDoc.getPage(0)
				console.log(page.getWidth())
				page.drawImage(pngImage, {
					x: 300,
					y: 10,
					width: pngImage.width / 4,
					height: pngImage.height / 4,
				});

				const blob = new Blob(
					[new Uint8Array(await pdfDoc.save())],
					{type: "application/pdf"}
				);
				const link = document.createElement('a');
				link.href=window.URL.createObjectURL(blob);
				link.download='test.pdf';
				link.click();
			});
		},
		onResize() {
			// The output resolution of the signature image
			const desiredOutputWidth = (this.width + this.paddingX * 2) * 2;

			// The size of the signature field in the UI
			const containerWidth = this.$refs.canvas.offsetWidth;
			const containerHeight = this.$refs.canvas.offsetHeight;
			const sizeRatio = Math.ceil(desiredOutputWidth / containerWidth);

			// The size of the canvas. A multiple of its real size, bigger than the desired output resolution
			this.$refs.canvas.width = containerWidth * sizeRatio;
			this.$refs.canvas.height = containerHeight * sizeRatio;
			this.$refs.canvas.style.maxWidth = `${containerWidth}px`;
			this.$refs.canvas.style.maxHeight = `${containerHeight}px`;

			this.$refs.canvas.getContext('2d').scale(sizeRatio, sizeRatio);

    		const backdropSizeRatio = ((this.width + this.paddingX * 2) / containerWidth);

			this.$refs.backdrop.style.width = `${this.width / backdropSizeRatio}px`;
			this.$refs.backdrop.style.height = `${this.height / backdropSizeRatio}px`;
			this.$refs.backdrop.style.top = `${this.paddingY / backdropSizeRatio}px`;
			this.$refs.backdrop.style.left = `${this.paddingX / backdropSizeRatio}px`;
		},
		onSignature(){
			this.signaturePad.toDataURL("image/svg+xml");
		}
	},
	mounted(){
		this.signaturePad = new SignaturePad(this.$refs.canvas, {
			minDistance: 1,
		});
	    this.signaturePad.addEventListener("beginStroke", () => {
	    	this.isEmpty = false;
		});

		this.resizeListener = window.addEventListener("resize", this.onResize);
		Vue.nextTick(() => {
			this.onResize();
		});
	},
	destroyed(){
		window.removeEventListener("resize", this.onResize);
	},
	template: `
		<div class="signature-input" @touchmove.prevent>
			<div class="signature-box" :class="{'empty': isEmpty}">
				<div class="backdrop" ref="backdrop"></div>
				<canvas
					class="canvas"
					ref="canvas"
					:width="width + paddingX * 2"
					:height="height + paddingY * 2"
					></canvas>
			</div>
		</div>
	`,
});
{% endraw %}{% endjs %}