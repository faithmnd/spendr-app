<script lang="ts">
    import { onMount } from 'svelte';
    import { getCategories, type Category } from '$lib/api/budgets';
    import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
    import ErrorMessage from '$lib/components/ErrorMessage.svelte';
    import AddCategoryModal from '$lib/components/AddCategoryModal.svelte';
    // You might need an EditCategoryModal if you want a dedicated modal for editing
    // import EditCategoryModal from '$lib/components/EditCategoryModal.svelte';

    let categories: Category[] = [];
    let isLoading = true;
    let error: string | null = null;
    let successMessage: string | null = null;

    let showAddCategoryModal = false;
    let showEditCategoryModal = false; // For a dedicated edit modal if implemented
    let categoryToEdit: Category | null = null; // To pass data to edit modal

    // Placeholder for category budgets (assuming your API might provide this or it's a future feature)
    // For now, we'll just show a placeholder budget value.
    interface CategoryWithBudget extends Category {
        monthly_budget?: number; // Optional budget for the category
        budget_progress?: number; // Optional progress percentage
    }

    async function fetchCategoriesData() {
        error = null;
        try {
            // Fetch categories. Assuming getCategories now returns CategoryWithBudget or we'll add dummy data.
            const fetchedCategories: Category[] = await getCategories();

            // For demonstration, let's add some dummy budget data if not provided by API
            categories = fetchedCategories.map(cat => ({
                ...cat,
                // Example: Add a dummy monthly budget and progress for demonstration
                // In a real app, this would come from your backend API
                monthly_budget: cat.type === 'expense' ? Math.floor(Math.random() * 500) + 50 : undefined,
                budget_progress: cat.type === 'expense' ? Math.floor(Math.random() * 120) : undefined,
                // Add a dummy icon/emoji if not provided by API
                icon: cat.icon || getRandomEmoji(), // Assuming 'icon' field on Category
            })) as CategoryWithBudget[];

        } catch (err: any) {
            console.error('Error loading categories data:', err);
            error = err.message || 'Failed to load categories.';
        } finally {
            isLoading = false;
        }
    }

    onMount(async () => {
        await fetchCategoriesData();
    });

    function handleModalClose() {
        showAddCategoryModal = false;
        showEditCategoryModal = false;
        categoryToEdit = null;
    }

    async function handleCategoryChange() {
        successMessage = 'Category data updated successfully!';
        handleModalClose(); // Close the modal after successful operation
        await fetchCategoriesData(); // Re-fetch all data to ensure the list is up-to-date
        setTimeout(() => successMessage = null, 3000); // Clear success message after 3 seconds
    }

    function handleEditCategory(category: Category) {
        console.log('Edit category:', category);
        categoryToEdit = category;
        showEditCategoryModal = true; // Or use a generic modal that takes `categoryToEdit`
        // TODO: Implement actual EditCategoryModal or integrate edit into AddCategoryModal
        alert(`Edit functionality for ${category.name} is not yet fully implemented.`); // Use a custom modal in a real app
    }

    function handleDeleteCategory(categoryId: number, categoryName: string) {
        console.log('Delete category with ID:', categoryId);
        if (confirm(`Are you sure you want to delete the category "${categoryName}"? This cannot be undone.`)) {
            // TODO: Implement logic to call delete API and then re-fetch data
            // Example: await deleteCategory(categoryId);
            // fetchCategoriesData();
            alert(`Delete functionality for ${categoryName} is not yet implemented.`); // Use a custom modal in a real app
        }
    }

    function handleSetDefaultCategory(categoryId: number, categoryName: string) {
        console.log('Set default category with ID:', categoryId);
        // TODO: Implement logic to call API to set default category
        // Example: await setDefaultCategory(categoryId);
        // fetchCategoriesData(); // Re-fetch to update UI if default is highlighted
        alert(`Setting "${categoryName}" as default is not yet implemented.`); // Use a custom modal in a real app
    }

    const emojis = ['🎀', '🌷', '👛', '🦩', '🩰', '🦢', '🍄', '🐇', '🐹'];
    function getRandomEmoji() {
        return emojis[Math.floor(Math.random() * emojis.length)];
    }

    $: expenseCategories = categories.filter(cat => cat.type === 'expense');
    $: incomeCategories = categories.filter(cat => cat.type === 'income');
