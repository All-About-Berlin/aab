export default function initializeChecklists(){
	window.addEventListener("DOMContentLoaded", function() {
		// Open footnotes when clicking on a footnote link
		document.querySelectorAll('.footnote-ref').forEach(link => {
			link.addEventListener('click', e => {
				document.getElementById('footnotes').setAttribute("open", "true");
			});
		});
	});
}