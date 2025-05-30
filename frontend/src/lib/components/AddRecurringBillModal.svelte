<script lang="ts">
    import { createRecurringBill, type Category } from '$lib/api/budgets';
    import LoadingSpinner from './LoadingSpinner.svelte';
    import ErrorMessage from './ErrorMessage.svelte';
    import { createEventDispatcher } from 'svelte';

    const dispatch = createEventDispatcher();

    export const categories: Category[] = []; 

    let name = '';
    let amount = 0;
    let dueDay = 1; 
    let categoryId: number | null = null;
    let isActive = true;
    let notes = '';

    let isLoading = false;
    let error: string | null = null;

    const daysOfMonth = Array.from({ length: 31 }, (_, i) => i + 1); 

    async function handleSubmit() {
        error = null;
        isLoading = true;
        try {
            const billData = {
                name,
                amount: parseFloat(amount.toString()),
                due_day: dueDay,
                category: categoryId,
                is_active: isActive,
                notes: notes || null
            };
            const newBill = await createRecurringBill(billData);
            dispatch('recurringBillAdded', newBill);
        } catch (err: any) {
            console.error('Error adding recurring bill:', err);
            error = err.message || 'Failed to add recurring bill.';
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
    role="button"        tabindex="0"         aria-label="Close add recurring bill modal" >
    <div class="modal-content" role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <h2 id="modal-title">Add New Recurring Bill</h2>
        <form on:submit|preventDefault={handleSubmit}>
            <div class="form-group">
                <label for="billName">Bill Name</label>
                <input type="text" id="billName" bind:value={name} required />
            </div>

            <div class="form-group">
                <label for="billAmount">Amount (₱)</label>
                <input type="number" id="billAmount" bind:value={amount} min="0" step="0.01" required />
            </div>

            <div class="form-group">
                <label for="dueDay">Due Day of Month</label>
                <select id="dueDay" bind:value={dueDay} required>
                    {#each daysOfMonth as day}
                        <option value={day}>{day}</option>
                    {/each}
                </select>
            </div>

            <div class="form-group">
                <label for="billCategory">Category (Optional)</label>
                <select id="billCategory" bind:value={categoryId}>
                    <option value={null}>No Category</option>
                    {#each categories as category (category.id)}
                        <option value={category.id}>{category.name}</option>
                    {/each}
                </select>
            </div>

            <div class="form-group checkbox-group">
                <input type="checkbox" id="isActive" bind:checked={isActive} />
                <label for="isActive">Is Active?</label>
            </div>

            <div class="form-group">
                <label for="billNotes">Notes (Optional)</label>
                <textarea id="billNotes" bind:value={notes}></textarea>
            </div>

            {#if isLoading}
                <LoadingSpinner message="Saving bill..." />
            {:else if error}
                <ErrorMessage message={error} />
            {/if}

            <div class="modal-actions">
                <button type="submit" disabled={isLoading}>Add Bill</button>
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
    .form-group input[type="text"],
    .form-group input[type="number"],
    .form-group textarea,
    .form-group select {
        width: calc(100% - 22px);
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 1em;
        box-sizing: border-box;
    }
    .checkbox-group {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
    }
    .checkbox-group input[type="checkbox"] {
        width: auto; 
        margin-right: 10px;
    }
    .checkbox-group label {
        margin-bottom: 0;
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