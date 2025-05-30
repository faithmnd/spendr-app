<script lang="ts">
    import { createWallet } from '$lib/api/budgets'; 
    import LoadingSpinner from './LoadingSpinner.svelte';
    import ErrorMessage from './ErrorMessage.svelte';
    import { createEventDispatcher } from 'svelte';

    const dispatch = createEventDispatcher();

    let name = '';
    let balance = 0;
    let currency = 'PHP';
    let description = '';

    let isLoading = false;
    let error: string | null = null;

    async function handleSubmit() {
        error = null;
        isLoading = true;
        try {
            const newWallet = await createWallet({ name, balance: parseFloat(balance.toString()), currency, description });
            dispatch('walletAdded', newWallet); 
        } catch (err: any) {
            console.error('Error adding wallet:', err);
            error = err.message || 'Failed to add wallet.';
        } finally {
            isLoading = false;
        }
    }

    function handleClose() {
        dispatch('close'); 
    }

    function handleBackdropKeydown(event: KeyboardEvent) {
        if (event.key === 'Escape' || event.key === 'Enter' || event.key === ' ') {
            handleClose();
        }
    }
</script>

<div
    class="modal-backdrop"
    on:click|self={handleClose}
    on:keydown={handleBackdropKeydown}
    role="button"
    tabindex="0"
    aria-label="Close add wallet modal"
>
    <div class="modal-content" role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <h2 id="modal-title">Add New Wallet</h2>
        <form on:submit|preventDefault={handleSubmit}>
            <div class="form-group">
                <label for="walletName">Wallet Name</label>
                <input type="text" id="walletName" bind:value={name} required />
            </div>
            <div class="form-group">
                <label for="initialBalance">Initial Balance (₱)</label>
                <input type="number" id="initialBalance" bind:value={balance} min="0" step="0.01" required />
            </div>
            <div class="form-group">
                <label for="currency">Currency</label>
                <input type="text" id="currency" bind:value={currency} maxlength="3" required />
            </div>
            <div class="form-group">
                <label for="walletDescription">Description (Optional)</label>
                <textarea id="walletDescription" bind:value={description}></textarea>
            </div>

            {#if isLoading}
                <LoadingSpinner message="Adding wallet..." />
            {:else if error}
                <ErrorMessage message={error} />
            {/if}

            <div class="modal-actions">
                <button type="submit" disabled={isLoading}>Add Wallet</button>
                <button type="button" on:click={handleClose} disabled={isLoading} class="cancel-button">Cancel</button>
            </div>
        </form>
    </div>
</div>

<style>
    .modal-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }
    .modal-content {
        background-color: white;
        padding: 30px;
        border-radius: 8px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        width: 90%;
        max-width: 500px;
        max-height: 90vh; 
        overflow-y: auto; 
    }
    .modal-content h2 {
        margin-top: 0;
        margin-bottom: 20px;
        color: #333;
        text-align: center;
    }
    .form-group {
        margin-bottom: 15px;
    }
    .form-group label {
        display: block;
        margin-bottom: 5px;
        font-weight: bold;
        color: #555;
    }
    .form-group input, .form-group textarea {
        width: calc(100% - 22px);
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 1em;
        box-sizing: border-box;
    }
    .modal-actions {
        display: flex;
        justify-content: flex-end;
        gap: 10px;
        margin-top: 20px;
    }
    .modal-actions button {
        padding: 10px 20px;
        border-radius: 5px;
        border: none;
        cursor: pointer;
        font-size: 1em;
        transition: background-color
    }
</style>