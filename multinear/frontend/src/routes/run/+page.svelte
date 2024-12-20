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
    import RunHeader from '$lib/components/RunHeader.svelte';
    import Loading from '$lib/components/Loading.svelte';
    import ErrorDisplay from '$lib/components/ErrorDisplay.svelte';
    import StatusBadge from '$lib/components/StatusBadge.svelte';

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
    {#if runDetails}
        <RunHeader runDetails={runDetails} showExportButton={true} />
    {/if}

    {#if loading}
        <Loading message="Loading run details..." />
    {:else if error}
        <ErrorDisplay errorMessage={error} onRetry={() => loadRunDetails(runId!)} />
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
                                        <StatusBadge status={task.status} />
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
                                                        <h4 class="font-semibold text-lg">Task Details</h4>
                                                        <div class="text-sm text-gray-800">
                                                            Duration: 
                                                            {#if task.task_details?.duration}
                                                                {formatDuration(
                                                                    intervalToDuration({
                                                                        start: new Date(task.executed_at),
                                                                        end: new Date(task.finished_at)
                                                                    }),
                                                                    { format: ['minutes', 'seconds'] }
                                                                )}
                                                            {/if}
                                                        </div>
                                                    </div>

                                                    {#if task.task_input}
                                                        <div>
                                                            <h5 class="text-sm font-semibold mb-2">Input</h5>
                                                            <div class="bg-white p-4 rounded border border-gray-200 whitespace-pre-wrap font-mono text-xs">
                                                                {typeof task.task_input === 'object' && 'str' in task.task_input 
                                                                    ? task.task_input.str 
                                                                    : JSON.stringify(task.task_input, null, 2)}
                                                            </div>
                                                        </div>
                                                    {/if}

                                                    {#if task.task_output}
                                                        <div>
                                                            <div class="flex justify-between items-center mb-1">
                                                                <h5 class="text-sm font-semibold">Output</h5>
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
                                                            <div class="bg-white p-4 rounded border border-gray-200 whitespace-pre-wrap font-mono text-xs">
                                                                {typeof task.task_output === 'object' && 'str' in task.task_output 
                                                                    ? task.task_output.str 
                                                                    : JSON.stringify(task.task_output, null, 2)}
                                                            </div>
                                                        </div>
                                                    {/if}

                                                    {#if task.task_details}
                                                        <div>
                                                            <h5 class="text-sm font-semibold mb-2">Details</h5>
                                                            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                                                {#each Object.entries(task.task_details) as [key, value]}
                                                                    <div>
                                                                        <div class="text-sm font-medium text-gray-600 mb-1">{key}</div>
                                                                        <div class="bg-white p-3 rounded border border-gray-200 whitespace-pre-wrap font-mono text-xs">
                                                                            {typeof value === 'string' ? value : JSON.stringify(value, null, 2)}
                                                                        </div>
                                                                    </div>
                                                                {/each}
                                                            </div>
                                                        </div>
                                                    {/if}

                                                    {#if task.task_logs}
                                                        <div>
                                                            <h5 class="text-sm font-semibold mb-2">Logs</h5>
                                                            <details class="bg-white rounded border border-gray-200">
                                                                <summary class="px-4 py-2 cursor-pointer hover:bg-gray-50">
                                                                    View Logs
                                                                </summary>
                                                                <table class="w-full text-sm">
                                                                    <thead class="bg-gray-50 border-y border-gray-200">
                                                                        <tr>
                                                                            <th class="px-4 py-2 text-left w-32">Info</th>
                                                                            <th class="px-4 py-2 text-left">Message</th>
                                                                        </tr>
                                                                    </thead>
                                                                    <tbody class="divide-y divide-gray-100">
                                                                        {#each task.task_logs.logs as log}
                                                                            <tr class="hover:bg-gray-50">
                                                                                <td class="px-4 py-2">
                                                                                    <div class="text-xs text-gray-500">{log.level}</div>
                                                                                    <div class="text-sm">{new Date(log.timestamp * 1000).toLocaleString()}</div>
                                                                                </td>
                                                                                <td class="px-4 py-2">{log.message}</td>
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
                                                                ${task.eval_passed ? 'status-completed' : 'status-failed'}`}>
                                                                {task.eval_passed ? 'PASSED' : 'FAILED'}
                                                            </div>
                                                        </div>
                                                    </div>
                                                    
                                                    {#if task.eval_details?.evaluations}
                                                        <div>
                                                            <h4 class="font-semibold text-lg mb-3">Evaluation Results</h4>
                                                            <div class="space-y-4 divide-y divide-gray-100">
                                                                {#each task.eval_details.evaluations as ev}
                                                                    <div class="pt-4 first:pt-0">
                                                                        <div class="flex items-center gap-3">
                                                                            <div class="flex-none flex items-center justify-center w-9 h-9 rounded-full border
                                                                                {ev.score >= 1 ? 'status-completed status-completed-border' : 
                                                                                ev.score > 0 ? 'status-default status-default-border' : 
                                                                                'status-failed status-failed-border'}">
                                                                                <span class="text-xs font-medium leading-none">
                                                                                    {(ev.score * 100).toFixed(0)}%
                                                                                </span>
                                                                            </div>
                                                                            <div class="text-sm font-medium flex-1">{ev.criterion}</div>
                                                                        </div>
                                                                        <div class="mt-1 text-sm text-gray-600">{ev.rationale}</div>
                                                                    </div>
                                                                {/each}
                                                            </div>
                                                        </div>
                                                    {/if}

                                                    {#if task.eval_details}
                                                        <div>
                                                            <h5 class="font-semibold mb-2">Details</h5>
                                                            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                                                {#each Object.entries(task.eval_details) as [key, value]}
                                                                    {#if key !== 'evaluations'}
                                                                        <div>
                                                                            <div class="text-sm font-medium text-gray-600 mb-1">{key}</div>
                                                                            <div class="bg-white p-3 rounded border border-gray-200 whitespace-pre-wrap font-mono text-xs">
                                                                                {typeof value === 'string' ? value : JSON.stringify(value, null, 2)}
                                                                            </div>
                                                                        </div>
                                                                    {/if}
                                                                {/each}
                                                            </div>
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
