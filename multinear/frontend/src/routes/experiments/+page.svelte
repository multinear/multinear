<script lang="ts">
    // import * as Card from "$lib/components/ui/card";
    // import { Button } from "$lib/components/ui/button";
    import { goto } from '$app/navigation';
    import { getRecentRuns } from '$lib/api';
    import type { RecentRun } from '$lib/api';
    import { selectedProjectId } from '$lib/stores/projects';
    import RunsWithFilters from '$lib/components/RunsWithFilters.svelte';
    import { searchTerm } from '$lib/stores/projects';

    let runs: RecentRun[] = [];
    let loading = true;
    let error: string | null = null;

    // Bind the search input to the store
    let localSearchTerm = '';
    
    // When the store changes (from URL), update local search
    $: {
        if ($searchTerm) {
            localSearchTerm = $searchTerm;
        }
    }

    async function loadData() {
        loading = true;
        error = null;
        try {
            const response = await getRecentRuns($selectedProjectId, 100, 0);
            runs = response.runs;
            // totalRuns = response.total;
        } catch (e) {
            error = e instanceof Error ? e.message : "Failed to load runs";
            console.error(e);
        } finally {
            loading = false;
        }
    }

    // Reactive statement to load data when selectedProjectId changes
    $: if ($selectedProjectId) {
        loadData();
    }

    function handleRunSelect(runId: string) {
        goto(`/run#${$selectedProjectId}/r:${runId}`);
    }
</script>

<div class="container mx-auto p-4 space-y-6">
    <h1 class="text-3xl font-bold">Experiments</h1>

    <!-- List of Runs Component -->
    <RunsWithFilters
        runsList={runs}
        isLoading={loading}
        loadingError={error}
        showViewAll={false}
        showFilters={true}
        initialSearchTerm={localSearchTerm}
    />

</div>
