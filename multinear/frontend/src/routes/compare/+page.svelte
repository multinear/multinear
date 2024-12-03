<script lang="ts">
    import { goto } from '$app/navigation';
    import { formatDuration, intervalToDuration } from 'date-fns';

    import * as Card from "$lib/components/ui/card";
    import * as Table from "$lib/components/ui/table";
    import { Label } from "$lib/components/ui/label";
    import { Input } from "$lib/components/ui/input";
    import { Checkbox } from "$lib/components/ui/checkbox";
    import TimeAgo from '$lib/components/TimeAgo.svelte';
    import StatusFilter from '$lib/components/StatusFilter.svelte';
    import StatusBadge from '$lib/components/StatusBadge.svelte';
    import ErrorDisplay from '$lib/components/ErrorDisplay.svelte';
    import DiffOutput from '$lib/components/DiffOutput.svelte';

    import { filterTasks, getStatusCounts, getTaskStatus } from '$lib/utils/tasks';
    import { getSameTasks } from '$lib/api';
    import { selectedProjectId, selectedChallengeId } from '$lib/stores/projects';


    let loading = true;
    let error: string | null = null;
    let tasks: any[] = [];

    async function loadTasks() {
        if (!$selectedProjectId || !$selectedChallengeId) return;
        
        loading = true;
        error = null;
        try {
            tasks = await getSameTasks($selectedProjectId, $selectedChallengeId);
        } catch (e) {
            error = e instanceof Error ? e.message : "Failed to load tasks";
        } finally {
            loading = false;
        }
    }

    // Watch for changes in project ID or challenge ID
    $: {
        if ($selectedProjectId && $selectedChallengeId) {
            loadTasks();
        }
    }

    let statusFilter = "";
    let searchTerm = "";
    let selectedTasks: Set<string> = new Set();
    let selectedFilter = false;

    // Watch for changes in selectedTasks
    $: {
        // When exactly 2 tasks are selected, switch to selected filter
        if (selectedTasks.size === 2) {
            selectedFilter = true;
            statusFilter = "";
        }
    }

    $: selectedTasksArray = Array.from(selectedTasks);
    $: isComparingTwo = selectedTasksArray.length === 2;
    $: comparisonTasks = isComparingTwo ? 
        tasks.filter(t => selectedTasks.has(t.id)) : [];

    $: filteredTasks = filterTasks(
        tasks, 
        statusFilter, 
        searchTerm,
        selectedFilter ? Array.from(selectedTasks) : null
    );
    $: statusCounts = getStatusCounts(tasks);
    
    // Assuming all tasks have the same input since they're from the same challenge
    $: commonInput = tasks?.[0]?.task_input;

    function getTaskOutput(task: any): string {
        return typeof task.task_output === 'object' && 'str' in task.task_output 
            ? task.task_output.str 
            : JSON.stringify(task.task_output, null, 2);
    }
</script>

