export default {
	props: {
		static: Boolean,
	},
	template: `
		<details class="collapsible" :open="static">
			<summary :hidden="static">
				<slot name="header"></slot>
			</summary>
			<slot></slot>
		</details>
	`,
}