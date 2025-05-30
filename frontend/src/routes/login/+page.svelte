<script lang="ts">
    import { loginUser } from '$lib/api/auth';
    import ErrorMessage from '$lib/components/ErrorMessage.svelte';
    import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
    import { goto } from '$app/navigation';

    let username = '';
    let password = '';
    let error: string | null = null;
    let isLoading = false;

    async function handleSubmit() {
        error = null;
        isLoading = true;

        try {
            await loginUser({ username, password });
            console.log('Login successful!');
            goto('/dashboard'); 
        } catch (err: unknown) {
            console.error('Login error:', err);
            let errorMessageForDisplay: string;

            if (err instanceof Error) {
                errorMessageForDisplay = err.message;
            } else if (typeof err === 'string') {
                errorMessageForDisplay = err;
            } else if (typeof err === 'object' && err !== null && 'message' in err && typeof err.message === 'string') {
                errorMessageForDisplay = err.message; 
            } else if (typeof err === 'object' && err !== null) {
                try {
                    const parsedError = JSON.parse(JSON.stringify(err)); 
                    if (typeof parsedError === 'object' && parsedError !== null) {
                        const errorEntries = Object.entries(parsedError);
                        if (errorEntries.length > 0) {
                            errorMessageForDisplay = errorEntries
                                .map(([key, value]) => {
                                    return `${key}: ${(Array.isArray(value) ? value : [value]).join(', ')}`;
                                })
                                .join('; ');
                        } else {
                            errorMessageForDisplay = 'An unexpected error occurred during login.';
                        }
                    } else {
                        errorMessageForDisplay = 'An unexpected error occurred during login.';
                    }
                } catch (parseError) {
                    console.warn('Could not parse error message as JSON:', parseError);
                    errorMessageForDisplay = 'An unexpected error occurred during login.';
                }
            } else {
                errorMessageForDisplay = 'Login failed. Please check your credentials.';
            }
            error = errorMessageForDisplay;
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="auth-background-wrapper">
    <div class="cash-bubble bubble-1"></div>
    <div class="cash-bubble bubble-2"></div>
    <div class="cash-bubble bubble-3"></div>
    <div class="cash-bubble bubble-4"></div>
    <div class="cash-bubble bubble-5"></div>
    <div class="cash-bubble bubble-6"></div>
    <div class="cash-bubble bubble-7"></div>
    <div class="cash-bubble bubble-8"></div>
    <div class="cash-bubble bubble-9"></div>
    <div class="cash-bubble bubble-10"></div>

    <div class="login-container">
        <img src="/assets/spendr-logo.png" alt="Spendr App Logo" class="spendr-logo"/>
        <h1>LOGIN</h1>

        <form on:submit|preventDefault={handleSubmit}>
            <div class="form-group">
                <label for="username">Username or Email:</label>
                <input type="text" id="username" bind:value={username} required />
            </div>

            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" id="password" bind:value={password} required />
            </div>

            {#if isLoading}
                <LoadingSpinner message="Logging in..." />
            {:else if error}
                <ErrorMessage message={error} />
            {/if}

            <button type="submit" disabled={isLoading}>
                Login
            </button>
        </form>

        <p>Don't have an account? <a href="/register">Register here</a></p>
    </div>
</div>

<style>
	.auth-background-wrapper {
		position: relative;
		min-height: 100vh;
		background-color: var(--very-light-pink);
		display: flex;
		justify-content: center;
		align-items: center;
		padding: 20px;
		box-sizing: border-box;
	}

	.cash-bubble {
		position: absolute;
		background-color: var(--light-pink);
		border-radius: 8px;
		opacity: 0;
		transform: scale(0.1) rotate(0deg);
		animation: cashPop 10s ease-out infinite;
		pointer-events: none;
		z-index: 0;
		box-shadow: 0 0 10px rgba(var(--light-pink), 0.5);

		position: absolute;
		display: flex;
		justify-content: center;
		align-items: center;
	}

	.cash-bubble::before {
		content: '';
		width: 40%;
		height: 60%;
		background-color: var(--dark-pink);
		border-radius: 50%;
		opacity: 0.8;
		box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.2);
	}

	@keyframes cashPop {
		0% {
			opacity: 0;
			transform: scale(0.1) rotate(0deg);
		}
		10% {
			opacity: 0.7;
			transform: scale(0.9) rotate(calc(var(--random-rotation) * 1deg));
		}
		20% {
			opacity: 0.5;
			transform: scale(0.7) rotate(calc(var(--random-rotation) * -1deg));
		}
		100% {
			opacity: 0;
			transform: scale(0.1) rotate(0deg);
		}
	}

	.bubble-1 {
		top: 10%;
		left: 5%;
		width: 120px;
		height: 60px;
		animation-delay: 0s;
		background-color: var(--primary-pink);
		--random-rotation: 15;
	}
	.bubble-2 {
		top: 50%;
		left: 85%;
		width: 100px;
		height: 50px;
		animation-delay: 2s;
		background-color: var(--dark-pink);
		--random-rotation: -10;
	}
	.bubble-3 {
		top: 80%;
		left: 10%;
		width: 130px;
		height: 65px;
		animation-delay: 4s;
		background-color: var(--accent-pink);
		--random-rotation: 25;
	}
	.bubble-4 {
		top: 25%;
		left: 70%;
		width: 90px;
		height: 45px;
		animation-delay: 6s;
		background-color: var(--light-pink);
		--random-rotation: -5;
	}
	.bubble-5 {
		top: 70%;
		left: 2%;
		width: 125px;
		height: 60px;
		animation-delay: 8s;
		background-color: var(--primary-pink);
		--random-rotation: 20;
	}
	.bubble-6 {
		top: 5%;
		left: 30%;
		width: 110px;
		height: 55px;
		animation-delay: 1s;
		background-color: var(--dark-pink);
		--random-rotation: -18;
	}
	.bubble-7 {
		top: 90%;
		left: 75%;
		width: 140px;
		height: 70px;
		animation-delay: 3s;
		background-color: var(--accent-pink);
		--random-rotation: 10;
	}
	.bubble-8 {
		top: 35%;
		left: 1%;
		width: 85px;
		height: 40px;
		animation-delay: 5s;
		background-color: var(--light-pink);
		--random-rotation: 30;
	}
	.bubble-9 {
		top: 60%;
		left: 92%;
		width: 115px;
		height: 58px;
		animation-delay: 7s;
		background-color: var(--primary-pink);
		--random-rotation: -7;
	}
	.bubble-10 {
		top: 18%;
		left: 65%;
		width: 120px;
		height: 60px;
		animation-delay: 9s;
		background-color: var(--dark-pink);
		--random-rotation: 22;
	}

    .spendr-logo {
        display: block;
        margin: 0 auto -30px auto;
        max-width: 400px; 
        height: auto;
    }

    .login-container {
        position: relative; 
        z-index: 1;
        width: 450px;
        padding: 35px;
        background-color: var(--text-white);
        border: 1px solid var(--primary-pink);
        border-radius: 12px;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
        margin: auto; 
        margin-top: 100px;
    }

    h1 {
        text-align: center;
        color: var(--dark-pink);
        margin-top: 15px; 
        margin-bottom: 20px;
        font-size: 2em;
    }

    .form-group {
        margin-bottom: 15px;
    }

    label {
        display: block;
        margin-bottom: 5px;
        font-weight: 500;
        color: var(--text-dark);
    }

    input[type="text"],
    input[type="password"] {
        width: 100%;
        padding: 10px;
        border: 1px solid var(--border-color);
        border-radius: 5px;
        box-sizing: border-box;
        font-size: 1em;
        font-family: 'Poppins', sans-serif;
    }

    input:focus {
        border-color: var(--primary-pink);
        outline: none;
        box-shadow: 0 0 0 2px rgba(var(--primary-pink), 0.2);
    }

    button {
        margin-top: 20px;
        width: 100%;
        padding: 12px;
        background-color: var(--primary-pink);
        color: var(--text-white);
        border: none;
        border-radius: 25px;
        font-size: 1.1em;
        font-weight: 600;
        cursor: pointer;
        transition: background-color 0.3s ease, transform 0.1s ease;
    }

    button:hover:enabled {
        background-color: var(--dark-pink);
        transform: translateY(-1px);
    }

    button:disabled {
        background-color: var(--light-pink);
        color: var(--text-light);
        cursor: not-allowed;
    }

    p {
        text-align: center;
        margin-top: 25px;
        font-size: 0.95em;
        color: var(--text-dark);
    }

    p a {
        color: var(--dark-pink);
        font-weight: 500;
        text-decoration: none;
    }

    p a:hover {
        text-decoration: underline;
        color: var(--accent-pink);
    }
</style>