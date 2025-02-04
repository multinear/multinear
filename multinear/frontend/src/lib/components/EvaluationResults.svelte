<script lang="ts">
    import ScoreCircle from './ScoreCircle.svelte';

    export let evaluations: Array<{ criterion: string; score: number; rationale: string }>;
    export let evalSpec: any;
    export let includePrintStyles: boolean = false;
    export let filter: string = "";

    function getMinScore(criterion: string): number {
        try {
            return evalSpec?.checklist?.find((item: { text: string; min_score?: number }) => 
                typeof item === 'object' && 
                item.text === criterion
            )?.min_score;
        } catch (e) {
            // console.error(e);
            return 1;
        }
    }

    function isPassed(ev: { criterion: string; score: number }): boolean {
        return ev.score >= getMinScore(ev.criterion);
    }

    $: filteredEvaluations = evaluations.filter(ev => 
        filter === "" || 
        (filter === "passed" && isPassed(ev)) ||
        (filter === "failed" && !isPassed(ev))
    );
</script>

<div class="space-y-5 divide-y divide-gray-100">
    {#each filteredEvaluations as ev}
        {@const minScore = getMinScore(ev.criterion)}
        <div class="pt-4 first:pt-0 {includePrintStyles ? 'print:break-inside-avoid' : ''}">
            <div class="flex gap-3 items-start">
                <div class="flex-none pt-[2px]">
                    <ScoreCircle 
                        score={ev.score} 
                        minScore={minScore} 
                        showMinScore={minScore !== undefined && minScore < 1}
                        {includePrintStyles} 
                    />
                </div>
                <div class="text-sm font-medium flex-1 {minScore ? 'pb-7' : 'pb-1'}">
                    {#each ev.criterion
                        .replace(/\\n/g, '\n')
                        .replace(/\\(\s{1,2})\\ /g, ' ')
                        .split('\n') as line}
                        <div>{line}</div>
                    {/each}
                </div>
            </div>
            <div class="mt-1 text-sm text-gray-600">{ev.rationale}</div>
        </div>
    {/each}
</div> 