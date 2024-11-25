<script lang="ts">
    import * as Card from '$lib/components/ui/card';
    import LineChart from '$lib/components/LineChart.svelte';

    export let data: {
        labels: string[];
        datasets: {
            label: string;
            data: number[];
            borderColor: string;
            fill: boolean;
        }[];
    };

    export let options = {
        responsive: true,
        maintainAspectRatio: false,
    };

    const trendData = [
        {
            date: "2024-03-10",
            score: 0.82,
            totalTests: 450,
            pass: 369,
            fail: 72,
            regression: 9,
        },
        {
            date: "2024-03-11",
            score: 0.85,
            totalTests: 460,
            pass: 391,
            fail: 60,
            regression: 9,
        },
        {
            date: "2024-03-12",
            score: 0.81,
            totalTests: 470,
            pass: 380,
            fail: 80,
            regression: 10,
        },
        {
            date: "2024-03-13",
            score: 0.87,
            totalTests: 480,
            pass: 417,
            fail: 55,
            regression: 8,
        },
        {
            date: "2024-03-14",
            score: 0.9,
            totalTests: 490,
            pass: 441,
            fail: 44,
            regression: 5,
        },
        {
            date: "2024-03-15",
            score: 0.88,
            totalTests: 500,
            pass: 440,
            fail: 50,
            regression: 10,
        },
    ];

    const lineChartData = {
        labels: trendData.map((d) => d.date),
        datasets: [
            {
                label: "Score",
                data: trendData.map((d) => d.score),
                borderColor: "#8884d8",
                fill: false,
            },
        ],
    };

    data = lineChartData;
</script>

<Card.Root>
    <Card.Header>
        <Card.Title>Evaluation Score Trend</Card.Title>
    </Card.Header>
    <Card.Content>
        <div class="h-[300px]">
            <LineChart {data} {options} />
        </div>
    </Card.Content>
</Card.Root>
