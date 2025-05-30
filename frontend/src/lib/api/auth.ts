import { goto } from '$app/navigation';
import { authStore } from '$lib/stores/auth';
import type { User } from '$lib/types/user'; 
import { PUBLIC_API_BASE_URL } from '$env/static/public';

const API_BASE_URL = PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';


export async function registerUser(userData: { username: string; email: string; password: string; passwordConfirm: string }) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/registration/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: userData.username,
                email: userData.email,
                password1: userData.password,
                password2: userData.passwordConfirm,
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            let errorMessage = "Registration failed.";
            if (data && data.detail) {
                errorMessage = data.detail;
            } else if (typeof data === 'object') {
                errorMessage = Object.entries(data)
                    .map(([key, value]) => {
                        const messages = Array.isArray(value) ? value : [value];
                        if (key === 'password' || key === 'password1' || key === 'password2') {
                            return messages.join(', ');
                        }
                        return `${key}: ${messages.join(', ')}`;
                    })
                    .join('; ');
            }
            throw new Error(errorMessage);
        }

        return data;
    } catch (error: unknown) {
        console.error('Registration failed in auth.ts:', error);
        throw error;
    }
}

export async function loginUser(credentials: { username: string; password: string }) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(credentials),
        });

        const data = await response.json();

        if (!response.ok) {
            let errorMessage = "Login failed.";
            if (data && data.non_field_errors && data.non_field_errors.length > 0) {
                errorMessage = data.non_field_errors[0];
            } else if (data && data.detail) {
                errorMessage = data.detail;
            } else if (typeof data === 'object') {
                errorMessage = Object.entries(data)
                    .map(([key, value]) => {
                        return `${key}: ${(Array.isArray(value) ? value : [value]).join(', ')}`;
                    })
                    .join('; ');
            }
            throw new Error(errorMessage);
        }

        const { access, refresh } = data;

        if (access && refresh) {
            localStorage.setItem('accessToken', access);
            localStorage.setItem('refreshToken', refresh);
            authStore.login(access);
            await goto('/dashboard');
            return data;
        } else {
            throw new Error('Authentication tokens not received.');
        }
    } catch (error: unknown) {
        console.error('Login failed:', error);
        throw error;
    }
}

export async function logoutUser() {
    try {
        const accessToken = localStorage.getItem('accessToken');
        if (accessToken) {
            await fetch(`${API_BASE_URL}/api/auth/logout/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`,
                },
            });
        }
    } catch (error) {
        console.warn('Backend logout failed (token might be invalid or network issue):', error);
    } finally {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        authStore.logout();
        goto('/login');
    }
}

export async function getCurrentUser(): Promise<User | null> {
    const accessToken = localStorage.getItem('accessToken');
    if (!accessToken) {
        authStore.logout();
        return null;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/user/`, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            }
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
            throw new Error(`API Error: ${response.status} - ${response.statusText || 'Unknown error'}`);
        }

        const data: User = await response.json();
        authStore.setUser(data);
        return data;
    } catch (error) {
        console.error('Error fetching current user:', error);
        logoutUser();
        return null;
    }
}

async function refreshAccessToken(): Promise<boolean> {
    const refreshToken = localStorage.getItem('refreshToken');
    if (!refreshToken) {
        return false;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/token/refresh/`, {
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
        if (newAccessToken) {
            localStorage.setItem('accessToken', newAccessToken);
            authStore.login(newAccessToken);
            return true;
        } else {
            throw new Error('New access token not received during refresh.');
        }
    } catch (error) {
        console.error('Error refreshing token:', error);
        logoutUser();
        return false;
    }
}

export function getAuthHeaders(): HeadersInit {
    const headers: HeadersInit = {
        'Content-Type': 'application/json',
    };
    const token = localStorage.getItem('accessToken');
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}