import uniqueIdsMixin from '/js/vue/mixins/uniqueIds.mjs';
import Pagination from '/js/vue/components/pagination.mjs';
import { formatLongDate, isoDay } from '/js/utils/date.mjs';
import metadata from '/js/vue/tools/search.metadata.json' with { type: 'json' };

const TYPE_LABELS = {
	guides: { label: 'Guides', url: '/guides' },
	tools: { label: 'Tools', url: '/tools' },
	glossary: { label: 'Glossary', url: '/glossary' },
	newsletter: { label: 'Newsletter', url: '/newsletter' },
	docs: { label: 'Documents' },
	pages: { label: 'Pages' },
	forum_thread: { label: 'Forum', url: '/forum' },
	forum_reply: { label: 'Forum', url: '/forum' },
};

export default {
	mixins: [uniqueIdsMixin],
	components: { Pagination },
	data() {
		const params = new URLSearchParams(window.location.search);
		return {
			metadata,
			query: (params.get('q') || '').trim(),
			page: Math.max(1, parseInt(params.get('page'), 10) || 1),
			results: [],
			totalHits: 0,
			totalPages: 0,
			status: '',
			isLoading: false,
			debounceTimer: null,
			minQueryLength: 3,
		};
	},
	mounted() {
		this.updateResults();
	},
	watch: {
		query() {
			this.page = 1;
			this.updateUrl();
			clearTimeout(this.debounceTimer);
			this.debounceTimer = setTimeout(() => this.updateResults(), 300);
		},
		page() {
			this.updateUrl();
			this.updateResults().then(() => {
				this.$el.scrollIntoView({ behavior: 'smooth', block: 'start' });
			});
		},
	},
	methods: {
		formatDate: formatLongDate,
		formatDateIso: isoDay,
		typeInfo(type) {
			return TYPE_LABELS[type] || { label: type };
		},
		updateUrl() {
			const query = this.query.trim();
			const url = new URL(window.location);
			if (query) {
				url.searchParams.set('q', query);
			} else {
				url.searchParams.delete('q');
			}
			if (this.page > 1) {
				url.searchParams.set('page', this.page);
			} else {
				url.searchParams.delete('page');
			}
			history.replaceState(null, '', url);
		},
		updateResults() {
			const query = this.query.trim();
			if (query.length < this.minQueryLength) {
				this.results = [];
				this.totalHits = 0;
				this.totalPages = 0;
				this.status = '';
				return Promise.resolve();
			}

			this.isLoading = true;
			return fetch(`/api/search/?q=${encodeURIComponent(query)}&page=${this.page}`)
				.then(response => {
					if (!response.ok) throw new Error('Search failed');
					return response.json();
				})
				.then(data => {
					this.results = (data.results || []).map(result => ({
						...result,
						date: new Date(result.date * 1000),
					}));
					this.totalHits = data.total_hits || 0;
					this.totalPages = data.total_pages || 0;
				})
				.catch(() => {
					this.results = [];
					this.totalHits = 0;
					this.totalPages = 0;
					this.status = 'Search is currently unavailable. The error is on our side.';
				})
				.finally(() => {
					this.isLoading = false;
				});
		},
	},
	template: `
		<div>
			<search title="Search All About Berlin" class="search-form no-print">
				<label title="Search keyword">
					<input
						:id="uid('query')"
						type="search"
						v-model="query"
						placeholder="Search this website"
						tabindex="0"
						aria-autocomplete="list"
						:aria-controls="uid('results')"
						aria-label="Search this website"
						autocomplete="off">
					<svg width="12" height="13" viewBox="0 0 12 13" aria-hidden="true">
						<title>Search</title>
						<g stroke-width="1.5" stroke="currentColor" fill="none"><path d="M11.29 11.71l-4-4"/><circle cx="5" cy="5" r="4"/></g>
					</svg>
				</label>
			</search>
			<p role="status" v-if="query">
				{{ totalHits }} result{{ totalHits === 1 ? '' : 's' }} found for “{{ query }}”
			</p>
			<p v-if="isLoading" class="loading">Loading results…</p>
			<ol class="entry-previews" :id="uid('results')" :aria-busy="isLoading ? 'true' : 'false'" aria-label="Search results">
				<li class="entry-preview" :class="result.type" v-for="result in results" :key="result.url">
					<div class="post-meta">
						<nav class="breadcrumbs" aria-label="Breadcrumbs">
							<ol>
								<li>
									<a v-if="typeInfo(result.type).url" :href="typeInfo(result.type).url">{{ typeInfo(result.type).label }}</a>
									<template v-else>{{ typeInfo(result.type).label }}</template>
								</li>
								<li class="title">
									{{ result.type === 'forum_reply' ? 'Reply to ' : '' }}<a :href="result.url" rel="bookmark" v-html="result.title"></a>
								</li>
							</ol>
						</nav>
						<div class="date">
							<time :datetime="formatDateIso(result.date)">{{ formatDate(result.date) }}</time>
						</div>
					</div>
					<p v-if="result.snippet" v-html="result.snippet"></p>
				</li>
			</ol>
			<pagination :value="page" @input="page = $event" :page-count="totalPages"></pagination>
		</div>
	`,
};
