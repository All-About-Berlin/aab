import { getReferrer } from '/js/utils/tracking.mjs';

export default function initializeSidebar(){
	const main = document.querySelector('main');
	const articleBody = main.querySelector('.article-body');
	const bodyTableOfContents = articleBody && articleBody.querySelector('.table-of-contents');
	const sidebar = document.querySelector('.sidebar');
	const sidebarTableOfContents = sidebar.querySelector('.table-of-contents');
	const floatingNav = sidebar.querySelector('#floating-nav')
	const sidebarOpenCloseButton = floatingNav.querySelector('.open-close');
	const sidebarSectionLinks = Array.from(sidebarTableOfContents.querySelectorAll('li a:not(.expand)'));
	const sidebarCallsToAction = Array.from(sidebar.querySelectorAll('.cta'));

	let toggleSidebarTracked = false;
	function toggleSidebar(shouldBeOpen){
		sidebar.classList.toggle('open', shouldBeOpen);
		const isOpen = document.body.classList.toggle('sidebar-open', shouldBeOpen);

		if(isOpen && !toggleSidebarTracked){
			plausible('Sidebar', { props: {
				action: 'Open',
				pageSection: null,
				referrer: getReferrer(),
			}});
			toggleSidebarTracked = true;
		}
	}

	// Hide mobile sidebar when clicking outside of it
	document.body.addEventListener('click', e => {
		if(!sidebar.contains(e.target)){
			toggleSidebar(false);
		}
	});

	// Hide mobile sidebar when a table of contents link is clicked
	// Track sidebar section link clicks
	sidebarSectionLinks.forEach((link, index) => {
		link.addEventListener('click', e => {
			toggleSidebar(false);

			const url = new URL(link.href);
			plausible('Sidebar', { props: { action: 'Section click',
				url: url.hash,
				pageSection: null,
				referrer: getReferrer(),
			}});
		});
	});

	// Track sidebar CTA clicks
	sidebarCallsToAction.forEach((link, index) => {
		link.addEventListener('click', (e) => {
			toggleSidebar(false);
			plausible('Sidebar', { props: {
				action: 'Link click',
				url: link.href, pageSection: null,
				referrer: getReferrer(),
			}});
		});
	});

	// Show/hide mobile sidebar
	sidebarOpenCloseButton.addEventListener('click', e => toggleSidebar());

	const sectionHeaders = document.querySelectorAll('.article-body h2, .article-body h3');
	const headerMap = sidebarSectionLinks.reduce((map, link) => {
		if(link.hash) {
			map[link.hash] = document.querySelector(link.hash);
		}
		return map;
	}, {});
	function onScroll() {
		const mainSectionIsInFocus = main.getBoundingClientRect().top <= 0;

		let highlightedLink = null;

		if(mainSectionIsInFocus) {
			highlightedLink = (
				// First visible header
				sidebarSectionLinks.find(link => {
					const header = headerMap[link.hash];
					if(!header) { return false }
					const headerBoundingRect = header.getBoundingClientRect();
					const headerIsInView = headerBoundingRect.bottom > 0 && headerBoundingRect.top < window.innerHeight;
					return headerIsInView;
				})
				||
				// Nearest invisible header (for long sections)
				sidebarSectionLinks
					.filter(link => {
						const header = headerMap[link.hash];
						if(!header) { return false }
						const hasScrolledPastHeader = header.getBoundingClientRect().bottom < 0;
						return hasScrolledPastHeader;
					})
					.sort((linkA, linkB) => {
						return linkB.getBoundingClientRect().top - linkA.getBoundingClientRect().top
					})[0]
			);
		}

		if(highlightedLink) {
			sidebarSectionLinks.forEach(l => l.parentElement.classList.toggle('current', l === highlightedLink));

			const parentSection = highlightedLink.parentElement.parentElement.parentElement;
			if (parentSection && !parentSection.classList.contains('expanded')) {
				parentSection.classList.add('current');
			}
		}

		const showMobileSidebarButton = (
			// The table of contents is in view
			(!bodyTableOfContents || bodyTableOfContents.getBoundingClientRect().bottom <= 0)

			// The main content is in view (so the button does not overlap the footer)
			&& articleBody.getBoundingClientRect().bottom >= window.innerHeight
		);
		if(floatingNav) {
			floatingNav.classList.toggle('visible', showMobileSidebarButton);
		}
	};
	onScroll();
	window.addEventListener("scroll", e => window.requestAnimationFrame(onScroll));
}