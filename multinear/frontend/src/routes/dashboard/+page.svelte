<script lang="ts">
    import { Loader2 } from 'lucide-svelte';
    import * as Card from '$lib/components/ui/card';
    import { Button } from '$lib/components/ui/button';
    import { getRecentRuns } from '$lib/api';
    import type { RecentRun } from '$lib/api';
    import { projects, projectsLoading, projectsError, selectedProjectId } from '$lib/stores/projects';
    import RunsWithFilters from '$lib/components/RunsWithFilters.svelte';
    import JobStatus from '$lib/components/JobStatus.svelte';
    import JobControls from '$lib/components/JobControls.svelte';
    import KeyAlerts from '$lib/components/KeyAlerts.svelte';
    import type { KeyAlert } from '$lib/types/alerts';
    import ErrorDisplay from '$lib/components/ErrorDisplay.svelte';
    import { handleStartExperiment, jobStore, pollJobStatus, pendingRunStore, executePendingRun } from '$lib/stores/jobs';
    import { getJobStatus } from '$lib/api';
    // import EvalScoreTrend from '$lib/components/EvalScoreTrend.svelte';
    // import TestsDistributionTrend from '$lib/components/TestsDistributionTrend.svelte';


    $: currentProject = $projects.find(p => p.id === $selectedProjectId);

    const summaryStats = {
        totalRuns: 1250,
        avgEvalScore: 0.85,
        regressions: 15,
        securityIssues: 3,
    };

    let recentRuns: RecentRun[] = [];
    let recentRunsError: string | null = null;
    let recentRunsLoading = false;
    let totalRuns = 0;

    async function loadRecentRuns() {
        recentRunsLoading = true;
        recentRunsError = null;
        try {
            const response = await getRecentRuns($selectedProjectId);
            recentRuns = response.runs;
            totalRuns = response.total;
        } catch (error) {
            console.error('Error loading recent runs:', error);
            recentRunsError = error instanceof Error ? error.message : 'Unknown error';
        } finally {
            recentRunsLoading = false;
        }
    }

    async function startPollingIfRunning() {
        if ($jobStore.currentJob && $jobStore.jobStatus && !['completed', 'failed', 'error'].includes($jobStore.jobStatus)) {
            await pollJobStatus($selectedProjectId, $jobStore.currentJob, loadRecentRuns);
        }
    }

    async function handlePendingRun() {
        if ($pendingRunStore) {
            await executePendingRun(loadRecentRuns);
        }
    }

    $: if (currentProject) {
        loadRecentRuns();
        startPollingIfRunning();
        handlePendingRun();
    }

    const alerts: KeyAlert[] = [];

    // const lineChartData = {
    //     labels: [],
    //     datasets: [],
    // };
</script>

<div class="container mx-auto p-4 space-y-6">
    {#if $projectsLoading}
        <div class="flex items-center justify-center h-[50vh] text-gray-500">
            <div class="flex items-center gap-2">
                <Loader2 class="h-6 w-6 animate-spin" />
                <span>Loading project details...</span>
            </div>
        </div>
    {:else if $projectsError}
        <div class="flex items-center justify-center h-[50vh] text-gray-500">
            <ErrorDisplay errorMessage={`${$projectsError} - Check if API is running`} onRetry={() => window.location.reload()} className="w-96" />
        </div>
    {:else if !currentProject}
        <div class="flex items-center justify-center h-[50vh] text-gray-500">
            <Card.Root class="border-yellow-200 bg-yellow-50 w-96 space-y-4">
                <Card.Header>
                    <Card.Title class="text-yellow-800">Project Not Found</Card.Title>
                    <Card.Description class="text-yellow-600 pt-2">
                        The project "{$selectedProjectId}" could not be found.
                    </Card.Description>
                </Card.Header>
                <Card.Footer class="flex justify-end">
                    <Button 
                        variant="outline" 
                        class="border-yellow-200 text-yellow-800 hover:bg-yellow-100"
                        on:click={() => window.location.href = '/'}
                    >
                        Go Back
                    </Button>
                </Card.Footer>
            </Card.Root>
        </div>
    {:else}
        <div class="flex justify-between items-center">
            <h1 class="text-3xl font-bold -mb-2 -mt-2">{currentProject.name}</h1>
            <JobControls reloadRecentRuns={loadRecentRuns} />
        </div>

        <JobStatus />

        <!-- Summary Statistics -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card.Root>
                <Card.Content class="flex items-center justify-between py-4">
                    <span class="text-md font-medium">Total Runs</span>
                    <div class="text-2xl font-bold">{totalRuns}</div>
                </Card.Content>
            </Card.Root>
            <!-- <Card.Root>
                <Card.Content class="flex items-center justify-between py-4">
                    <span class="text-md font-medium">Regressions</span>
                    <div class="text-2xl font-bold text-yellow-600">
                        {summaryStats.regressions}
                    </div>
                </Card.Content>
            </Card.Root>
            <Card.Root>
                <Card.Content class="flex items-center justify-between py-4">
                    <span class="text-md font-medium">Security Issues</span>
                    <div class="text-2xl font-bold text-red-600">
                        {summaryStats.securityIssues}
                    </div>
                </Card.Content>
            </Card.Root> -->
        </div>

        <!-- List of Runs Component -->
        <RunsWithFilters
            runsList={recentRuns}
            isLoading={recentRunsLoading}
            loadingError={recentRunsError}
            showViewAll={true}
        />

        <!-- Key Alerts and Notifications -->
        <KeyAlerts {alerts} />

        <!-- Visualizations -->
        <!-- <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <EvalScoreTrend data={lineChartData} />
            <TestsDistributionTrend />
        </div> -->
    {/if}
</div>
