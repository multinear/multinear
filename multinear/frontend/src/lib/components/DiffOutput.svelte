<script lang="ts">
    import DiffMatchPatch from 'diff-match-patch';

    export let text1: string;
    export let text2: string;

    const dmp = new DiffMatchPatch();

    $: diffs = dmp.diff_main(text1, text2);
    $: {
        // Cleanup semantic differences
        dmp.diff_cleanupSemantic(diffs);
    }
</script>

<div class="text-sm bg-white p-2 rounded border overflow-auto">
    {#each diffs as [type, text]}
        {#if type === 0}
            <span>{text}</span>
        {:else if type === 1}
            <span class="bg-green-100 text-green-900">{text}</span>
        {:else}
            <span class="bg-red-100 text-red-900">{text}</span>
        {/if}
    {/each}
</div> 