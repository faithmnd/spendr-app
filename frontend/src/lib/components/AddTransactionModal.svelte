<script lang="ts">
    import { createTransaction, type Wallet, type Category, type Transaction } from '$lib/api/budgets';
    import LoadingSpinner from './LoadingSpinner.svelte';
    import ErrorMessage from './ErrorMessage.svelte';
    import { createEventDispatcher } from 'svelte';

    const dispatch = createEventDispatcher();

    export let wallets: Wallet[] = [];
    export let categories: Category[] = [];

    let amount: number = 0;
    let transactionType: 'income' | 'expense' = 'expense';
    let description: string = '';
    let date: string = new Date().toISOString().split('T')[0];
    let selectedWalletId: number | null = wallets.length > 0 ? wallets[0].id : null;
    let selectedCategoryId: number | null = null;

    let isLoading = false;
    let error: string | null = null;

    $: filteredCategories = categories.filter(cat => cat.type === transactionType);
    // Reset selected category if type changes and current category is not valid for new type
    $: if (selectedCategoryId && !filteredCategories.find(cat => cat.id === selectedCategoryId)) {
        selectedCategoryId = null;
    }

    async function handleSubmit() {
        error = null;
        isLoading = true;
        try {
            if (selectedWalletId === null) {
                throw new Error('Please select a wallet.');
            }

            const transactionData: Partial<Transaction> = {
                amount: parseFloat(amount.toString()),
                transaction_type: transactionType,
                description: description || null,
                date,
                wallet: selectedWalletId,
                category: selectedCategoryId || undefined // Send undefined if null to avoid 'null' in JSON for optional field
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
        if (event.key === 'Escape') {
            handleClose();
        }
    }
</script>

<div
    class="modal-backdrop"
    on:click|self={handleClose}
    on:keydown={handleBackdropKeydown}
    role="button" tabindex="-1" aria-label="Close add transaction modal"
>
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
                            <option value={wallet.id}>{wallet.name} (₱{Number(wallet.balance).toFixed(2)})</option>
                        {/each}
                    </select>
                {:else}
                    <p class="message-text error-text">No wallets found. Please add a wallet first.</p>
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
                    <p class="message-text warning-text">No {transactionType} categories found. Please add some.</p>
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
                <button type="submit" class="submit-button" disabled={isLoading || wallets.length === 0}>Add Transaction</button>
                <button type="button" on:click={handleClose} disabled={isLoading} class="cancel-button">Cancel</button>
            </div>
        </form>
    </div>
</div>

<style>
    /* Your existing CSS styles for modal-backdrop, modal-content, form-group, etc. */
    /* Ensure your CSS variables are defined, e.g., in a global stylesheet or layout.svelte */
    :root {
        --primary-pink: #FF69B4;
        --dark-pink: #C71585;
        --accent-pink: #FF1493;
        --light-pink: #FFC0CB;
        --text-white: #FFFFFF;
        --text-dark: #333333;
        --text-medium: #555555;
        --border-light: #F0F0F0;
        --shadow-light: rgba(0, 0, 0, 0.08);
        --shadow-medium: rgba(0, 0, 0, 0.12);
        --success-bg: #d4edda;
        --success-text: #155724;
        --error-bg: #f8d7da;
        --error-text: #dc3545;
        --warning-bg: #fff3cd;
        --warning-text: #856404;
        --info-bg: #e0f2f7;
        --info-text: #0056b3;
    }

    .modal-backdrop {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(0, 0, 0, 0.6); display: flex; justify-content: center; align-items: center; z-index: 1000;
    }
    .modal-content {
        background-color: var(--text-white); padding: 30px; border-radius: 15px;
        box-shadow: 0 8px 20px var(--shadow-medium); width: 90%; max-width: 500px;
        max-height: 90vh; overflow-y: auto; animation: fadeIn 0.3s ease-out forwards;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: scale(0.95); }
        to { opacity: 1; transform: scale(1); }
    }
    .modal-content h2 {
        margin-top: 0; margin-bottom: 25px; color: var(--dark-pink); text-align: center;
        font-size: 2em; text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.05);
    }
    .form-group { margin-bottom: 20px; }
    .form-group label {
        display: block; margin-bottom: 8px; font-weight: bold; color: var(--text-dark);
    }
    .form-group input, .form-group textarea, .form-group select {
        width: calc(100% - 20px); padding: 12px; border: 2px solid var(--light-pink);
        border-radius: 10px; font-size: 1em; box-sizing: border-box;
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }
    .form-group input:focus, .form-group textarea:focus, .form-group select:focus {
        outline: none; border-color: var(--primary-pink);
        box-shadow: 0 0 0 3px rgba(255, 105, 180, 0.2);
    }
    .modal-actions {
        display: flex; justify-content: flex-end; gap: 15px; margin-top: 30px;
    }
    .modal-actions button {
        padding: 12px 25px; border-radius: 25px; border: none; cursor: pointer;
        font-size: 1em; font-weight: bold; transition: all 0.3s ease;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    }
    .submit-button { background-color: var(--primary-pink); color: var(--text-white); }
    .submit-button:hover:not(:disabled) {
        background-color: var(--dark-pink); transform: translateY(-3px);
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
    }
    .cancel-button { background-color: var(--light-pink); color: var(--text-dark); }
    .cancel-button:hover:not(:disabled) {
        background-color: var(--primary-pink); color: var(--text-white);
        transform: translateY(-3px); box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
    }
    .modal-actions button:disabled {
        opacity: 0.6; cursor: not-allowed; transform: none !important; box-shadow: none;
    }
    .message-text {
        font-size: 0.9em; margin-top: 5px; display: block; padding: 8px 12px; border-radius: 8px;
    }
    .error-text {
        color: var(--error-text); background-color: var(--error-bg); border: 1px solid var(--error-text);
    }
    .warning-text {
        color: var(--warning-text); background-color: var(--warning-bg); border: 1px solid var(--warning-text);
    }
</style>