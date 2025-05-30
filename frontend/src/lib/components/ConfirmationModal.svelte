<script lang="ts">
    import { createEventDispatcher } from 'svelte';

    export let message: string;
    export let confirmText: string = 'Confirm';
    export let cancelText: string = 'Cancel';
    export let title: string = 'Confirm Action';

    const dispatch = createEventDispatcher();

    function handleConfirm() {
        dispatch('confirm');
    }

    function handleCancel() {
        dispatch('cancel');
    }
</script>

<div class="modal-overlay">
    <div class="modal-content">
        <h2>{title}</h2>
        <p>{message}</p>
        <div class="modal-actions">
            <button class="cancel-button" on:click={handleCancel}>{cancelText}</button>
            <button class="confirm-button" on:click={handleConfirm}>{confirmText}</button>
        </div>
    </div>
</div>

<style>
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.6);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }

    .modal-content {
        background-color: var(--text-white);
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
        max-width: 450px;
        width: 90%;
        text-align: center;
        animation: fadeIn 0.3s ease-out forwards;
    }

    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: scale(0.9);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }

    h2 {
        color: var(--dark-pink);
        margin-bottom: 20px;
        font-size: 1.8em;
    }

    p {
        font-size: 1.1em;
        color: var(--text-dark);
        margin-bottom: 30px;
    }

    .modal-actions {
        display: flex;
        justify-content: center;
        gap: 15px;
    }

    .confirm-button,
    .cancel-button {
        padding: 12px 25px;
        border-radius: 25px;
        font-size: 1em;
        font-weight: bold;
        cursor: pointer;
        transition: background-color 0.3s ease, transform 0.2s ease, box-shadow 0.3s ease;
        border: none;
    }

    .confirm-button {
        background-color: var(--accent-pink);
        color: var(--text-white);
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    }

    .confirm-button:hover {
        background-color: var(--dark-pink);
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
    }

    .cancel-button {
        background-color: var(--border-light);
        color: var(--text-medium);
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
    }

    .cancel-button:hover {
        background-color: #e0e0e0;
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
    }
</style>
