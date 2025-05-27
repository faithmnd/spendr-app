import { writable } from 'svelte/store';
import { browser } from '$app/environment'; 

interface User {
    id: number;
    username: string;
    email: string;
}

interface AuthState {
    isAuthenticated: boolean;
    accessToken: string | null;
    user: User | null;
    isLoading: boolean; 
}

const initialAuthState: AuthState = {
    isAuthenticated: false,
    accessToken: null,
    user: null,
    isLoading: true, 
};

const auth = writable<AuthState>(initialAuthState);

export const authStore = {
    subscribe: auth.subscribe, 

    /**
     * Call this when a user successfully logs in or registers and gets a token.
     * @param {string} token
     */
    login: (token: string) => {
        if (browser) { 
            localStorage.setItem('accessToken', token);
        }
        auth.update(state => ({
            ...state,
            isAuthenticated: true,
            accessToken: token,
            isLoading: false,
        }));
    },

    logout: () => {
        if (browser) {
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken'); 
        }
        auth.set({
            isAuthenticated: false,
            accessToken: null,
            user: null,
            isLoading: false,
        });
    },

    /**
     * Set the current authenticated user's data.
     * @param {User} userData
     */
    setUser: (userData: User) => {
        auth.update(state => ({
            ...state,
            user: userData,
            isAuthenticated: true, 
            isLoading: false,
        }));
    },

    /**
     * Call this to set the loading state.
     * @param {boolean} loading 
     */
    setLoading: (loading: boolean) => {
        auth.update(state => ({
            ...state,
            isLoading: loading,
        }));
    },

    initializeAuth: async () => {
        authStore.setLoading(true);
        if (browser) {
            const accessToken = localStorage.getItem('accessToken');
            if (accessToken) {
                authStore.login(accessToken); 
                const { getCurrentUser } = await import('$lib/api/auth');
                await getCurrentUser(); 
            } else {
                authStore.setLoading(false);
            }
        } else {
            authStore.setLoading(false);
        }
    }
};
