<script lang="ts">
    import { loginUser } from '$lib/api/auth';
    // No need for goto here, as loginUser handles redirection

    let username = ''; // Or email, depending on your backend
    let password = '';
    let error: string | null = null;
    let isLoading = false;

    async function handleSubmit() {
        error = null;
        isLoading = true;

        try {
            await loginUser({ username, password });
            // Redirection is handled inside loginUser, so nothing more needed here
        } catch (err: any) {
            console.error('Login error:', err);
            error = err.message || 'Login failed. Please check your credentials.';
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="login-container">
    <h1>Login</h1>

    <form on:submit|preventDefault={handleSubmit}>
        <div class="form-group">
            <label for="username">Username or Email:</label>
            <input type="text" id="username" bind:value={username} required />
        </div>

        <div class="form-group">
            <label for="password">Password:</label>
            <input type="password" id="password" bind:value={password} required />
        </div>

        {#if error}
            <p class="error-message">{error}</p>
        {/if}

        <button type="submit" disabled={isLoading}>
            {#if isLoading}
                Logging in...
            {:else}
                Login
            {/if}
        </button>
    </form>

    <p>Don't have an account? <a href="/register">Register here</a></p>
</div>

<style>
    /* Reuse styles from register/+page.svelte or move them to a global CSS file */
    .login-container {
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
        box-sizing: border-box;
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