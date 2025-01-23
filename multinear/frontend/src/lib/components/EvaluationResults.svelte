<script lang="ts">
    import ScoreCircle from './ScoreCircle.svelte';
    import { Button } from "$lib/components/ui/button";

    export let evaluations: Array<{ criterion: string; score: number; rationale: string }>;
    export let evalSpec: any;
    export let includePrintStyles: boolean = false;
    export let showFilter: boolean = false;

    let evaluationFilter = "";

    $: filteredEvaluations = evaluations.filter(ev => 
        evaluationFilter === "" || 
        (evaluationFilter === "passed" && ev.score >= 1) ||
        (evaluationFilter === "failed" && ev.score < 1)
    );
</script>

<div>
    {#if showFilter && (evaluations.some(ev => ev.score >= 1) && evaluations.some(ev => ev.score < 1)) || evaluationFilter !== ""}
        <div class="flex gap-2">
            <Button
                variant="outline"
                size="sm"
                class={evaluationFilter === "" ? 'bg-gray-100 border-gray-200' : ''}
                on:click={() => evaluationFilter = ""}
            >
                All
            </Button>
            <Button
                variant="outline"
                size="sm"
                class={evaluationFilter === "passed" ? 'bg-green-50 border-green-200 text-green-700' : ''}
                on:click={() => evaluationFilter = "passed"}
            >
                Passed
            </Button>
            <Button
                variant="outline"
                size="sm"
                class={evaluationFilter === "failed" ? 'bg-red-50 border-red-200 text-red-700' : ''}
                on:click={() => evaluationFilter = "failed"}
            >
                Failed
            </Button>
        </div>
    {/if}

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
</div> 