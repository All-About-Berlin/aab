import { site } from '/js/utils/constants.mjs';

export function getReferrer() {
	const source = localStorage.getItem('referralSource');
	const timestamp = localStorage.getItem('referralDate');

	if (!source || !timestamp) return null;

	const daysAgo = (Date.now() - Number(timestamp) * 1000) / (1000 * 60 * 60 * 24);
	return daysAgo <= 30 ? source : null;
}

// Find the nearest parent H2, H3 or H4 heading in .article-body, return its ID for tracking purposes
export function getNearestHeadingId(el) {
	const articleBody = document.querySelector('.article-body');
	if (articleBody && el && articleBody.contains(el)) {
		const nearestHeading = Array.from(articleBody.querySelectorAll(':scope > :is(h2,h3,h4)'))
			.findLast(h => el.compareDocumentPosition(h) === Node.DOCUMENT_POSITION_PRECEDING);

		return (nearestHeading && nearestHeading.id) ? `#${nearestHeading.id}` : null;
	}
	return null;
}

// Save referrals for 30 days
const urlParams = new URLSearchParams(window.location.search);
const ref = urlParams.get('ref') || urlParams.get('utm_source')
if (ref) {
	try {
		localStorage.setItem('referralSource', ref);
		localStorage.setItem('referralDate', Math.round(Date.now() / 1000));
	} catch (e) {}
}

function getLinkElement(l) {
	while (l && (typeof l.tagName === 'undefined' || l.tagName.toLowerCase() !== 'a' || !l.href)) {
		l = l.parentNode
	}
	return l;
}

function shouldOpenLinkAfterTracking(e, link) {
	// If default has been prevented by an external script, Plausible should not intercept navigation.
	if (e.defaultPrevented) {
		return false
	}
	const targetsCurrentWindow = !link.target || link.target.match(/^_(self|parent|top)$/i);
	const isRegularClick = !(e.ctrlKey || e.metaKey || e.shiftKey) && e.type === 'click';
	return targetsCurrentWindow && isRegularClick;
}

const middleMouse = 1;

function handleLinkClick(e) {
	if (e.type === 'auxclick' && e.button !== middleMouse) {
		return
	}
	const link = getLinkElement(e.target);
	if (link && shouldTrackUrl(link.href)) {
		return sendLinkClickEvent(e, link, 'Outbound Link: Click', {
			url: link.href,
			pageSection: getNearestHeadingId(link)
		});
	}
}

function plausibleFallback() {
	console.log(`Plausible: ${arguments[0]}`, arguments[1]?.props);
	(window.plausible.q ??= []).push(arguments);
}

function sendLinkClickEvent(event, link, eventName, eventProps) {
	let followedLink = false;

	function followLink() {
		if (!followedLink) {
			followedLink = true;
			window.location = link.href;
		}
	}
	if (shouldOpenLinkAfterTracking(event, link)) {
		plausible(eventName, {
			props: eventProps,
			callback: followLink
		});

		// Redirect after 1.5s if tracking fails, 0s if plausible script was blocked
		setTimeout(followLink, window.plausible === plausibleFallback ? 0 : 1500);
		event.preventDefault();
	} else {
		plausible(eventName, {
			props: eventProps
		});
	}
}

export function shouldTrackUrl(url) {
	return (
		url.startsWith('/out/') ||
		url.startsWith(site.url + '/out/') ||
		url.startsWith(site.url + '/donate') ||
		url.startsWith('mailto:') ||
		(url.startsWith('http') && !url.startsWith(site.url || '/'))
	);
}

export function initializeTracking() {
	document.addEventListener('click', handleLinkClick);
	document.addEventListener('auxclick', handleLinkClick);

	// Fallback if Plausible is not loading properly
	window.plausible ??= plausibleFallback
}