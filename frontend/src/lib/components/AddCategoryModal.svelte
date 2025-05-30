<script lang="ts">
    import { createCategory } from '$lib/api/budgets';
    import LoadingSpinner from './LoadingSpinner.svelte';
    import ErrorMessage from './ErrorMessage.svelte';
    import { createEventDispatcher } from 'svelte';

    const dispatch = createEventDispatcher();

    let name = '';
    let type: 'income' | 'expense' = 'expense'; 
    let description = '';

    let isLoading = false;
    let error: string | null = null;

    async function handleSubmit() {
        error = null;
        isLoading = true;
        try {
            const newCategory = await createCategory({ name, type, description });
            dispatch('categoryAdded', newCategory);
        } catch (err: any) {
            console.error('Error adding category:', err);
            error = err.message || 'Failed to add category.';
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
    role="button"        tabindex="0"         aria-label="Close add category modal" >
    <div class="modal-content" role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <h2 id="modal-title">Add New Category</h2>
        <form on:submit|preventDefault={handleSubmit}>
            <div class="form-group">
                <label for="categoryName">Category Name</label>
                <input type="text" id="categoryName" bind:value={name} required />
            </div>
            <div class="form-group">
                <label for="categoryType">Type</label>
                <select id="categoryType" bind:value={type} required>
                    <option value="expense">Expense</option>
                    <option value="income">Income</option>
                </select>
            </div>
            <div class="form-group">
                <label for="categoryDescription">Description (Optional)</label>
                <textarea id="categoryDescription" bind:value={description}></textarea>
            </div>

            {#if isLoading}
                <LoadingSpinner message="Adding category..." />
            {:else if error}
                <ErrorMessage message={error} />
            {/if}

            <div class="modal-actions">
                <button type="submit" disabled={isLoading}>Add Category</button>
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
</style>