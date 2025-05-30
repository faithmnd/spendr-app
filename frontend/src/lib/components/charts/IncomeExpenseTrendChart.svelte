<script lang="ts">
    // Import Chart.js directly, no svelte-chartjs-2 or svelte-chartjs
    import { Chart, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
    import type { MonthlyTrendData } from '$lib/api/budgets';
    import { onDestroy } from 'svelte'; // We need onDestroy for cleanup

    // Register Chart.js components globally (important for Chart.js)
    Chart.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

    export let data: MonthlyTrendData[] = [];

    let chartCanvas: HTMLCanvasElement; // Reference to the canvas element
    let myChart: Chart | null = null; // To hold the Chart.js instance

    // Reactive statement for chart labels (formatting 'YYYY-MM' to 'Month YYYY')
    $: chartLabels = data.map(item => {
        const [year, month] = item.month.split('-');
        return new Date(parseInt(year), parseInt(month) - 1, 1).toLocaleString('default', { month: 'short', year: 'numeric' });
    });

    // Reactive declaration for chart data. This will automatically re-run if `data` or `chartLabels` changes.
    $: chartData = {
        labels: chartLabels,
        datasets: [
            {
                label: 'Income',
                data: data.map(item => item.income),
                borderColor: '#28a745', // Green for income
                backgroundColor: 'rgba(40, 167, 69, 0.2)', // Light green fill
                tension: 0.3, // Smooth curve
                fill: true,
            },
            {
                label: 'Expenses', // Changed from 'Expense' to 'Expenses' for consistency if desired
                data: data.map(item => item.expense),
                borderColor: '#dc3545', // Red for expense
                backgroundColor: 'rgba(220, 53, 69, 0.2)', // Light red fill
                tension: 0.3, // Smooth curve
                fill: true,
            },
        ],
    };

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top' as const,
            },
            title: {
                display: false, // We'll use our own h2 for title if needed in parent component
            },
            tooltip: {
                callbacks: {
                    label: function(context: any) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (context.parsed.y !== null) {
                            // Format to Philippine Peso
                            label += new Intl.NumberFormat('en-PH', { style: 'currency', currency: 'PHP' }).format(context.parsed.y);
                        }
                        return label;
                    }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Amount (PHP)'
                }
            },
            x: {
                title: {
                    display: true,
                    text: 'Month'
                }
            }
        }
    };

    // Svelte Action: This function will be called with the canvas element when it's rendered
    function lineChartAction(canvas: HTMLCanvasElement) {
        chartCanvas = canvas; // Store reference to the canvas element
        
        // Initialize the chart
        myChart = new Chart(chartCanvas, {
            type: 'line', // This is a line chart
            data: chartData, // Initial data
            options: chartOptions
        });

        // The action can return an object with an `update` method to handle reactive changes
        return {
            update() {
                // This `update` method will be called when `chartData` or `chartOptions` (if reactive) change
                if (myChart) {
                    myChart.data = chartData; // Update chart data
                    myChart.update(); // Re-render the chart
                }
            },
            destroy() {
                // This `destroy` method will be called when the component is unmounted
                if (myChart) {
                    myChart.destroy();
                }
            }
        };
    }

    // Reactive statement to update the chart if 'data' (and thus 'chartData') changes
    // This catches updates not directly triggered by the action's 'update' method,
    // useful if 'data' is updated *after* the initial component mount.
    $: if (myChart) {
        myChart.data = chartData;
        myChart.update();
    }

    // Ensure chart is destroyed when component is removed from DOM (redundant with action's destroy, but good for safety)
    onDestroy(() => {
        if (myChart) {
            myChart.destroy();
        }
    });
</script>

<div class="chart-container">
    {#if data.length > 0}
        <canvas use:lineChartAction></canvas> {:else}
        <p>Not enough transaction data to show income/expense trend.</p>
    {/if}
</div>

<style>
    .chart-container {
        position: relative;
        height: 400px; /* Fixed height for consistency */
        width: 100%;
        margin: auto;
    }
    @media (max-width: 768px) {
        .chart-container {
            height: 350px;
        }
    }
</style>