<script lang="ts">
    import { registerUser } from '$lib/api/auth';
    import { goto } from '$app/navigation';
    import ErrorMessage from '$lib/components/ErrorMessage.svelte';
    import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';

    let username = '';
    let email = '';
    let password = '';
    let passwordConfirm = '';
    let error: string | null = null;
    let successMessage: string | null = null;
    let isLoading = false;

    async function handleSubmit() {
        error = null;
        successMessage = null;
        isLoading = true;

        if (password !== passwordConfirm) {
            error = 'Passwords do not match.';
            isLoading = false;
            return;
        }

        try {
            await registerUser({ username, email, password, passwordConfirm });

            successMessage = 'Registration successful! Redirecting to login...';
            username = '';
            email = '';
            password = '';
            passwordConfirm = '';

            setTimeout(() => {
                goto('/login');
            }, 2000);
        } catch (err: unknown) {
            console.error('Registration error in +page.svelte:', err);
            // --- MODIFIED ERROR HANDLING START ---
            if (err instanceof Error) {
                // Here, err.message will already be the cleaned-up string from auth.ts
                error = err.message;
            } else {
                error = 'An unexpected error occurred.';
            }
            // --- MODIFIED ERROR HANDLING END ---
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

    <div class="register-container">
        <img src="/assets/spendr-logo.png" alt="Spendr App Logo" class="spendr-logo" />
        <h1>CREATE ACCOUNT</h1>

        <form on:submit|preventDefault={handleSubmit}>
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" bind:value={username} required />
            </div>

            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" bind:value={email} required />
            </div>

            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" bind:value={password} required />
            </div>

            <div class="form-group">
                <label for="passwordConfirm">Confirm Password</label>
                <input type="password" id="passwordConfirm" bind:value={passwordConfirm} required />
            </div>

            {#if isLoading}
                <LoadingSpinner message="Registering..." />
            {:else if error}
                <ErrorMessage message={error} />
            {:else if successMessage}
                <div class="success-message">
                    <p>{successMessage}</p>
                </div>
            {/if}

            <button type="submit" disabled={isLoading}> Register </button>
        </form>

        <p>Already have an account? <a href="/login">Login here</a></p>
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

	.register-container {
		position: relative;
		z-index: 1;
		width: 450px;
		padding: 35px;
		background-color: var(--text-white);
		border: 1px solid var(--primary-pink);
		border-radius: 12px;
		box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
        margin-top: -40px;
	}

	.spendr-logo {
		display: block;
		margin: 0 auto -30px auto;
		max-width: 400px;
		height: auto;
	}

	h1 {
		text-align: center;
		color: var(--dark-pink);
		margin-bottom: 20px;
		font-size: 2em;
	}

	button {
		margin-top: 20px;
		width: 100%;
		padding: 12px;
		font-size: 1.1em;
		font-weight: 600;
		background-color: var(--primary-pink);
		color: var(--text-white);
		border-radius: 25px;
	}

	button:hover:enabled {
		background-color: var(--dark-pink);
	}

	.success-message {
		color: var(--success-color);
		background-color: #d4edda;
		border: 1px solid #c3e6cb;
		padding: 10px;
		border-radius: 5px;
		margin-bottom: 15px;
		text-align: center;
		font-weight: 500;
	}

	p {
		text-align: center;
		margin-top: 25px;
		font-size: 0.95em;
		color: var(--text-dark);
	}

	p a {
		font-weight: 500;
		color: var(--dark-pink);
	}

	p a:hover {
		text-decoration: underline;
		color: var(--accent-pink);
	}
</style>
