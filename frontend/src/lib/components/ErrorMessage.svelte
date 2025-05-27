<div class="error-container">
    <p class="error-text">{message || 'Something went wrong... but your money’s safe. Pinky promise.ᐟ ₍^. .^₎Ⳋ'}</p>
    {#if details}
        <pre class="error-details">{details}</pre>
    {/if}
</div>

<script lang="ts">
    export let message: string;
    export let details: string | null = null; 
</script>

<style>
    .error-container {
        background-color: #f8d7da;
        color: #721c24; 
        border: 1px solid #f5c6cb; 
        border-radius: 5px;
        padding: 15px;
        margin-bottom: 20px;
        text-align: center;
    }

    .error-text {
        font-weight: bold;
        margin: 0;
    }

    .error-details {
        margin-top: 10px;
        font-size: 0.8em;
        color: #a7424a;
        white-space: pre-wrap; 
        text-align: left;
        background-color: #fcebeb;
        padding: 8px;
        border-radius: 3px;
        overflow-x: auto; 
    }
</style>