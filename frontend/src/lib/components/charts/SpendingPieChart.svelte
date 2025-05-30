<script lang="ts">
    import { Chart, Title, Tooltip, Legend, ArcElement, CategoryScale } from 'chart.js';
    import type { SpendingByCategory } from '$lib/api/budgets';
    import { onMount, onDestroy } from 'svelte';
    
    Chart.register(Title, Tooltip, Legend, ArcElement, CategoryScale);

    export let data: SpendingByCategory[] = [];

    let chartCanvas: HTMLCanvasElement; // Reference to the canvas element
    let myChart: Chart | null = null; // To hold the Chart.js instance

    // Reactive declaration for chart data. This will automatically re-run if `data` changes.
    $: chartData = {
        labels: data.map(item => item.category_name),
        datasets: [
            {
                data: data.map(item => item.total_amount),
                backgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40',
                    '#E7E9ED', '#A0C4FF', '#BFFCC6', '#FFE082', '#DAA520', '#CDB7F2'
                ],
                hoverOffset: 4
            }
        ]
    };

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'right' as const,
            },
            tooltip: {
                callbacks: {
                    label: function(context: any) {
                        let label = context.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (context.parsed !== null) {
                            // Format to Philippine Peso
                            label += new Intl.NumberFormat('en-PH', { style: 'currency', currency: 'PHP' }).format(context.parsed);
                        }
                        return label;
                    }
                }
            }
        },
        layout: {
            padding: 10
        }
    };

    // Svelte Action: This function will be called with the canvas element when it's rendered
    function pieChartAction(canvas: HTMLCanvasElement) {
        chartCanvas = canvas; // Store reference to the canvas element
        
        // Initialize the chart
        myChart = new Chart(chartCanvas, {
            type: 'pie',
            data: chartData, // Use the reactive chartData
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
        <canvas use:pieChartAction></canvas> {:else}
        <p>No expense data available for the pie chart.</p>
    {/if}
</div>

<style>
    .chart-container {
        position: relative;
        height: 350px;
        width: 100%;
        margin: auto;
    }
    @media (max-width: 768px) {
        .chart-container {
            height: 300px;
        }
    }
</style>