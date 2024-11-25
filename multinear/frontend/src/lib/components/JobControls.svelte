<script lang="ts">
    import { selectedProjectId } from '$lib/stores/projects';
    import { handleStartExperiment, jobStore } from '$lib/stores/jobs';
    import { Button } from '$lib/components/ui/button';
    import { Play } from 'lucide-svelte';
    import { Loader2 } from 'lucide-svelte';

    export let reloadRecentRuns: () => Promise<void>;
</script>

<div>
    {#if $jobStore.currentJob && $jobStore.jobStatus && !['completed', 'failed', 'error'].includes($jobStore.jobStatus)}
        <div class="flex items-center gap-2">
            <Loader2 class="h-4 w-4 animate-spin" />
            <span class="text-gray-500">{$jobStore.jobStatus}</span>
        </div>
    {:else}
        <Button variant="primary" on:click={() => handleStartExperiment($selectedProjectId, reloadRecentRuns)} class="flex items-center gap-2">
            <Play class="h-4 w-4" />
            Run Experiment
        </Button>
    {/if}
</div>
