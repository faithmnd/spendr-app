<script lang="ts">
    import { createTransaction, type Wallet, type Category } from '$lib/api/budgets';
    import LoadingSpinner from './LoadingSpinner.svelte';
    import ErrorMessage from './ErrorMessage.svelte';
    import { createEventDispatcher } from 'svelte';

    const dispatch = createEventDispatcher();

    export const wallets: Wallet[] = []; 
    export const categories: Category[] = []; 

    let amount: number = 0;
    let transactionType: 'income' | 'expense' = 'expense';
    let description: string = '';
    let date: string = new Date().toISOString().split('T')[0]; 
    let selectedWalletId: number | null = wallets.length > 0 ? wallets[0].id : null;
    let selectedCategoryId: number | null = null; 

    let isLoading = false;
    let error: string | null = null;

    $: filteredCategories = categories.filter(cat => cat.type === transactionType);

    async function handleSubmit() {
        error = null;
        isLoading = true;
        try {
            if (selectedWalletId === null) {
                throw new Error('Please select a wallet.');
            }

            const transactionData = {
                amount: parseFloat(amount.toString()),
                transaction_type: transactionType,
                description: description || null,
                date,
                wallet: selectedWalletId,
                category: selectedCategoryId 
            };

            const newTransaction = await createTransaction(transactionData);
            dispatch('transactionAdded', newTransaction); 
        } catch (err: any) {
            console.error('Error adding transaction:', err);
            error = err.message || 'Failed to add transaction.';
            if (err.message.includes("The selected category type")) {
                error = "Selected category type does not match transaction type. Please choose an appropriate category.";
            }
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
    role="button"        tabindex="0"         aria-label="Close add transaction modal" >
    <div class="modal-content" role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <h2 id="modal-title">Add New Transaction</h2>
        <form on:submit|preventDefault={handleSubmit}>
            <div class="form-group">
                <label for="transactionType">Transaction Type</label>
                <select id="transactionType" bind:value={transactionType} required>
                    <option value="expense">Expense</option>
                    <option value="income">Income</option>
                </select>
            </div>

            <div class="form-group">
                <label for="amount">Amount (₱)</label>
                <input type="number" id="amount" bind:value={amount} min="0.01" step="0.01" required />
            </div>

            <div class="form-group">
                <label for="date">Date</label>
                <input type="date" id="date" bind:value={date} required />
            </div>

            <div class="form-group">
                <label for="wallet">Wallet</label>
                {#if wallets.length > 0}
                    <select id="wallet" bind:value={selectedWalletId} required>
                        {#each wallets as wallet (wallet.id)}
                            <option value={wallet.id}>{wallet.name} (₱{wallet.balance.toFixed(2)})</option>
                        {/each}
                    </select>
                {:else}
                    <p class="error-text">No wallets found. Please add a wallet first.</p>
                {/if}
            </div>

            <div class="form-group">
                <label for="category">Category</label>
                {#if filteredCategories.length > 0}
                    <select id="category" bind:value={selectedCategoryId}>
                        <option value={null}>No Category</option>
                        {#each filteredCategories as category (category.id)}
                            <option value={category.id}>{category.name}</option>
                        {/each}
                    </select>
                {:else}
                    <p class="warning-text">No {transactionType} categories found. Please add some.</p>
                    <select id="category" bind:value={selectedCategoryId} disabled>
                        <option value={null}>No Categories Available</option>
                    </select>
                {/if}
            </div>

            <div class="form-group">
                <label for="description">Description (Optional)</label>
                <textarea id="description" bind:value={description}></textarea>
            </div>

            {#if isLoading}
                <LoadingSpinner message="Adding transaction..." />
            {:else if error}
                <ErrorMessage message={error} />
            {/if}

            <div class="modal-actions">
                <button type="submit" disabled={isLoading || wallets.length === 0}>Add Transaction</button>
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
    .form-group input, .form-group textarea, .form-group select {
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
        transition: background-color 0.2s ease;
    }
    .modal-actions button[type="submit"] {
        background-color: #007bff;
        color: white;
    }
    .modal-actions button[type="submit"]:hover:not(:disabled) {
        background-color: #0056b3;
    }
    .modal-actions button.cancel-button {
        background-color: #6c757d;
        color: white;
    }
    .modal-actions button.cancel-button:hover:not(:disabled) {
        background-color: #5a6268;
    }
    .modal-actions button:disabled {
        background-color: #cccccc;
        cursor: not-allowed;
    }
    .error-text, .warning-text {
        color: #dc3545; 
        font-size: 0.9em;
        margin-top: 5px;
        display: block;
    }
    .warning-text {
        color: #ffc107; 
    }
</style>