<script lang="ts">
	import { onMount } from 'svelte';
	// Corrected import: 'addWallet' changed to 'createWallet' to match budgets.ts
	import {
		getWallets,
		createWallet,
		updateWallet,
		deleteWallet,
		transferFunds,
		type Wallet,
		type Category
	} from '$lib/api/budgets';
	import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
	import ErrorMessage from '$lib/components/ErrorMessage.svelte';
	import AddWalletModal from '$lib/components/AddWalletModal.svelte'; // Re-using for "Add Account"
	import TransferFundsModal from '$lib/components/TransferFundsModal.svelte'; // New modal for transfers

	let accounts: Wallet[] = []; // Renamed from 'wallets' to 'accounts' for clarity on this page
	let isLoading = true;
	let error: string | null = null;
	let successMessage: string | null = null;

	let showAddAccountModal = false;
	let showEditAccountModal = false; // For editing existing accounts
	let showTransferFundsModal = false;

	let accountToEdit: Wallet | null = null; // To pass data to edit modal

	async function fetchAccountsData() {
		error = null; // Clear previous errors
		try {
			accounts = await getWallets(); // Fetch all wallets (accounts)
		} catch (err: any) {
			console.error('Error loading accounts data:', err);
			error = err.message || 'Failed to load accounts.';
		} finally {
			isLoading = false;
		}
	}

	onMount(async () => {
		isLoading = true;
		await fetchAccountsData();
	});

	function handleModalClose() {
		showAddAccountModal = false;
		showEditAccountModal = false;
		showTransferFundsModal = false;
		accountToEdit = null; // Clear account to edit
	}

	async function handleDataChange(event: CustomEvent<Wallet>) {
		const newWallet = event.detail; // Get the newly created wallet from the event
		accounts = [...accounts, newWallet]; // Add it to the existing accounts array
		successMessage = 'Account data updated successfully!';
		handleModalClose();
		setTimeout(() => (successMessage = null), 3000);
	}

	function handleEditAccount(account: Wallet) {
		console.log('Edit account:', account);
		accountToEdit = account;
		showEditAccountModal = true; // This would typically open an EditWalletModal or similar
		// TODO: Implement actual EditWalletModal or integrate edit into AddWalletModal
		alert(`Edit functionality for ${account.name} is not yet fully implemented.`); // Use a custom modal in a real app
	}

	async function handleDeleteAccount(accountId: number, accountName: string) {
		console.log('Delete account with ID:', accountId);
		if (
			confirm(
				`Are you sure you want to delete the account "${accountName}"? This cannot be undone.`
			)
		) {
			try {
				// Assuming deleteWallet API call exists
				await deleteWallet(accountId);
				successMessage = `Account "${accountName}" deleted successfully!`;
				await fetchAccountsData(); // Re-fetch data
				setTimeout(() => (successMessage = null), 3000);
			} catch (err: any) {
				console.error('Error deleting account:', err);
				error = err.message || 'Failed to delete account.';
			}
		}
	}

	function handleOpenTransferModal() {
		showTransferFundsModal = true;
	}
</script>

<svelte:head>
	<title>Spendr - Accounts</title>
</svelte:head>

