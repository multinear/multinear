<script lang="ts">
    import * as Card from '$lib/components/ui/card';
    // import BarChart from './BarChart.svelte';

    // export let data: {
    //     labels: string[];
    //     datasets: {
    //         label: string;
    //         data: number[];
    //         backgroundColor: string;
    //     }[];
    // };

    // export let options = {
    //     responsive: true,
    //     maintainAspectRatio: false,
    // };

    /*    const barChartData = {
        labels: trendData.map(d => d.date),
        datasets: [
            {
                label: 'Pass',
                data: trendData.map(d => d.pass),
                backgroundColor: '#82ca9d',
            },
            {
                label: 'Fail',
                data: trendData.map(d => d.fail),
                backgroundColor: '#ffc658',
            },
            {
                label: 'Regression',
                data: trendData.map(d => d.regression),
                backgroundColor: '#ff8042',
            }
        ]
    };*/

</script>

<Card.Root>
    <Card.Header>
        <Card.Title>Tests per Run and Distribution Trend</Card.Title>
    </Card.Header>
    <Card.Content>
        <div class="h-[300px]">
            <!-- <BarChart chartData={data} chartOptions={options} /> -->
        </div>
    </Card.Content>
</Card.Root>