<div class="container mx-auto p-4">
    <div class="flex justify-between items-center mb-4">
        <h1 class="text-3xl font-bold">Compare Tasks</h1>
    </div>

    {#if loading}
        <div class="text-center text-gray-500">Loading tasks...</div>
    {:else if error}
        <ErrorDisplay errorMessage={error} onRetry={loadTasks} />
    {:else if tasks.length}
        <div class="space-y-6">
            <!-- Common Input Card -->
            <Card.Root>
                <Card.Header>
                    <Card.Title>Common Input</Card.Title>
                    <Card.Description>
                        <div class="bg-white p-2 rounded border overflow-auto" style="white-space: pre-wrap;">
                            {typeof commonInput === 'object' && 'str' in commonInput 
                                ? commonInput.str 
                                : JSON.stringify(commonInput, null, 2)}
                        </div>
                    </Card.Description>
                </Card.Header>
            </Card.Root>

            <!-- Filters Card -->
            <Card.Root>
                <Card.Header>
                    <Card.Description>
                        <div class="grid grid-cols-2 gap-4">
                            <div class="space-y-1.5">
                                <Label for="search">Search</Label>
                                <Input
                                    id="search"
                                    placeholder="Search tasks..."
                                    bind:value={searchTerm}
                                />
                            </div>
                            
                            <StatusFilter 
                                bind:statusFilter
                                bind:selectedFilter
                                statusCounts={statusCounts}
                                totalCount={tasks.length}
                                selectedCount={selectedTasks.size}
                            />
                        </div>
                    </Card.Description>
                </Card.Header>
            </Card.Root>

            <!-- Tasks Table -->
            <Card.Root>
                <Card.Content>
                    <Table.Root>
                        <Table.Header>
                            <Table.Row>
                                <Table.Head class="w-[50px]">
                                    <Checkbox disabled={true}
                                        checked={selectedTasks.size === filteredTasks.length}
                                        onCheckedChange={(checked) => {
                                            if (checked) {
                                                selectedTasks = new Set(filteredTasks.map(t => t.id));
                                            } else {
                                                selectedTasks = new Set();
                                            }
                                        }}
                                    />
                                </Table.Head>
                                <Table.Head class="w-[50%]">Output</Table.Head>
                                <Table.Head>Details</Table.Head>
                            </Table.Row>
                        </Table.Header>
                        <Table.Body>
                            {#each filteredTasks as task}
                                {@const {isPassed, statusClass} = getTaskStatus(task)}
                                {@const isSelected = selectedTasks.has(task.id)}
                                <Table.Row 
                                    class={`${statusClass} ${selectedTasks.size === 2 && !isSelected ? 'opacity-50' : ''}`}
                                >
                                    <Table.Cell>
                                        <Checkbox 
                                            checked={isSelected}
                                            onCheckedChange={(checked) => {
                                                if (checked) {
                                                    selectedTasks.add(task.id);
                                                } else {
                                                    selectedTasks.delete(task.id);
                                                }
                                                selectedTasks = selectedTasks;
                                            }}
                                        />
                                    </Table.Cell>
                                    <Table.Cell>
                                        {#if isComparingTwo && isSelected}
                                            {@const otherTask = comparisonTasks.find(t => t.id !== task.id)}
                                            {#if otherTask}
                                                <DiffOutput 
                                                    text1={getTaskOutput(task)}
                                                    text2={getTaskOutput(otherTask)}
                                                />
                                            {/if}
                                        {:else}
                                            <div class="text-sm bg-white p-2 rounded border overflow-auto">
                                                {typeof task.task_output === 'object' && 'str' in task.task_output 
                                                    ? task.task_output.str 
                                                    : JSON.stringify(task.task_output, null, 2)}
                                            </div>
                                        {/if}
                                    </Table.Cell>
                                    <Table.Cell>
                                        <div class="grid grid-cols-[auto_1fr] gap-x-6 gap-y-2 items-center">
                                            <!-- Left column -->
                                            <div class="font-medium text-gray-500 text-sm">ID</div>
                                            <div class="font-mono text-sm">{task.id.slice(-8)}</div>

                                            <div class="font-medium text-gray-500 text-sm">Job</div>
                                            <div class="font-mono text-sm">
                                                <button
                                                    class="text-blue-600 hover:underline"
                                                    on:click={() => goto(`/experiments#${$selectedProjectId}/search:${task.job_id.slice(-8)}`)}
                                                >
                                                    {task.job_id.slice(-8)}
                                                </button>
                                            </div>

                                            <div class="font-medium text-gray-500 text-sm">Model</div>
                                            <div class="text-sm">{task.task_details.model}</div>

                                            <div class="font-medium text-gray-500 text-sm">Status</div>
                                            <div class="flex items-center gap-2">
                                                <StatusBadge status={task.status} />
                                                <div class="flex items-center gap-1">
                                                    <div class="w-16 bg-gray-200 rounded-sm h-2 overflow-hidden flex">
                                                        <div
                                                            class="h-2 min-w-[3px] {isPassed ? 'bg-green-600' : 'bg-red-600'}"
                                                            style="width: {(task.eval_score * 100).toFixed(0)}%"
                                                        ></div>
                                                    </div>
                                                    <div class="text-xs text-gray-600">
                                                        {(task.eval_score * 100).toFixed(0)}%
                                                    </div>
                                                </div>
                                            </div>

                                            <div class="font-medium text-gray-500 text-sm">Time</div>
                                            <div class="flex items-center gap-3 text-sm text-gray-600">
                                                <TimeAgo date={task.created_at} />
                                                {#if task.finished_at}
                                                    <span class="text-gray-400">·</span>
                                                    <span>{formatDuration(
                                                        intervalToDuration({
                                                            start: new Date(task.created_at),
                                                            end: new Date(task.finished_at)
                                                        }),
                                                        { format: ['minutes', 'seconds'] }
                                                    )}</span>
                                                {/if}
                                            </div>

                                            {#if task.task_details.temperature || task.task_details.max_tokens}
                                                <div class="font-medium text-gray-500 text-sm">Parameters</div>
                                                <div class="flex gap-3 text-sm text-gray-600">
                                                    {#if task.task_details.temperature}
                                                        <span>temperature: {task.task_details.temperature}</span>
                                                    {/if}
                                                    {#if task.task_details.max_tokens}
                                                        {#if task.task_details.temperature}
                                                            <span class="text-gray-400">·</span>
                                                        {/if}
                                                        <span>max tokens: {task.task_details.max_tokens}</span>
                                                    {/if}
                                                </div>
                                            {/if}
                                        </div>
                                    </Table.Cell>
                                </Table.Row>
                            {/each}
                        </Table.Body>
                    </Table.Root>
                </Card.Content>
            </Card.Root>
        </div>
    {:else}
        <div class="text-center text-gray-500">No tasks found</div>
    {/if}
</div>