<div class="accounts-wrapper">
	<div class="accounts-header">
		<h1>𝜗𝜚 Accounts Page ⋆. 𐙚 ˚</h1>
		<p>Add your banks, e-wallets, and side hustle stashes. Keep tabs so your money stops ghosting you.</p>
	</div>

	{#if isLoading}
		<LoadingSpinner message="Loading your wallet ♡ — don’t worry, we didn’t spend anything ₊˚⊹" />
	{:else if error}
		<ErrorMessage message={error} />
	{:else}
		{#if successMessage}
			<div class="success-message">{successMessage}</div>
		{/if}

		<div class="controls-section">
			<button class="add-button" on:click={() => (showAddAccountModal = true)}
				>+ Add New Account</button
			>
			<button class="add-button transfer-button" on:click={handleOpenTransferModal}
				>🔄 Transfer Funds</button
			>
		</div>

		<div class="accounts-list-container">
			{#if accounts.length > 0}
				<ul class="accounts-list">
					{#each accounts as account (account.id)}
						<li class="account-item">
							<div class="account-info">
								<span class="account-icon"
									>{account.type === 'Cash'
										? '💵'
										: account.type === 'Bank'
											? '🏦'
											: account.type === 'Credit Card'
												? '💳'
												: account.type === 'eWallet'
													? '📱'
													: '💰'}</span
								>
								<span class="account-name">{account.name}</span>
								<span class="account-type">{account.type}</span>
							</div>
							<div class="account-balance">
								<span>Balance:</span>
								<span class="balance-amount"
									>₱{account.balance != null ? account.balance.toFixed(2) : 'N/A'}
									{account.currency}</span
								>
							</div>
							<div class="account-actions">
								<button
									class="action-button edit-button"
									on:click={() => handleEditAccount(account)}>✏️ Edit</button
								>
								<button
									class="action-button delete-button"
									on:click={() => handleDeleteAccount(account.id, account.name)}>🗑️ Delete</button
								>
							</div>
						</li>
					{/each}
				</ul>
			{:else}
				<p class="no-data-message">
					No accounts added yet. Click "Add New Account" to get started!
				</p>
			{/if}
		</div>
	{/if}
</div>

{#if showAddAccountModal}
	<AddWalletModal on:close={handleModalClose} on:walletAdded={handleDataChange} />
{/if}

{#if showTransferFundsModal}
	<TransferFundsModal
		wallets={accounts}
		on:close={handleModalClose}
		on:transferCompleted={handleDataChange}
	/>
{/if}

<style>
	/* Define CSS Variables for the pink theme (assuming these are globally available, e.g., in app.css) */
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
	}

	/* General Layout */
	.accounts-wrapper {
		padding: 20px;
		max-width: 1000px; /* Slightly narrower for accounts list */
		margin: 0 auto;
		font-family: 'Inter', sans-serif;
		color: var(--text-dark);
	}

	.accounts-header {
		text-align: center;
		margin-bottom: 30px;
		padding: 25px;
		background: linear-gradient(135deg, var(--light-pink), var(--primary-pink));
		color: var(--text-white);
		border-radius: 15px;
		box-shadow: 0 6px 15px var(--shadow-medium);
	}
	.accounts-header h1 {
		color: var(--text-white);
		font-size: 2.8em;
		margin-bottom: 10px;
		text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
	}
	.accounts-header p {
		color: var(--text-white);
		font-size: 1.2em;
		opacity: 0.9;
	}

	.controls-section {
		display: flex;
		flex-wrap: wrap;
		justify-content: flex-end; /* Align buttons to the right */
		gap: 15px; /* Space between buttons */
		margin-bottom: 30px;
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
		white-space: nowrap;
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

	.transfer-button {
		background-color: #6f42c1; /* Purple for transfer */
	}
	.transfer-button:hover {
		background-color: #5a32a3;
	}

	.accounts-list-container {
		background-color: var(--text-white);
		padding: 30px;
		border-radius: 15px;
		box-shadow: 0 6px 18px var(--shadow-light);
		border: 1px solid var(--border-light);
	}

	.accounts-list {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.account-item {
		display: flex;
		flex-wrap: wrap; /* Allow wrapping */
		align-items: center;
		justify-content: space-between;
		padding: 18px 0; /* More vertical padding */
		border-bottom: 1px dashed var(--border-light);
		font-size: 1.1em;
		color: var(--text-dark);
		gap: 10px; /* Space between flex items */
	}
	.account-item:last-child {
		border-bottom: none;
	}

	.account-info {
		display: flex;
		align-items: center;
		flex-grow: 1; /* Allows info to take available space */
		gap: 10px;
	}

	.account-icon {
		font-size: 1.8em; /* Larger emoji/icon */
		flex-shrink: 0;
	}

	.account-name {
		font-weight: bold;
		font-size: 1.2em;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.account-type {
		font-size: 0.9em;
		padding: 4px 10px;
		border-radius: 15px;
		background-color: var(--light-pink);
		color: var(--dark-pink);
		font-weight: 600;
		white-space: nowrap;
	}

	.account-balance {
		display: flex;
		flex-direction: column; /* Stack balance info */
		align-items: flex-end; /* Align numbers to the right */
		font-size: 1.1em;
		color: var(--text-medium);
		flex-shrink: 0; /* Prevent shrinking */
		margin-left: 15px; /* Space from info */
	}
	.account-balance span:first-child {
		font-size: 0.85em;
		color: var(--text-medium);
	}
	.balance-amount {
		font-weight: bold;
		color: var(--primary-pink); /* Pink for balance amount */
		font-size: 1.3em;
	}

	.account-actions {
		display: flex;
		gap: 8px;
		margin-left: 20px; /* Space from balance */
		flex-shrink: 0;
		flex-wrap: wrap; /* Allow buttons to wrap */
		justify-content: flex-end; /* Align actions to the right */
	}

	.action-button {
		padding: 8px 15px;
		border-radius: 20px;
		cursor: pointer;
		font-size: 0.9em;
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
		padding: 40px;
		font-size: 1.2em;
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

	/* Responsive adjustments */
	@media (max-width: 768px) {
		.controls-section {
			justify-content: center; /* Center buttons on small screens */
		}
		.account-item {
			flex-direction: column;
			align-items: flex-start;
			gap: 10px;
			padding: 15px; /* More padding for mobile touch */
		}
		.account-info,
		.account-balance,
		.account-actions {
			width: 100%; /* Take full width */
			justify-content: flex-start; /* Align content to left */
			margin-left: 0; /* Remove extra margin */
		}
		.account-balance {
			align-items: flex-start; /* Align numbers to left */
		}
		.account-actions {
			justify-content: center; /* Center action buttons */
		}
	}
</style>
