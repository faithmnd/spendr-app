<script context="module">
	import { slide } from 'svelte/transition';
</script>

<script lang="ts">
	import { onMount } from 'svelte';
	import {
		getCategories,
		getBudgetGoals,
		getTransactions,
		type Category,
		type BudgetGoal,
		type Transaction,
		deleteCategory,
		updateCategory,
		createOrUpdateBudgetGoal
	} from '$lib/api/budgets';
	import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
	import ErrorMessage from '$lib/components/ErrorMessage.svelte';
	import AddCategoryModal from '$lib/components/AddCategoryModal.svelte';
	import EditCategoryModal from '$lib/components/EditCategoryModal.svelte';
	import ConfirmationModal from '$lib/components/ConfirmationModal.svelte';
	import BudgetModal from '$lib/components/BudgetModal.svelte';

	let categories: CategoryWithBudget[] = [];
	let isLoading = true;
	let error: string | null = null;
	let successMessage: string | null = null;

	let showAddCategoryModal = false;
	let showEditCategoryModal = false;
	let showConfirmationModal = false;
	let showBudgetModal = false;

	let categoryToEdit: Category | null = null;
	let categoryToDelete: { id: number; name: string } | null = null;
	let categoryToSetDefault: { id: number; name: string } | null = null;
	let categoryToSetBudget: Category | null = null;

	let totalBudget = 0;
	let totalExpenses = 0;
	let totalIncome = 0;
	let overallBudgetPercentage = 0;
	let showTotalBudgetSection = false;

	interface CategoryWithBudget extends Category {
		monthly_budget: number;
		actual_expense: number;
		budget_percentage: number;
	}

	interface CategoryUpdateEvent extends CustomEvent<any> {
		detail: {
			monthly_budget?: number;
		};
	}

	async function fetchCategoriesData() {
		error = null;
		try {
			const [fetchedCategories, budgetGoals, transactions] = await Promise.all([
				getCategories(),
				getBudgetGoals(),
				getTransactions()
			]);

			// Create a map of category budgets from budget goals
			const categoryBudgets = new Map<number, number>();
			const categoryExpenses = new Map<number, number>();
			const today = new Date();
			const currentMonth = today.getMonth() + 1;
			const currentYear = today.getFullYear();

			// Find the overall budget goal
			const overallBudgetGoal = budgetGoals.find(
				(goal) => !goal.category && goal.month === currentMonth && goal.year === currentYear
			);

			// Process category-specific budget goals
			budgetGoals.forEach((goal) => {
				if (goal.category && goal.month === currentMonth && goal.year === currentYear) {
					categoryBudgets.set(goal.category, goal.amount);
				}
			});

			// Process transactions to get actual expenses
			transactions.forEach((transaction) => {
				if (
					transaction.transaction_type === 'expense' &&
					new Date(transaction.date).getMonth() + 1 === currentMonth &&
					new Date(transaction.date).getFullYear() === currentYear
				) {
					const currentAmount = categoryExpenses.get(transaction.category) || 0;
					categoryExpenses.set(transaction.category, currentAmount + transaction.amount);
				}
			});

			// Calculate total expenses first
			totalExpenses = Array.from(categoryExpenses.values()).reduce(
				(sum, amount) => sum + amount,
				0
			);

			// Set total budget from overall budget goal
			totalBudget = overallBudgetGoal ? overallBudgetGoal.amount : 0;

			// Calculate overall budget percentage
			overallBudgetPercentage = totalBudget > 0 ? (totalExpenses / totalBudget) * 100 : 0;

			// Map categories with their budgets and expenses
			categories = fetchedCategories.map(
				(cat): CategoryWithBudget => ({
					...cat,
					icon: cat.icon || '💰',
					monthly_budget: categoryBudgets.get(cat.id) || 0,
					actual_expense: categoryExpenses.get(cat.id) || 0,
					budget_percentage: categoryBudgets.get(cat.id)
						? ((categoryExpenses.get(cat.id) || 0) / categoryBudgets.get(cat.id)!) * 100
						: 0
				})
			);

			// Calculate total income from income categories
			totalIncome = categories
				.filter((cat) => cat.type === 'income')
				.reduce((sum, cat) => sum + cat.actual_expense, 0);
		} catch (err: any) {
			console.error('Error loading categories data:', err);
			error = err.message || 'Failed to load categories.';
		} finally {
			isLoading = false;
		}
	}

	async function handleTotalBudgetSubmit(event: CustomEvent) {
		const newBaseBudget = event.detail;
		try {
			// First, create/update the overall budget goal
			await createOrUpdateBudgetGoal({
				category_id: null,
				amount: newBaseBudget
			});

			const expenseCategories = categories.filter((cat) => cat.type === 'expense');
			const totalCurrentExpenseBudget = expenseCategories.reduce(
				(sum, cat) => sum + (cat.monthly_budget ?? 0),
				0
			);

			if (expenseCategories.length > 0) {
				for (const category of expenseCategories) {
					const proportion =
						totalCurrentExpenseBudget > 0
							? (category.monthly_budget ?? 0) / totalCurrentExpenseBudget
							: 1 / expenseCategories.length;

					const newCategoryBudget = newBaseBudget * proportion;

					await createOrUpdateBudgetGoal({
						category_id: category.id,
						amount: newCategoryBudget
					});
				}
			}

			showTotalBudgetSection = false;
			successMessage = 'Total budget updated successfully!';
			setTimeout(() => (successMessage = null), 3000);

			await fetchCategoriesData();
		} catch (err: any) {
			console.error('Error updating total budget:', err);
			error = err.message || 'Failed to update total budget.';
			await fetchCategoriesData();
		}
	}

	function handleEditBudget(category: Category) {
		categoryToSetBudget = category;
		showBudgetModal = true;
	}

	async function handleBudgetUpdated() {
		showBudgetModal = false;
		categoryToSetBudget = null;
		successMessage = 'Budget updated successfully!';
		setTimeout(() => (successMessage = null), 3000);
		await fetchCategoriesData();
	}

	onMount(async () => {
		await fetchCategoriesData();
	});

	function handleModalClose() {
		showAddCategoryModal = false;
		showEditCategoryModal = false;
		showConfirmationModal = false;
		showBudgetModal = false;
		categoryToEdit = null;
		categoryToDelete = null;
		categoryToSetDefault = null;
		categoryToSetBudget = null;
	}

	async function handleCategoryChange(event: CustomEvent<any>) {
		// Get the updated category from the event
		const updatedCategory = event.detail;

		// Update the category in the list
		const categoryIndex = categories.findIndex((c) => c.id === categoryToEdit?.id);
		if (categoryIndex !== -1) {
			// Update the category with new data
			categories[categoryIndex] = {
				...categories[categoryIndex],
				...updatedCategory,
				monthly_budget: updatedCategory.monthly_budget || categories[categoryIndex].monthly_budget
			};

			// Trigger reactivity
			categories = [...categories];

			// Recalculate total expenses from transactions
			totalExpenses = categories
				.filter((cat) => cat.type === 'expense')
				.reduce((sum, cat) => sum + (cat.actual_expense || 0), 0);

			// Update budget percentages
			overallBudgetPercentage = totalBudget > 0 ? (totalExpenses / totalBudget) * 100 : 0;

			// Update individual category budget percentage
			categories = categories.map((cat) => ({
				...cat,
				budget_percentage:
					cat.monthly_budget && cat.monthly_budget > 0
						? ((cat.actual_expense || 0) / cat.monthly_budget) * 100
						: 0
			}));
		}

		successMessage = 'Category data updated successfully!';
		handleModalClose();
		setTimeout(() => (successMessage = null), 3000);
	}

	async function handleEditCategory(category: Category) {
		categoryToEdit = category;
		showEditCategoryModal = true;
	}

	function confirmDeleteCategory(categoryId: number, categoryName: string) {
		categoryToDelete = { id: categoryId, name: categoryName };
		showConfirmationModal = true;
	}

	async function executeDeleteCategory() {
		if (categoryToDelete) {
			try {
				await deleteCategory(categoryToDelete.id);
				successMessage = `Category "${categoryToDelete.name}" deleted successfully!`;
				await fetchCategoriesData();
				setTimeout(() => (successMessage = null), 3000);
			} catch (err: any) {
				console.error('Error deleting category:', err);
				error = err.message || 'Failed to delete category.';
			} finally {
				handleModalClose();
			}
		}
	}

	function confirmSetDefaultCategory(categoryId: number, categoryName: string) {
		categoryToSetDefault = { id: categoryId, name: categoryName };
		showConfirmationModal = true;
	}

	async function executeSetDefaultCategory() {
		if (categoryToSetDefault) {
			try {
				for (const cat of categories) {
					if (cat.is_default && cat.id !== categoryToSetDefault.id) {
						await updateCategory(cat.id, { is_default: false });
					}
				}
				await updateCategory(categoryToSetDefault.id, { is_default: true });
				successMessage = `Set "${categoryToSetDefault.name}" as default category!`;
				await fetchCategoriesData();
				setTimeout(() => (successMessage = null), 3000);
			} catch (err: any) {
				console.error('Error setting default category:', err);
				error = err.message || 'Failed to set default category.';
			} finally {
				handleModalClose();
			}
		}
	}

	$: expenseCategories = categories.filter((cat) => cat.type === 'expense');
	$: incomeCategories = categories.filter((cat) => cat.type === 'income');
