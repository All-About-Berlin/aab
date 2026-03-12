export default function initializeTableOfContents(argument) {
	// Expandable subsections in the table of contents
	window.addEventListener("DOMContentLoaded", function() {
		document.querySelectorAll(".table-of-contents .expand").forEach(expandButton => {
			expandButton.addEventListener('click', e => {
				e.preventDefault();
				expandButton.parentNode.classList.toggle('expanded');
			})
		});
	});
}