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
        background-color: #333;
        padding: 15px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: white;
    }

    .navbar-brand a {
        color: white;
        text-decoration: none;
        font-size: 1.5em;
        font-weight: bold;
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
        color: white;
        text-decoration: none;
        padding: 5px 10px;
        border-radius: 4px;
        transition: background-color 0.3s ease;
    }

    .navbar-links a:hover,
    .navbar-links a.active {
        background-color: #555;
    }

    .user-info {
        display: flex;
        align-items: center;
        gap: 10px;
        color: white;
    }

    .user-info button {
        background-color: #dc3545;
        color: white;
        border: none;
        padding: 8px 12px;
        border-radius: 4px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }

    .user-info button:hover {
        background-color: #c82333;
    }
</style>    