</script>

<svelte:head>
    <title>Spendr - Categories</title>
</svelte:head>

<div class="categories-wrapper">
    <div class="categories-header">
        <h1>𝜗𝜚 Categories Page ⋆. 𐙚 ˚</h1>
        <p>Make cute little labels for your chaos. Rename, edit, vibe—it’s your budget era.</p>
    </div>

    {#if isLoading}
        <LoadingSpinner message="Loading your wallet ♡ — don’t worry, we didn’t spend anything ₊˚⊹" />
    {:else if error}
        <ErrorMessage message={error} />
    {:else}
        {#if successMessage}
            <div class="success-message">{successMessage}</div>
        {/if}

        <div class="controls-section">
            <button class="add-button" on:click={() => showAddCategoryModal = true}>+ Add New Category</button>
        </div>

        <div class="category-sections">
            <section class="category-section expense-categories">
                <h2>Expense Categories</h2>
                {#if expenseCategories.length > 0}
                    <ul class="category-list">
                        {#each expenseCategories as category (category.id)}
                            <li class="category-item">
                                <span class="category-icon">{category.icon || '❓'}</span>
                                <span class="category-name">{category.name}</span>
                                <span class="category-type type-expense">{category.type}</span>
                                {#if category.monthly_budget !== undefined && category.monthly_budget > 0}
                                    <div class="category-budget">
                                        Budget: ₱{category.monthly_budget.toFixed(2)}
                                        <div class="budget-progress-bar-container">
                                            <div class="budget-progress-bar" style="width: {Math.min(category.budget_progress || 0, 100)}%;"></div>
                                        </div>
                                        <span class="budget-progress-text" class:overbudget={category.budget_progress && category.budget_progress > 100}>
                                            {category.budget_progress?.toFixed(1) || 0}% Used
                                        </span>
                                    </div>
                                {/if}
                                <div class="category-actions">
                                    <button class="action-button edit-button" on:click={() => handleEditCategory(category)}>✏️ Edit</button>
                                    <button class="action-button delete-button" on:click={() => handleDeleteCategory(category.id, category.name)}>🗑️ Delete</button>
                                    <button class="action-button default-button" on:click={() => handleSetDefaultCategory(category.id, category.name)}>⭐ Set Default</button>
                                </div>
                            </li>
                        {/each}
                    </ul>
                {:else}
                    <p class="no-data-message">No expense categories added yet. Time to organize your spending!</p>
                {/if}
            </section>

            <section class="category-section income-categories">
                <h2>Income Categories</h2>
                {#if incomeCategories.length > 0}
                    <ul class="category-list">
                        {#each incomeCategories as category (category.id)}
                            <li class="category-item">
                                <span class="category-icon">{category.icon || '❓'}</span>
                                <span class="category-name">{category.name}</span>
                                <span class="category-type type-income">{category.type}</span>
                                <div class="category-actions">
                                    <button class="action-button edit-button" on:click={() => handleEditCategory(category)}>✏️ Edit</button>
                                    <button class="action-button delete-button" on:click={() => handleDeleteCategory(category.id, category.name)}>🗑️ Delete</button>
                                    <button class="action-button default-button" on:click={() => handleSetDefaultCategory(category.id, category.name)}>⭐ Set Default</button>
                                </div>
                            </li>
                        {/each}
                    </ul>
                {:else}
                    <p class="no-data-message">No income categories added yet. Track your earnings!</p>
                {/if}
            </section>
        </div>
    {/if}
</div>

{#if showAddCategoryModal}
    <AddCategoryModal on:close={handleModalClose} on:categoryAdded={handleCategoryChange} />
{/if}

<!--
{#if showEditCategoryModal && categoryToEdit}
    <EditCategoryModal category={categoryToEdit} on:close={handleModalClose} on:categoryUpdated={handleCategoryChange} />
{/if}
-->

<style>
    /* Define CSS Variables for the pink theme (assuming these are globally available, e.g., in app.css) */
    :root {
        --primary-pink: #FF69B4; /* Hot Pink */
        --dark-pink: #C71585;    /* Medium Violet Red */
        --accent-pink: #FF1493;  /* Deep Pink */
        --light-pink: #FFC0CB;   /* Light Pink */
        --text-white: #FFFFFF;
        --text-dark: #333333;
        --text-medium: #555555;
        --border-light: #F0F0F0;
        --shadow-light: rgba(0, 0, 0, 0.08);
        --shadow-medium: rgba(0, 0, 0, 0.12);
        --success-bg: #d4edda;
        --success-text: #155724;
        --error-bg: #f8d7da;
        --error-text: #dc3545;
        --warning-bg: #fff3cd;
        --warning-text: #856404;
        --info-bg: #e0f2f7; /* Light blue for header */
        --info-text: #0056b3;
    }

    /* General Layout */
    .categories-wrapper {
        padding: 20px;
        max-width: 1200px; /* Slightly narrower than dashboard for content focus */
        margin: 0 auto;
        font-family: 'Inter', sans-serif;
        color: var(--text-dark);
    }

    .categories-header {
        text-align: center;
        margin-bottom: 30px;
        padding: 25px;
        background: linear-gradient(135deg, var(--light-pink), var(--primary-pink));
        color: var(--text-white);
        border-radius: 15px;
        box-shadow: 0 6px 15px var(--shadow-medium);
    }
    .categories-header h1 {
        color: var(--text-white);
        font-size: 2.8em;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .categories-header p {
        color: var(--text-white);
        font-size: 1.2em;
        opacity: 0.9;
    }

    .controls-section {
        display: flex;
        justify-content: flex-end; /* Align button to the right */
        margin-bottom: 30px;
    }

    .add-button {
        background-color: var(--accent-pink);
        color: var(--text-white);
        border: none;
        padding: 12px 22px;
        border-radius: 25px;
        cursor: pointer;
        font-size: 1em;
        font-weight: bold;
        transition: background-color 0.3s ease, transform 0.2s ease, box-shadow 0.3s ease;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
        white-space: nowrap;
    }
    .add-button:hover {
        background-color: var(--dark-pink);
        transform: translateY(-3px);
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.25);
    }
    .add-button:active {
        transform: translateY(0);
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }

    .category-sections {
        display: grid;
        grid-template-columns: 1fr;
        gap: 30px;
    }

    @media (min-width: 768px) {
        .category-sections {
            grid-template-columns: 1fr 1fr; /* Two columns for larger screens */
        }
    }

    .category-section {
        background-color: var(--text-white);
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 6px 18px var(--shadow-light);
        border: 1px solid var(--border-light);
        transition: box-shadow 0.3s ease-in-out;
    }
    .category-section:hover {
        box-shadow: 0 10px 25px var(--shadow-medium);
    }

    .category-section h2 {
        margin-top: 0;
        color: var(--text-dark);
        border-bottom: 1px solid var(--border-light);
        padding-bottom: 15px;
        margin-bottom: 25px;
        font-size: 1.8em;
        font-weight: 700;
        text-align: center;
    }

    .category-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }

    .category-item {
        display: flex;
        flex-wrap: wrap; /* Allow wrapping */
        align-items: center;
        padding: 15px 0;
        border-bottom: 1px dashed var(--border-light);
        font-size: 1.1em;
        color: var(--text-medium);
        gap: 10px; /* Space between elements */
    }
    .category-item:last-child {
        border-bottom: none;
    }

    .category-icon {
        font-size: 1.5em; /* Larger emoji/icon */
        margin-right: 5px;
        flex-shrink: 0; /* Prevent shrinking */
    }

    .category-name {
        font-weight: bold;
        color: var(--text-dark);
        flex-grow: 1; /* Allows name to take up space */
    }

    .category-type {
        font-size: 0.9em;
        padding: 4px 8px;
        border-radius: 15px;
        text-transform: capitalize;
        font-weight: 600;
        white-space: nowrap;
    }
    .type-expense {
        background-color: var(--light-pink);
        color: var(--dark-pink);
    }
    .type-income {
        background-color: #d4edda; /* Light green */
        color: #155724; /* Dark green */
    }

    .category-budget {
        flex-basis: 100%; /* Take full width on new line */
        margin-top: 10px;
        font-size: 0.95em;
        color: var(--text-medium);
    }

    .budget-progress-bar-container {
        width: 100%;
        background-color: var(--light-pink);
        border-radius: 8px;
        height: 10px;
        overflow: hidden;
        margin-top: 5px;
        box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    .budget-progress-bar {
        height: 100%;
        background-color: var(--primary-pink);
        border-radius: 8px;
        transition: width 0.5s ease-in-out, background-color 0.3s ease-in-out;
    }
    .budget-progress-text {
        font-size: 0.85em;
        margin-top: 5px;
        display: block;
        text-align: right;
        font-weight: bold;
        color: var(--dark-pink);
    }
    .budget-progress-text.overbudget {
        color: var(--error-text); /* Red if over budget */
    }

    .category-actions {
        display: flex;
        gap: 8px;
        margin-top: 10px; /* Space from budget info */
        flex-basis: 100%; /* Take full width on small screens */
        justify-content: flex-end; /* Align buttons to the right */
        flex-wrap: wrap;
    }

    .action-button {
        padding: 8px 12px;
        border-radius: 20px;
        cursor: pointer;
        font-size: 0.8em; /* Smaller buttons */
        font-weight: 600;
        transition: background-color 0.2s ease, transform 0.1s ease;
        border: none;
        white-space: nowrap;
    }

    .edit-button {
        background-color: #007bff; /* Blue for edit */
        color: var(--text-white);
    }
    .edit-button:hover {
        background-color: #0056b3;
        transform: translateY(-1px);
    }

    .delete-button {
        background-color: var(--error-text); /* Red for delete */
        color: var(--text-white);
    }
    .delete-button:hover {
        background-color: #a71d2a;
        transform: translateY(-1px);
    }

    .default-button {
        background-color: #ffc107; /* Yellow for default */
        color: var(--text-dark);
    }
    .default-button:hover {
        background-color: #e0a800;
        transform: translateY(-1px);
    }

    .no-data-message {
        text-align: center;
        padding: 30px;
        font-size: 1.1em;
        color: var(--text-medium);
        background-color: var(--light-pink); /* Light pink background */
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        margin-top: 20px;
        border: 1px solid var(--primary-pink);
    }

    .success-message {
        background-color: var(--success-bg);
        color: var(--success-text);
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 30px;
        text-align: center;
        font-weight: bold;
        border: 1px solid #a3e6b3;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .controls-section {
            justify-content: center; /* Center add button on small screens */
        }
        .category-item {
            flex-direction: column;
            align-items: flex-start;
            gap: 5px;
        }
        .category-actions {
            justify-content: flex-start; /* Align buttons to the left */
            margin-top: 15px; /* More space from other elements */
        }
        .category-icon {
            margin-right: 0;
            margin-bottom: 5px; /* Space below icon */
        }
        .category-name, .category-type, .category-budget {
            width: 100%; /* Take full width */
            text-align: left;
        }
        .budget-progress-text {
            text-align: left;
        }
    }
</style>
