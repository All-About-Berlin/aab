import { formatLongDate } from '/js/utils/date.mjs';

export default {
	props: ['comment'],
	computed: {
		isoDate() {
			return new Date(this.comment.creation_date).toISOString();
		},
		prettyDate() {
			return formatLongDate(this.comment.creation_date);
		},
	},
	template: `
		<li class="comment">
			<div class="comment-meta">
				<span itemprop="author" itemscope itemtype="https://schema.org/Person">
					<span itemprop="name" v-text="comment.user.username"></span>
				</span>
				<time itemprop="datePublished" :datetime="isoDate" v-text="prettyDate"></time>
			</div>
			<div class="message" itemprop="text" v-text="comment.message"></div>
			<ol class="comments" v-if="comment.children.length">
				<comment :comment="c" v-for="c in comment.children" :key="c.id"></comment>
			</ol>
		</li>
	`,
}