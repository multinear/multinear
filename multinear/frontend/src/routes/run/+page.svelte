<script lang="ts">
    import * as Card from "$lib/components/ui/card";
    import { Button } from "$lib/components/ui/button";
    import { getRunDetails } from '$lib/api';
    import { selectedRunId } from '$lib/stores/projects';
    import * as Table from "$lib/components/ui/table";
    import { Label } from "$lib/components/ui/label";
    import { Input } from "$lib/components/ui/input";
    import { formatDuration, intervalToDuration } from 'date-fns';
    import { ChevronRight } from 'lucide-svelte';
    import TimeAgo from '$lib/components/TimeAgo.svelte';
    import StatusFilter from '$lib/components/StatusFilter.svelte';
    import { filterTasks, getStatusCounts, getTaskStatus, truncateInput } from '$lib/utils/tasks';
    import { goto } from '$app/navigation';
    import { tick } from 'svelte';

    let runId: string | null = null;
    let runDetails: any = null;
    let loading = true;
    let error: string | null = null;
    let expandedTaskId: string | null = null;

    $: {
        if ($selectedRunId) loadRunDetails($selectedRunId);
    }

    async function loadRunDetails(id: string) {
        loading = true;
        error = null;
        try {
            runDetails = await getRunDetails(id);
        } catch (e) {
            error = e instanceof Error ? e.message : "Failed to load run details";
            console.error(e);
        } finally {
            loading = false;
        }
    }

    let statusFilter = "";
    let searchTerm = "";
    
    $: filteredTasks = filterTasks(runDetails?.tasks || [], statusFilter, searchTerm);
    $: statusCounts = getStatusCounts(runDetails?.tasks || []);

    async function scrollToExpandedTask() {
        if (!expandedTaskId) return;
        
        // Wait for the DOM to update
        await tick();

        // Find the expanded row element
        const expandedRow = document.querySelector(`[data-task-id="${expandedTaskId}"]`);
        if (expandedRow) {
            expandedRow.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start'
            });
        }
    }

    async function expandNextTask() {
        if (!filteredTasks.length) return;
        
        const currentIndex = expandedTaskId 
            ? filteredTasks.findIndex(t => t.id === expandedTaskId)
            : -1;
        
        const nextIndex = currentIndex < filteredTasks.length - 1 
            ? currentIndex + 1 
            : 0;
            
        expandedTaskId = filteredTasks[nextIndex].id;
        await scrollToExpandedTask();
    }

    async function expandPreviousTask() {
        if (!filteredTasks.length) return;
        
        const currentIndex = expandedTaskId 
            ? filteredTasks.findIndex(t => t.id === expandedTaskId)
            : 0;
        
        const previousIndex = currentIndex > 0 
            ? currentIndex - 1 
            : filteredTasks.length - 1;
            
        expandedTaskId = filteredTasks[previousIndex].id;
        await scrollToExpandedTask();
    }

    function handleKeydown(event: KeyboardEvent) {
        if (event.target instanceof HTMLInputElement || 
            event.target instanceof HTMLTextAreaElement) {
            return;
        }

        if (event.key === 'j') {
            expandNextTask();
        } else if (event.key === 'k') {
            expandPreviousTask();
        }
    }
</script>

<svelte:window on:keydown={handleKeydown} />

