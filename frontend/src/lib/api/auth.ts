import { goto } from '$app/navigation';
import { authStore } from '$lib/stores/auth';

const API_BASE_URL = 'http://localhost:8000/api';
/**
 * Registers a new user.
 * @param {object} userData 
 * @param {string} userData.username    
 * @param {string} userData.email 
 * @param {string} userData.password 
 * @param {string} userData.password2 
 * @returns {Promise<object>} 
 */
export async function registerUser(userData: { username: string; email: string; password: string; password2: string }) {
    try {
        const response = await fetch(`${API_BASE_URL}/register/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || JSON.stringify(data)); 
        }

        return data;

    } catch (error: unknown) {
        console.error('Registration failed:', error);
        throw error; 
    }
}

/**
 * Logs in a user.
 * @param {object} credentials 
 * @param {string} credentials.username 
 * @param {string} credentials.password 
 * @returns {Promise<object>} 
 */
export async function loginUser(credentials: { username: string; password: string }) {
    try {
        const response = await fetch(`${API_BASE_URL}/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(credentials),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Login failed');
        }

        const { access, refresh } = data;

        localStorage.setItem('accessToken', access);
        localStorage.setItem('refreshToken', refresh);

        authStore.login(access); 

        await goto('/dashboard'); 

        return data;

    } catch (error: unknown) {
        console.error('Login failed:', error);
        throw error;
    }
}

export function logoutUser() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    authStore.logout();
    goto('/login'); 
}

/**
 * Fetches the current authenticated user's details.
 * @returns {Promise<object | null>} 
 */
export async function getCurrentUser() {
    const accessToken = localStorage.getItem('accessToken');
    if (!accessToken) {
        authStore.logout();
        return null;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/user/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`, 
            },
        });

        if (response.status === 401) {
            console.warn('Access token expired or invalid. Attempting refresh...');
            const success = await refreshAccessToken();
            if (success) {
                return getCurrentUser();
            } else {
                logoutUser();
                return null;
            }
        }

        if (!response.ok) {
            throw new Error('Failed to fetch user data');
        }

        const data = await response.json();
        authStore.setUser(data); 
        return data;

    } catch (error) {
        console.error('Error fetching current user:', error);
        logoutUser(); 
        return null;
    }
}

/**
 * Refreshes the access token using the refresh token.
 * @returns {Promise<boolean>} - True if refresh was successful, false otherwise.
 */
async function refreshAccessToken(): Promise<boolean> {
    const refreshToken = localStorage.getItem('refreshToken');
    if (!refreshToken) {
        return false;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/token/refresh/`, { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh: refreshToken }),
        });

        if (!response.ok) {
            throw new Error('Token refresh failed');
        }

        const data = await response.json();
        const newAccessToken = data.access;
        localStorage.setItem('accessToken', newAccessToken);
        authStore.login(newAccessToken); 
        return true;
    } catch (error) {
        console.error('Error refreshing token:', error);
        logoutUser();
        return false;
    }
}