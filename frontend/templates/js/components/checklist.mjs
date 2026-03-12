export default function initializeChecklists(){
	window.addEventListener("DOMContentLoaded", function() {
		// Click anywhere on a checklist item to check the item
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
	});
}