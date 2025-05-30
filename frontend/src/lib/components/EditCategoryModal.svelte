<script lang="ts">
    import { updateCategory, type Category } from '$lib/api/budgets';
    import LoadingSpinner from './LoadingSpinner.svelte';
    import ErrorMessage from './ErrorMessage.svelte';
    import { createEventDispatcher } from 'svelte';

    export let category: Category;

    const dispatch = createEventDispatcher();

    let name = category.name;
    let type = category.type;
    let description = category.description || '';
    let icon = category.icon || '💰';
    // CHANGED: Use monthlyBudget for budget goal
    let monthlyBudget = category.monthly_budget || 0;
    let isLoading = false;
    let error: string | null = null;

    async function handleSubmit() {
        error = null;
        isLoading = true;
        try {
            const dataToUpdate: Partial<Category> = {
                name,
                type,
                description,
                icon
            };

            // Only include monthly_budget if the type is expense
            if (type === 'expense') {
                dataToUpdate.monthly_budget = monthlyBudget;
            } else {
                // If an income category, ensure monthly_budget isn't sent or is set to null/0 on backend
                // This depends on whether monthly_budget applies to income categories as well.
                // For now, let's explicitly set it to 0 if it's an income category and you don't budget income.
                dataToUpdate.monthly_budget = 0;
            }

            const updatedCategory = await updateCategory(category.id, dataToUpdate);
            // Dispatch the full updated category object for potential UI updates
            dispatch('categoryUpdated', updatedCategory);
        } catch (err: any) {
            console.error('Error updating category:', err);
            error = err.message || 'Failed to update category.';
        } finally {
            isLoading = false;
        }
    }

    function handleClose() {
        dispatch('close');
    }

    const emojis = [
        '💰', '💳', '🏦', '💵', '🧾', '🛒', '🏠', '🚗', '🍽️', '🎮', '📚', '💊',
        '✈️', '🎁', '👕', '📱', '⚡', '💧', '🎯', '💼'
    ];
</script>

<div
    class="modal-backdrop"
    on:click|self={handleClose}
    on:keydown={(e) => {
        if (e.key === 'Escape') handleClose();
    }}
    role="button"
    tabindex="-1"
>
    <div class="modal-content" role="dialog" aria-modal="true">
        <h2>Edit Category</h2>
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

            {#if type === 'expense'}
                <div class="form-group">
                    <label for="monthlyBudget">Monthly Budget Goal (₱)</label> <input
                        type="number"
                        id="monthlyBudget"
                        bind:value={monthlyBudget} min="0"
                        step="0.01"
                        placeholder="Enter monthly budget goal"
                    />
                    <p class="help-text">Set a recurring monthly spending limit for this category.</p> </div>
            {/if}

            {#if type === 'income'}
                <div class="form-group">
                    <label for="monthlyBudget">Target Monthly Income (₱)</label> <input
                        type="number"
                        id="monthlyBudget"
                        bind:value={monthlyBudget} min="0"
                        step="0.01"
                        placeholder="Enter target monthly income"
                    />
                    <p class="help-text">This is your expected recurring monthly income for this category.</p>
                </div>
            {/if}

            <div class="form-group">
                <label for="categoryIcon">Icon</label>
                <div class="icon-selector">
                    <input type="text" id="categoryIcon" bind:value={icon} maxlength="2" />
                    <div class="emoji-list">
                        {#each emojis as emoji}
                            <button
                                type="button"
                                class="emoji-button"
                                on:click={() => (icon = emoji)}
                                class:selected={icon === emoji}
                            >
                                {emoji}
                            </button>
                        {/each}
                    </div>
                </div>
            </div>

            <div class="form-group">
                <label for="categoryDescription">Description (Optional)</label>
                <textarea id="categoryDescription" bind:value={description}></textarea>
            </div>

            {#if isLoading}
                <LoadingSpinner message="Updating category..." />
            {:else if error}
                <ErrorMessage message={error} />
            {/if}

            <div class="modal-actions">
                <button type="submit" class="submit-button" disabled={isLoading}> Update Category </button>
                <button type="button" class="cancel-button" on:click={handleClose} disabled={isLoading}>
                    Cancel
                </button>
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
    .icon-selector { display: flex; flex-direction: column; gap: 10px; }
    .emoji-list {
        display: grid; grid-template-columns: repeat(auto-fill, minmax(40px, 1fr));
        gap: 8px; margin-top: 10px;
    }
    .emoji-button {
        background: none; border: 2px solid var(--light-pink); border-radius: 8px;
        padding: 8px; font-size: 1.2em; cursor: pointer; transition: all 0.2s ease;
    }
    .emoji-button:hover { background-color: #fff0f5; transform: scale(1.1); }
    .emoji-button.selected { background-color: var(--primary-pink); border-color: var(--primary-pink); }
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
    .help-text {
        font-size: 0.9em; color: #666; margin-top: 8px; font-style: italic;
    }
</style>