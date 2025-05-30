<script lang="ts">
	import { createOrUpdateBudgetGoal, type Category } from '$lib/api/budgets';
	import LoadingSpinner from './LoadingSpinner.svelte';
	import ErrorMessage from './ErrorMessage.svelte';
	import { createEventDispatcher } from 'svelte';

	export let category: Category;
	export let currentBudget = 0;
	export let actualExpense = 0;

	const dispatch = createEventDispatcher();

	let monthly_budget = currentBudget || 0;
	let isLoading = false;
	let error: string | null = null;

	async function handleSubmit() {
		error = null;
		isLoading = true;
		try {
			await createOrUpdateBudgetGoal({
				category_id: category.id,
				amount: monthly_budget
			});
			dispatch('budgetUpdated');
		} catch (err: any) {
			console.error('Error updating budget:', err);
			error = err.message || 'Failed to update budget.';
		} finally {
			isLoading = false;
		}
	}

	function handleClose() {
		dispatch('close');
	}

	$: remainingBudget = monthly_budget - actualExpense;
	$: budgetPercentage = monthly_budget > 0 ? (actualExpense / monthly_budget) * 100 : 0;
</script>

<div class="modal-backdrop" on:click|self={handleClose} role="button" tabindex="0">
	<div class="modal-content" role="dialog" aria-modal="true">
		<h2>Set Budget for {category.name}</h2>
		<form on:submit|preventDefault={handleSubmit}>
			<div class="budget-info">
				<div class="info-row">
					<span class="label">Total Spent:</span>
					<span class="value expense"
						>₱{(actualExpense || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}</span
					>
				</div>
			</div>

			<div class="form-group">
				<label for="monthlyBudget">Budget Amount (₱)</label>
				<input
					type="number"
					id="monthlyBudget"
					bind:value={monthly_budget}
					min="0"
					step="0.01"
					placeholder="Set budget amount"
				/>
			</div>

			{#if monthly_budget > 0}
				<div class="budget-status">
					<div class="progress-bar-container">
						<div
							class="progress-bar"
							class:warning={budgetPercentage >= 80}
							class:danger={budgetPercentage >= 100}
							style="width: {Math.min(budgetPercentage, 100)}%"
						></div>
					</div>
					<div class="status-text" class:negative={remainingBudget < 0}>
						{#if remainingBudget >= 0}
							Remaining: ₱{remainingBudget.toLocaleString('en-US', { minimumFractionDigits: 2 })}
						{:else}
							Over Budget by: ₱{Math.abs(remainingBudget).toLocaleString('en-US', {
								minimumFractionDigits: 2
							})}
						{/if}
						<span class="percentage">({budgetPercentage.toFixed(1)}% Used)</span>
					</div>
				</div>
			{/if}

			{#if isLoading}
				<LoadingSpinner message="Updating budget..." />
			{:else if error}
				<ErrorMessage message={error} />
			{/if}

			<div class="modal-actions">
				<button type="submit" class="submit-button" disabled={isLoading}> Update Budget </button>
				<button type="button" class="cancel-button" on:click={handleClose} disabled={isLoading}>
					Cancel
				</button>
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
		border-radius: 15px;
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
		font-size: 1.8em;
	}

	.budget-info {
		background-color: rgba(255, 105, 180, 0.1);
		padding: 15px;
		border-radius: 8px;
		margin-bottom: 20px;
		border: 1px solid rgba(255, 105, 180, 0.2);
	}

	.info-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 8px;
	}

	.info-row:last-child {
		margin-bottom: 0;
	}

	.label {
		color: #666;
		font-size: 0.9em;
	}

	.value {
		font-weight: bold;
		font-size: 1.1em;
	}

	.value.expense {
		color: var(--dark-pink);
	}

	.form-group {
		margin-bottom: 20px;
	}

	.form-group label {
		display: block;
		margin-bottom: 8px;
		font-weight: bold;
		color: #555;
	}

	.form-group input {
		width: 100%;
		padding: 10px;
		border: 2px solid #ffc0cb;
		border-radius: 8px;
		font-size: 1em;
		transition: border-color 0.3s ease;
	}

	.form-group input:focus {
		outline: none;
		border-color: #ff69b4;
	}

	.budget-status {
		margin-top: 15px;
		padding: 15px;
		background-color: #f8f9fa;
		border-radius: 8px;
	}

	.progress-bar-container {
		width: 100%;
		height: 10px;
		background-color: #eee;
		border-radius: 5px;
		overflow: hidden;
		margin-bottom: 10px;
	}

	.progress-bar {
		height: 100%;
		background-color: #ff69b4;
		transition: width 0.3s ease;
	}

	.progress-bar.warning {
		background-color: #ffd700;
	}

	.progress-bar.danger {
		background-color: #ff4444;
	}

	.status-text {
		text-align: right;
		font-size: 0.9em;
		color: #2ecc71;
		font-weight: 500;
	}

	.status-text.negative {
		color: #e74c3c;
	}

	.percentage {
		color: #666;
		margin-left: 8px;
	}

	.modal-actions {
		display: flex;
		justify-content: flex-end;
		gap: 10px;
		margin-top: 20px;
	}

	.modal-actions button {
		padding: 12px 24px;
		border-radius: 25px;
		border: none;
		cursor: pointer;
		font-size: 1em;
		font-weight: bold;
		transition: all 0.3s ease;
	}

	.submit-button {
		background-color: #ff69b4;
		color: white;
	}

	.submit-button:hover {
		background-color: #ff1493;
		transform: translateY(-2px);
	}

	.cancel-button {
		background-color: #ffc0cb;
		color: #333;
	}

	.cancel-button:hover {
		background-color: #ffb6c1;
		transform: translateY(-2px);
	}

	button:disabled {
		opacity: 0.7;
		cursor: not-allowed;
		transform: none !important;
	}
</style>
