export interface User {
    id: number;
    username: string;
    email: string;
}

export interface Account {
    id: number;
    name: string;
    balance: number;
    currency: string; 
}

export interface Category {
    id: number;
    name: string;
    type: 'income' | 'expense'; 
}

export interface Transaction {
    id: number;
    description: string;
    amount: number;
    type: 'income' | 'expense'; 
    date: string; 
    category: Category; 
    account: Account;
}