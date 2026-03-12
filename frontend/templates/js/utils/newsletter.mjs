{% js %}
function addNewsletterSubscriber(email) {
	return fetch('/api/forms/newsletter', {
		method: "POST",
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({email}),
	});
}
{% endjs %}