{% include '_js/vue.js' %}
{% js %}{% raw %}
Vue.component('file-input', {
	props: {
		accept: String,
		required: Boolean,
		type: {
			type: String,
			default: 'files',
		}
	},
	data() {
		return {
			files: [],
		};
	},
	methods: {
		onFilesSelected(event){
			Array.from(event.target.files).forEach(f => {

				const fileExists = this.files.some(
					curr => {
						return f.name === curr.name && f.size === curr.size && f.lastModified === curr.lastModified;
					}
				);

				if(!fileExists){
					this.files.push(f);
				}
			});
			event.target.value = null;
		},
		openFileInput(){
			this.$refs.fileInput.click();
		},
		removeFile(file){
			const fileIndex = this.files.indexOf(file);
			if (fileIndex !== -1) {
				this.files.splice(fileIndex, 1);
			}
		},
		fileImage(file){
			return URL.createObjectURL(file);
		},
	},
	template: `
		<div class="file-input">
			<ul v-if="files.length > 0">
				<li v-for="file in files">
					<div class="placeholder" v-if="file.type === 'application/pdf'">
						{% endraw %}{% include "_css/icons/pdf.svg" %}{% raw %}
					</div>
					<img v-if="file.type.startsWith('image/')" :src="fileImage(file)">
					{{ file.name }}
					<a class="icon close" href="#" @click.prevent="removeFile(file)" title="Remove this file"></a>
				</li>
			</ul>
			<div class="placeholder" v-if="files.length === 0"><slot></slot></div>
			<input ref="fileInput" type="file" multiple :accept="accept" @change="onFilesSelected">
			<div class="buttons">
				<button class="button" :class="{primary: files.length === 0}" for="file-input" @click="openFileInput">
					<i class="icon add" aria-hidden="true"></i>
					{{ (files.length > 0 ? 'Add more ' : 'Add ') + type }}
				</button>
			</div>
		</div>
	`,
});
{% endraw %}{% endjs %}