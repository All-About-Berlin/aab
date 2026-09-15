import uniqueIdsMixin from '/js/vue/mixins/uniqueIds.mjs';
import Pagination from '/js/vue/components/pagination.mjs';
import { formatLongDate, isoDay } from '/js/utils/date.mjs';
import metadata from '/js/vue/tools/search.metadata.json' with { type: 'json' };

export default {
	mixins: [uniqueIdsMixin],
	components: { Pagination },
	data() {
		const params = new URLSearchParams(window.location.search);
		const typeParam = (params.get('type') || '').trim();
		return {
			metadata,
			typeFilters: {
				docs: 'Documents',
				forum: 'Forum',
				glossary: 'Glossary',
				guides: 'Guides',
				newsletter: 'Newsletter',
				tools: 'Tools',
			},
			type: null,
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
		this.type = this.typeFilters.some(t => t.value === typeParam) ? typeParam : '',
		this.updateResults();
	},
	watch: {
		query() {
			this.page = 1;
			this.updateUrl();
			clearTimeout(this.debounceTimer);
			this.debounceTimer = setTimeout(() => this.updateResults(), 300);
		},
		type() {
			this.page = 1;
			this.updateUrl();
			this.updateResults();
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
		contentType(type) {
			return {
				guides: {
					label: 'Guides',
					url: '/guides'
				},
				tools: {
					label: 'Tools',
					url: '/tools'
				},
				glossary: {
					label: 'Glossary',
					url: '/glossary'
				},
				newsletter: {
					label: 'Newsletter',
					url: '/newsletter'
				},
				docs: {
					label: 'Documents'
				},
				pages: {
					label: 'Pages'
				},
				forum_thread: {
					label: 'Forum',
					url: '/forum'
				},
				forum_reply: {
					label: 'Forum',
					url: '/forum'
				},
			}[type] || { label: type };
		},
		updateUrl() {
			const query = this.query.trim();
			const url = new URL(window.location);
			if (query) {
				url.searchParams.set('q', query);
			} else {
				url.searchParams.delete('q');
			}
			if (this.type) {
				url.searchParams.set('type', this.type);
			} else {
				url.searchParams.delete('type');
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
			const params = new URLSearchParams({ q: query, page: this.page });
			if (this.type) params.set('type', this.type);
			return fetch(`/api/search/?${params}`)
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
			<search title="Search All About Berlin" class="form-group no-label">
				<div class="input-group">
					<input
						:id="uid('query')"
						type="search"
						v-model="query"
						placeholder="Search this website"
						tabindex="0"
						aria-autocomplete="list"
						:aria-controls="uid('results')"
						aria-label="Search query"
						autocomplete="off"
						autofocus>
					<select v-model="type" aria-label="Filter result types">
						<option value="">Search everything</option>
						<option disabled>──────────</option>
						<option v-for="filter in typeFilters" :key="filter.value" :value="filter.value">{{ filter.label }}</option>
					</select>
				</div>
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
									<a v-if="contentType(result.type).url" :href="contentType(result.type).url">{{ contentType(result.type).label }}</a>
									<template v-else>{{ contentType(result.type).label }}</template>
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
