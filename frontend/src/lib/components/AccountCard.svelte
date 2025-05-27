<script lang="ts">
    import type { Account } from '$lib/types';

    export let account: Account;

    function formatCurrency(amount: number, currency: string): string {
        return new Intl.NumberFormat(navigator.language, {
            style: 'currency',
            currency: currency,
        }).format(amount);
    }
</script>

<div class="account-card">
    <h3 class="account-name">{account.name}</h3>
    <p class="account-balance">
        {formatCurrency(account.balance, account.currency)}
    </p>
    <div class="account-actions">
        <button on:click={() => console.log('Edit', account.id)}>Edit</button>
        <button on:click={() => console.log('Delete', account.id)} class="delete-btn">Delete</button>
    </div>
</div>

<style>
    .account-card {
        background-color: var(--text-white); 
        border: 1px solid var(--light-pink); 
        border-radius: 12px; 
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08); 
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 0.2s ease;
    }

    .account-card:hover {
        transform: translateY(-5px); 
    }

    .account-name {
        margin-top: 0;
        margin-bottom: 10px;
        color: var(--dark-pink);
        font-size: 1.4em; 
        font-weight: 600;
    }

    .account-balance {
        font-size: 2.2em; 
        font-weight: 700;
        color: var(--accent-pink);
        margin-bottom: 15px;
    }

    .account-actions button {
        background-color: var(--primary-pink);
        color: var(--text-white);
        border: none;
        padding: 10px 18px;
        border-radius: 25px;
        cursor: pointer;
        font-size: 0.95em;
        margin-right: 12px;
        transition: background-color 0.3s ease, transform 0.1s ease;
    }

    .account-actions button:hover {
        background-color: var(--dark-pink);
        transform: translateY(-1px);
    }

    .account-actions .delete-btn {
        background-color: var(--error-color); 
    }

    .account-actions .delete-btn:hover {
        background-color: #c82333; 
    }
</style>