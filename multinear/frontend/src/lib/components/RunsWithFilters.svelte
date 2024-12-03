<script lang="ts">
    import { 
        Loader2,
        AlertCircle,
        // Bookmark,
        X,
    } from "lucide-svelte";
    import { goto } from '$app/navigation';

    import * as Card from "$lib/components/ui/card";
    import * as Table from "$lib/components/ui/table";
    import * as Alert from "$lib/components/ui/alert";
    import { Badge } from "$lib/components/ui/badge";
    // import { Button } from "$lib/components/ui/button";
    import { Input } from "$lib/components/ui/input";
    import { Label } from "$lib/components/ui/label";
    import * as Select from "$lib/components/ui/select";
    import * as Tooltip from "$lib/components/ui/tooltip";
    import type { RecentRun } from "$lib/api";
    import { selectedProjectId } from "$lib/stores/projects";
    import TimeAgo from "$lib/components/TimeAgo.svelte";
    import { formatDuration, intervalToDuration } from 'date-fns';
    import Loading from '$lib/components/Loading.svelte';
    import ErrorDisplay from '$lib/components/ErrorDisplay.svelte';

    // Props passed from the parent component
    export let runsList: RecentRun[];
    export let isLoading: boolean;
    export let loadingError: string | null;
    export let showFilters: boolean = false;
    export let showViewAll: boolean = false;
    export let initialSearchTerm: string = "";

    $: modelVersions = ["", ...new Set(runsList.map(run => run.model))];
    $: codeRevisions = ["", ...new Set(runsList.map(run => run.revision))];

    const dateRanges = ["", ...["Today", "This Week", "This Month", "Custom Range"]];
    const testGroups = ["", "Security Tests", "Performance Tests", "Functionality Tests"];

    // Define types for select items
    type SelectItem = { value: string; label: string };

    // State for selected values
    let selectedDateRange: SelectItem = { value: '', label: ''};
    let selectedModelVersion: SelectItem = { value: '', label: ''};
    let selectedCodeRevision: SelectItem = { value: '', label: ''};
    let selectedTestGroup: SelectItem = { value: '', label: ''};
    let searchTerm: string = initialSearchTerm;

    // Watch for changes in initialSearchTerm
    $: {
        if (initialSearchTerm) {
            searchTerm = initialSearchTerm;
        }
    }

    // Add filtered runs reactive statement
    $: filteredRuns = runsList.filter(run => {
        // Date range filter
        if (selectedDateRange?.value) {
            const runDate = new Date(run.created_at);
            const today = new Date();
            switch (selectedDateRange.value) {
                case "today":
                    if (runDate.toDateString() !== today.toDateString()) return false;
                    break;
                case "this week":
                    const weekAgo = new Date(today.setDate(today.getDate() - 7));
                    if (runDate < weekAgo) return false;
                    break;
                case "this month":
                    const monthAgo = new Date(today.setMonth(today.getMonth() - 1));
                    if (runDate < monthAgo) return false;
                    break;
            }
        }

        // Model version filter
        if (selectedModelVersion?.value && run.model !== selectedModelVersion.value) return false;

        // Code revision filter
        if (selectedCodeRevision?.value && run.revision !== selectedCodeRevision.value) return false;

        // Test group filter
        if (selectedTestGroup?.value && selectedTestGroup.value !== "all-tests") {
            // Implement test group filtering logic
        }

        // Search term filter
        if (searchTerm) {
            const searchLower = searchTerm.toLowerCase();
            return (
                run.id.toLowerCase().includes(searchLower) ||
                run.model.toLowerCase().includes(searchLower) ||
                run.revision.toLowerCase().includes(searchLower)
            );
        }

        return true;
    });

    function handleRunSelect(runId: string) {
        goto(`/run#${$selectedProjectId}/r:${runId}`);
    }

</script>

