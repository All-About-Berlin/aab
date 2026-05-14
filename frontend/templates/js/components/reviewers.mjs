export default function initializeReviewers(){
	window.addEventListener("DOMContentLoaded", function() {
		document.querySelectorAll('.post-reviewers button').forEach(link => link.addEventListener('click', e => {
			link.classList.toggle('expanded');
			document.getElementById('reviewers').classList.toggle('hidden');
		}));
	});
}