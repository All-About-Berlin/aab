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
			oldControlWidth: null,
			resizeTimeout: null,
			signatureData: null,
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

			// The size of the output image
			const outputWidth = (this.width + this.paddingX * 2) * 2;
			const outputHeight = (this.height + this.paddingY * 2) * 2;

			// The size of the signature control
			const containerWidth = this.$el.offsetWidth;
			const containerHeight = (outputHeight / outputWidth) * containerWidth;

			const canvasPixelDensity = Math.ceil(outputWidth / containerWidth);

			// The size of the canvas. A multiple of its real size, bigger than the desired output resolution
			this.$refs.canvas.width = containerWidth * canvasPixelDensity;
			this.$refs.canvas.height = containerHeight * canvasPixelDensity;
			this.$refs.canvas.style.maxWidth = `${containerWidth}px`;
			this.$refs.canvas.style.maxHeight = `${containerHeight}px`;
			this.$refs.canvas.getContext('2d').scale(canvasPixelDensity, canvasPixelDensity);

			// The size of the backdrop
    		const backdropSizeRatio = (this.width + this.paddingX * 2) / containerWidth;
			this.$refs.backdrop.style.width = `${this.width / backdropSizeRatio}px`;
			this.$refs.backdrop.style.height = `${this.height / backdropSizeRatio}px`;
			this.$refs.backdrop.style.top = `${this.paddingY / backdropSizeRatio}px`;
			this.$refs.backdrop.style.left = `${this.paddingX / backdropSizeRatio}px`;

			// Backup the signature. When the resize is finish, restore the scaled signature.
			if(!this.signaturePad.isEmpty()){
				this.signatureData = this.signaturePad.toData();
				this.signaturePad.clear();
				this.oldControlWidth = this.$el.getBoundingClientRect().width - 2;

				// Debounce the resize event
				clearTimeout(this.resizeTimeout);
				this.resizeTimeout = setTimeout(() => {
					// Restore the signature, scaled to the new canvas
					const signatureResizeRatio = (this.$el.getBoundingClientRect().width - 2) / this.oldControlWidth;
					this.signatureData.forEach((pointGroup) => {
						pointGroup.points.forEach((point) => {
							point.x *= signatureResizeRatio;
							point.y *= signatureResizeRatio;
						});
					});
					this.signaturePad.fromData(this.signatureData);
					this.signatureData = null;
					console.log('Resize')
				}, 100);
			}
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
		<div class="signature-input" :class="{'empty': isEmpty}" @touchmove.prevent>
			<div class="signature-box">
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