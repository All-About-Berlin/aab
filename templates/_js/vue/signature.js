{% include '_js/vue.js' %}
{% include "_js/signaturePad.js" %}
{% js %}{% raw %}
Vue.component('signature', {
	props: {
		paddingX: Number,
		paddingY: Number,
		width: Number,
		height: Number,
		value: Array,
	},
	data() {
		return {
			isEmpty: true,
			oldControlWidth: null,
			resizeTimeout: null,
			signatureData: null,
			signaturePad: null,
			showEraseButton: false,
		};
	},
	methods: {
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
			this.$refs.backdrop.style.top = `${(this.height + this.paddingY) / backdropSizeRatio}px`;
			this.$refs.erase.style.top = `${(this.height + this.paddingY) / backdropSizeRatio}px`;

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
				}, 100);
			}
		},
		clearSignature(){
			this.signaturePad.clear();
			this.isEmpty = true;
			this.showEraseButton = false;
			this.$emit('input', this.signaturePad.toData());
			this.$refs.canvas.toBlob(blob => this.$emit('signature', blob));
		},
	},
	mounted(){
		this.signaturePad = new SignaturePad(this.$refs.canvas, {
			minDistance: 1,
		});

		if(this.value){
			this.signaturePad.fromData(this.value);
			this.isEmpty = false;
		}

	    this.signaturePad.addEventListener("beginStroke", () => {
	    	this.isEmpty = false;
	    	this.showEraseButton = false;
		});

	    this.signaturePad.addEventListener("endStroke", () => {
	    	this.$emit('input', this.signaturePad.toData());
	    	this.$refs.canvas.toBlob(blob => this.$emit('signature', blob));
	    	this.showEraseButton = true;
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
				<a class="erase" v-show="showEraseButton" ref="erase" href="#" @click.prevent="clearSignature" title="Erase the signature">Erase</a>
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