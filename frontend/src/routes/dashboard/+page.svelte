<script lang="ts">
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';
    import { getCurrentUser } from '$lib/api/auth';
    import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
    import ErrorMessage from '$lib/components/ErrorMessage.svelte';
    import { getCategories, getDashboardSummary, getMonthlySummary, type Wallet, type Category, type Transaction, type DashboardSummary, type MonthlyTrendData } from '$lib/api/budgets';

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

    async function fetchDashboardData() {
        error = null; // Clear previous errors
        try {
            userData = await getCurrentUser(); // Get authenticated user's basic info
            dashboardSummary = await getDashboardSummary();
            monthlyTrendData = await getMonthlySummary();

            // Update data for modals from the summary or dedicated calls
            wallets = dashboardSummary.wallets;
            // Fetch all categories separately for forms as dashboard summary only provides expense categories by spending
            categories = await getCategories();

        } catch (err: any) {
            console.error('Error loading dashboard data:', err);
            error = err.message || 'Failed to load dashboard data.';
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
        setTimeout(() => successMessage = null, 3000); // Clear success message after 3 seconds
    }

    // Reactive statement for confetti (if budget goal is met)
    // Use non-null assertion (!) because this block is inside {#if dashboardSummary}
    $: overallBudgetMet = dashboardSummary!?.overall_budget_goal > 0 && dashboardSummary!?.expense_this_month <= dashboardSummary!?.overall_budget_goal;
    $: showConfetti = overallBudgetMet;
</script>

<svelte:head>
    <title>Spendr - Dashboard</title>
</svelte:head>

<div class="dashboard-wrapper">
    <div class="dashboard-header">
        <h1>Welcome to Spendr! ˚ ༘ ೀ⋆｡˚ </h1>
        <p>Helping you slay bills, not just selfies 𖹭.ᐟ </p>
    </div>

    {#if isLoading}
        <LoadingSpinner message="Loading your wallet ♡ — don’t worry, we didn’t spend anything ₊˚⊹" />
    {:else if error}
        <ErrorMessage message={error} />
    {:else if dashboardSummary}
        {#if successMessage}
            <div class="success-message">{successMessage}</div>
        {/if}

        <div class="summary-cards">
            <div class="card total-balance">
                <h2>Total Wallet Balance</h2>
                <p>₱{dashboardSummary.total_balance.toFixed(2)}</p>
            </div>
            <div class="card income-month">
                <h2>Income ({dashboardSummary.current_month_str})</h2>
                <p>₱{dashboardSummary.income_this_month.toFixed(2)}</p>
            </div>
            <div class="card expense-month">
                <h2>Expenses ({dashboardSummary.current_month_str})</h2>
                <p>₱{dashboardSummary.expense_this_month.toFixed(2)}</p>
            </div>
            <div class="card net-month">
                <h2>Net Income/Expense</h2>
                <p class:positive={dashboardSummary.net_balance_this_month > 0}
                   class:negative={dashboardSummary.net_balance_this_month < 0}>
                    ₱{dashboardSummary.net_balance_this_month.toFixed(2)}
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
                        <p>No expense transactions recorded for this month to display in the pie chart.</p>
                    {/if}
                </section>

                <section class="section-charts">
                    <h2>Income/Expense Trend Over Time</h2>
                    {#if monthlyTrendData && monthlyTrendData.length > 0}
                        <IncomeExpenseTrendChart data={monthlyTrendData} />
                    {:else}
                        <p>Not enough historical transaction data to display the trend chart.</p>
                    {/if}
                </section>
            </div>

            <div class="grid-column right-column">
                <section class="section-budget-goals">
                    <h2>Budget Goal Progress ({dashboardSummary.current_month_str})</h2>
                    <button class="add-button" on:click={() => showAddBudgetGoalModal = true}>+ Set Goal</button>

                    {#if dashboardSummary.overall_budget_goal > 0}
                        <div class="goal-item overall-goal">
                            <h3>Overall Monthly Budget</h3>
                            <p>Goal: ₱{dashboardSummary.overall_budget_goal.toFixed(2)} / Spent: ₱{dashboardSummary.expense_this_month.toFixed(2)}</p>
                            <div class="progress-bar-container">
                                <div class="progress-bar" style="width: {Math.min(dashboardSummary.overall_budget_progress, 100)}%;"></div>
                            </div>
                            <span class="progress-text" class:overspent={dashboardSummary.overall_budget_progress > 100}>
                                {dashboardSummary.overall_budget_progress.toFixed(1)}% Used
                                {#if showConfetti} <span class="confetti">🎉 You're Adulting! 🎉</span>{/if}
                            </span>
                        </div>
                    {:else}
                        <p>No overall monthly budget goal set. Click "Set Goal" to define your spending limit!</p>
                    {/if}

                    {#if dashboardSummary.budget_goals_progress && dashboardSummary.budget_goals_progress.length > 0}
                        <h3>Category Specific Goals:</h3>
                        <ul class="goal-list">
                            {#each dashboardSummary.budget_goals_progress as goal (goal.goal_id)}
                                <li class="goal-item">
                                    <h4>{goal.category_name}</h4>
                                    <p>Goal: ₱{goal.goal_amount.toFixed(2)} / Spent: ₱{goal.spent_amount.toFixed(2)}</p>
                                    <div class="progress-bar-container">
                                        <div class="progress-bar" style="width: {Math.min(goal.progress_percentage, 100)}%;"></div>
                                    </div>
                                    <span class="progress-text" class:overspent={goal.is_overbudget}>
                                        {goal.progress_percentage.toFixed(1)}% Used
                                        {#if goal.is_overbudget} (Overspent!){/if}
                                    </span>
                                </li>
                            {/each}
                        </ul>
                    {/if}
                </section>

                <section class="section-upcoming-bills">
                    <h2>Upcoming Recurring Bills</h2>
                    <button class="add-button" on:click={() => showAddRecurringBillModal = true}>+ Add Bill</button>
                    {#if dashboardSummary.upcoming_bills && dashboardSummary.upcoming_bills.length > 0}
                        <ul class="bill-list">
                            {#each dashboardSummary.upcoming_bills as bill (bill.id)}
                                <li>
                                    <span>{bill.name}</span>
                                    <span>₱{bill.amount.toFixed(2)}</span>
                                    <span class="bill-date">Due: {new Date(bill.due_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                                </li>
                            {/each}
                        </ul>
                    {:else}
                        <p>No upcoming recurring bills in the next 30 days. Enjoy the calm!</p>
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
                        <p>Everything looks good! Keep up the great work. 👍</p>
                    {/if}
                </section>

                <section class="section-wallets">
                    <h2>Your Wallets</h2>
                    <button class="add-button" on:click={() => showAddWalletModal = true}>+ Add Wallet</button>
                    {#if wallets && wallets.length > 0}
                        <ul class="wallet-list">
                            {#each wallets as wallet (wallet.id)}
                                <li>{wallet.name}: ₱{wallet.balance.toFixed(2)} {wallet.currency}</li>
                            {/each}
                        </ul>
                    {:else}
                        <p>No wallets added yet. Click "Add Wallet" to get started!</p>
                    {/if}
                </section>

                <section class="section-transactions">
                    <h2>Recent Transactions</h2>
                    <button class="add-button" on:click={() => showAddTransactionModal = true}>+ Add Transaction</button>
                    <button class="add-button" on:click={() => showAddCategoryModal = true} style="margin-left: 10px;">+ Add Category</button>
                    {#if dashboardSummary.recent_transactions && dashboardSummary.recent_transactions.length > 0}
                        <ul class="transaction-list">
                            {#each dashboardSummary.recent_transactions as transaction (transaction.id)}
                                <li>
                                    <span>{new Date(transaction.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
                                    <span>{transaction.description || 'No description'}</span>
                                    <span class:income={transaction.transaction_type === 'income'} class:expense={transaction.transaction_type === 'expense'}>
                                        {transaction.transaction_type === 'income' ? '+' : '-'}{transaction.amount.toFixed(2)}
                                    </span>
                                    <span>({transaction.category_name || 'N/A'}) in {transaction.wallet_name}</span>
                                </li>
                            {/each}
                        </ul>
                    {:else}
                        <p>No recent transactions recorded. Click "Add Transaction" to start tracking!</p>
                    {/if}
                </section>
            </div>
        </div>
    {/if}
</div>

{#if showAddWalletModal}
    <AddWalletModal on:close={handleModalClose} on:walletAdded={handleDataChange} />
{/if}

{#if showAddTransactionModal}
    <AddTransactionModal
        wallets={wallets}
        categories={categories}
        on:close={handleModalClose}
        on:transactionAdded={handleDataChange}
    />
{/if}

{#if showAddCategoryModal}
    <AddCategoryModal on:close={handleModalClose} on:categoryAdded={handleDataChange} />
{/if}

{#if showAddBudgetGoalModal}
    <AddBudgetGoalModal
        categories={categories.filter(cat => cat.type === 'expense')}
        currentMonth={dashboardSummary?.current_month_num}
        currentYear={dashboardSummary?.current_year}
        on:close={handleModalClose}
        on:budgetGoalAdded={handleDataChange}
    />
{/if}

{#if showAddRecurringBillModal}
    <AddRecurringBillModal
        categories={categories.filter(cat => cat.type === 'expense')}
        on:close={handleModalClose}
        on:recurringBillAdded={handleDataChange}
    />
{/if}

<style>
    /* Define CSS Variables for the pink theme (assuming these are globally available, e.g., in app.css) */
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
    }

    /* General Layout */
    .dashboard-wrapper {
        padding: 20px;
        max-width: 1400px; /* Wider for charts */
        margin: 0 auto;
        font-family: 'Inter', sans-serif; /* Consistent font */
        color: var(--text-dark);
    }
    .dashboard-header {
        text-align: center;
        margin-bottom: 30px;
        padding: 25px; /* Slightly more padding */
        background: linear-gradient(135deg, var(--light-pink), var(--primary-pink)); /* Pink gradient header */
        color: var(--text-white); /* White text for header */
        border-radius: 15px; /* More rounded corners */
        box-shadow: 0 6px 15px var(--shadow-medium); /* Deeper shadow */
    }
    .dashboard-header h1 {
        color: var(--text-white); /* White text */
        font-size: 2.8em; /* Larger heading */
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2); /* Stronger text shadow */
    }
    .dashboard-header p {
        color: var(--text-white); /* White text */
        font-size: 1.2em;
        opacity: 0.9;
    }

    /* Summary Cards */
    .summary-cards {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 25px;
        margin-bottom: 40px;
    }
    .card {
        background: var(--text-white); /* White background for cards */
        padding: 25px;
        border-radius: 15px; /* More rounded corners */
        box-shadow: 0 8px 20px var(--shadow-light); /* Softer, larger shadow */
        text-align: center;
        transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
        border: 1px solid var(--border-light); /* Subtle border */
    }
    .card:hover {
        transform: translateY(-8px); /* More pronounced lift */
        box-shadow: 0 12px 25px var(--shadow-medium); /* Stronger shadow on hover */
    }
    .card h2 {
        font-size: 1.4em; /* Slightly larger */
        margin-bottom: 10px;
        color: var(--text-medium); /* Darker text for headings */
        letter-spacing: 0.8px; /* More prominent letter spacing */
    }
    .card p {
        font-size: 2.5em; /* Larger numbers */
        font-weight: bold;
        margin: 0;
    }
    .total-balance p { color: var(--primary-pink); } /* Pink for total balance */
    .income-month p { color: #28a745; } /* Green for income */
    .expense-month p { color: var(--accent-pink); } /* Deep Pink for expenses */
    .net-month p {
        color: var(--dark-pink); /* Default Net balance */
        font-size: 2.5em; /* Ensure same size */
    }
    .net-month p.positive {
        color: #28a745; /* Green for positive net */
    }
    .net-month p.negative {
        color: var(--accent-pink); /* Deep Pink for negative net */
    }

    /* Dashboard Grid Layout */
    .dashboard-grid {
        display: grid;
        grid-template-columns: 1fr; /* Stack columns on small screens */
        gap: 30px;
    }
    @media (min-width: 992px) { /* Two columns on larger screens */
        .dashboard-grid {
            grid-template-columns: 2fr 1fr; /* Left column wider for charts */
        }
    }

    .grid-column section {
        background-color: var(--text-white);
        padding: 30px;
        border-radius: 15px; /* More rounded corners */
        box-shadow: 0 6px 18px var(--shadow-light); /* Softer shadow */
        margin-bottom: 30px;
        transition: box-shadow 0.3s ease-in-out;
        border: 1px solid var(--border-light); /* Subtle border */
    }
    .grid-column section:hover {
        box-shadow: 0 10px 25px var(--shadow-medium); /* Stronger shadow on hover */
    }
    .grid-column section:last-child {
        margin-bottom: 0;
    }

    section h2 {
        margin-top: 0;
        color: var(--text-dark);
        border-bottom: 1px solid var(--border-light);
        padding-bottom: 15px;
        margin-bottom: 25px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 1.8em; /* Larger section titles */
        font-weight: 700;
    }
    .add-button {
        background-color: var(--accent-pink); /* Pink add button */
        color: var(--text-white);
        border: none;
        padding: 12px 22px; /* Larger padding */
        border-radius: 25px; /* Pill shape */
        cursor: pointer;
        font-size: 1em; /* Slightly larger font */
        font-weight: bold;
        transition: background-color 0.3s ease, transform 0.2s ease, box-shadow 0.3s ease;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15); /* Button shadow */
    }
    .add-button:hover {
        background-color: var(--dark-pink); /* Darker pink on hover */
        transform: translateY(-3px); /* More pronounced lift */
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.25); /* Stronger shadow on hover */
    }
    .add-button:active {
        transform: translateY(0);
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }

    /* Lists Styling */
    .wallet-list, .transaction-list, .bill-list, .alerts-list, .goal-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    .wallet-list li, .bill-list li, .alerts-list li, .goal-list li {
        padding: 15px 0; /* More padding */
        border-bottom: 1px dashed var(--border-light);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        font-size: 1.1em; /* Slightly larger text */
        color: var(--text-medium);
    }
    .transaction-list li {
        padding: 15px 0;
        border-bottom: 1px dashed var(--border-light);
        display: grid;
        grid-template-columns: 0.8fr 2fr 1fr 1.5fr;
        gap: 10px;
        align-items: center;
        font-size: 1.1em;
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
    .transaction-list .income { color: #28a745; font-weight: bold; }
    .transaction-list .expense { color: var(--accent-pink); font-weight: bold; } /* Deep Pink for expense */
    .alerts-list li {
        color: var(--warning-text);
        font-weight: bold;
        background-color: var(--warning-bg);
        border-radius: 8px; /* More rounded */
        padding: 12px 18px; /* More padding */
        margin-bottom: 15px;
        border: 1px solid #ffda8a; /* Slightly darker border for warning */
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    }

    /* Budget Goal Progress Bar */
    .goal-item {
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 1px dashed var(--border-light);
    }
    .goal-item:last-child {
        border-bottom: none;
        margin-bottom: 0;
        padding-bottom: 0;
    }
    .goal-item h3, .goal-item h4 {
        margin-top: 0;
        margin-bottom: 8px;
        color: var(--text-dark);
        font-size: 1.3em; /* Slightly larger */
    }
    .goal-item p {
        margin-bottom: 8px;
        font-size: 1em; /* Adjusted font size */
        color: var(--text-medium);
    }
    .progress-bar-container {
        width: 100%;
        background-color: var(--light-pink); /* Light pink background for progress bar */
        border-radius: 8px; /* More rounded */
        height: 15px; /* Taller progress bar */
        overflow: hidden;
        margin-top: 10px;
        box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.15); /* Stronger inner shadow */
    }
    .progress-bar {
        height: 100%;
        background-color: var(--primary-pink); /* Primary pink for progress */
        border-radius: 8px;
        transition: width 0.5s ease-in-out, background-color 0.3s ease-in-out;
    }
    .progress-text {
        font-size: 1em; /* Slightly larger */
        margin-top: 10px; /* More space */
        display: block;
        text-align: right;
        font-weight: bold;
        color: var(--dark-pink); /* Darker pink for progress text */
    }
    .progress-text.overspent {
        color: var(--error-text); /* Red if overspent */
    }
    .confetti {
        color: #FFD700; /* Gold color for confetti */
        font-size: 1.2em;
        margin-left: 8px;
        animation: pulse 1s infinite alternate; /* Simple pulse animation */
    }
    @keyframes pulse {
        from { transform: scale(1); }
        to { transform: scale(1.1); }
    }

    .goal-item .progress-bar {
        background-color: #28a745; /* Default: Green for within budget */
    }
    /* This rule will catch when overall_budget_progress (or category progress) is >= 100% */
    .progress-bar-container .progress-bar[style*="width: 100%"] {
        background-color: var(--accent-pink); /* Deep Pink if over or exactly 100% */
    }


    .success-message {
        background-color: var(--success-bg);
        color: var(--success-text);
        padding: 15px; /* More padding */
        border-radius: 10px; /* More rounded */
        margin-bottom: 30px; /* More margin */
        text-align: center;
        font-weight: bold;
        border: 1px solid #a3e6b3; /* Slightly darker border */
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    }

    .bill-list .bill-date {
        font-size: 0.95em; /* Slightly larger */
        color: var(--text-medium);
    }
</style>
