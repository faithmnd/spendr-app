<script lang="ts">
    import '../app.css'; // Import your global CSS
    import { authStore } from '$lib/stores/auth';
    import Navbar from '$lib/components/Navbar.svelte';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
		
    // Initialize authentication state when the component mounts in the browser
    onMount(async () => {
        await authStore.initializeAuth();
    });

    // Reactive statement to handle redirection if authentication state changes
    $: if (!$authStore.isAuthenticated && !$authStore.isLoading) {
        // Only redirect if we are not authenticated AND not currently loading
        // And if the current route is not login or register (to prevent infinite loops)
        const currentPath = window.location.pathname;
        if (!currentPath.startsWith('/login') && !currentPath.startsWith('/register')) {
            goto('/login');
        }
    }
</script>

<div class="app-layout">
    {#if $authStore.isAuthenticated}
        <Navbar />
    {/if}

    <main>
        <slot /> </main>

    <footer>
        <p>&copy; {new Date().getFullYear()} Spendr App</p>
    </footer>
</div>

<style>
    .app-layout {
        display: flex;
        flex-direction: column;
        min-height: 100vh;
    }

    main {
        flex: 1; /* Takes up available space */
        padding: 20px;
    }

    footer {
        background-color: #f0f0f0;
        padding: 10px;
        text-align: center;
        border-top: 1px solid #eee;
    }
</style>