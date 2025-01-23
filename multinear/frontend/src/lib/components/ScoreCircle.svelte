<script lang="ts">
    import { getScoreStyles } from '$lib/utils/scores';

    export let score: number;
    export let minScore: number | undefined = undefined;
    export let includePrintStyles: boolean = false;
    export let showMinScore: boolean = true;

    $: normalizedScore = minScore ? (score / minScore) : score;
</script>

<div class="flex flex-col" style="min-height: 40px">
    <div class="h-9">
        <div class="flex-none flex items-center justify-center w-9 h-9 rounded-full border
            {getScoreStyles(normalizedScore, includePrintStyles).color}">
            <span class="text-xs font-medium leading-none">
                {(score * 100).toFixed(0)}%
            </span>
        </div>
    </div>
    {#if minScore && showMinScore}
        <div class="mt-1 -mr-2.5">
            <span class="text-[10px] font-medium {getScoreStyles(score, includePrintStyles).text}">
                min: {(minScore * 100).toFixed(0)}%
            </span>
        </div>
    {/if}
</div> 