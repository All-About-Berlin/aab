import { getReferrer } from '/js/utils/tracking.mjs';

function addNewsletterSubscriber(email) {
	return fetch('/api/forms/newsletter', {
		method: "POST",
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({email}),
	});
}

export default function initializeNewsletterForm() {
	// Form to add newsletter subscribers
	window.addEventListener("DOMContentLoaded", function() {
		Array.from(document.querySelectorAll('.newsletter-form')).forEach(form => {
			const emailInput = form.querySelector('input[type="email"]');
			const submitButton = form.querySelector('.button');

			emailInput.value = localStorage.getItem('email') || '';
			form.addEventListener('submit', e => {
				e.preventDefault();
				if(!emailInput.checkValidity()){
					return;
				}
				submitButton.disabled = true;
				submitButton.classList.add('loading');
				emailInput.classList.add('show-errors');
				addNewsletterSubscriber(emailInput.value).then(response => {
					if(response.ok){
						plausible('Newsletter signup', { props: {
							pageSection: 'sidebar',
							referrer: getReferrer(),
						}});
					}
					form.innerHTML = response.ok ?
						"<span><strong>Subscribed!</strong> Check your email for a confirmation link. Click it to receive my newsletter.</span>"
						: "<span><strong>Error!</strong> We could not sign you up. <a href='/newsletter' target='_blank'>Try again.</a></span>";
				});
			});
		});
	});	
}