<script lang="ts">
    import TimeAgo from '$lib/components/TimeAgo.svelte';
    import { Button } from "$lib/components/ui/button";

    export let runDetails: any;
    export let showExportButton: boolean = true;
</script>

{#if runDetails}
    <div class="flex justify-between items-center mb-4">
        <div class="flex gap-12 items-center">
            <h1 class="text-3xl font-bold">Run: {runDetails.id.slice(-8)}</h1>
            {#if runDetails}
                <span class="text-xl text-gray-500">
                    <TimeAgo date={runDetails.date} />
                </span>
            {/if}
        </div>
        {#if showExportButton}
            <div class="flex gap-4 items-center">
                <div class="flex gap-2 items-center">
                    <span class="text-sm text-gray-500">Project</span>
                    <span class="text-md text-gray-800">{runDetails.project.name}</span>
                </div>
                <Button
                    variant="outline"
                    class="text-sm"
                    on:click={() => {
                        const url = `/export/run#${runDetails.project.id}/${runDetails.id}`;
                        window.open(url, '_blank');
                    }}
                >
                    Export
                </Button>
            </div>
        {:else}
            <div class="flex gap-2 items-center">
                <span class="text-sm text-gray-500">Project</span>
                <span class="text-md text-gray-800">{runDetails.project.name}</span>
            </div>
        {/if}
    </div>
{/if}
