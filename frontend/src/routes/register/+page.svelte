<script lang="ts">
    import { registerUser } from '$lib/api/auth';
    import { goto } from '$app/navigation'; // For redirection

    let username = '';
    let email = '';
    let password = '';
    let password2 = '';
    let error: string | null = null;
    let successMessage: string | null = null;
    let isLoading = false;

    async function handleSubmit() {
        error = null; // Clear previous errors
        successMessage = null; // Clear previous success messages
        isLoading = true;

        if (password !== password2) {
            error = 'Passwords do not match.';
            isLoading = false;
            return;
        }

        try {
            await registerUser({ username, email, password, password2 });
            successMessage = 'Registration successful! You can now log in.';
            // Optionally, clear the form fields
            username = '';
            email = '';
            password = '';
            password2 = '';

            // Redirect to login page after a short delay or directly
            setTimeout(() => {
                goto('/login'); // Redirect to your login page
            }, 2000); // Wait 2 seconds before redirecting

        } catch (err: any) {
            console.error('Registration error:', err);
            // Assuming the error object from auth.ts contains a 'message' or 'detail'
            error = err.message || 'An unexpected error occurred during registration.';
            // If it's a JSON string from backend, parse it to show better error.
            try {
                const parsedError = JSON.parse(error);
                if (typeof parsedError === 'object') {
                    // Flatten errors for display, e.g., { username: ['This field is required'], password: ['Too short'] }
                    error = Object.entries(parsedError)
                        .map(([key, value]) => `${key}: ${(value as string[]).join(', ')}`)
                        .join('; ');
                }
            } catch (e) {
                // If parsing fails, use the original error message
            }
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="register-container">
    <h1>Register</h1>

    <form on:submit|preventDefault={handleSubmit}>
        <div class="form-group">
            <label for="username">Username:</label>
            <input type="text" id="username" bind:value={username} required />
        </div>

        <div class="form-group">
            <label for="email">Email:</label>
            <input type="email" id="email" bind:value={email} required />
        </div>

        <div class="form-group">
            <label for="password">Password:</label>
            <input type="password" id="password" bind:value={password} required />
        </div>

        <div class="form-group">
            <label for="password2">Confirm Password:</label>
            <input type="password" id="password2" bind:value={password2} required />
        </div>

        {#if error}
            <p class="error-message">{error}</p>
        {/if}

        {#if successMessage}
            <p class="success-message">{successMessage}</p>
        {/if}

        <button type="submit" disabled={isLoading}>
            {#if isLoading}
                Registering...
            {:else}
                Register
            {/if}
        </button>
    </form>

    <p>Already have an account? <a href="/login">Login here</a></p>
</div>

<style>
    .register-container {
        max-width: 400px;
        margin: 50px auto;
        padding: 20px;
        border: 1px solid #ccc;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        background-color: #fff;
    }

    h1 {
        text-align: center;
        color: #333;
        margin-bottom: 20px;
    }

    .form-group {
        margin-bottom: 15px;
    }

    label {
        display: block;
        margin-bottom: 5px;
        font-weight: bold;
        color: #555;
    }

    input[type="text"],
    input[type="email"],
    input[type="password"] {
        width: 100%;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 4px;
        box-sizing: border-box; /* Ensures padding doesn't increase width */
        font-size: 16px;
    }

    button {
        width: 100%;
        padding: 10px;
        background-color: #007bff;
        color: white;
        border: none;
        border-radius: 4px;
        font-size: 18px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }

    button:hover:enabled {
        background-color: #0056b3;
    }

    button:disabled {
        background-color: #cccccc;
        cursor: not-allowed;
    }

    .error-message {
        color: #dc3545;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        padding: 10px;
        border-radius: 4px;
        margin-bottom: 15px;
        text-align: center;
    }

    .success-message {
        color: #28a745;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 10px;
        border-radius: 4px;
        margin-bottom: 15px;
        text-align: center;
    }

    p {
        text-align: center;
        margin-top: 20px;
    }

    p a {
        color: #007bff;
        text-decoration: none;
    }

    p a:hover {
        text-decoration: underline;
    }
</style>