document.addEventListener('DOMContentLoaded', () => {
    console.log('init');
    const registrationForm = document.getElementById('registrationForm');
    const loginForm = document.getElementById('loginForm');

    registrationForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const registerUsername = document.getElementById('registerUsername').value;
        const registerPassword = document.getElementById('registerPassword').value;
        const registerEmail = document.getElementById('registerEmail').value;

        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username: registerUsername, password: registerPassword, email: registerEmail }),
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.message);
            registrationForm.reset();
        } else {
            alert(data.error);
        }
    });

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const loginUsername = document.getElementById('loginUsername').value;
        const loginPassword = document.getElementById('loginPassword').value;

        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username: loginUsername, password: loginPassword }),
        });

        if (response.ok) {
            const data = await response.json();
            alert('Login successful');
            localStorage.setItem('id',data.user.id)
            loginForm.reset();

            // Check if there's a redirect URL in the response data
            if (data.redirectUrl) {
                // Redirect to the home page
                window.location.href = data.redirectUrl;
            }
        } else {
            alert('Invalid username or password');
        }
    });


});
    // Add event listener for the Delete Account button
    const deleteAccountButton = document.getElementById('deleteAccountButton');
    deleteAccountButton.addEventListener('click', async () => {
        const confirmation = confirm('Are you sure you want to delete your account? This action cannot be undone.');

    //    const userId = localStorage.getItem('id')
        if (confirmation) {
            const response = await fetch(`/api/delete-account/${2}`, {
                method: 'DELETE',
            });

            if (response.ok) {
                alert('Your account has been deleted.');
                // Redirect to the login or registration page as needed
                window.location.href = '/'; // Replace with the appropriate URL
            } else {
                alert('Failed to delete your account. Please try again.');
            }
        }
    });