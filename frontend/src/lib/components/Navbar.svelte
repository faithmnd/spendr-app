<script lang="ts">
    import { authStore } from '$lib/stores/auth';
    import { logoutUser } from '$lib/api/auth';
    import { page } from '$app/stores';

    $: isAuthenticated = $authStore.isAuthenticated;
    $: user = $authStore.user;

    function handleLogout() {
        logoutUser();
    }
</script>

<nav class="navbar">
    <div class="navbar-brand">
        <a href="/dashboard" class="logo-link" aria-label="Go to Dashboard">
            <img src="/assets/spendr-logo.png" alt="Spendr Logo" class="image-logo"/>
        </a>
    </div>
    <ul class="navbar-links">
        {#if isAuthenticated}
            <li><a href="/dashboard" class:active={$page.url.pathname === '/dashboard'}>Dashboard</a></li>
            <li><a href="/transactions" class:active={$page.url.pathname.startsWith('/transactions')}>Transactions</a></li>
            <li><a href="/categories" class:active={$page.url.pathname.startsWith('/categories')}>Categories</a></li>
            <li><a href="/accounts" class:active={$page.url.pathname.startsWith('/accounts')}>Accounts</a></li>
            <li class="user-info">
                <span class="user-greeting">Hello, {user?.username || 'User'}!</span>
                <button on:click={handleLogout} class="logout-button">Logout</button>
            </li>
        {:else}
            <li><a href="/login" class:active={$page.url.pathname === '/login'}>Login</a></li>
            <li><a href="/register" class:active={$page.url.pathname === '/register'}>Register</a></li>
        {/if}
    </ul>
</nav>

<style>
    .navbar {
        background-color: var(--primary-pink);
        padding: 1rem 1.5rem; /* Increased padding for a more substantial feel */
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: var(--text-white);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2); /* Enhanced shadow for depth */
        border-bottom-left-radius: 15px; /* Rounded bottom corners */
        border-bottom-right-radius: 15px;
        font-family: 'Inter', sans-serif; /* Using Inter font */
    }

    .navbar-brand {
        display: flex;
        align-items: center;
    }

    .image-logo {
        width: auto;
        height: 120px;
        padding-top: 0.5rem;
        padding-left: 1rem;
    }

    .logo-link {
        display: flex;
        align-items: center;
        text-decoration: none;
        color: var(--text-white);
        transition: transform 0.2s ease;
    }

    .logo-link:hover {
        transform: translateX(3px); 
    }

    .navbar-links {
        font-family: 'Poppins', sans-serif;
        list-style: none;
        margin: 0;
        padding: 0;
        display: flex;
        align-items: center;
        gap: 15px; /* Space between nav items */
    }

    .navbar-links a {
        color: var(--text-white);
        text-decoration: none;
        padding: 0.6rem 1rem; 
        border-radius: 25px; /* More rounded pills */
        transition: background-color 0.3s ease, transform 0.2s ease, box-shadow 0.3s ease;
        font-weight: 700; /* Slightly bolder nav links */
        white-space: nowrap; /* Prevent wrapping on smaller screens */
        font-size: 1.1rem;
    }

    .navbar-links a:hover,
    .navbar-links a.active {
        background-color: var(--dark-pink);
        transform: translateY(-2px); /* Lift effect on hover/active */
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* Shadow on hover/active */
    }

    .user-info {
        font-size: 1.1rem;
        display: flex;
        align-items: center;
        gap: 12px; /* Space between greeting and button */
        color: var(--text-white);
        font-weight: 500;
        background-color: rgba(255, 255, 255, 0.1); /* Subtle background for user info */
        padding: 0.5rem 1rem;
        border-radius: 25px; /* Rounded user info box */
    }

    .user-greeting {
        white-space: nowrap; /* Prevent wrapping */
    }

    .logout-button {
        background-color: var(--accent-pink);
        color: var(--text-white);
        border: none;
        padding: 0.6rem 1.2rem; /* Adjusted padding */
        border-radius: 25px; /* More rounded button */
        cursor: pointer;
        transition: background-color 0.3s ease, transform 0.2s ease, box-shadow 0.3s ease;
        font-weight: 600;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15); /* Button shadow */
    }

    .logout-button:hover {
        background-color: var(--dark-pink);
        transform: translateY(-1px); /* Subtle lift */
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.25); /* Stronger shadow on hover */
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .navbar {
            flex-direction: column;
            padding: 1rem;
            border-bottom-left-radius: 0; /* Remove rounded corners on small screens if desired */
            border-bottom-right-radius: 0;
        }

        .navbar-brand {
            margin-bottom: 1rem;
        }

        .navbar-links {
            flex-direction: column;
            width: 100%;
            gap: 10px; /* Adjust gap for vertical stacking */
        }

        .navbar-links li {
            margin-left: 0;
            width: 100%;
            text-align: center;
        }

        .navbar-links a,
        .user-info {
            width: calc(100% - 2rem); /* Account for padding */
            justify-content: center;
            padding: 0.8rem 1rem; /* More vertical padding for touch targets */
        }

        .user-info {
            flex-direction: column;
            gap: 8px;
        }

        .logout-button {
            width: 100%;
            margin-top: 5px; /* Space between greeting and button in column layout */
        }
    }
</style>
