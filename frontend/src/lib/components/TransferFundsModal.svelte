<script lang="ts">
    import { transferFunds, type Wallet } from '$lib/api/budgets'; // Assuming transferFunds API call exists

    export let wallets: Wallet[]; // List of available wallets (accounts) to transfer between

    let fromWalletId: number | null = null;
    let toWalletId: number | null = null;
    let amount: number | null = null;
    let description: string = '';

    let error: string | null = null;
    let isLoading = false;

    // Filter out the 'from' wallet from the 'to' wallet options
    $: toWalletsOptions = wallets.filter(w => w.id !== fromWalletId);

    async function handleSubmit() {
        error = null;
        isLoading = true;

        if (!fromWalletId || !toWalletId || !amount || amount <= 0) {
            error = 'Please fill in all required fields and ensure amount is positive.';
            isLoading = false;
            return;
        }

        if (fromWalletId === toWalletId) {
            error = 'Cannot transfer funds to the same account.';
            isLoading = false;
            return;
        }

        try {
            // Assuming transferFunds API call exists in budgets.ts
            await transferFunds(fromWalletId, toWalletId, amount, description);
            dispatch('transferCompleted'); // Notify parent component of success
        } catch (err: any) {
            console.error('Transfer failed:', err);
            error = err.message || 'Failed to transfer funds.';
        } finally {
            isLoading = false;
        }
    }

    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();

    function closeModal() {
        dispatch('close');
    }
</script>

<div class="modal-overlay" on:click|self={closeModal}>
    <div class="modal-content">
        <h2>🔄 Transfer Funds</h2>
        <form on:submit|preventDefault={handleSubmit}>
            <div class="form-group">
                <label for="fromWallet">From Account:</label>
                <select id="fromWallet" bind:value={fromWalletId} required>
                    <option value={null} disabled>Select account</option>
                    {#each wallets as wallet (wallet.id)}
                        <option value={wallet.id}>{wallet.name} (₱{wallet.balance.toFixed(2)})</option>
                    {/each}
                </select>
            </div>

            <div class="form-group">
                <label for="toWallet">To Account:</label>
                <select id="toWallet" bind:value={toWalletId} required>
                    <option value={null} disabled>Select account</option>
                    {#each toWalletsOptions as wallet (wallet.id)}
                        <option value={wallet.id}>{wallet.name} (₱{wallet.balance.toFixed(2)})</option>
                    {/each}
                </select>
            </div>

            <div class="form-group">
                <label for="amount">Amount:</label>
                <input type="number" id="amount" bind:value={amount} min="0.01" step="0.01" required />
            </div>

            <div class="form-group">
                <label for="description">Description (Optional):</label>
                <input type="text" id="description" bind:value={description} placeholder="e.g., Savings to Checking" />
            </div>

            {#if error}
                <p class="error-message">{error}</p>
            {/if}

            <div class="modal-actions">
                <button type="submit" class="submit-button" disabled={isLoading}>
                    {#if isLoading}
                        Transferring...
                    {:else}
                        Transfer
                    {/if}
                </button>
                <button type="button" class="cancel-button" on:click={closeModal} disabled={isLoading}>Cancel</button>
            </div>
        </form>
    </div>
</div>

<style>
    /* Modal Overlay */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.6); /* Darker overlay */
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
        backdrop-filter: blur(5px); /* Blurred background */
    }

    /* Modal Content */
    .modal-content {
        background-color: var(--text-white);
        padding: 30px;
        border-radius: 15px; /* More rounded */
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3); /* Deeper shadow */
        width: 90%;
        max-width: 500px;
        position: relative;
        animation: fadeInScale 0.3s ease-out forwards; /* Entry animation */
        font-family: 'Inter', sans-serif;
        color: var(--text-dark);
    }

    @keyframes fadeInScale {
        from {
            opacity: 0;
            transform: scale(0.9);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }

    .modal-content h2 {
        text-align: center;
        color: var(--primary-pink); /* Pink heading */
        margin-bottom: 25px;
        font-size: 2em;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }

    /* Form Group Styling */
    .form-group {
        margin-bottom: 20px;
    }

    .form-group label {
        display: block;
        margin-bottom: 8px;
        font-weight: 600;
        color: var(--text-dark);
        font-size: 1.05em;
    }

    .form-group input[type="text"],
    .form-group input[type="number"],
    .form-group select {
        width: 100%;
        padding: 12px 15px; /* More padding */
        border: 1px solid var(--border-light);
        border-radius: 8px; /* Rounded inputs */
        box-sizing: border-box;
        font-size: 1em;
        color: var(--text-dark);
        background-color: var(--light-gray); /* Light background for inputs */
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }

    .form-group input:focus,
    .form-group select:focus {
        border-color: var(--primary-pink);
        box-shadow: 0 0 0 3px rgba(255, 105, 180, 0.2); /* Pink focus ring */
        outline: none;
        background-color: var(--text-white);
    }

    /* Error Message */
    .error-message {
        color: var(--error-text);
        background-color: var(--error-bg);
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 20px;
        text-align: center;
        border: 1px solid #f5c6cb;
    }

    /* Modal Actions (Buttons) */
    .modal-actions {
        display: flex;
        justify-content: flex-end;
        gap: 15px; /* Space between buttons */
        margin-top: 30px;
    }

    .submit-button, .cancel-button {
        padding: 12px 25px; /* Larger buttons */
        border: none;
        border-radius: 25px; /* Pill shape */
        cursor: pointer;
        font-size: 1.05em;
        font-weight: bold;
        transition: background-color 0.3s ease, transform 0.2s ease, box-shadow 0.3s ease;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    }

    .submit-button {
        background-color: var(--accent-pink); /* Pink submit button */
        color: var(--text-white);
    }
    .submit-button:hover:enabled {
        background-color: var(--dark-pink);
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
    }
    .submit-button:disabled {
        background-color: #cccccc;
        cursor: not-allowed;
        box-shadow: none;
    }

    .cancel-button {
        background-color: var(--border-light); /* Light gray for cancel */
        color: var(--text-dark);
    }
    .cancel-button:hover:enabled {
        background-color: #e0e0e0;
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
    }
    .cancel-button:disabled {
        cursor: not-allowed;
    }

    /* Responsive adjustments */
    @media (max-width: 600px) {
        .modal-content {
            padding: 20px;
        }
        .modal-actions {
            flex-direction: column;
            gap: 10px;
        }
        .submit-button, .cancel-button {
            width: 100%;
        }
    }
</style>
