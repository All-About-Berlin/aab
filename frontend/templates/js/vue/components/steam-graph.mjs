import uniqueIdsMixin from '/js/vue/mixins/uniqueIds.mjs';

// Height and vertical layout are fixed; width is reactive (see svgWidth data property)

export default {
	mixins: [uniqueIdsMixin],
	props: {
		data: { type: Object, required: true },
	},
	data() {
		return {
			resizeObserver: null,

			// Size of the entire <svg> element
			fullHeight: 200, // Fixed
			fullWidth: 600,  // Reactive to element width

			selectedMonth: null,
			lockedMonth: null,
		};
	},
	mounted() {
		// When the element size changes, resize the graph. This lets us maintain the same font sizes as the parent page.
		this.resizeObserver = new ResizeObserver(([entry]) => {
			this.fullWidth = Math.max(entry.contentRect.width, 600);
		});
		this.resizeObserver.observe(this.$el);
	},
	beforeDestroy() {
		this.resizeObserver.disconnect();
	},
	computed: {
		chart() {
			const padding = 3;
			const monthWidth = this.fullWidth / (this.monthlyData.length || 1);
			const xAxisHeight = 25;

			const left = monthWidth / 2;
			const right = this.fullWidth - monthWidth / 2;

			const top = padding;
			const bottom = this.fullHeight - xAxisHeight;

			const height = bottom - top;
			const width = this.fullWidth - left - right;

			return {
				width, height, top, left, bottom, right, monthWidth, xAxisHeight,
				xAxisTop: bottom + xAxisHeight,
				viewbox: `0 0 ${this.fullWidth} ${this.fullHeight}`,
			};
		},

		monthlyData() {
			const allMonths = this.data?.start_to_finish?.by_month;
			const firstMonthWithData = allMonths.findIndex(d => d.median != null);
			return firstMonthWithData === -1 ? [] : allMonths.slice(firstMonthWithData);
		},

		monthShapes(){
			return this.monthlyData.map(
				(monthData, index) => {
					const [year, isoMonth] = monthData.month.split('-');
					return {
						xMiddle: this.xForIndex(index),
						xStart: this.xForIndex(index) - this.chart.monthWidth / 2,
						xEnd: this.xForIndex(index) + this.chart.monthWidth / 2,
						width: this.chart.monthWidth,
						y: this.yForValue(monthData.median),
						monthLabel: this.formatMonth(monthData.month),
						yearLabel: (index === 0 || isoMonth === '01') ? year : null,

						// Right-align the last months to make them fit in the frame
						isLastMonths: index >= this.monthlyData.length - 3,
					};
				}
			);
		},

		yMax() {
			// Largest value on the y axis
			const yValues = this.monthlyData
				.flatMap(monthData => [monthData.percentile_20, monthData.percentile_80, monthData.median])
				.filter(y => y != null);
			return Math.max(...yValues) || 1;
		},

		varianceBandPath() {
			const segments = this.contiguousSegments(
				d => d.median != null,
				(d, index) => ({
					x: this.xForIndex(index),
					yTop: this.yForValue(d.percentile_80 || d.median),
					yBottom: this.yForValue(d.percentile_20 || d.median),
					yMedian: this.yForValue(d.median),
				}),
			);
			const half = this.chart.monthWidth / 2;
			const paths = segments.filter(s => s.length >= 2).map(points => {
				const first = points[0];
				const last = points[points.length - 1];
				const tapered = [
					{ x: first.x - half, yTop: first.yMedian, yBottom: first.yMedian },
					...points,
					{ x: last.x + half, yTop: last.yMedian, yBottom: last.yMedian },
				];
				const topEdge = this.smoothPath(tapered.map(p => ({ x: p.x, y: p.yTop })));
				const bottomEdge = this.smoothPath([...tapered].reverse().map(p => ({ x: p.x, y: p.yBottom })));
				return `${topEdge} ${bottomEdge.replace(/^M/, 'L')}Z`;
			});
			return paths.join(' ') || null;
		},

		allMedianSegments() {
			return this.contiguousSegments(
				d => d.median != null,
				(d, index) => ({ x: this.xForIndex(index), y: this.yForValue(d.median) }),
			);
		},
		medianLinePath() {
			return this.allMedianSegments
				.filter(s => s.length >= 2)
				.map(points => this.smoothPath(points))
				.join(' ') || null;
		},

		// This line fills gaps in the data, and at each edge of the graph
		medianDottedLinePath() {
			const half = this.chart.monthWidth / 2;
			const padding = 2; // For the rounded ends of the line
			const segs = this.allMedianSegments;
			if (!segs.length) return null;
			const paths = [];
			segs.forEach((points, i) => {
				const first = points[0];
				const last = points[points.length - 1];
				if (i === 0) {
					paths.push(this.smoothPath([{ x: 0 + padding, y: first.y }, { x: first.x, y: first.y }]));
				}
				if (i === segs.length - 1) {
					paths.push(this.smoothPath([{ x: last.x, y: last.y }, { x: this.fullWidth - padding, y: last.y }]));
				}
				if (i < segs.length - 1) {
					const nextFirst = segs[i + 1][0];
					paths.push(this.smoothPath([last, nextFirst]));
				}
			});
			return paths.join(' ') || null;
		},
	},
	methods: {
		xForIndex(index) {
			return (this.chart.monthWidth * index) + this.chart.left;
		},
		yForValue(value) {
			if (value == null) return null;
			// SVG coordinates start from the bottom. Higher value = lower y
			return this.chart.bottom - (value / this.yMax) * this.chart.height;
		},
		formatMonth(yearMonth) {
			const [year, month] = yearMonth.split('-');
			return new Date(+year, +month - 1).toLocaleDateString('en-GB', { month: 'long', year: 'numeric' });
		},
		smoothPath(points) {
			// Cubic Bézier curve through each point, using horizontal control points
			// offset by ⅓ of the x-distance
			return points.map((point, index) => {
				if (index === 0) return `M${point.x},${point.y}`;
				const prev = points[index - 1];
				const controlOffset = (point.x - prev.x) / 3;
				const cp1 = `${prev.x + controlOffset},${prev.y}`;
				const cp2 = `${point.x - controlOffset},${point.y}`;
				return `C${cp1} ${cp2} ${point.x},${point.y}`;
			}).join(' ');
		},
		lockMonth(index) {
			if (this.lockedMonth === this.monthlyData[index]) {
				this.lockedMonth = null;
				this.selectedMonth = null;
			} else {
				this.lockedMonth = this.monthlyData[index];
				this.selectedMonth = this.lockedMonth;
			}
		},
		contiguousSegments(predicate, mapper) {
			const segments = [];
			let current = [];
			this.monthlyData.forEach((d, index) => {
				if (predicate(d)) {
					current.push(mapper(d, index));
				} else if (current.length) {
					segments.push(current);
					current = [];
				}
			});
			if (current.length) segments.push(current);
			return segments;
		},
	},
	template: `
		<div class="steam-graph">
			<figure>
				<svg :viewBox="chart.viewbox" width="100%" :height="fullHeight" role="img">
					<title>Immigration office wait times, by month</title>
					<defs>
						<clipPath v-for="(month, index) in monthShapes" :key="index" :id="uid('clip-' + index)">
							<rect :x="month.xStart" y="0" :width="month.width" :height="fullHeight" />
						</clipPath>
					</defs>
					<path class="variance-band" v-if="varianceBandPath" :d="varianceBandPath"/>
					<path class="median-line" v-if="medianLinePath" :d="medianLinePath"/>
					<path class="median-line median-dotted-line" v-if="medianDottedLinePath" :d="medianDottedLinePath"/>
					<g class="month" :class="{ selected: selectedMonth === monthlyData[index] }" v-for="(month, index) in monthShapes" :key="index"
						@mouseenter="selectedMonth = monthlyData[index]"
						@mouseleave="selectedMonth = lockedMonth"
						@click="lockMonth(index)"
					>
						<rect
							class="datapoint-bounds"
							:x="month.xStart" y="0"
							:width="month.width" :height="fullHeight"
						/>
						<path
							class="variance-band-highlight"
							v-if="varianceBandPath"
							:d="varianceBandPath"
							:clip-path="'url(#' + uid('clip-' + index) + ')'"
						/>
						<circle
							class="median-point"
							v-if="month.y !== null"
							:cx="month.xMiddle" :cy="month.y" r="3"
						/>
						<line
							class="x-axis-tick"
							:x1="month.xStart"
							:x2="month.xStart"
							:y1="chart.bottom + (month.yearLabel ? chart.xAxisHeight : 0)"
							:y2="chart.bottom - 5"
						/>
						<text
							class="month-label"
							v-text="month.monthLabel"
							:x="month.isLastMonths ? month.xEnd - 8 : month.xStart + 8" :y="chart.xAxisTop"
							:text-anchor="month.isLastMonths ? 'end' : 'start'"
						/>
						<text
							class="year-label"
							v-if="month.yearLabel"
							v-text="month.yearLabel"
							:x="month.isLastMonths ? month.xEnd - 8 : month.xStart + 8" :y="chart.xAxisTop"
							:text-anchor="month.isLastMonths ? 'end' : 'start'"
						/>
						<text
							class="year-label"
							v-if="month.description"
							v-text="month.yearLabel"
							:x="month.isLastMonths ? month.xEnd - 8 : month.xStart + 8" :y="chart.xAxisTop"
							:text-anchor="month.isLastMonths ? 'end' : 'start'"
						/>
					</g>

					<line
						class="x-axis"
						:x1="0"
						:x2="fullWidth"
						:y1="chart.bottom"
						:y2="chart.bottom"
					/>
				</svg>
			</figure>
			<details class="table-wrapper">
				<summary>
					Wait {{ (selectedMonth || data.start_to_finish.all_time).readable_range }} — {{ (selectedMonth || data.start_to_finish.all_time).readable_median }} on average
				</summary>
				<table>
					<thead>
						<tr>
							<th>Pick-up date</th>
							<th>20<sup>th</sup> percentile</th>
							<th>Median wait</th>
							<th>80<sup>th</sup> percentile</th>
							<th>Responses</th>
						</tr>
					</thead>
					<tr v-for="month in monthlyData">
						<td><time :datetime="month.month + '-01'" v-text="formatMonth(month.month)"></time></td>
						<td>{{ month.percentile_20 ? Math.round(month.percentile_20) + ' days' : '—' }}</td>
						<td>{{ month.median ? Math.round(month.median) + ' days' : '—' }}</td>
						<td>{{ month.percentile_80 ? Math.round(month.percentile_80) + ' days' : '—' }}</td>
						<td><i class="icon person" aria-hidden="true"></i>{{ month.count }}</td>
					</tr>
				</table>
			</details>
		</div>
	`,
};
