{% include '_js/vue.js' %}
{% js %}{% raw %}
Vue.component('file-input', {
	props: {
		value: Array,
		accept: String,
		required: Boolean,
		type: {
			type: String,
			default: 'files',
		}
	},
	computed: {
		isValid(){
			return this.value.every(this.fileTypeIsValid);
		},
	},
	methods: {
		onFilesSelected(event){
			Array.from(event.target.files).forEach(f => {
				const fileExists = this.value.some(
					curr => {
						return f.name === curr.name && f.size === curr.size;
					}
				);

				if(!fileExists){
					this.value.push(f);
				}
			});
			event.target.value = null;
		},
		openFileInput(){
			this.$refs.fileInput.click();
		},
		removeFile(file){
			const fileIndex = this.value.indexOf(file);
			if (fileIndex !== -1) {
				this.value.splice(fileIndex, 1);
			}
		},
		fileImage(file){
			return URL.createObjectURL(file);
		},
		fileTypeIsValid(file){
			return this.accept
				.split(',')
				.map(t => t.trim())
				.some(t => {
					// t is a mimetype or an extension
					return file.type == t || file.name.endsWith(t);
				});
		}
	},
	watch: {
		files(newFiles){
			if(this.isValid){
				this.$emit('input', newFiles);
			}
		},
	},
	template: `
		<fieldset class="file-input">
			<ul v-if="value.length > 0">
				<li v-for="file in value" :class="{'error': !fileTypeIsValid(file)}">
					<div class="placeholder" v-if="file.type === 'application/pdf'">
						{% endraw %}{% include "_css/icons/pdf.svg" %}{% raw %}
					</div>
					<div class="placeholder" v-if="!fileTypeIsValid(file)">⚠</div>
					<img v-if="file.type.startsWith('image/')" :src="fileImage(file)">
					<div>
						{{ file.name }}
						<small class="input-error" v-if="!fileTypeIsValid(file)">This file type is not supported.</small>
					</div>
					<a class="icon close" href="#" @click.prevent="removeFile(file)" title="Remove this file"></a>
				</li>
			</ul>
			<div class="placeholder" v-if="value.length === 0"><slot></slot></div>
			<input ref="fileInput" type="file" multiple :accept="accept" @change="onFilesSelected">
			<div class="buttons">
				<button ref="button" class="button" :class="{primary: value.length === 0}" for="file-input" @click="openFileInput">
					<i class="icon add" aria-hidden="true"></i>
					{{ (value.length > 0 ? 'Add more ' : 'Add ') + type }}
				</button>
			</div>
		</fieldset>
	`,
});
{% endraw %}{% endjs %}