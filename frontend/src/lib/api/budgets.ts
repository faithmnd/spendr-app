import { API_BASE_URL } from '$lib/config';
import { getAuthHeaders } from './auth';

export interface Wallet {
    id: number;
    name: string;
    balance: number;
    currency: string;
    description: string | null;
    user: number;
    created_at: string;
    updated_at: string;
    // Added for Accounts page:
    type: 'Cash' | 'Bank' | 'eWallet' | 'Credit Card' | 'Other'; // Type of account
    icon?: string; // Optional icon for the account type (e.g., emoji)
}

export interface Category {
    id: number;
    name: string;
    type: 'income' | 'expense';
    description: string | null;
    user: number;
    created_at: string;
    updated_at: string;
    // Added for Categories page:
    icon?: string; // Optional icon/emoji for the category
    monthly_budget?: number; // Optional budget for the category (e.g., for current month)
    budget_progress?: number; // Optional progress percentage against the budget
    is_default?: boolean; // Optional: indicates if this is a default category for quick-adding
}

export interface Transaction {
    id: number;
    amount: number;
    transaction_type: 'income' | 'expense';
    description: string | null;
    date: string;
    wallet: number;
    wallet_name: string;
    category: number | null;
    category_name: string | null;
    category_type: string | null;
    user: number;
    created_at: string;
    updated_at: string;
}

export interface BudgetGoal {
    id: number;
    month: number;
    year: number;
    category: number | null;
    category_name: string | null;
    amount: number;
    description: string | null;
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

async function fetchData(url: string, options?: RequestInit) {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/api/budget/${url}`, {
        ...options,
        headers: {
            ...headers,
            ...options?.headers,
            'Content-Type': 'application/json'
        }
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        const errorMessage = errorData.detail || JSON.stringify(errorData);
        throw new Error(`API Error: ${response.status} - ${errorMessage}`);
    }
    return response.json();
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
        method: 'PUT', // Use PUT for full replacement, PATCH for partial update
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

export async function updateCategory(id: number, categoryData: Partial<Category>): Promise<Category> {
    return fetchData(`categories/${id}/`, {
        method: 'PUT', // Use PUT for full replacement, PATCH for partial update
        body: JSON.stringify(categoryData)
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
        method: 'PUT', // Use PUT for full replacement, PATCH for partial update
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
        method: 'PUT', // Use PUT for full replacement, PATCH for partial update
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
        method: 'PUT', // Use PUT for full replacement, PATCH for partial update
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

/**
 * Transfers funds between two wallets (accounts).
 * @param {number} fromWalletId - The ID of the source wallet.
 * @param {number} toWalletId - The ID of the destination wallet.
 * @param {number} amount - The amount to transfer.
 * @param {string} description - Description of the transfer.
 * @returns {Promise<any>} - Response from the transfer API.
 */
export async function transferFunds(fromWalletId: number, toWalletId: number, amount: number, description: string): Promise<any> {
    try {
        const response = await fetch(`${API_BASE_URL}/api/budget/transfers/`, { // Assuming a /transfers/ endpoint under /api/budget/
            method: 'POST',
            headers: await getAuthHeaders(),
            body: JSON.stringify({
                from_wallet: fromWalletId,
                to_wallet: toWalletId,
                amount: amount,
                description: description,
            }),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errorData.detail || JSON.stringify(errorData));
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error transferring funds:', error);
        throw error;
    }
}
