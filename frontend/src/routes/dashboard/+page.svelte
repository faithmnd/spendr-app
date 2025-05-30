<script lang="ts">
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';
    import { getCurrentUser } from '$lib/api/auth';
    import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
    import ErrorMessage from '$lib/components/ErrorMessage.svelte';
    import {
        getCategories,
        getDashboardSummary,
        getMonthlySummary,
        type Wallet,
        type Category,
        type Transaction,
        type DashboardSummary,
        type MonthlyTrendData
    } from '$lib/api/budgets';

    // Modals (newly created or existing)
    import AddWalletModal from '$lib/components/AddWalletModal.svelte';
    import AddTransactionModal from '$lib/components/AddTransactionModal.svelte';
    import AddCategoryModal from '$lib/components/AddCategoryModal.svelte';
    import AddBudgetGoalModal from '$lib/components/AddBudgetGoalModal.svelte';
    import AddRecurringBillModal from '$lib/components/AddRecurringBillModal.svelte';

    // Chart Components
    import SpendingPieChart from '$lib/components/charts/SpendingPieChart.svelte';
    import IncomeExpenseTrendChart from '$lib/components/charts/IncomeExpenseTrendChart.svelte';

    let userData: any = null;
    let dashboardSummary: DashboardSummary | null = null;
    let monthlyTrendData: MonthlyTrendData[] = [];

    // Data props for modals (fetched from API)
    let wallets: Wallet[] = [];
    let categories: Category[] = []; // All categories, filtered later for specific modals

    let isLoading = true;
    let error: string | null = null;
    let successMessage: string | null = null;

    // Modal visibility states
    let showAddWalletModal = false;
    let showAddTransactionModal = false;
    let showAddCategoryModal = false;
    let showAddBudgetGoalModal = false;
    let showAddRecurringBillModal = false;

    async function fetchDashboardData(retryCount = 0) {
        error = null; // Clear previous errors
        try {
            userData = await getCurrentUser(); // Get authenticated user's basic info

            // If getCurrentUser succeeds but returns null, we're not authenticated
            if (!userData) {
                error = 'Authentication required. Please log in.';
                return;
            }

            // Fetch dashboard data with retry logic
            try {
                dashboardSummary = await getDashboardSummary();
                monthlyTrendData = await getMonthlySummary();

                // Update data for modals from the summary or dedicated calls
                wallets = dashboardSummary.wallets;
                // Fetch all categories separately for forms as dashboard summary only provides expense categories by spending
                categories = await getCategories();
            } catch (apiError) {
                console.error('Error fetching dashboard data:', apiError);

                // If we haven't retried too many times and it's a potentially recoverable error
                if (
                    retryCount < 2 &&
                    apiError instanceof Error &&
                    !apiError.message.includes('Authentication required')
                ) {
                    console.log(`Retrying dashboard data fetch (attempt ${retryCount + 1})...`);
                    await new Promise((resolve) => setTimeout(resolve, 1000)); // Wait 1 second before retry
                    return fetchDashboardData(retryCount + 1);
                }

                throw apiError; // Re-throw if we've retried too many times or it's an auth error
            }
        } catch (err: any) {
            console.error('Error in fetchDashboardData:', err);
            error = err.message || 'Failed to load dashboard data.';

            // If it's an authentication error, redirect to login
            if (err.message.includes('Authentication required')) {
                try {
                    await goto('/login', { replaceState: true });
                } catch (navError) {
                    console.error('Navigation error:', navError);
                    window.location.href = '/login';
                }
            }
        }
    }

    onMount(async () => {
        isLoading = true;
        await fetchDashboardData();
        isLoading = false;
    });

    // Event handlers for closing modals and refreshing data
    function handleModalClose() {
        showAddWalletModal = false;
        showAddTransactionModal = false;
        showAddCategoryModal = false;
        showAddBudgetGoalModal = false;
        showAddRecurringBillModal = false;
    }

    async function handleDataChange() {
        successMessage = 'Data updated successfully!';
        handleModalClose(); // Close the modal after successful operation
        await fetchDashboardData(); // Re-fetch all data to ensure dashboard is up-to-date
        setTimeout(() => (successMessage = null), 3000); // Clear success message after 3 seconds
    }

    // Reactive statement for confetti (if budget goal is met)
    // Use optional chaining for dashboardSummary properties to prevent errors if null
    $: overallBudgetMet =
        (dashboardSummary?.overall_budget_goal ?? 0) > 0 &&
        (dashboardSummary?.expense_this_month ?? 0) <= (dashboardSummary?.overall_budget_goal ?? 0);
    $: showConfetti = overallBudgetMet;
