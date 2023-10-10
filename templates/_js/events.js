{% js %}
function validateForm(formElement) {
	let formIsValid = true;

	const honeypotField = formElement.querySelector('input[name="username"]');
	formElement.querySelectorAll('input, textarea, select').forEach(function(input) {
		if(input !== honeypotField && !input.checkValidity()) {
			formIsValid = false;
		}
	});

	if(formElement.querySelectorAll('.signature-input.empty[required]').length > 0){
		formIsValid = false;
	}

	if(honeypotField && honeypotField.value){
		formIsValid = false; // Rudimentary bot prevention
	}
	formElement.classList.toggle('show-errors', !formIsValid);

	return formIsValid;
}

window.addEventListener("DOMContentLoaded", function() {
	/* Fixes align-items: baseline bug in Safari */
	document.querySelectorAll('input, textarea').forEach((input) => {
		input.placeholder = input.placeholder || ' ';
	});

	/* Reviewers */
	document.querySelectorAll('.post-reviewers a').forEach(link => {
		link.addEventListener('click', (e) => {
			e.preventDefault();
			link.classList.toggle('expanded');
			document.getElementById('reviewers').classList.toggle('hidden');
		});
	});

	/* Checklists */
	document.querySelectorAll('li.checkbox').forEach(checklistItem => {
		checklistItem.addEventListener('click', (e) => {
			if(
				e.target.tagName !== 'A'
				&& e.target.tagName !== 'INPUT'
				&& (e.target.parentElement && e.target.parentElement.tagName) !== 'A'
			){
				const checkbox = checklistItem.querySelector('[type=checkbox]');
				checkbox.checked = !checkbox.checked;
				e.stopPropagation();
			}
		});
	});

	/* Open footnotes when clicking on a footnote link */
	document.querySelectorAll('.footnote-ref').forEach(link => {
		link.addEventListener('click', e => {
			document.getElementById('footnotes').setAttribute("open", "true"); 
		});
	});

	/* Expandable lists */
	document.querySelectorAll(".table-of-contents .expand").forEach(expandButton => {
		expandButton.addEventListener('click', e => {
			e.preventDefault();
			expandButton.parentNode.classList.toggle('expanded');
		})
	});
});
{% endjs %}