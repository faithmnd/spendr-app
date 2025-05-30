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
        if (event.key === 'Escape') { // Only close on Escape key for modals
            handleClose();
        }
    }
</script>

<div
    class="modal-backdrop"
    on:click|self={handleClose}
    on:keydown={handleBackdropKeydown}
    role="button" tabindex="-1" aria-label="Close add category modal"
>
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
                <button type="submit" class="submit-button" disabled={isLoading}>Add Category</button>
                <button type="button" on:click={handleClose} disabled={isLoading} class="cancel-button">Cancel</button>
            </div>
        </form>
    </div>
</div>

<style>
    /* CSS Variables (assuming they are in a global file like app.css or layout.svelte) */
    :root {
        --primary-pink: #FF69B4; /* Hot Pink */
        --dark-pink: #C71585;    /* Medium Violet Red */
        --accent-pink: #FF1493;  /* Deep Pink */
        --light-pink: #FFC0CB;   /* Light Pink */
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
        --info-bg: #e0f2f7; /* Light blue for header */
        --info-text: #0056b3;
    }

    .modal-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.6); /* Slightly darker backdrop */
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }
    .modal-content {
        background-color: var(--text-white); /* White content background */
        padding: 30px;
        border-radius: 15px; /* More rounded corners */
        box-shadow: 0 8px 20px var(--shadow-medium); /* Deeper shadow */
        width: 90%;
        max-width: 500px;
        max-height: 90vh;
        overflow-y: auto;
        animation: fadeIn 0.3s ease-out forwards; /* Fade in animation */
    }

    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: scale(0.95);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }

    .modal-content h2 {
        margin-top: 0;
        margin-bottom: 25px; /* More margin below title */
        color: var(--dark-pink); /* Dark pink title */
        text-align: center;
        font-size: 2em; /* Larger title */
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.05);
    }
    .form-group {
        margin-bottom: 20px; /* More space between form groups */
    }
    .form-group label {
        display: block;
        margin-bottom: 8px;
        font-weight: bold;
        color: var(--text-dark); /* Darker text for labels */
    }
    .form-group input,
    .form-group textarea,
    .form-group select {
        width: calc(100% - 20px); /* Adjust width for padding */
        padding: 12px; /* More padding */
        border: 2px solid var(--light-pink); /* Light pink border */
        border-radius: 10px; /* More rounded inputs */
        font-size: 1em;
        box-sizing: border-box;
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }
    .form-group input:focus,
    .form-group textarea:focus,
    .form-group select:focus {
        outline: none;
        border-color: var(--primary-pink); /* Primary pink on focus */
        box-shadow: 0 0 0 3px rgba(255, 105, 180, 0.2); /* Subtle pink glow */
    }
    .modal-actions {
        display: flex;
        justify-content: flex-end;
        gap: 15px; /* More space between buttons */
        margin-top: 30px; /* More margin above buttons */
    }
    .modal-actions button {
        padding: 12px 25px; /* Larger buttons */
        border-radius: 25px; /* Pill shape */
        border: none;
        cursor: pointer;
        font-size: 1em;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); /* Button shadow */
    }
    .submit-button {
        background-color: var(--primary-pink); /* Primary pink submit button */
        color: var(--text-white);
    }
    .submit-button:hover:not(:disabled) {
        background-color: var(--dark-pink); /* Darker pink on hover */
        transform: translateY(-3px); /* Lift effect */
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2); /* Stronger shadow on hover */
    }
    .cancel-button {
        background-color: var(--light-pink); /* Light pink cancel button */
        color: var(--text-dark); /* Dark text for contrast */
    }
    .cancel-button:hover:not(:disabled) {
        background-color: var(--primary-pink); /* Primary pink on hover */
        color: var(--text-white); /* White text on hover */
        transform: translateY(-3px);
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
    }
    .modal-actions button:disabled {
        opacity: 0.6; /* More subtle disabled state */
        cursor: not-allowed;
        transform: none !important; /* Prevent hover transform when disabled */
        box-shadow: none; /* No shadow when disabled */
    }
</style>