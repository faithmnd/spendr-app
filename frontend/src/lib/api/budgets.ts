import { goto } from '$app/navigation';
import { authStore } from '$lib/stores/auth';

// Default to localhost if environment variable is not set
const API_BASE_URL = 'http://127.0.0.1:8000';

// Helper function for API requests
async function fetchData(url: string, options: RequestInit = {}) {
    const accessToken = localStorage.getItem('accessToken');

    const headers = {
        'Content-Type': 'application/json',
        ...(accessToken && { 'Authorization': `Bearer ${accessToken}` }),
        ...options.headers
    };

    const config: RequestInit = {
        ...options,
        headers
    };

    try {
        const response = await fetch(`${API_BASE_URL}/api/budget/${url}`, config);

        if (response.status === 401) {
            authStore.logout();
            await goto('/login', { replaceState: true });
            throw new Error('Authentication required');
        }

        if (!response.ok) {
            let errorMessage = 'API Error';
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorData.message || JSON.stringify(errorData);
            } catch {
                errorMessage = response.statusText || `HTTP ${response.status}`;
            }
            throw new Error(`API Error: ${response.status} - ${errorMessage}`);
        }

        if (response.status === 204) {
            return null;
        }

        return await response.json();
    } catch (error) {
        console.error(`API Error for ${url}:`, error);
        if (error instanceof Error && (error.message.includes('Authentication required') || error.message.includes('navigation'))) {
            throw error;
        }
        throw new Error(`Failed to fetch data: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
}

export interface Wallet {
    id: number;
    name: string;
    balance: number;
    currency: string;
    description: string | null;
    user: number;
    created_at: string;
    updated_at: string;
    type: 'Cash' | 'Bank' | 'eWallet' | 'Credit Card' | 'Other';
    icon?: string;
}

export interface Category {
    id: number;
    name: string;
    type: 'income' | 'expense';
    description?: string;
    user: number;
    created_at: string;
    updated_at: string;
    icon?: string;
    is_default?: boolean;
    // This should be a derived value from transactions, not set directly
    actual_expense?: number;
    // This is the correct field for the budget goal for the category
    monthly_budget?: number;
}

export interface Transaction {
    id: number;
    amount: number;
    transaction_type: 'income' | 'expense';
    date: string;
    category: number; // category ID
    description?: string;
    wallet: number; // wallet ID
    user: number;
    created_at: string;
    updated_at: string;
}

export interface BudgetGoal {
    id: number;
    month: number;
    year: number;
    category: number | null;
    amount: number;
    description?: string;
    user: number;
    created_at: string;
    updated_at: string;
}

export interface RecurringBill {
    id: number;
    name: string;
    amount: number;
    due_day: number;
    category: number | null;
    category_name: string | null;
    is_active: boolean;
    notes: string | null;
    user: number;
    created_at: string;
    updated_at: string;
}

export interface SpendingByCategory {
    category_id: number;
    category_name: string;
    total_amount: number;
}

export interface MonthlyTrendData {
    month: string;
    income: number;
    expense: number;
}

export interface DashboardSummary {
    total_balance: number;
    income_this_month: number;
    expense_this_month: number;
    net_balance_this_month: number;
    spending_by_category: SpendingByCategory[];
    wallets: Wallet[];
    recent_transactions: Transaction[];
    current_month_str: string;
    current_month_num: number;
    current_year: number;
    overall_budget_goal: number;
    overall_budget_progress: number;
    budget_goals_progress: {
        goal_id: number;
        category_name: string;
        goal_amount: number;
        spent_amount: number;
        progress_percentage: number;
        is_overbudget: boolean;
    }[];
    upcoming_bills: {
        id: number;
        name: string;
        amount: number;
        due_date: string;
        category_name: string | null;
    }[];
    alerts: string[];
}


export async function getWallets(): Promise<Wallet[]> {
    return fetchData('wallets/');
}

export async function createWallet(walletData: Partial<Wallet>): Promise<Wallet> {
    return fetchData('wallets/', {
        method: 'POST',
        body: JSON.stringify(walletData)
    });
}

export async function updateWallet(id: number, walletData: Partial<Wallet>): Promise<Wallet> {
    return fetchData(`wallets/${id}/`, {
        method: 'PUT',
        body: JSON.stringify(walletData)
    });
}

export async function deleteWallet(id: number): Promise<void> {
    return fetchData(`wallets/${id}/`, {
        method: 'DELETE'
    });
}

export async function getCategories(): Promise<Category[]> {
    return fetchData('categories/');
}

export async function createCategory(categoryData: Partial<Category>): Promise<Category> {
    return fetchData('categories/', {
        method: 'POST',
        body: JSON.stringify(categoryData)
    });
}

export async function updateCategory(categoryId: number, data: {
    name?: string;
    type?: 'income' | 'expense';
    description?: string | null;
    icon?: string;
    is_default?: boolean;
    // CHANGED: Use monthly_budget for the budget goal
    monthly_budget?: number;
}): Promise<Category> {
    return fetchData(`categories/${categoryId}/`, {
        method: 'PATCH',
        body: JSON.stringify(data)
    });
}

export async function deleteCategory(id: number): Promise<void> {
    return fetchData(`categories/${id}/`, {
        method: 'DELETE'
    });
}

export async function getTransactions(filters: { wallet_id?: number, category_id?: number, type?: 'income' | 'expense', start_date?: string, end_date?: string } = {}): Promise<Transaction[]> {
    const queryParams = new URLSearchParams(filters as Record<string, string>).toString();
    return fetchData(`transactions/?${queryParams}`);
}

export async function createTransaction(transactionData: Partial<Transaction>): Promise<Transaction> {
    return fetchData('transactions/', {
        method: 'POST',
        body: JSON.stringify(transactionData)
    });
}

export async function updateTransaction(id: number, transactionData: Partial<Transaction>): Promise<Transaction> {
    return fetchData(`transactions/${id}/`, {
        method: 'PUT',
        body: JSON.stringify(transactionData)
    });
}

export async function deleteTransaction(id: number): Promise<void> {
    return fetchData(`transactions/${id}/`, {
        method: 'DELETE'
    });
}

export async function getBudgetGoals(): Promise<BudgetGoal[]> {
    return fetchData('budget-goals/');
}

export async function createBudgetGoal(goalData: Partial<BudgetGoal>): Promise<BudgetGoal> {
    return fetchData('budget-goals/', {
        method: 'POST',
        body: JSON.stringify(goalData)
    });
}

export async function updateBudgetGoal(id: number, goalData: Partial<BudgetGoal>): Promise<BudgetGoal> {
    return fetchData(`budget-goals/${id}/`, {
        method: 'PUT',
        body: JSON.stringify(goalData)
    });
}

export async function deleteBudgetGoal(id: number): Promise<void> {
    return fetchData(`budget-goals/${id}/`, {
        method: 'DELETE'
    });
}

export async function getRecurringBills(): Promise<RecurringBill[]> {
    return fetchData('recurring-bills/');
}

export async function createRecurringBill(billData: Partial<RecurringBill>): Promise<RecurringBill> {
    return fetchData('recurring-bills/', {
        method: 'POST',
        body: JSON.stringify(billData)
    });
}

export async function updateRecurringBill(id: number, billData: Partial<RecurringBill>): Promise<RecurringBill> {
    return fetchData(`recurring-bills/${id}/`, {
        method: 'PUT',
        body: JSON.stringify(billData)
    });
}

export async function deleteRecurringBill(id: number): Promise<void> {
    return fetchData(`recurring-bills/${id}/`, {
        method: 'DELETE'
    });
}

export async function getDashboardSummary(): Promise<DashboardSummary> {
    return fetchData('dashboard-summary/');
}

export async function getMonthlySummary(): Promise<MonthlyTrendData[]> {
    return fetchData('monthly-summary/');
}

export async function transferFunds(fromWalletId: number, toWalletId: number, amount: number, description: string): Promise<any> {
    return fetchData('transfers/', {
        method: 'POST',
        body: JSON.stringify({
            from_wallet: fromWalletId,
            to_wallet: toWalletId,
            amount: amount,
            description: description,
        }),
    });
}

// You might not need this if you primarily use monthly_budget on Category
// or if your backend handles creating/updating BudgetGoal records automatically.
export async function createOrUpdateBudgetGoal(data: {
    category_id: number | null;
    amount: number;
    month?: number;
    year?: number;
}): Promise<BudgetGoal> {
    const today = new Date();
    const month = data.month || today.getMonth() + 1;
    const year = data.year || today.getFullYear();

    return fetchData('budget-goals/', {
        method: 'POST', // Or a dedicated PUT/PATCH for existing goals
        body: JSON.stringify({
            category: data.category_id,
            amount: data.amount,
            month,
            year
        })
    });
}