<div class="container mx-auto p-4">
    <div class="flex justify-between items-center mb-4">
        <div class="flex gap-12 items-center">
            <h1 class="text-3xl font-bold">Run: {$selectedRunId.slice(-8)}</h1>
            {#if runDetails}
                <span class="text-xl text-gray-500">
                    <TimeAgo date={runDetails.date} />
                </span>
            {/if}
        </div>
        {#if runDetails}
            <div class="flex gap-2 items-center">
                <span class="text-sm text-gray-500">Project</span>
                <span class="text-md text-gray-800">{runDetails.project.name}</span>
            </div>
        {/if}
    </div>

    {#if loading}
        <div class="text-center text-gray-500">Loading run details...</div>
    {:else if error}
        <Card.Root class="border-red-200 bg-red-50">
            <Card.Header>
                <Card.Title class="text-red-800">Error</Card.Title>
                <Card.Description class="text-red-600">
                    {error}
                </Card.Description>
            </Card.Header>
            <Card.Footer class="flex justify-end">
                <Button 
                    variant="outline" 
                    class="border-red-200 text-red-800 hover:bg-red-100"
                    on:click={() => loadRunDetails(runId!)}
                >
                    Try Again
                </Button>
            </Card.Footer>
        </Card.Root>
    {:else if runDetails}
        <div class="space-y-6">
            <!-- Summary Card -->
            <Card.Root class="pb-4">
                <Card.Header>
                    <Card.Description>
                        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div class="space-y-1">
                                <div class="text-sm text-gray-500">Status</div>
                                <div class="font-semibold">{runDetails.status}</div>
                            </div>
                            <!-- <div class="space-y-1">
                                <div class="text-sm text-gray-500">Project</div>
                                <div class="font-semibold">{runDetails.project.name}</div>
                            </div> -->
                            <div class="space-y-1">
                                <div class="text-sm text-gray-500">Total Tasks</div>
                                <div class="font-semibold">{runDetails.tasks.length}</div>
                            </div>
                            <div class="space-y-1">
                                <div class="text-sm text-gray-500">Model</div>
                                <div class="font-semibold">{runDetails.details.model || 'N/A'}</div>
                            </div>

                            <div class="space-y-1">
                                <Label for="search">Search</Label>
                                <Input
                                    id="search"
                                    placeholder="Search tasks..."
                                    bind:value={searchTerm}
                                />
                            </div>
                        </div>
                        
                        <!-- Filters Row -->
                        <div class="flex gap-8 items-end mt-4">
                            {#if runDetails.tasks.length >= 5}
                                <StatusFilter 
                                    bind:statusFilter
                                    statusCounts={statusCounts}
                                    totalCount={runDetails.tasks.length}
                                />
                            {/if}
                        </div>
                    </Card.Description>
                </Card.Header>
            </Card.Root>

            <!-- Tasks Table -->
            <Card.Root>
                <!-- <Card.Header>
                    <Card.Title>Tasks</Card.Title>
                </Card.Header> -->
                <Card.Content>
                    <Table.Root class="-mt-4">
                        <Table.Header>
                            <Table.Row>
                                <Table.Head></Table.Head>
                                <Table.Head>Task ID</Table.Head>
                                <Table.Head>Started</Table.Head>
                                <Table.Head>Duration</Table.Head>
                                <Table.Head>Model</Table.Head>
                                <Table.Head>Input</Table.Head>
                                <Table.Head>Status</Table.Head>
                                <Table.Head>Score</Table.Head>
                            </Table.Row>
                        </Table.Header>
                        <Table.Body>
                            {#each filteredTasks as task}
                                {@const isExpanded = expandedTaskId === task.id}
                                {@const {isPassed, statusClass} = getTaskStatus(task)}
                                <Table.Row 
                                    data-task-id={task.id}
                                    class={`cursor-pointer ${statusClass}`}
                                    on:click={() => {
                                        expandedTaskId = isExpanded ? null : task.id;
                                        if (isExpanded) scrollToExpandedTask();
                                    }}
                                >
                                    <Table.Cell class="w-4">
                                        <Button variant="ghost" size="sm" class="h-4 w-4 p-0">
                                            <ChevronRight 
                                                class="h-4 w-4 transition-transform duration-200 text-gray-400
                                                {isExpanded ? 'rotate-90' : ''}"
                                            />
                                        </Button>
                                    </Table.Cell>
                                    <Table.Cell class="font-medium font-mono">
                                        {task.id.slice(-8)}
                                    </Table.Cell>
                                    <Table.Cell>
                                        <TimeAgo date={task.created_at} />
                                    </Table.Cell>
                                    <Table.Cell>
                                        {#if task.finished_at}
                                            {formatDuration(
                                                intervalToDuration({
                                                    start: new Date(task.created_at),
                                                    end: new Date(task.finished_at)
                                                }),
                                                { format: ['minutes', 'seconds'] }
                                            )}
                                        {:else}
                                            -
                                        {/if}
                                    </Table.Cell>
                                    <Table.Cell>
                                        {task.task_details?.model || '-'}
                                    </Table.Cell>
                                    <Table.Cell class="max-w-xs">
                                        {truncateInput(task.task_input)}
                                    </Table.Cell>
                                    <Table.Cell>
                                        <span class={`inline-flex items-center px-2.5 py-0.5 rounded-full text-sm font-medium
                                            ${task.status === 'completed' ? 'bg-green-100 text-green-800' : 
                                            task.status === 'failed' ? 'bg-red-100 text-red-800' : 
                                            'bg-gray-100 text-gray-800'}`}>
                                            {task.status}
                                        </span>
                                    </Table.Cell>
                                    <Table.Cell>
                                        <div class="w-full bg-gray-200 rounded-sm h-4 dark:bg-gray-700 overflow-hidden flex">
                                            <div
                                                class="h-4 min-w-[5px] {isPassed ? 'bg-green-600' : 'bg-red-600'}"
                                                style="width: {(task.eval_score * 100).toFixed(0)}%"
                                            ></div>
                                        </div>
                                        <div class="text-center text-xs font-medium">
                                            {(task.eval_score * 100).toFixed(0)}%
                                        </div>
                                    </Table.Cell>
                                </Table.Row>
                                {#if isExpanded}
                                    <Table.Row class="bg-gray-50 hover:bg-gray-50">
                                        <Table.Cell colspan={8} class="border-t border-gray-100">
                                            <div class="p-4 grid grid-cols-1 md:grid-cols-2 gap-6">
                                                <!-- Task Details Column -->
                                                <div class="space-y-4 pr-12 border-r border-gray-200">
                                                    <div class="flex justify-between items-center mb-2">
                                                        <h4 class="font-semibold text-lg">Task</h4>
                                                        <div class="text-sm text-gray-800">
                                                            Duration: 
                                                            {#if task.executed_at}
                                                                {formatDuration(
                                                                    intervalToDuration({
                                                                        start: new Date(task.created_at),
                                                                        end: new Date(task.executed_at)
                                                                    }),
                                                                    { format: ['minutes', 'seconds'] }
                                                                )}
                                                            {:else}
                                                                -
                                                            {/if}
                                                        </div>
                                                    </div>
                                                    {#if task.task_input}
                                                        <div>
                                                            <h5 class="font-semibold mb-1">Input</h5>
                                                            <div class="text-sm bg-white p-2 rounded border overflow-auto" style="white-space: pre-wrap;">
                                                                {typeof task.task_input === 'object' && 'str' in task.task_input 
                                                                    ? task.task_input.str 
                                                                    : JSON.stringify(task.task_input, null, 2)}
                                                            </div>
                                                        </div>
                                                    {/if}
                                                    {#if task.task_output}
                                                        <div>
                                                            <div class="flex justify-between items-center mb-1">
                                                                <h5 class="font-semibold">Output</h5>
                                                                <Button 
                                                                    variant="outline" 
                                                                    size="sm"
                                                                    class="text-sm bg-gray-200 hover:bg-gray-300 dark:hover:bg-gray-700 transition-colors"
                                                                    on:click={() => {
                                                                        const projectId = runDetails.project.id;
                                                                        const challengeId = task.challenge_id;
                                                                        goto(`/compare#${projectId}/c:${challengeId}`);
                                                                    }}
                                                                >
                                                                    Cross-Compare
                                                                </Button>
                                                            </div>
                                                            <div class="text-sm bg-white p-2 rounded border overflow-auto" style="white-space: pre-wrap;">
                                                                {typeof task.task_output === 'object' && 'str' in task.task_output 
                                                                    ? task.task_output.str 
                                                                    : JSON.stringify(task.task_output, null, 2)}
                                                            </div>
                                                        </div>
                                                    {/if}
                                                    {#if task.task_details}
                                                        <div>
                                                            <h5 class="font-semibold mb-1">Details</h5>
                                                            {#each Object.entries(task.task_details) as [key, value]}
                                                                <div class="mb-1 pl-2">
                                                                    <h6 class="font-semibold">{key}</h6>
                                                                    <div class="text-sm bg-white p-2 rounded border overflow-auto" style="white-space: pre-wrap;">
                                                                        {typeof value === 'string' ? value : JSON.stringify(value, null, 2)}
                                                                    </div>
                                                                </div>
                                                            {/each}
                                                        </div>
                                                    {/if}
                                                    {#if task.task_logs}
                                                        <div>
                                                            <h5 class="font-semibold mb-1">Logs</h5>
                                                            <details>
                                                                <summary class="cursor-pointer text-blue-500">Show Logs</summary>
                                                                <table class="text-sm bg-white p-2 rounded border overflow-auto w-full mt-2">
                                                                    <thead>
                                                                        <tr>
                                                                            <th class="text-left">Level</th>
                                                                            <th class="text-left">Timestamp</th>
                                                                            <th class="text-left">Message</th>
                                                                        </tr>
                                                                    </thead>
                                                                    <tbody>
                                                                        {#each task.task_logs.logs as log}
                                                                            <tr>
                                                                                <td>{log.level}</td>
                                                                                <td>{new Date(log.timestamp * 1000).toLocaleString()}</td>
                                                                                <td>{log.message}</td>
                                                                            </tr>
                                                                        {/each}
                                                                    </tbody>
                                                                </table>
                                                            </details>
                                                        </div>
                                                    {/if}
                                                </div>

                                                <!-- Evaluation Details Column -->
                                                <div class="space-y-4 pl-4">
                                                    <div class="flex justify-between items-center mb-2">
                                                        <h4 class="font-semibold text-lg">Evaluation</h4>
                                                        <div class="flex items-center gap-4">
                                                            <div class="text-sm text-gray-800">
                                                                Duration: 
                                                                {#if task.evaluated_at}
                                                                    {formatDuration(
                                                                        intervalToDuration({
                                                                            start: new Date(task.executed_at),
                                                                            end: new Date(task.evaluated_at)
                                                                        }),
                                                                        { format: ['minutes', 'seconds'] }
                                                                    )}
                                                                {:else}
                                                                    -
                                                                {/if}
                                                            </div>
                                                            <div class="text-sm text-gray-800">
                                                                Score: {(task.eval_score * 100).toFixed(0)}%
                                                            </div>
                                                            <div class={`px-4 py-1 rounded-lg font-semibold
                                                                ${task.eval_passed ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                                                {task.eval_passed ? 'PASSED' : 'FAILED'}
                                                            </div>
                                                        </div>
                                                    </div>
                                                    
                                                    {#if task.eval_details?.evaluations}
                                                        <div>
                                                            <!-- <h5 class="font-semibold mb-2">Evaluation Criteria</h5> -->
                                                            <Table.Root>
                                                                <Table.Header>
                                                                    <Table.Row>
                                                                        <Table.Head>Criteria</Table.Head>
                                                                        <Table.Head class="w-24 text-center">Score</Table.Head>
                                                                    </Table.Row>
                                                                </Table.Header>
                                                                <Table.Body>
                                                                    {#each task.eval_details.evaluations as ev}
                                                                        <Table.Row>
                                                                            <Table.Cell>
                                                                                <div class="space-y-1">
                                                                                    <div>{ev.criterion}</div>
                                                                                    <div class="text-sm text-gray-500">{ev.rationale}</div>
                                                                                </div>
                                                                            </Table.Cell>
                                                                            <Table.Cell class="text-center">
                                                                                <div class="inline-flex items-center justify-center w-12 h-12 rounded-full 
                                                                                    {ev.score >= 1 ? 'bg-green-100 text-green-800' : 
                                                                                     ev.score > 0 ? 'bg-yellow-100 text-yellow-800' : 
                                                                                     'bg-red-100 text-red-800'}">
                                                                                    {(ev.score * 100).toFixed(0)}%
                                                                                </div>
                                                                            </Table.Cell>
                                                                        </Table.Row>
                                                                    {/each}
                                                                </Table.Body>
                                                            </Table.Root>
                                                        </div>
                                                    {/if}

                                                    {#if task.eval_details}
                                                        <div>
                                                            <h5 class="font-semibold mb-1">Details</h5>
                                                            {#each Object.entries(task.eval_details) as [key, value]}
                                                                {#if key !== 'evaluations'}
                                                                    <div class="mb-1 pl-2">
                                                                        <h6 class="font-semibold">{key}</h6>
                                                                        <div class="text-sm bg-white p-2 rounded border overflow-auto" style="white-space: pre-wrap;">
                                                                            {typeof value === 'string' ? value : JSON.stringify(value, null, 2)}
                                                                        </div>
                                                                    </div>
                                                                {/if}
                                                            {/each}
                                                        </div>
                                                    {/if}
                                                </div>
                                            </div>
                                        </Table.Cell>
                                    </Table.Row>
                                {/if}
                            {/each}
                        </Table.Body>
                    </Table.Root>
                </Card.Content>
            </Card.Root>
        </div>
    {:else}
        <div class="text-center text-gray-500">No run found</div>
    {/if}
</div>
