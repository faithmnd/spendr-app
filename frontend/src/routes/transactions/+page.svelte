<script lang="ts">
	import { onMount } from 'svelte';
	import {
		getTransactions,
		getCategories,
		type Transaction,
		type Wallet,
		type Category
	} from '$lib/api/budgets';
	import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
	import ErrorMessage from '$lib/components/ErrorMessage.svelte';
	import AddTransactionModal from '$lib/components/AddTransactionModal.svelte';

	let transactions: Transaction[] = [];
	let wallets: Wallet[] = []; // Needed for AddTransactionModal
	let categories: Category[] = []; // Needed for AddTransactionModal and filtering
	let isLoading = true;
	let error: string | null = null;
	let showAddTransactionModal = false;

	// Filtering and Sorting state
	let searchTerm = '';
	let selectedCategory: string | null = null;
	let selectedWallet: string | null = null;
	let sortColumn: keyof Transaction = 'date'; // Default sort by date
	let sortDirection: 'asc' | 'desc' = 'desc'; // Default descending for date

	// Date filtering states
	let startDate: string | null = null;
	let endDate: string | null = null;

	async function fetchTransactionsData() {
		error = null;
		try {
			// Fetch all transactions
			transactions = await getTransactions();
			// Fetch wallets and categories for the AddTransactionModal and filters
			const dashboardSummary = await (await import('$lib/api/budgets')).getDashboardSummary();
			wallets = dashboardSummary.wallets;
			categories = await getCategories(); // Get all categories, not just expense ones
		} catch (err: any) {
			console.error('Error loading transactions data:', err);
			error = err.message || 'Failed to load transactions.';
		} finally {
			isLoading = false;
		}
	}

	onMount(async () => {
		await fetchTransactionsData();
	});

	function handleModalClose() {
		showAddTransactionModal = false;
	}

	async function handleTransactionAdded() {
		showAddTransactionModal = false;
		await fetchTransactionsData(); // Re-fetch all data to update the table
	}

	// Placeholder functions for Edit/Delete (implementation for modals/API calls would go here)
	function handleEditTransaction(transaction: Transaction) {
		console.log('Edit transaction:', transaction);
		// TODO: Implement logic to open an EditTransactionModal with transaction data
	}

	function handleDeleteTransaction(transactionId: number) {
		console.log('Delete transaction with ID:', transactionId);
		// TODO: Implement logic to call delete API and then re-fetch data
		if (confirm('Are you sure you want to delete this transaction?')) {
			// Call your API to delete the transaction
			// Example: await deleteTransaction(transactionId);
			// Then re-fetch data:
			// fetchTransactionsData();
			alert('Delete functionality is not yet implemented.'); // Use a custom modal in a real app
		}
	}

	// Reactive statement for filtered and sorted transactions
	$: filteredTransactions = transactions.filter((transaction) => {
		const transactionDate = new Date(transaction.date);

		const matchesSearch = searchTerm
			? transaction.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
				transaction.category_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
				transaction.wallet_name?.toLowerCase().includes(searchTerm.toLowerCase())
			: true;

		const matchesCategory = selectedCategory
			? transaction.category_name === selectedCategory
			: true;
		const matchesWallet = selectedWallet ? transaction.wallet_name === selectedWallet : true;

		const matchesStartDate = startDate ? transactionDate >= new Date(startDate) : true;
		const matchesEndDate = endDate ? transactionDate <= new Date(endDate) : true;

		return matchesSearch && matchesCategory && matchesWallet && matchesStartDate && matchesEndDate;
	});

	$: sortedTransactions = [...filteredTransactions].sort((a, b) => {
		let aValue: any = a[sortColumn];
		let bValue: any = b[sortColumn];

		// Handle date sorting
		if (sortColumn === 'date') {
			aValue = new Date(aValue).getTime();
			bValue = new Date(bValue).getTime();
		}
		// Handle amount sorting
		if (sortColumn === 'amount') {
			aValue = parseFloat(aValue);
			bValue = parseFloat(bValue);
		}

		if (aValue < bValue) {
			return sortDirection === 'asc' ? -1 : 1;
		}
		if (aValue > bValue) {
			return sortDirection === 'asc' ? 1 : -1;
		}
		return 0;
	});

	function requestSort(column: keyof Transaction) {
		if (sortColumn === column) {
			sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
		} else {
			sortColumn = column;
			sortDirection = 'asc'; // Default to ascending when changing column
		}
	}

	function getSortArrow(column: keyof Transaction) {
		if (sortColumn === column) {
			return sortDirection === 'asc' ? '▲' : '▼';
		}
		return '';
	}

	function setDateRange(period: 'today' | 'week' | 'month' | 'year' | 'all') {
		const now = new Date();
		now.setHours(0, 0, 0, 0); // Reset to start of day for consistent calculations

		if (period === 'today') {
			startDate = now.toISOString().split('T')[0];
			endDate = now.toISOString().split('T')[0];
		} else if (period === 'week') {
			const firstDayOfWeek = new Date(now);
			firstDayOfWeek.setDate(now.getDate() - now.getDay()); // Sunday as first day of week
			startDate = firstDayOfWeek.toISOString().split('T')[0];
			const lastDayOfWeek = new Date(firstDayOfWeek);
			lastDayOfWeek.setDate(firstDayOfWeek.getDate() + 6);
			endDate = lastDayOfWeek.toISOString().split('T')[0];
		} else if (period === 'month') {
			const firstDayOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
			startDate = firstDayOfMonth.toISOString().split('T')[0];
			const lastDayOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0);
			endDate = lastDayOfMonth.toISOString().split('T')[0];
		} else if (period === 'year') {
			const firstDayOfYear = new Date(now.getFullYear(), 0, 1);
			startDate = firstDayOfYear.toISOString().split('T')[0];
			const lastDayOfYear = new Date(now.getFullYear(), 11, 31);
			endDate = lastDayOfYear.toISOString().split('T')[0];
		} else if (period === 'all') {
			startDate = null;
			endDate = null;
		}
	}