<!-- Filters and Controls -->
{#if showFilters}
    <Card.Root>
        <!-- <Card.Header>
            <Card.Title>Filters and Search</Card.Title>
        </Card.Header> -->
        <Card.Content class="flex flex-wrap gap-4">
            <!-- Date Range Filter -->
            <div class="flex flex-col space-y-1.5">
                <Label for="date-range">Date Range</Label>
                <Select.Root
                    selected={selectedDateRange}
                    onSelectedChange={(v) => { 
                        if (v) selectedDateRange = {value: v.value, label: v.label!};
                        else selectedDateRange = { value: '', label: ''};
                    }}
                >
                    <Select.Trigger class="w-[180px]" id="date-range">
                        <Select.Value placeholder="Select date range" />
                    </Select.Trigger>
                    <Select.Content>
                        <Select.Group>
                            {#each dateRanges as range}
                                <Select.Item 
                                    value={range.toLowerCase()} 
                                    label={range}
                                    class="min-h-[32px]"
                                >
                                    {range}
                                </Select.Item>
                            {/each}
                        </Select.Group>
                    </Select.Content>
                </Select.Root>
            </div>
            
            <!-- Model Version Filter -->
            <div class="flex flex-col space-y-1.5">
                <Label for="model-version">Model Version</Label>
                <Select.Root
                    selected={selectedModelVersion}
                    onSelectedChange={(v) => { 
                        if (v) selectedModelVersion = {value: v.value, label: v.label!};
                        else selectedModelVersion = { value: '', label: ''};
                    }}
                >
                    <Select.Trigger class="w-[180px]" id="model-version">
                        <Select.Value placeholder="Select model version" />
                    </Select.Trigger>
                    <Select.Content>
                        <Select.Group>
                            {#each modelVersions as version}
                                <Select.Item 
                                    value={version} 
                                    label={version}
                                    class="min-h-[32px]"
                                >
                                    {version}
                                </Select.Item>
                            {/each}
                        </Select.Group>
                    </Select.Content>
                </Select.Root>
            </div>
            
            <!-- Code Revision Filter -->
            <div class="flex flex-col space-y-1.5">
                <Label for="code-revision">Code Revision</Label>
                <Select.Root
                    selected={selectedCodeRevision}
                    onSelectedChange={(v) => { 
                        if (v) selectedCodeRevision = {value: v.value, label: v.label!};
                        else selectedCodeRevision = { value: '', label: ''};
                    }}
                >
                    <Select.Trigger class="w-[180px]" id="code-revision">
                        <Select.Value placeholder="Select code revision" />
                    </Select.Trigger>
                    <Select.Content>
                        <Select.Group>
                            {#each codeRevisions as revision}
                                <Select.Item 
                                    value={revision} 
                                    label={revision}
                                    class="min-h-[32px]"
                                >
                                    {revision}
                                </Select.Item>
                            {/each}
                        </Select.Group>
                    </Select.Content>
                </Select.Root>
            </div>
            
            <!-- Test Group Filter -->
            <!-- <div class="flex flex-col space-y-1.5">
                <Label for="test-group">Test Group</Label>
                <Select.Root
                    selected={selectedTestGroup}
                    onSelectedChange={(v) => { 
                        if (v) selectedTestGroup = {value: v.value, label: v.label!};
                        else selectedTestGroup = { value: '', label: ''};
                    }}
                >
                    <Select.Trigger class="w-[180px]" id="test-group">
                        <Select.Value placeholder="Select test group" />
                    </Select.Trigger>
                    <Select.Content>
                        <Select.Group>
                            {#each testGroups as group}
                                <Select.Item 
                                    value={group.toLowerCase().replace(' ', '-')}
                                    label={group}
                                    class="min-h-[32px]"
                                >
                                    {group}
                                </Select.Item>
                            {/each}
                        </Select.Group>
                    </Select.Content>
                </Select.Root>
            </div> -->
            
            <!-- Search Input -->
            <div class="flex flex-col space-y-1.5 flex-grow">
                <Label for="search">Search</Label>
                <div class="relative">
                    <Input
                        id="search"
                        placeholder="Search by Run ID, name, or metadata"
                        bind:value={searchTerm}
                    />
                    {#if searchTerm}
                        <button
                            type="button"
                            class="absolute right-2 top-1/2 -translate-y-1/2 p-1 rounded-full bg-gray-100 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
                            on:click={() => searchTerm = ""}
                        >
                            <X class="h-4 w-4 text-gray-500" />
                        </button>
                    {/if}
                </div>
            </div>
        </Card.Content>
    </Card.Root>
{/if}

<!-- Recent Runs -->
<Card.Root>
    {#if isLoading}
        <Loading message="Loading recent runs..." />
    {:else if loadingError}
        <ErrorDisplay errorMessage={loadingError} onRetry={() => {/* Define retry logic if applicable */}} />
    {:else}
        <Table.Root>
            {#if showViewAll}
                <Table.Caption>
                    <a href="/experiments#{$selectedProjectId}">View all runs</a>
                </Table.Caption>
            {/if}
            <Table.Header>
                <Table.Row>
                    <Table.Head>Run ID</Table.Head>
                    <Table.Head>Date & Time</Table.Head>
                    <Table.Head>Duration</Table.Head>
                    <Table.Head>Code Revision</Table.Head>
                    <Table.Head>Model Version</Table.Head>
                    <Table.Head>Total Tests</Table.Head>
                    <Table.Head>Evaluation Score</Table.Head>
                    <Table.Head>Test Results</Table.Head>
                    <!-- <Table.Head>Actions</Table.Head> -->
                </Table.Row>
            </Table.Header>
            <Table.Body>
                {#each filteredRuns as run}
                    <Table.Row class="group cursor-pointer" on:click={() => handleRunSelect(run.id)}>
                        <Table.Cell class="font-medium">
                            <Tooltip.Root>
                                <Tooltip.Trigger>{run.id.slice(-8)}</Tooltip.Trigger>
                                <Tooltip.Content>
                                    <p>Run ID: {run.id}</p>
                                </Tooltip.Content>
                            </Tooltip.Root>
                        </Table.Cell>
                        <Table.Cell>
                            <TimeAgo date={run.created_at} />
                        </Table.Cell>
                        <Table.Cell>
                            {#if run.finished_at}
                                {formatDuration(
                                    intervalToDuration({
                                        start: new Date(run.created_at),
                                        end: new Date(run.finished_at)
                                    }),
                                    { format: ['minutes', 'seconds'] }
                                )}
                            {:else}
                                -
                            {/if}
                        </Table.Cell>
                        <Table.Cell>{run.revision.slice(-8)}</Table.Cell>
                        <Table.Cell>{run.model}</Table.Cell>
                        <Table.Cell>{run.totalTests}</Table.Cell>
                        <Table.Cell>
                            <Badge
                                variant={run.score >= 0.9
                                    ? "success"
                                    : run.score >= 0.7
                                        ? "warning"
                                        : "destructive"}
                            >
                                {run.score.toFixed(2)}
                            </Badge>
                        </Table.Cell>
                        <Table.Cell class="w-[300px]">
                            <Tooltip.Root>
                                <Tooltip.Trigger class="w-full">
                                    <div
                                        class="w-full bg-gray-200 rounded-sm h-4 dark:bg-gray-700 overflow-hidden flex"
                                    >
                                        {#if run.pass > 0}
                                            <div
                                                class="bg-green-600 h-4 min-w-[5px]"
                                                style="width: {(run.pass / run.totalTests) * 100}%"
                                            ></div>
                                        {/if}
                                        {#if run.fail > 0}
                                            <div
                                                class="bg-red-600 h-4 min-w-[5px]"
                                                style="width: {(run.fail / run.totalTests) * 100}%"
                                            ></div>
                                        {/if}
                                        {#if run.regression > 0}
                                            <div
                                                class="bg-yellow-400 h-4 min-w-[5px]"
                                                style="width: {(run.regression / run.totalTests) * 100}%"
                                            ></div>
                                        {/if}
                                    </div>
                                </Tooltip.Trigger>
                                <Tooltip.Content>
                                    <div class="space-y-1">
                                        <div class="flex items-center gap-2">
                                            <div class="w-3 h-3 bg-green-600 rounded-full"></div>
                                            <span>Pass: {run.pass} <span class="text-gray-400">({((run.pass / run.totalTests) * 100).toFixed(1)}%)</span></span>
                                        </div>
                                        <div class="flex items-center gap-2">
                                            <div class="w-3 h-3 bg-red-600 rounded-full"></div>
                                            <span>Fail: {run.fail} <span class="text-gray-400">({((run.fail / run.totalTests) * 100).toFixed(1)}%)</span></span>
                                        </div>
                                        {#if run.regression > 0}
                                            <div class="flex items-center gap-2">
                                                <div class="w-3 h-3 bg-yellow-400 rounded-full"></div>
                                                <span>Regression: {run.regression} <span class="text-gray-400">({((run.regression / run.totalTests) * 100).toFixed(1)}%)</span></span>
                                            </div>
                                        {/if}
                                        <div class="pt-1 border-t">
                                            <span>Total: {run.totalTests}</span>
                                        </div>
                                    </div>
                                </Tooltip.Content>
                            </Tooltip.Root>
                        </Table.Cell>
                        <!-- 
                        <Table.Cell>
                            <div
                                class="flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity"
                            >
                                {#if run.bookmarked}
                                    <Bookmark
                                        class="h-4 w-4 text-blue-500"
                                    />
                                {:else if run.noted}
                                    <FileEdit
                                        class="h-4 w-4 text-green-500"
                                    />
                                {:else}
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        class="h-8 w-8 p-0"
                                    >
                                        <Bookmark class="h-4 w-4" />
                                    </Button>
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        class="h-8 w-8 p-0"
                                    >
                                        <FileEdit class="h-4 w-4" />
                                    </Button>
                                {/if}
                            </div>
                        </Table.Cell> 
                        -->
                    </Table.Row>
                {/each}
            </Table.Body>
        </Table.Root>
    {/if}
</Card.Root>
