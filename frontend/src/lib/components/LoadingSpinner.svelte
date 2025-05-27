<div class="spinner-container">
    <div class="spinner"></div>
    <p>{message || 'Loading...'}</p>
</div>

<script lang="ts">
    export let message: string = 'Loading your wallet ♡ — don’t worry, we didn’t spend anything ₊˚⊹'; 
</script>

<style>
    .spinner-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 20px;
        color: #C71585;
    }

    .spinner {
        border: 4px solid rgba(0, 0, 0, 0.1);
        border-left-color: #C71585;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin-bottom: 10px;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .spinner-container p {
        font-size: 1em;
        margin: 0;
    }
</style>