</script>

<svelte:head>
	<title>Spendr - Transactions</title>
</svelte:head>

<div class="transactions-wrapper">

    <div class="transactions-header">
        <h1>𝜗𝜚 Transactions Page ⋆. 𐙚 ˚</h1>
        <p>Log every spend—even the “treat yo’self” ones. No gatekeeping your own wallet.</p>
    </div>

	{#if isLoading}
		<LoadingSpinner message="Loading your wallet ♡ — don’t worry, we didn’t spend anything ₊˚⊹" />
	{:else if error}
		<ErrorMessage message={error} />
	{:else}
		<div class="controls-section">
			<button class="add-button" on:click={() => (showAddTransactionModal = true)}
				>+ Add New Transaction</button
			>

			<div class="filters">
				<input
					type="text"
					placeholder="Search transactions..."
					bind:value={searchTerm}
					class="search-input"
				/>
				<select bind:value={selectedCategory} class="filter-select">
					<option value={null}>All Categories</option>
					{#each categories as category (category.id)}
						<option value={category.name}>{category.name}</option>
					{/each}
				</select>
				<select bind:value={selectedWallet} class="filter-select">
					<option value={null}>All Wallets</option>
					{#each wallets as wallet (wallet.id)}
						<option value={wallet.name}>{wallet.name}</option>
					{/each}
				</select>
				<input type="date" bind:value={startDate} class="date-input" title="Start Date" />
				<input type="date" bind:value={endDate} class="date-input" title="End Date" />
				<div class="date-range-buttons">
					<button on:click={() => setDateRange('today')} class="date-range-button">Today</button>
					<button on:click={() => setDateRange('week')} class="date-range-button">This Week</button>
					<button on:click={() => setDateRange('month')} class="date-range-button"
						>This Month</button
					>
					<button on:click={() => setDateRange('year')} class="date-range-button">This Year</button>
					<button on:click={() => setDateRange('all')} class="date-range-button">All Time</button>
				</div>
			</div>
		</div>

		{#if sortedTransactions.length > 0}
			<div class="transactions-table-container">
				<table class="transactions-table">
					<thead>
						<tr>
							<th
								on:click={() => requestSort('date')}
								class:sortable={true}
								class:active-sort={sortColumn === 'date'}
								data-sort-arrow={getSortArrow('date')}
							>
								Date
							</th>
							<th
								on:click={() => requestSort('description')}
								class:sortable={true}
								class:active-sort={sortColumn === 'description'}
								data-sort-arrow={getSortArrow('description')}
							>
								Description
							</th>
							<th
								on:click={() => requestSort('amount')}
								class:sortable={true}
								class:active-sort={sortColumn === 'amount'}
								data-sort-arrow={getSortArrow('amount')}
							>
								Amount
							</th>
							<th
								on:click={() => requestSort('transaction_type')}
								class:sortable={true}
								class:active-sort={sortColumn === 'transaction_type'}
								data-sort-arrow={getSortArrow('transaction_type')}
							>
								Type
							</th>
							<th
								on:click={() => requestSort('category_name')}
								class:sortable={true}
								class:active-sort={sortColumn === 'category_name'}
								data-sort-arrow={getSortArrow('category_name')}
							>
								Category
							</th>
							<th
								on:click={() => requestSort('wallet_name')}
								class:sortable={true}
								class:active-sort={sortColumn === 'wallet_name'}
								data-sort-arrow={getSortArrow('wallet_name')}
							>
								Wallet
							</th>
							<th>Actions</th>
						</tr>
					</thead>
					<tbody>
						{#each sortedTransactions as transaction (transaction.id)}
							<tr>
								<td
									>{new Date(transaction.date).toLocaleDateString('en-US', {
										year: 'numeric',
										month: 'short',
										day: 'numeric'
									})}</td
								>
								<td>{transaction.description || 'N/A'}</td>
								<td
									class:income={transaction.transaction_type === 'income'}
									class:expense={transaction.transaction_type === 'expense'}
								>
									₱{transaction.amount.toFixed(2)}
								</td>
								<td>{transaction.transaction_type}</td>
								<td>{transaction.category_name || 'N/A'}</td>
								<td>{transaction.wallet_name || 'N/A'}</td>
								<td class="actions-cell">
									<button
										class="action-button edit-button"
										on:click={() => handleEditTransaction(transaction)}>Edit</button
									>
									<button
										class="action-button delete-button"
										on:click={() => handleDeleteTransaction(transaction.id)}>Delete</button
									>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{:else}
			<p class="no-data-message">No transactions found matching your criteria. Time to add some!</p>
		{/if}
	{/if}
</div>

{#if showAddTransactionModal}
	<AddTransactionModal
		{wallets}
		{categories}
		on:close={handleModalClose}
		on:transactionAdded={handleTransactionAdded}
	/>
{/if}

<style>

	.transactions-wrapper {
		padding: 20px;
		max-width: 1400px;
		margin: 0 auto;
		font-family: 'Inter', sans-serif;
		color: var(--text-dark);
	}

    .transactions-header {
        text-align: center;
        margin-bottom: 30px;
        padding: 25px;
        background: linear-gradient(135deg, var(--light-pink), var(--primary-pink));
        color: var(--text-white);
        border-radius: 15px;
        box-shadow: 0 6px 15px var(--shadow-medium);
    }
    .transactions-header h1 {
        color: var(--text-white);
        font-size: 2.8em;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .transactions-header p {
        color: var(--text-white);
        font-size: 1.2em;
        opacity: 0.9;
    }
    
    .controls-section {
		display: flex;
		flex-wrap: wrap; /* Allow wrapping on smaller screens */
		justify-content: space-between;
		align-items: center;
		margin-bottom: 30px;
		gap: 15px; /* Space between elements */
	}

	.add-button {
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
		white-space: nowrap; /* Prevent button text from wrapping */
	}
	.add-button:hover {
		background-color: var(--dark-pink);
		transform: translateY(-3px);
		box-shadow: 0 6px 15px rgba(0, 0, 0, 0.25);
	}
	.add-button:active {
		transform: translateY(0);
		box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
	}

	.filters {
		display: flex;
		flex-wrap: wrap;
		gap: 10px; /* Space between filter elements */
		align-items: center;
	}

	.search-input,
	.filter-select,
	.date-input {
		padding: 10px 15px;
		border: 1px solid var(--border-light);
		border-radius: 8px;
		font-size: 1em;
		color: var(--text-dark);
		background-color: var(--text-white);
		box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
		transition:
			border-color 0.2s ease,
			box-shadow 0.2s ease;
	}
	.search-input:focus,
	.filter-select:focus,
	.date-input:focus {
		border-color: var(--primary-pink);
		box-shadow: 0 0 0 3px rgba(255, 105, 180, 0.2); /* Pink focus ring */
		outline: none;
	}

	.date-range-buttons {
		display: flex;
		flex-wrap: wrap;
		gap: 8px; /* Space between date range buttons */
	}

	.date-range-button {
		background-color: var(--light-pink); /* Light pink for date range buttons */
		color: var(--dark-pink);
		border: 1px solid var(--primary-pink);
		padding: 8px 15px;
		border-radius: 20px;
		cursor: pointer;
		font-size: 0.9em;
		font-weight: 600;
		transition:
			background-color 0.2s ease,
			color 0.2s ease,
			transform 0.1s ease;
		white-space: nowrap;
	}
	.date-range-button:hover {
		background-color: var(--primary-pink);
		color: var(--text-white);
		transform: translateY(-1px);
	}
	.date-range-button:active {
		transform: translateY(0);
	}

	/* Transactions Table */
	.transactions-table-container {
		overflow-x: auto; /* Enable horizontal scrolling on small screens */
		background-color: var(--text-white);
		border-radius: 15px;
		box-shadow: 0 6px 18px var(--shadow-light);
		padding: 20px;
		border: 1px solid var(--border-light);
	}

	.transactions-table {
		width: 100%;
		border-collapse: collapse;
		margin-top: 20px;
	}

	.transactions-table th,
	.transactions-table td {
		padding: 15px 10px;
		text-align: left;
		border-bottom: 1px solid var(--border-light);
		white-space: nowrap; /* Prevent text wrapping in table cells */
	}

	.transactions-table th {
		background-color: var(--light-pink); /* Light pink header */
		color: var(--dark-pink); /* Darker pink text for header */
		font-weight: 700;
		cursor: pointer;
		transition: background-color 0.2s ease;
	}
	.transactions-table th:hover {
		background-color: rgba(255, 192, 203, 0.7); /* Slightly darker on hover */
	}
	.transactions-table th.sortable {
		position: relative;
		padding-right: 25px; /* Space for arrow */
	}
	.transactions-table th.sortable::after {
		content: attr(data-sort-arrow); /* Use data attribute for arrow */
		position: absolute;
		right: 10px;
		top: 50%;
		transform: translateY(-50%);
		font-size: 0.8em;
		color: var(--dark-pink);
	}
	/* No need for active-sort::after as it's now handled by data-sort-arrow attribute */
	.transactions-table th.active-sort {
		color: var(--accent-pink); /* Highlight active sort column */
	}

	.transactions-table td {
		color: var(--text-dark);
	}

	.transactions-table tr:last-child td {
		border-bottom: none;
	}

	.transactions-table .income {
		color: #28a745; /* Green for income */
		font-weight: bold;
	}
	.transactions-table .expense {
		color: var(--accent-pink); /* Deep Pink for expense */
		font-weight: bold;
	}

	.actions-cell {
		display: flex;
		gap: 8px;
		justify-content: flex-start; /* Align buttons to the left */
		flex-wrap: wrap; /* Allow buttons to wrap if space is tight */
	}

	.action-button {
		padding: 8px 12px;
		border-radius: 20px;
		cursor: pointer;
		font-size: 0.85em;
		font-weight: 600;
		transition:
			background-color 0.2s ease,
			transform 0.1s ease;
		border: none;
		white-space: nowrap;
	}

	.edit-button {
		background-color: #007bff; /* Blue for edit */
		color: var(--text-white);
	}
	.edit-button:hover {
		background-color: #0056b3;
		transform: translateY(-1px);
	}

	.delete-button {
		background-color: var(--error-text); /* Red for delete */
		color: var(--text-white);
	}
	.delete-button:hover {
		background-color: #a71d2a;
		transform: translateY(-1px);
	}

	.no-data-message {
		text-align: center;
		padding: 50px;
		font-size: 1.2em;
		color: var(--text-medium);
		background-color: var(--text-white);
		border-radius: 15px;
		box-shadow: 0 4px 10px var(--shadow-light);
		margin-top: 30px;
	}

	/* Responsive adjustments */
	@media (max-width: 768px) {
		.controls-section {
			flex-direction: column;
			align-items: stretch;
		}
		.filters {
			flex-direction: column;
			align-items: stretch;
			width: 100%;
		}
		.search-input,
		.filter-select,
		.date-input {
			width: 100%;
		}
		.add-button {
			width: 100%;
		}
		.date-range-buttons {
			justify-content: center; /* Center buttons on small screens */
			width: 100%;
		}
		.transactions-table th,
		.transactions-table td {
			font-size: 0.9em; /* Smaller font for table on mobile */
			padding: 10px 5px;
		}
		.actions-cell {
			justify-content: center; /* Center action buttons on mobile */
		}
	}
</style>