</script>

<svelte:head>
	<title>Spendr - Categories</title>
</svelte:head>

<div class="categories-wrapper">
	<div class="categories-header">
		<h1>𝜗𝜚 Categories Page ⋆. 𐙚 ˚</h1>
		<p>Make cute little labels for your chaos. Rename, edit, vibe—it's your budget era.</p>

		<div class="budget-overview-card">
			<div class="budget-stats">
				<div class="budget-stat">
					<span class="stat-label">Total Budget</span>
					<span class="stat-value"
						>₱{(totalBudget ?? 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}</span
					>
				</div>
				<div class="budget-stat">
					<span class="stat-label">Total Spent</span>
					<span class="stat-value expense"
						>₱{(totalExpenses ?? 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}</span
					>
				</div>
				<div class="budget-stat">
					<span class="stat-label">Remaining Budget</span>
					<span class="stat-value" class:danger={totalBudget - totalExpenses < 0}>
						₱{((totalBudget ?? 0) - (totalExpenses ?? 0)).toLocaleString('en-US', {
							minimumFractionDigits: 2
						})}
					</span>
				</div>
			</div>
			<div class="budget-progress-bar-container">
				<div
					class="budget-progress-bar"
					class:warning={overallBudgetPercentage >= 80 && overallBudgetPercentage < 100}
					class:danger={overallBudgetPercentage >= 100}
					style="width: {Math.min(overallBudgetPercentage ?? 0, 100)}%;"
				></div>
			</div>
			<div class="budget-percentage">
				{(overallBudgetPercentage ?? 0).toFixed(1)}% of Budget Used (₱{(
					totalExpenses ?? 0
				).toLocaleString('en-US', { minimumFractionDigits: 2 })} of ₱{(
					totalBudget ?? 0
				).toLocaleString('en-US', { minimumFractionDigits: 2 })})
			</div>
		</div>
	</div>

	<div class="controls-section">
		<button class="add-button" on:click={() => (showAddCategoryModal = true)}
			>+ Add New Category</button
		>
		<button
			class="edit-budget-button"
			on:click={() => (showTotalBudgetSection = !showTotalBudgetSection)}
		>
			{showTotalBudgetSection ? 'Cancel' : '+ Edit Total Budget'}
		</button>
	</div>

	{#if showTotalBudgetSection}
		<div class="total-budget-section" transition:slide>
			<form
				class="budget-form"
				on:submit|preventDefault={(e) => {
					const form = e.target as HTMLFormElement;
					const input = form.querySelector('input') as HTMLInputElement;
					handleTotalBudgetSubmit(new CustomEvent('submit', { detail: parseFloat(input.value) }));
				}}
			>
				<div class="form-group">
					<label for="totalBudgetInput">Set Total Expense Budget Amount (₱)</label>
					<div class="input-group">
						<input
							type="number"
							id="totalBudgetInput"
							value={totalBudget - (totalIncome ?? 0)}
							min="0"
							step="0.01"
							placeholder="Enter total budget amount"
							required
						/>
						<button type="submit" class="submit-button">Update Budget</button>
					</div>
					<p class="help-text">
						This amount will be distributed proportionally across all your expense categories.
					</p>
				</div>
			</form>
		</div>
	{/if}

	<div class="category-sections">
		<section class="category-section expense-categories">
			<h2>Expense Categories</h2>
			{#if expenseCategories.length > 0}
				<ul class="category-list">
					{#each expenseCategories as category (category.id)}
						<li class="category-item">
							<span class="category-icon">{category.icon || '❓'}</span>
							<div class="category-info">
								<span class="category-name">{category.name}</span>
								<span class="category-type type-expense">{category.type}</span>
								<div class="amount-display">
									<span class="amount-label">Spent:</span>
									<span class="amount-value expense">
										₱{(category.actual_expense ?? 0).toLocaleString('en-US', {
											minimumFractionDigits: 2
										})}
									</span>
								</div>
								<div class="budget-progress-bar-container category-progress">
									<div
										class="budget-progress-bar"
										class:warning={category.budget_percentage >= 80 &&
											category.budget_percentage < 100}
										class:danger={category.budget_percentage >= 100}
										style="width: {Math.min(category.budget_percentage ?? 0, 100)}%;"
									></div>
								</div>
								<span
									class="budget-progress-text"
									class:warning={category.budget_percentage >= 80 &&
										category.budget_percentage < 100}
									class:danger={category.budget_percentage >= 100}
								>
									{(category.budget_percentage ?? 0).toFixed(1)}% Used (₱{(
										category.actual_expense ?? 0
									).toLocaleString('en-US', { minimumFractionDigits: 2 })}
									of ₱{(category.monthly_budget ?? 0).toLocaleString('en-US', {
										minimumFractionDigits: 2
									})})
								</span>
							</div>
							<div class="category-actions">
								<button
									class="action-button budget-button"
									on:click={() => handleEditBudget(category)}
								>
									💰 Budget
								</button>
								<button
									class="action-button edit-button"
									on:click={() => handleEditCategory(category)}
								>
									✏️ Edit
								</button>
								<button
									class="action-button delete-button"
									on:click={() => confirmDeleteCategory(category.id, category.name)}
								>
									🗑️ Delete
								</button>
								<button
									class="action-button default-button"
									class:is-default={category.is_default}
									on:click={() => confirmSetDefaultCategory(category.id, category.name)}
								>
									{category.is_default ? '⭐ Default' : '⭐ Set Default'}
								</button>
							</div>
						</li>
					{/each}
				</ul>
			{:else}
				<p class="no-data-message">
					No expense categories added yet. Time to organize your spending!
				</p>
			{/if}
		</section>

		<section class="category-section income-categories">
			<h2>Income Categories</h2>
			{#if incomeCategories.length > 0}
				<ul class="category-list">
					{#each incomeCategories as category (category.id)}
						<li class="category-item">
							<span class="category-icon">{category.icon || '❓'}</span>
							<div class="category-info">
								<span class="category-name">{category.name}</span>
								<span class="category-type type-income">{category.type}</span>
								<div class="amount-display">
									<span class="amount-label">Received:</span>
									<span class="amount-value income"
										>₱{(category.actual_expense ?? 0).toLocaleString('en-US', {
											minimumFractionDigits: 2
										})}</span
									>
								</div>
							</div>
							<div class="category-actions">
								<button
									class="action-button edit-button"
									on:click={() => handleEditCategory(category)}
								>
									✏️ Edit
								</button>
								<button
									class="action-button delete-button"
									on:click={() => confirmDeleteCategory(category.id, category.name)}
								>
									> 🗑️ Delete
								</button>
								<button
									class="action-button default-button"
									class:is-default={category.is_default}
									on:click={() => confirmSetDefaultCategory(category.id, category.name)}
								>
									{category.is_default ? '⭐ Default' : '⭐ Set Default'}
								</button>
							</div>
						</li>
					{/each}
				</ul>
			{:else}
				<p class="no-data-message">No income categories added yet. Track your earnings!</p>
			{/if}
		</section>
	</div>
</div>

{#if successMessage}
	<div class="success-message" transition:slide>{successMessage}</div>
{/if}

{#if isLoading}
	<LoadingSpinner message="Loading your wallet ♡ — don't worry, we didn't spend anything ₊˚⊹" />
{:else if error}
	<ErrorMessage message={error} />
{/if}

{#if showAddCategoryModal}
	<AddCategoryModal on:close={handleModalClose} on:categoryAdded={handleCategoryChange} />
{/if}

{#if showEditCategoryModal && categoryToEdit}
	<EditCategoryModal
		category={categoryToEdit}
		on:close={handleModalClose}
		on:categoryUpdated={handleCategoryChange}
	/>
{/if}

{#if showConfirmationModal && (categoryToDelete || categoryToSetDefault)}
	<ConfirmationModal
		title={categoryToDelete ? 'Confirm Delete' : 'Confirm Set Default'}
		message={categoryToDelete
			? `Are you sure you want to delete the category "${categoryToDelete.name}"? This cannot be undone.`
			: `Are you sure you want to set "${categoryToSetDefault?.name}" as the default category? This will unset any other default categories.`}
		on:confirm={categoryToDelete ? executeDeleteCategory : executeSetDefaultCategory}
		on:cancel={handleModalClose}
	/>
{/if}

{#if showBudgetModal && categoryToSetBudget}
	<BudgetModal
		category={categoryToSetBudget}
		currentBudget={categories.find((c) => c.id === categoryToSetBudget?.id)?.monthly_budget || 0}
		actualExpense={categories.find((c) => c.id === categoryToSetBudget?.id)?.actual_expense || 0}
		on:budgetUpdated={handleBudgetUpdated}
		on:close={() => {
			showBudgetModal = false;
			categoryToSetBudget = null;
		}}
	/>
{/if}

<style>
	/* CSS Variables (assuming they are in a global file like app.css or layout.svelte) */
	:root {
		--primary-pink: #ff69b4; /* Hot Pink */
		--dark-pink: #c71585; /* Medium Violet Red */
		--accent-pink: #ff1493; /* Deep Pink */
		--light-pink: #ffc0cb; /* Light Pink */
		--text-white: #ffffff;
		--text-dark: #333333;
		--text-medium: #555555;
		--border-light: #f0f0f0;
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

		--income-color: #28a745; /* Green */
		--expense-color: #dc3545; /* Red */
		--balance-color: #007bff; /* Blue */
		--wallet-color: #6c757d; /* Gray */
	}

	.categories-wrapper {
		padding: 20px;
		max-width: 1200px;
		margin: 0 auto;
		font-family: 'Inter', sans-serif;
		color: var(--text-dark);
	}

	.categories-header {
		text-align: center;
		margin-bottom: 30px;
		padding: 25px;
		background: linear-gradient(135deg, var(--light-pink), var(--primary-pink));
		color: var(--text-white);
		border-radius: 15px;
		box-shadow: 0 6px 15px var(--shadow-medium);
	}
	.categories-header h1 {
		color: var(--text-white);
		font-size: 2.8em;
		margin-bottom: 10px;
		text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
	}
	.categories-header p {
		color: var(--text-white);
		font-size: 1.2em;
		opacity: 0.9;
	}

	.budget-overview-card {
		background: rgba(255, 255, 255, 0.15); /* Slightly transparent white on pink gradient */
		border-radius: 15px;
		padding: 25px;
		margin-top: 20px;
		backdrop-filter: blur(5px); /* Subtle blur effect */
		border: 1px solid rgba(255, 255, 255, 0.2); /* Light border */
		box-shadow: inset 0 0 10px rgba(255, 255, 255, 0.1); /* Inner shadow */
	}

	.budget-stats {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); /* Responsive grid */
		gap: 20px;
		margin-bottom: 15px;
	}

	.budget-stat {
		text-align: center;
		padding: 10px;
		background-color: rgba(255, 255, 255, 0.1); /* Lighter background for individual stats */
		border-radius: 10px;
	}

	.stat-label {
		display: block;
		font-size: 0.9em;
		margin-bottom: 5px;
		color: rgba(255, 255, 255, 0.9);
		font-weight: 500;
	}

	.stat-value {
		font-size: 1.6em;
		font-weight: bold;
		color: white;
		text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
	}

	.stat-value.expense {
		color: var(--expense-color);
	}

	.stat-value.danger {
		color: var(--error-text);
	}

	.budget-progress-bar-container {
		width: 100%;
		background-color: rgba(255, 255, 255, 0.3); /* Lighter background for bar container */
		border-radius: 8px;
		height: 12px; /* Slightly taller bar */
		overflow: hidden;
		margin-top: 15px;
		box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
	}
	.budget-progress-bar {
		height: 100%;
		background-color: var(--accent-pink); /* Accent pink for progress */
		border-radius: 8px;
		transition:
			width 0.5s ease-in-out,
			background-color 0.3s ease-in-out;
	}
	.budget-progress-bar.warning {
		background-color: #ffa000; /* Orange for warning */
	}
	.budget-progress-bar.danger {
		background-color: var(--error-text); /* Red for danger */
	}

	.budget-percentage {
		font-size: 1.1em;
		font-weight: bold;
		color: var(--text-white);
		text-align: right;
		margin-top: 10px;
		text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
	}

	.controls-section {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 15px;
		margin: 30px 0;
	}

	.add-button,
	.edit-budget-button {
		background-color: var(--accent-pink);
		color: var(--text-white);
		border: none;
		padding: 12px 22px;
		border-radius: 25px;
		cursor: pointer;
		font-size: 1em;
		font-weight: bold;
		transition:
			background-color 0.3s ease,
			transform 0.2s ease,
			box-shadow 0.3s ease;
		box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
		white-space: nowrap;
	}

	.edit-budget-button {
		background-color: var(--primary-pink);
	}

	.add-button:hover,
	.edit-budget-button:hover {
		background-color: var(--dark-pink);
		transform: translateY(-3px);
		box-shadow: 0 6px 15px rgba(0, 0, 0, 0.25);
	}

	.add-button:active,
	.edit-budget-button:active {
		transform: translateY(0);
		box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
	}

	.category-sections {
		display: grid;
		grid-template-columns: 1fr;
		gap: 30px;
	}

	@media (min-width: 768px) {
		.category-sections {
			grid-template-columns: 1fr 1fr;
		}
	}

	.category-section {
		background-color: var(--text-white);
		padding: 30px;
		border-radius: 15px;
		box-shadow: 0 6px 18px var(--shadow-light);
		border: 1px solid var(--border-light);
		transition: box-shadow 0.3s ease-in-out;
	}
	.category-section:hover {
		box-shadow: 0 10px 25px var(--shadow-medium);
	}

	.category-section h2 {
		margin-top: 0;
		color: var(--text-dark);
		border-bottom: 1px solid var(--border-light);
		padding-bottom: 15px;
		margin-bottom: 25px;
		font-size: 1.8em;
		font-weight: 700;
		text-align: center;
	}

	.category-list {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.category-item {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		padding: 15px 0;
		border-bottom: 1px dashed var(--border-light);
		font-size: 1.1em;
		color: var(--text-medium);
		gap: 10px;
	}
	.category-item:last-child {
		border-bottom: none;
	}

	.category-icon {
		font-size: 1.5em;
		margin-right: 5px;
		flex-shrink: 0;
	}

	.category-info {
		flex: 1;
		min-width: 0;
	}

	.category-name {
		font-weight: bold;
		color: var(--text-dark);
		flex-grow: 1;
		display: block;
	}

	.category-type {
		font-size: 0.9em;
		padding: 4px 8px;
		border-radius: 15px;
		text-transform: capitalize;
		font-weight: 600;
		white-space: nowrap;
		margin-left: 5px;
	}
	.type-expense {
		background-color: var(--light-pink);
		color: var(--dark-pink);
	}
	.type-income {
		background-color: #d4edda;
		color: #155724;
	}

	.amount-display {
		display: flex;
		align-items: center;
		gap: 5px;
		margin-top: 5px;
		font-size: 0.95em;
	}
	.amount-label {
		color: var(--text-medium);
	}
	.amount-value {
		font-weight: 600;
		color: var(--text-dark);
	}
	.amount-value.expense {
		color: var(--expense-color);
	}
	.amount-value.income {
		color: var(--income-color);
	}

	.category-progress {
		margin-top: 10px;
		height: 8px;
	}
	.budget-progress-text {
		font-size: 0.85em;
		margin-top: 5px;
		display: block;
		text-align: left;
		color: var(--text-medium);
		font-weight: bold;
	}
	.budget-progress-text.warning {
		color: #ffa000;
	}
	.budget-progress-text.danger {
		color: #ff4444;
	}

	.category-actions {
		display: flex;
		gap: 8px;
		margin-top: 10px;
		flex-basis: 100%;
		justify-content: flex-end;
		flex-wrap: wrap;
	}

	.action-button {
		padding: 8px 15px;
		border-radius: 20px;
		cursor: pointer;
		font-size: 0.9em;
		font-weight: 600;
		transition: all 0.2s ease;
		border: none;
		white-space: nowrap;
		background-color: var(--accent-pink);
		color: var(--text-white);
	}

	.action-button:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
	}

	.edit-button {
		background-color: var(--primary-pink);
	}
	.edit-button:hover {
		background-color: var(--dark-pink);
	}

	.delete-button {
		background-color: var(--error-text);
	}
	.delete-button:hover {
		background-color: #a71d2a;
	}

	.default-button {
		background-color: var(--light-pink);
		color: var(--dark-pink);
	}
	.default-button:hover {
		background-color: var(--primary-pink);
		color: var(--text-white);
	}
	.default-button.is-default {
		background-color: var(--primary-pink);
		color: var(--text-white);
		box-shadow:
			inset 0 0 0 2px var(--text-white),
			0 2px 5px rgba(0, 0, 0, 0.1);
	}

	.no-data-message {
		text-align: center;
		padding: 30px;
		font-size: 1.1em;
		color: var(--text-medium);
		background-color: var(--light-pink);
		border-radius: 10px;
		box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
		margin-top: 20px;
		border: 1px solid var(--primary-pink);
	}

	.success-message {
		background-color: var(--success-bg);
		color: var(--success-text);
		padding: 15px;
		border-radius: 10px;
		margin-bottom: 30px;
		text-align: center;
		font-weight: bold;
		border: 1px solid #a3e6b3;
		box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
	}

	.total-budget-section {
		background: white;
		border-radius: 15px;
		padding: 20px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
		margin-bottom: 30px;
		border: 1px solid var(--border-light);
	}

	.budget-form {
		width: 100%;
	}

	.form-group label {
		display: block;
		margin-bottom: 5px;
		font-weight: 600;
		color: var(--text-dark);
	}

	.input-group {
		display: flex;
		gap: 10px;
		margin-top: 8px;
	}

	.input-group input {
		flex: 1;
		padding: 12px;
		border: 2px solid var(--light-pink);
		border-radius: 8px;
		font-size: 1em;
		transition: border-color 0.3s ease;
	}

	.input-group input:focus {
		outline: none;
		border-color: var(--primary-pink);
	}

	.input-group .submit-button {
		background-color: var(--primary-pink);
		color: white;
		border: none;
		padding: 12px 24px;
		border-radius: 8px;
		cursor: pointer;
		font-weight: bold;
		transition: all 0.3s ease;
	}

	.input-group .submit-button:hover {
		background-color: var(--dark-pink);
		transform: translateY(-2px);
	}

	.help-text {
		font-size: 0.9em;
		color: #666;
		margin-top: 8px;
		font-style: italic;
	}

	/* Responsive adjustments */
	@media (max-width: 768px) {
		.controls-section {
			flex-direction: column;
		}
		.input-group {
			flex-direction: column;
		}
		.input-group .submit-button {
			width: 100%;
		}
		.budget-stats {
			grid-template-columns: 1fr;
			gap: 15px;
		}
		.budget-overview-card {
			padding: 20px;
		}
		.category-item {
			flex-direction: column;
			align-items: flex-start;
			gap: 5px;
		}
		.category-actions {
			justify-content: flex-start;
			margin-top: 15px;
		}
		.category-icon {
			margin-right: 0;
			margin-bottom: 5px;
		}
		.category-name,
		.category-type,
		.amount-display {
			width: 100%;
			text-align: left;
		}
		.budget-progress-text {
			text-align: left;
		}
	}

	.action-button.budget-button {
		background-color: #4caf50; /* Green color for budget */
		color: white;
	}
	.action-button.budget-button:hover {
		background-color: #388e3c;
	}
</style>
