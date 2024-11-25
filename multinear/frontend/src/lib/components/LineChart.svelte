<!-- LineChart.svelte -->
<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { Chart, registerables } from 'chart.js';
    Chart.register(...registerables);

    export let data;
    export let options;

    let canvas: HTMLCanvasElement;
    let chartInstance: Chart;

    onMount(() => {
        chartInstance = new Chart(canvas, {
            type: 'line',
            data,
            options
        });

        return () => {
            chartInstance.destroy();
        };
    });

    onDestroy(() => {
        if (chartInstance) {
            chartInstance.destroy();
        }
    });
</script>

<canvas bind:this={canvas}></canvas>
