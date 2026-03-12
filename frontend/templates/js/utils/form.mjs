export function validateForm(formElement) {
	let formIsValid = true;

	const honeypotField = formElement.querySelector('input[name="username"]');
	formElement.querySelectorAll('input, textarea, select').forEach(function(input) {
		if(input !== honeypotField && !input.checkValidity()) {
			formIsValid = false;
		}
	});

	if(honeypotField && honeypotField.value){
		formIsValid = false; // Rudimentary bot prevention
	}
	formElement.classList.toggle('show-errors', !formIsValid);

	return formIsValid;
}