</script>

<svelte:head>
    <title>Spendr - Dashboard</title>
</svelte:head>

<div class="dashboard-wrapper">
    <div class="dashboard-header">
        <h1>Welcome to Spendr! ˚ ༘ ೀ⋆｡˚</h1>
        <p>Helping you slay bills, not just selfies 𖹭.ᐟ</p>
    </div>

    {#if isLoading}
        <LoadingSpinner message="Loading your wallet ♡ — don't worry, we didn't spend anything ₊˚⊹" />
    {:else if error}
        <ErrorMessage message={error} />
    {:else if dashboardSummary}
        {#if successMessage}
            <div class="success-message">{successMessage}</div>
        {/if}

        <div class="summary-cards">
            <div class="card total-balance">
                <h2>Total Wallet Balance</h2>
                <p>₱{isNaN(Number(dashboardSummary.total_balance)) ? '0.00' : Number(dashboardSummary.total_balance).toFixed(2)}</p>
            </div>
            <div class="card income-month">
                <h2>Income ({dashboardSummary.current_month_str})</h2>
                <p>₱{isNaN(Number(dashboardSummary.income_this_month)) ? '0.00' : Number(dashboardSummary.income_this_month).toFixed(2)}</p>
            </div>
            <div class="card expense-month">
                <h2>Expenses ({dashboardSummary.current_month_str})</h2>
                <p>₱{isNaN(Number(dashboardSummary.expense_this_month)) ? '0.00' : Number(dashboardSummary.expense_this_month).toFixed(2)}</p>
            </div>
            <div class="card net-month">
                <h2>Net Income/Expense</h2>
                <p
                    class:positive={(dashboardSummary.net_balance_this_month ?? 0) > 0}
                    class:negative={(dashboardSummary.net_balance_this_month ?? 0) < 0}
                >
                    ₱{isNaN(Number(dashboardSummary.net_balance_this_month)) ? '0.00' : Number(dashboardSummary.net_balance_this_month).toFixed(2)}
                </p>
            </div>
        </div>

        <div class="dashboard-grid">
            <div class="grid-column left-column">
                <section class="section-charts">
                    <h2>Spending by Category ({dashboardSummary.current_month_str})</h2>
                    {#if dashboardSummary.spending_by_category && dashboardSummary.spending_by_category.length > 0}
                        <SpendingPieChart data={dashboardSummary.spending_by_category} />
                    {:else}
                        <p class="no-data-text">No expense transactions recorded for this month to display in the pie chart.</p>
                    {/if}
                </section>

                <section class="section-charts">
                    <h2>Income/Expense Trend Over Time</h2>
                    {#if monthlyTrendData && monthlyTrendData.length > 0}
                        <IncomeExpenseTrendChart data={monthlyTrendData} />
                    {:else}
                        <p class="no-data-text">Not enough historical transaction data to display the trend chart.</p>
                    {/if}
                </section>
            </div>

            <div class="grid-column right-column">
                <section class="section-budget-goals">
                    <h2>Budget Goal Progress ({dashboardSummary.current_month_str})</h2>
                    <button class="add-button" on:click={() => (showAddBudgetGoalModal = true)}
                        >+ Set Goal</button
                    >

                    {#if (dashboardSummary.overall_budget_goal ?? 0) > 0}
                        <div class="goal-item overall-goal">
                            <h3>Overall Monthly Budget</h3>
                            <p>
                                Goal: ₱{isNaN(Number(dashboardSummary.overall_budget_goal)) ? '0.00' : Number(dashboardSummary.overall_budget_goal).toFixed(2)} / Spent: ₱{isNaN(Number(dashboardSummary.expense_this_month)) ? '0.00' : Number(dashboardSummary.expense_this_month).toFixed(2)}
                            </p>
                            <div class="progress-bar-container">
                                <div
                                    class="progress-bar"
                                    style="width: {Math.min(dashboardSummary.overall_budget_progress ?? 0, 100)}%;"
                                ></div>
                            </div>
                            <span
                                class="progress-text"
                                class:overspent={(dashboardSummary.overall_budget_progress ?? 0) > 100}
                            >
                                {isNaN(Number(dashboardSummary.overall_budget_progress)) ? '0.0' : Number(dashboardSummary.overall_budget_progress).toFixed(1)}% Used
                                {#if showConfetti}
                                    <span class="confetti">🎉 You're Adulting! 🎉</span>{/if}
                            </span>
                        </div>
                    {:else}
                        <p class="no-data-text">
                            No overall monthly budget goal set. Click "Set Goal" to define your spending limit!
                        </p>
                    {/if}

                    {#if dashboardSummary.budget_goals_progress && dashboardSummary.budget_goals_progress.length > 0}
                        <h3>Category Specific Goals:</h3>
                        <ul class="goal-list">
                            {#each dashboardSummary.budget_goals_progress as goal (goal.goal_id)}
                                <li class="goal-item">
                                    <h4>{goal.category_name}</h4>
                                    <p>
                                        Goal: ₱{isNaN(Number(goal.goal_amount)) ? '0.00' : Number(goal.goal_amount).toFixed(2)} / Spent: ₱{isNaN(Number(goal.spent_amount)) ? '0.00' : Number(goal.spent_amount).toFixed(2)}
                                    </p>
                                    <div class="progress-bar-container">
                                        <div
                                            class="progress-bar"
                                            style="width: {Math.min(goal.progress_percentage ?? 0, 100)}%;"
                                        ></div>
                                    </div>
                                    <span class="progress-text" class:overspent={goal.is_overbudget}>
                                        {isNaN(Number(goal.progress_percentage)) ? '0.0' : Number(goal.progress_percentage).toFixed(1)}% Used
                                        {#if goal.is_overbudget}
                                            (Overspent!){/if}
                                    </span>
                                </li>
                            {/each}
                        </ul>
                    {/if}
                </section>

                <section class="section-upcoming-bills">
                    <h2>Upcoming Recurring Bills</h2>
                    <button class="add-button" on:click={() => (showAddRecurringBillModal = true)}
                        >+ Add Bill</button
                    >
                    {#if dashboardSummary.upcoming_bills && dashboardSummary.upcoming_bills.length > 0}
                        <ul class="bill-list">
                            {#each dashboardSummary.upcoming_bills as bill (bill.id)}
                                <li>
                                    <span>{bill.name}</span>
                                    <span>₱{isNaN(Number(bill.amount)) ? '0.00' : Number(bill.amount).toFixed(2)}</span>
                                    <span class="bill-date"
                                        >Due: {new Date(bill.due_date).toLocaleDateString('en-US', {
                                            month: 'short',
                                            day: 'numeric',
                                            year: 'numeric'
                                        })}</span
                                    >
                                </li>
                            {/each}
                        </ul>
                    {:else}
                        <p class="no-data-text">No upcoming recurring bills in the next 30 days. Enjoy the calm!</p>
                    {/if}
                </section>

                <section class="section-quick-tips">
                    <h2>Quick Tips & Alerts</h2>
                    {#if dashboardSummary.alerts && dashboardSummary.alerts.length > 0}
                        <ul class="alerts-list">
                            {#each dashboardSummary.alerts as alert}
                                <li>⚠️ {alert}</li>
                            {/each}
                        </ul>
                    {:else}
                        <p class="no-data-text">Everything looks good! Keep up the great work. 👍</p>
                    {/if}
                </section>

                <section class="section-wallets">
                    <h2>Your Wallets</h2>
                    <button class="add-button" on:click={() => (showAddWalletModal = true)}
                        >+ Add Wallet</button
                    >
                    {#if wallets && wallets.length > 0}
                        <ul class="wallet-list">
                            {#each wallets as wallet (wallet.id)}
                                <li>
                                    {wallet.name}: ₱{
                                        isNaN(Number(wallet.balance)) ? '0.00' : Number(wallet.balance).toFixed(2)
                                    }
                                    {wallet.currency}
                                </li>
                            {/each}
                        </ul>
                    {:else}
                        <p class="no-data-text">No wallets added yet. Click "Add Wallet" to get started!</p>
                    {/if}
                </section>

                <section class="section-transactions">
                    <h2>Recent Transactions</h2>
                    <button class="add-button" on:click={() => (showAddTransactionModal = true)}
                        >+ Add Transaction</button
                    >
                    <b> </b>
                    <button
                        class="add-button"
                        on:click={() => (showAddCategoryModal = true)}
                        style="padding-left: 28px; padding-right: 28px;">+ Add Category</button
                    >
                    {#if dashboardSummary.recent_transactions && dashboardSummary.recent_transactions.length > 0}
                        <ul class="transaction-list">
                            {#each dashboardSummary.recent_transactions as transaction (transaction.id)}
                                <li>
                                    <span
                                        >{new Date(transaction.date).toLocaleDateString('en-US', {
                                            month: 'short',
                                            day: 'numeric'
                                        })}</span
                                    >
                                    <span>{transaction.description || 'No description'}</span>
                                    <span
                                        class:income={transaction.transaction_type === 'income'}
                                        class:expense={transaction.transaction_type === 'expense'}
                                    >
                                        {transaction.transaction_type === 'income'
                                            ? '+'
                                            : '-'}{isNaN(Number(transaction.amount)) ? '0.00' : Number(transaction.amount).toFixed(2)}
                                    </span>
                                    <span>({transaction.category_name || 'N/A'}) in {transaction.wallet_name}</span>
                                </li>
                            {/each}
                        </ul>
                    {:else}
                        <p class="no-data-text">No recent transactions recorded. Click "Add Transaction" to start tracking!</p>
                    {/if}
                </section>
            </div>
        </div>
    {:else}
        <p class="no-data-message">
            No dashboard data available. Please ensure your backend is running and data is present.
        </p>
    {/if}
</div>

{#if showAddWalletModal}
    <AddWalletModal on:close={handleModalClose} on:walletAdded={handleDataChange} />
{/if}

{#if showAddTransactionModal}
    <AddTransactionModal
        {wallets}
        {categories}
        on:close={handleModalClose}
        on:transactionAdded={handleDataChange}
    />
{/if}

{#if showAddCategoryModal}
    <AddCategoryModal on:close={handleModalClose} on:categoryAdded={handleDataChange} />
{/if}

{#if showAddBudgetGoalModal}
    <AddBudgetGoalModal
        categories={categories.filter((cat) => cat.type === 'expense')}
        currentMonth={dashboardSummary?.current_month_num}
        currentYear={dashboardSummary?.current_year}
        on:close={handleModalClose}
        on:budgetGoalAdded={handleDataChange}
    />
{/if}

{#if showAddRecurringBillModal}
    <AddRecurringBillModal
        categories={categories.filter((cat) => cat.type === 'expense')}
        on:close={handleModalClose}
        on:recurringBillAdded={handleDataChange}
    />
{/if}

<style>
    /* General Layout */
    :root {
        /* Define your color palette here */
        --primary-pink: #ff69b4; /* Brighter Pink */
        --light-pink: #ffccf0; /* Lighter Pink */
        --accent-pink: #ff1493; /* Deeper Hot Pink */
        --dark-pink: #c71585; /* Darker Pink */
        --text-white: #ffffff;
        --text-dark: #333333;
        --text-medium: #555555;
        --border-light: #f0f0f0;
        --shadow-light: rgba(0, 0, 0, 0.08); /* Lighter shadow */
        --shadow-medium: rgba(0, 0, 0, 0.15); /* Medium shadow */
        --warning-bg: #fff3cd;
        --warning-text: #856404;
        --success-bg: #d4edda;
        --success-text: #155724;
        --error-text: #dc3545; /* Red for errors/overspent */
    }

    .dashboard-wrapper {
        padding: 15px; /* Slightly less padding */
        max-width: 1300px; /* Slightly narrower max-width */
        margin: 0 auto;
        font-family: 'Inter', sans-serif;
        color: var(--text-dark);
    }
    .dashboard-header {
        text-align: center;
        margin-bottom: 25px; /* Slightly less margin */
        padding: 20px; /* Slightly less padding */
        background: linear-gradient(
            135deg,
            var(--light-pink),
            var(--primary-pink)
        );
        color: var(--text-white);
        border-radius: 12px; /* Slightly less rounded */
        box-shadow: 0 5px 12px var(--shadow-medium); /* Slightly softer shadow */
    }
    .dashboard-header h1 {
        color: var(--text-white);
        font-size: 2.5em; /* Slightly smaller heading */
        margin-bottom: 8px;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.15); /* Softer text shadow */
    }
    .dashboard-header p {
        color: var(--text-white);
        font-size: 1.1em; /* Slightly smaller */
        opacity: 0.9;
    }

    /* Summary Cards */
    .summary-cards {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); /* Min width adjusted */
        gap: 20px; /* Slightly less gap */
        margin-bottom: 30px; /* Slightly less margin */
    }
    .card {
        background: var(--text-white);
        padding: 20px; /* Slightly less padding */
        border-radius: 12px; /* Slightly less rounded */
        box-shadow: 0 6px 15px var(--shadow-light); /* Softer shadow */
        text-align: center;
        transition:
            transform 0.2s ease-in-out,
            box-shadow 0.2s ease-in-out;
        border: 1px solid var(--border-light);
    }
    .card:hover {
        transform: translateY(-5px); /* Less pronounced lift */
        box-shadow: 0 8px 18px var(--shadow-medium); /* Softer shadow on hover */
    }
    .card h2 {
        font-size: 1.2em; /* Smaller */
        margin-bottom: 8px;
        color: var(--text-medium);
        letter-spacing: 0.5px; /* Less prominent letter spacing */
    }
    .card p {
        font-size: 2.2em; /* Smaller numbers */
        font-weight: bold;
        margin: 0;
    }
    .total-balance p {
        color: var(--primary-pink);
    }
    .income-month p {
        color: #28a745;
    }
    .expense-month p {
        color: var(--accent-pink);
    }
    .net-month p {
        color: var(--dark-pink);
        font-size: 2.2em; /* Ensure consistent size */
    }
    .net-month p.positive {
        color: #28a745;
    }
    .net-month p.negative {
        color: var(--accent-pink);
    }

    /* Dashboard Grid Layout */
    .dashboard-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 25px; /* Slightly less gap */
    }
    @media (min-width: 992px) {
        .dashboard-grid {
            grid-template-columns: 2fr 1fr;
        }
    }

    .grid-column section {
        background-color: var(--text-white);
        padding: 25px; /* Slightly less padding */
        border-radius: 12px; /* Slightly less rounded */
        box-shadow: 0 5px 15px var(--shadow-light); /* Softer shadow */
        margin-bottom: 25px;
        transition: box-shadow 0.2s ease-in-out;
        border: 1px solid var(--border-light);
    }
    .grid-column section:hover {
        box-shadow: 0 8px 20px var(--shadow-medium); /* Softer shadow on hover */
    }
    .grid-column section:last-child {
        margin-bottom: 0;
    }

    section h2 {
        margin-top: 0;
        color: var(--text-dark);
        border-bottom: 1px solid var(--border-light);
        padding-bottom: 12px; /* Slightly less padding */
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 1.6em; /* Slightly smaller section titles */
        font-weight: 700;
    }
    .add-button {
        background-color: var(--accent-pink);
        color: var(--text-white);
        border: none;
        padding: 10px 18px; /* Slightly less padding */
        border-radius: 20px; /* Slightly less rounded */
        cursor: pointer;
        font-size: 0.95em; /* Slightly smaller font */
        font-weight: bold;
        transition:
            background-color 0.2s ease,
            transform 0.1s ease,
            box-shadow 0.2s ease;
        box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1); /* Softer button shadow */
    }
    .add-button:hover {
        background-color: var(--dark-pink);
        transform: translateY(-2px); /* Less pronounced lift */
        box-shadow: 0 5px 12px rgba(0, 0, 0, 0.2); /* Softer shadow on hover */
    }
    .add-button:active {
        transform: translateY(0);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
    }

    /* Lists Styling */
    .wallet-list,
    .transaction-list,
    .bill-list,
    .alerts-list,
    .goal-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    .wallet-list li,
    .bill-list li,
    .alerts-list li,
    .goal-list li {
        padding: 12px 0; /* Slightly less padding */
        border-bottom: 1px dashed var(--border-light);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        font-size: 1em; /* Slightly smaller text */
        color: var(--text-medium);
    }
    .transaction-list li {
        padding: 12px 0;
        border-bottom: 1px dashed var(--border-light);
        display: grid;
        grid-template-columns: 0.8fr 2fr 1fr 1.5fr;
        gap: 8px; /* Slightly less gap */
        align-items: center;
        font-size: 1em;
        color: var(--text-medium);
    }
    @media (max-width: 768px) {
        .transaction-list li {
            grid-template-columns: 1fr;
            gap: 5px;
        }
    }

    .wallet-list li:last-child,
    .transaction-list li:last-child,
    .bill-list li:last-child,
    .alerts-list li:last-child,
    .goal-list li:last-child {
        border-bottom: none;
    }
    .transaction-list .income {
        color: #28a745;
        font-weight: bold;
    }
    .transaction-list .expense {
        color: var(--accent-pink);
        font-weight: bold;
    }
    .alerts-list li {
        color: var(--warning-text);
        font-weight: bold;
        background-color: var(--warning-bg);
        border-radius: 6px; /* Slightly less rounded */
        padding: 10px 15px; /* Slightly less padding */
        margin-bottom: 12px;
        border: 1px solid #ffda8a;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    .no-data-text {
        font-style: italic;
        color: var(--text-medium);
        text-align: center; /* Center these messages */
        margin-top: 20px;
    }


    /* Budget Goal Progress Bar */
    .goal-item {
        margin-bottom: 18px; /* Slightly less margin */
        padding-bottom: 12px;
        border-bottom: 1px dashed var(--border-light);
    }
    .goal-item:last-child {
        border-bottom: none;
        margin-bottom: 0;
        padding-bottom: 0;
    }
    .goal-item h3,
    .goal-item h4 {
        margin-top: 0;
        margin-bottom: 6px;
        color: var(--text-dark);
        font-size: 1.2em; /* Slightly smaller */
    }
    .goal-item p {
        margin-bottom: 6px;
        font-size: 0.95em; /* Adjusted font size */
        color: var(--text-medium);
    }
    .progress-bar-container {
        width: 100%;
        background-color: var(--light-pink);
        border-radius: 6px; /* Slightly less rounded */
        height: 12px; /* Slightly thinner progress bar */
        overflow: hidden;
        margin-top: 8px;
        box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.1); /* Softer inner shadow */
    }
    .progress-bar {
        height: 100%;
        background-color: var(--primary-pink);
        border-radius: 6px;
        transition:
            width 0.5s ease-in-out,
            background-color 0.3s ease-in-out;
    }
    .progress-text {
        font-size: 0.95em; /* Slightly smaller */
        margin-top: 8px; /* Slightly less space */
        display: block;
        text-align: right;
        font-weight: bold;
        color: var(--dark-pink);
    }
    .progress-text.overspent {
        color: var(--error-text);
    }
    .confetti {
        color: #ffd700;
        font-size: 1.1em; /* Slightly smaller */
        margin-left: 6px;
        animation: pulse 1s infinite alternate;
    }
    @keyframes pulse {
        from {
            transform: scale(1);
        }
        to {
            transform: scale(1.05); /* Less intense pulse */
        }
    }

    .goal-item .progress-bar {
        background-color: #28a745;
    }
    .progress-bar-container .progress-bar[style*='width: 100%'] {
        background-color: var(--accent-pink);
    }

    .success-message {
        background-color: var(--success-bg);
        color: var(--success-text);
        padding: 12px; /* Slightly less padding */
        border-radius: 8px; /* Slightly less rounded */
        margin-bottom: 25px; /* Slightly less margin */
        text-align: center;
        font-weight: bold;
        border: 1px solid #a3e6b3;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }

    .bill-list .bill-date {
        font-size: 0.9em; /* Slightly smaller */
        color: var(--text-medium);
    }
</style>