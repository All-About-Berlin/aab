import { getNearestHeadingId } from '/js/utils/tracking.mjs';

const tooltip = document.getElementById('tooltip');
let pronounciationAudio = null;

export function showTooltip(clickEvent) {
	const tooltipBody = tooltip.querySelector('.article-body');

	// When switching from a tooltip to another, prevent the old content from showing on the new tooltip
	tooltip.querySelector('h2 a dfn').innerHTML = 'Loading…';
	tooltip.querySelector('h2 a small').innerHTML = '…';
	tooltipBody.innerHTML = '<p>...</p>';

	// Fetch description
	const anchor = clickEvent.currentTarget || clickEvent.target;
	if(!tooltip.open){
		tooltip.showModal();
	}
	fetch(anchor.getAttribute('href') + '.json').then(r => r.json()).then(data => {
		tooltip.querySelector('h2 a').setAttribute('href', anchor.getAttribute('href'));
		tooltip.querySelector('h2 a dfn').innerHTML = data.title;
		tooltip.querySelector('h2 a small').innerHTML = data.englishTerm || '';
		tooltip.querySelector('h2 a small').classList.toggle('hidden', (!data.englishTerm || data.englishTerm == data.germanTerm));
		tooltipBody.innerHTML = data.definition;
		tooltipBody.querySelectorAll('a').forEach(a => a.target = '_blank');

		pronounciationAudio = new Audio(data.audioUrl);
		tooltip.querySelector('.pronounce-button').href = data.audioUrl;

		const footnotes = tooltipBody.querySelector('#footnotes');
		if(footnotes){
			footnotes.remove();
		}
		setTooltipLinks(tooltipBody);

		plausible('Glossary tooltip', { props: {
			url: anchor.getAttribute('href'),
			pageSection: getNearestHeadingId(anchor)
		}});
	});
}

function hideTooltip(event) {
	event.preventDefault();
	tooltip.close();
	if(pronounciationAudio){
		pronounciationAudio.pause();
	}
}

function setTooltipLinks(element){
	element.querySelectorAll('a[href*="/glossary/"]').forEach((anchor) => {
		if(typeof tooltip.show === 'function') {
			anchor.addEventListener('click', (event) => {
				event.preventDefault();
				event.stopPropagation();
				showTooltip(event);
			});
		}
		else {
			anchor.setAttribute('target', '_blank');
		}
	});
}

function pronounceTerm(event){
	event.preventDefault();
	pronounciationAudio.play();
}

export function initializeTooltip(){
	window.addEventListener("DOMContentLoaded", function() {
		tooltip.querySelector('.close-button').addEventListener('click', hideTooltip);
		tooltip.addEventListener('click', clickEvent => {
			if(clickEvent.target === tooltip) {
				tooltip.close();
			}
		});
		document.querySelectorAll('main .article-body, .sidebar').forEach(el => setTooltipLinks(el));
		tooltip.querySelector('.pronounce-button').addEventListener('click', pronounceTerm);
	});
}