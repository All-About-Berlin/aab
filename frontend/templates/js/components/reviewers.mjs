export default function initializeReviewers(){
	window.addEventListener("DOMContentLoaded", function() {
		// Reviewers menu toggle
		document.querySelectorAll('.post-reviewers button').forEach(button => button.addEventListener('click', e => {
			const menu = document.getElementById(button.getAttribute("aria-controls"));
			menu.hidden = !menu.hidden;
			button.setAttribute('aria-expanded', !menu.hidden);
		}));
	});
}