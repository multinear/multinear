<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { Chart, registerables } from 'chart.js';
    import type { AggregationResultResponse } from '$lib/api';

    Chart.register(...registerables);

    export let aggregation: AggregationResultResponse;

    let canvas: HTMLCanvasElement;
    let chartInstance: Chart;

    // Helper function to format field names
    function formatFieldName(field: string): string {
        return field
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    // Helper function to get color based on score
    function getScoreColor(score: number): string {
        if (score >= 0.8) return '#16a34a'; // green-600
        if (score >= 0.5) return '#ca8a04'; // yellow-600
        return '#dc2626'; // red-600
    }

    // Helper function to get background color based on score
    function getScoreBackgroundColor(score: number): string {
        if (score >= 0.8) return '#16a34a20'; // green-600 with opacity
        if (score >= 0.5) return '#ca8a0420'; // yellow-600 with opacity
        return '#dc262620'; // red-600 with opacity
    }

    // Convert aggregation data to chart format
    function prepareChartData() {
        const results = aggregation.results.results;
        const entries = Object.entries(results);
        
        // Sort by score descending
        entries.sort(([, a], [, b]) => b.score - a.score);
        
        const labels = entries.map(([key, data]) => {
            // If we have field definitions, format the label nicely
            if (aggregation.results.fields.length > 0) {
                const fieldValues = key.split('__');
                if (fieldValues.length === 1) {
                    return fieldValues[0];
                } else {
                    // For multiple fields, create a compact label with "/" separator
                    return fieldValues.join(' / ');
                }
            }
            return key;
        });
        
        const scores = entries.map(([, data]) => data.score * 100); // Convert to percentage
        const counts = entries.map(([, data]) => data.count);
        
        const backgroundColors = scores.map(score => getScoreBackgroundColor(score / 100));
        const borderColors = scores.map(score => getScoreColor(score / 100));
        
        return {
            labels,
            datasets: [{
                label: 'Score (%)',
                data: scores,
                backgroundColor: backgroundColors,
                borderColor: borderColors,
                borderWidth: 2,
                counts: counts // Store counts for tooltip
            }]
        };
    }

    function createChart() {
        if (chartInstance) {
            chartInstance.destroy();
        }

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const chartData = prepareChartData();
        
        chartInstance = new Chart(ctx, {
            type: 'bar',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y', // Horizontal bars
                categoryPercentage: 0.8, // Reduce bar thickness
                barPercentage: 0.9, // Reduce spacing between bars
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title: function(context) {
                                return context[0].label;
                            },
                            label: function(context) {
                                const score = context.parsed.x.toFixed(1);
                                const count = context.dataset.counts[context.dataIndex];
                                return [
                                    `Score: ${score}%`,
                                    `Tasks: ${count}`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Score (%)'
                        },
                        grid: {
                            color: '#f3f4f6'
                        }
                    },
                    y: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            maxRotation: 0,
                            maxTicksLimit: false, // Show all labels
                            display: true,
                            font: {
                                size: 11 // Smaller font size for denser display
                            }
                        }
                    }
                },
                layout: {
                    padding: {
                        top: 10,
                        right: 10,
                        bottom: 10,
                        left: Math.min(window.innerWidth * 0.4, 300) // 40% of screen width, max 300px
                    }
                }
            }
        });
    }

    // Reactive statement to recreate chart when data changes
    $: if (canvas && aggregation) {
        createChart();
    }

    onMount(() => {
        if (aggregation) {
            createChart();
        }
    });

    onDestroy(() => {
        if (chartInstance) {
            chartInstance.destroy();
        }
    });
</script>

<div class="w-full">
    {#if Object.keys(aggregation.results.results).length > 0}
        <div class="w-full" style="height: {Math.max(300, Object.keys(aggregation.results.results).length * 25)}px;">
            <canvas bind:this={canvas}></canvas>
        </div>
        
        <!-- Summary stats -->
        <div class="mt-4 p-4 bg-gray-50 rounded-lg">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                    <div class="font-medium text-gray-700">Total Groups</div>
                    <div class="text-lg font-semibold">
                        {Object.keys(aggregation.results.results).length}
                    </div>
                </div>
                <div>
                    <div class="font-medium text-gray-700">Average Score</div>
                    <div class="text-lg font-semibold">
                        {(() => {
                            const scores = Object.values(aggregation.results.results).map(r => r.score);
                            const avg = scores.reduce((a, b) => a + b, 0) / scores.length;
                            return (avg * 100).toFixed(1);
                        })()}%
                    </div>
                </div>
                <div>
                    <div class="font-medium text-gray-700">Best Score</div>
                    <div class="text-lg font-semibold text-green-600">
                        {(Math.max(...Object.values(aggregation.results.results).map(r => r.score)) * 100).toFixed(1)}%
                    </div>
                </div>
                <div>
                    <div class="font-medium text-gray-700">Worst Score</div>
                    <div class="text-lg font-semibold text-red-600">
                        {(Math.min(...Object.values(aggregation.results.results).map(r => r.score)) * 100).toFixed(1)}%
                    </div>
                </div>
            </div>
        </div>
    {:else}
        <div class="text-center py-8 text-gray-500">
            <p>No data available for chart visualization.</p>
        </div>
    {/if}
</div>