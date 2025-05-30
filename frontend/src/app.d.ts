// D:/spendr-app/frontend/src/app.d.ts

/// <reference types="@sveltejs/kit" />

// See https://kit.svelte.dev/docs/types#app for information about these interfaces
declare global {
    namespace App {
        // interface Error {}
        // interface Locals {}
        // interface PageData {}
        // interface Platform {}
    }
}

// This block is for environment variables.
// Make sure your .env file has PUBLIC_API_BASE_URL=http://127.0.0.1:8000
interface ImportMetaEnv {
    readonly PUBLIC_API_BASE_URL: string;
    // Add any other PUBLIC_ prefixed environment variables here
}

interface ImportMeta {
    readonly env: ImportMetaEnv;
}

export { };