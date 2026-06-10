import { getNearestHeadingId } from '/js/utils/tracking.mjs';

let dialog = null; // The tooltip <dialog> element
let pronounciationAudio = null;

function createTooltip() {
	if (dialog) return;

	dialog = document.createElement('dialog');
	dialog.id = 'glossary-tooltip';
	dialog.setAttribute('aria-labelledby', 'h-dialog');
	dialog.setAttribute('closedby', 'any');
	dialog.innerHTML = `<header>
		<h2>
			<a href="#" title="Open definition in new tab" target="_blank">
				<dfn role="term" lang="en" id="h-dialog"></dfn>
				<small lang="de"></small>
			</a>
		</h2>
		<button title="Hear how this term is pronounced" class="pronounce-button" role="button" aria-label="Hear how this term is pronounced"><i class="icon sound" aria-hidden="true"></i></button>
		<button title="Close" class="close-button" role="button" aria-label="Close dialog"><i class="icon close" aria-hidden="true"></i></button>
	</header>
	<div class="article-body" role="definition"></div>`;
	document.body.appendChild(dialog);

	dialog.querySelector('.close-button').addEventListener('click', hideTooltip);
	dialog.querySelector('.pronounce-button').addEventListener('click', pronounceTerm);

	dialog = dialog;
}

function setTooltipAsLoading(dialog){
	dialog.querySelector('h2 a dfn').innerHTML = 'Loading…';
	dialog.querySelector('h2 a small').innerHTML = '…';
	dialog.querySelector('.article-body').innerHTML = '<p>…</p>';
}

export function showTooltip(clickEvent) {
	createTooltip();
	setTooltipAsLoading(dialog);

	// Pause previous audio
	if (pronounciationAudio) {
		pronounciationAudio.pause();
	}

	// Fetch description
	const anchor = clickEvent.currentTarget || clickEvent.target;
	if (!dialog.open) {
		dialog.showModal();
	}
	fetch(anchor.getAttribute('href') + '.json').then(r => r.json()).then(data => {
		dialog.querySelector('h2 a').setAttribute('href', anchor.getAttribute('href'));
		dialog.querySelector('h2 a dfn').innerHTML = data.englishTerm || data.germanTerm;
		dialog.querySelector('h2 a small').innerHTML = data.germanTerm || '';
		dialog.querySelector('h2 a small').classList.toggle('hidden', (!data.englishTerm || data.englishTerm == data.germanTerm));

		const dialogBody = dialog.querySelector('.article-body');
		dialogBody.innerHTML = data.definition;
		dialogBody.querySelectorAll('a').forEach(a => a.target = '_blank');

		pronounciationAudio = new Audio(data.audioUrl);
		dialog.querySelector('.pronounce-button').href = data.audioUrl;

		const footnotes = dialogBody.querySelector('#footnotes');
		if (footnotes) {
			footnotes.remove();
		}
		setDialogLinks(dialogBody);

		plausible('Glossary dialog', { props: {
			url: anchor.getAttribute('href'),
			pageSection: getNearestHeadingId(anchor)
		}});
	});
}

function hideTooltip(event) {
	event.preventDefault();
	dialog.close();
	if (pronounciationAudio) {
		pronounciationAudio.pause();
	}
}

function setDialogLinks(element) {
	element.querySelectorAll('a[href*="/glossary/"]').forEach(anchor => {
		// If HTML5 dialogs are supported - otherwise default to link
		if ('showModal' in document.createElement('dialog')) {
			anchor.addEventListener('click', event => {
				event.preventDefault();
				event.stopPropagation();
				showTooltip(event);
			});

			if (!anchor.classList.contains('recommended')) {
				anchor.classList.add('glossary-link');
			}
		} else {
			anchor.setAttribute('target', '_blank');
		}
	});
}

function pronounceTerm(event) {
	event.preventDefault();
	pronounciationAudio.play();
}

export default function initializeGlossaryTooltip() {
	window.addEventListener('DOMContentLoaded', function() {
		document.querySelectorAll('.glossary-links').forEach(el => setDialogLinks(el));
	});
}
