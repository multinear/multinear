<script lang="ts">
    import ScoreCircle from './ScoreCircle.svelte';

    export let evaluations: Array<{ criterion: string; score: number; rationale: string }>;
    export let evalSpec: any;
    export let includePrintStyles: boolean = false;
    export let filter: string = "";

    function isPassed(ev: { criterion: string; score: number }): boolean {
        const minScore = evalSpec?.checklist?.find((item: { text: string; min_score?: number }) => 
            typeof item === 'object' && 
            item.text === ev.criterion
        )?.min_score;
        return minScore ? ev.score >= minScore : ev.score >= 1;
    }

    $: filteredEvaluations = evaluations.filter(ev => 
        filter === "" || 
        (filter === "passed" && isPassed(ev)) ||
        (filter === "failed" && !isPassed(ev))
    );
</script>

<div class="space-y-5 divide-y divide-gray-100">
    {#each filteredEvaluations as ev}
        {@const minScore = evalSpec?.checklist?.find((item: { text: string; min_score?: number }) => 
            typeof item === 'object' && 
            item.text === ev.criterion
        )?.min_score}
        <div class="pt-4 first:pt-0 {includePrintStyles ? 'print:break-inside-avoid' : ''}">
            <div class="flex gap-3 items-center">
                <div class="flex-none pt-[2px]">
                    <ScoreCircle 
                        score={ev.score} 
                        minScore={minScore} 
                        {includePrintStyles} 
                    />
                </div>
                <div class="text-sm font-medium flex-1 {minScore ? 'pb-7' : 'pb-1'}">{ev.criterion}</div>
            </div>
            <div class="mt-1 text-sm text-gray-600">{ev.rationale}</div>
        </div>
    {/each}
</div> 