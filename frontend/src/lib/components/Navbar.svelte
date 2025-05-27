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
        <a href="/dashboard">Spendr</a>
    </div>
    <ul class="navbar-links">
        {#if isAuthenticated}
            <li><a href="/dashboard" class:active={$page.url.pathname === '/dashboard'}>Dashboard</a></li>
            <li><a href="/transactions" class:active={$page.url.pathname.startsWith('/transactions')}>Transactions</a></li>
            <li><a href="/categories" class:active={$page.url.pathname.startsWith('/categories')}>Categories</a></li>
            <li><a href="/accounts" class:active={$page.url.pathname.startsWith('/accounts')}>Accounts</a></li>
            <li class="user-info">
                <span>Hello, {user?.username || 'User'}!</span>
                <button on:click={handleLogout}>Logout</button>
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
        padding: 15px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: var(--text-white);
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }

    .navbar-brand a {
        color: var(--text-white);
        text-decoration: none;
        font-size: 1.8em; 
        font-weight: 700; 
        letter-spacing: 1px; 
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }

    .navbar-links {
        list-style: none;
        margin: 0;
        padding: 0;
        display: flex;
        align-items: center;
    }

    .navbar-links li {
        margin-left: 20px;
    }

    .navbar-links a {
        color: var(--text-white);
        text-decoration: none;
        padding: 8px 12px;
        border-radius: 20px;
        transition: background-color 0.3s ease, color 0.3s ease;
        font-weight: 500;
    }

    .navbar-links a:hover,
    .navbar-links a.active {
        background-color: var(--dark-pink); 
        color: var(--text-white);
    }

    .user-info {
        display: flex;
        align-items: center;
        gap: 10px;
        color: var(--text-white);
        font-weight: 400;
    }

    .user-info button {
        background-color: var(--accent-pink); 
        color: var(--text-white);
        border: none;
        padding: 8px 15px;
        border-radius: 20px; 
        cursor: pointer;
        transition: background-color 0.3s ease;
        font-weight: 500;
    }

    .user-info button:hover {
        background-color: var(--dark-pink);
    }
</style>