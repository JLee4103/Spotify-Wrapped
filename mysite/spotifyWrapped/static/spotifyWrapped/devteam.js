/**
 * Initializes the contact form submission functionality when the DOM content is fully loaded.
 * 
 * Adds a submit event listener to the contact form, which prevents the default form submission
 * behavior, gathers form data, and sends it via a POST request to the specified URL using `fetch`.
 * Handles CSRF token requirements for Django and provides user feedback on the success or failure
 * of the operation.
 */
document.addEventListener("DOMContentLoaded", () => {
    /**
     * @type {HTMLFormElement | null}
     * Reference to the contact form element in the DOM.
     */
    const contactForm = document.getElementById("contactForm");

    if (contactForm) {
        contactForm.addEventListener("submit", (event) => {
            event.preventDefault();

            // Collect form data
            const formData = new FormData(contactForm);

            // Get the CSRF token from the HTML meta tag
            const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

            // Send the data using fetch
            fetch("{% url 'spotifyWrapped:contact_dev_team' %}", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                },
                body: formData,
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.success) {
                        alert("Your message has been sent successfully!");
                        contactForm.reset(); // Clear the form
                    } else {
                        alert("Failed to send message: " + data.error);
                    }
                })
                .catch((error) => {
                    console.error("Error:", error);
                    alert("An unexpected error occurred. Please try again.");
                });
        });
    }
});

/**
 * Retrieves the value of a specified cookie.
 * 
 * @param {string} name - The name of the cookie to retrieve.
 * @returns {string | null} - The value of the cookie if found, otherwise null.
 */
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