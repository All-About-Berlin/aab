export default function initializeReviewers(){
	window.addEventListener("DOMContentLoaded", function() {
		document.querySelectorAll('.post-reviewers a').forEach(link => link.addEventListener('click', e => {
			e.preventDefault();
			link.classList.toggle('expanded');
			document.getElementById('reviewers').classList.toggle('hidden');
		}));
	});
}