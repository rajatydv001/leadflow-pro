document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('leadForm');
    const submitBtn = document.getElementById('submitBtn');
    const formMessage = document.getElementById('formMessage');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        clearErrors();

        const formData = {
            fullName: document.getElementById('fullName').value.trim(),
            email: document.getElementById('email').value.trim(),
            companyName: document.getElementById('companyName').value.trim(),
            website: document.getElementById('website').value.trim(),
            industry: document.getElementById('industry').value,
            companySize: document.getElementById('companySize').value,
            notes: document.getElementById('notes').value.trim()
        };

        const validationErrors = validateForm(formData);

        if (Object.keys(validationErrors).length > 0) {
            displayErrors(validationErrors);
            return;
        }

        submitBtn.classList.add('loading');
        submitBtn.disabled = true;

        try {
            const response = await fetch('/api/leads', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (response.ok) {
                showMessage('success', result.message);
                form.reset();
            } else {
                if (result.errors) {
                    displayErrors(result.errors);
                }
                showMessage('error', result.message || 'Something went wrong. Please try again.');
            }

        } catch (error) {
            showMessage('error', 'Network error. Please check your connection and try again.');
            console.error('Error:', error);

        } finally {
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
        }
    });

    function validateForm(data) {
        const errors = {};

        if (!data.fullName) {
            errors.fullName = 'Full name is required';
        }

        if (!data.email) {
            errors.email = 'Email is required';
        } else if (!isValidEmail(data.email)) {
            errors.email = 'Please enter a valid email address';
        }

        if (!data.companyName) {
            errors.companyName = 'Company name is required';
        }

        if (data.website && !isValidUrl(data.website)) {
            errors.website = 'Please enter a valid website URL';
        }

        if (!data.industry) {
            errors.industry = 'Please select an industry';
        }

        if (!data.companySize) {
            errors.companySize = 'Please select company size';
        }

        return errors;
    }

    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    function isValidUrl(url) {
        const urlRegex = /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/i;
        return urlRegex.test(url);
    }

    function displayErrors(errors) {
        for (const [field, message] of Object.entries(errors)) {
            const input = document.getElementById(field);
            const errorSpan = document.getElementById(`${field}-error`);

            if (input) {
                input.classList.add('error');
            }

            if (errorSpan) {
                errorSpan.textContent = message;
            }
        }
    }

    function clearErrors() {
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => input.classList.remove('error'));

        const errorMessages = form.querySelectorAll('.error-message');
        errorMessages.forEach(span => span.textContent = '');

        formMessage.classList.add('hidden');
        formMessage.className = 'form-message hidden';
    }

    function showMessage(type, message) {
        formMessage.className = `form-message ${type}`;
        formMessage.textContent = message;
        formMessage.classList.remove('hidden');

        window.scrollTo({
            top: formMessage.offsetTop - 100,
            behavior: 'smooth'
        });
    }

    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            if (this.classList.contains('error')) {
                this.classList.remove('error');
                const errorSpan = document.getElementById(`${this.id}-error`);
                if (errorSpan) {
                    errorSpan.textContent = '';
                }
            }
        });
    });
});