document.addEventListener("DOMContentLoaded", () => {
    const contactForm = document.getElementById("contactForm");

    contactForm.addEventListener("submit", (event) => {
        event.preventDefault();

        const formData = new FormData(contactForm);
        const name = formData.get("name");
        const email = formData.get("email");
        const message = formData.get("message");

        alert(`Thank you, ${name}! Your message has been sent successfully.`);

        // Optional: Send the data to a server
        fetch('/contact-dev/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'), // Ensure CSRF protection
            },
            body: formData,
        })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('Error:', error));

        contactForm.reset(); // Clear the form
    });
});

// Utility function to get CSRF token
function getCookie(name) {
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
        const trimmed = cookie.trim();
        if (trimmed.startsWith(name + '=')) {
            return trimmed.substring(name.length + 1);
        }
    }
    return null;
}
