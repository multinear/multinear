<script lang="ts">
    import * as Card from "$lib/components/ui/card";
    import { Button } from "$lib/components/ui/button";
    import { getRunDetails } from '$lib/api';
    import { selectedRunId } from '$lib/stores/projects';
    import * as Table from "$lib/components/ui/table";
    import { Label } from "$lib/components/ui/label";
    import { Input } from "$lib/components/ui/input";
    import { formatDuration, intervalToDuration } from 'date-fns';
    import { ChevronRight, Play } from 'lucide-svelte';
    import TimeAgo from '$lib/components/TimeAgo.svelte';
    import StatusFilter from '$lib/components/StatusFilter.svelte';
    import { filterTasks, getStatusCounts, getTaskStatus, truncateInput } from '$lib/utils/tasks';
    import { goto } from '$app/navigation';
    import { tick } from 'svelte';
    import RunHeader from '$lib/components/RunHeader.svelte';
    import Loading from '$lib/components/Loading.svelte';
    import ErrorDisplay from '$lib/components/ErrorDisplay.svelte';
    import StatusBadge from '$lib/components/StatusBadge.svelte';
    import { handleRerunTask } from '$lib/stores/jobs';
    import { marked } from 'marked';
    import { Switch } from "$lib/components/ui/switch";
    import EvaluationResults from '$lib/components/EvaluationResults.svelte';
    import { truncateText } from '$lib/utils/scores';


    let runId: string | null = null;
    let runDetails: any = null;
    let loading = true;
    let error: string | null = null;
    let expandedTaskId: string | null = null;
    let showOutputMarkdown = false;
    let showPromptMarkdown = false;

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
    let evaluationFilter = "";
    
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

    async function loadRecentRuns() {
        // No-op since we don't need to reload runs in this view
    }

    async function handleRerunTaskClick(task: any) {
        try {
            await handleRerunTask(runDetails.project.id, task.challenge_id, loadRecentRuns);
            goto('/');
        } catch (error) {
            console.error('Error rerunning task:', error);
        }
    }

    function formatTimeInterval(start: string, end: string): string {
        const duration = intervalToDuration({
            start: new Date(start),
            end: new Date(end)
        });

        if (duration.minutes || duration.seconds) {
            return formatDuration(duration, { 
                format: ['minutes', 'seconds'] 
            });
        }

        return '<1 second';
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
                                <div class="font-semibold">
                                    <StatusBadge status={runDetails.details?.status || runDetails.status} />
                                </div>
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
                        
                        {#if runDetails.details?.error}
                            <div class="mt-4">
                                <ErrorDisplay 
                                    errorMessage={runDetails.details.error} 
                                />
                            </div>
                        {/if}
                        
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
                                            {formatTimeInterval(task.created_at, task.finished_at)}
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
                                            {#if task.eval_details?.evaluations}
                                                {#each task.eval_details.evaluations as ev}
                                                    <div
                                                        class="h-4 min-w-[5px] {ev.score >= 1 ? 'bg-green-600' : ev.score > 0 ? 'bg-yellow-400' : 'bg-red-600'}"
                                                        style="width: {(1 / task.eval_details.evaluations.length * 100).toFixed(0)}%"
                                                    ></div>
                                                {/each}
                                            {:else}
                                                <div
                                                    class="h-4 min-w-[5px] {isPassed ? 'bg-green-600' : 'bg-red-600'}"
                                                    style="width: {(task.eval_score * 100).toFixed(0)}%"
                                                ></div>
                                            {/if}
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
                                                    <div class="flex items-center mb-2">
                                                        <h4 class="font-semibold text-lg">
                                                            Task Details 
                                                            <span class="text-sm font-normal text-gray-800 ml-2">
                                                                {#if task.finished_at}
                                                                    (time: {formatTimeInterval(task.created_at, task.finished_at)})
                                                                {:else}
                                                                    -
                                                                {/if}
                                                            </span>
                                                        </h4>
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
                                                                <div class="flex items-center gap-4">
                                                                    <div class="flex items-center space-x-2">
                                                                        <Switch id="output-markdown" bind:checked={showOutputMarkdown} />
                                                                        <Label for="output-markdown" class="text-sm">Markdown</Label>
                                                                    </div>
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
                                                            </div>
                                                            <div class="bg-white p-4 rounded border border-gray-200">
                                                                {#if showOutputMarkdown}
                                                                    <div class="markdown-content">
                                                                        {@html marked(typeof task.task_output === 'object' && 'str' in task.task_output 
                                                                            ? task.task_output.str 
                                                                            : JSON.stringify(task.task_output, null, 2))}
                                                                    </div>
                                                                {:else}
                                                                    <div class="whitespace-pre-wrap font-mono text-xs">
                                                                        {typeof task.task_output === 'object' && 'str' in task.task_output 
                                                                            ? task.task_output.str 
                                                                            : JSON.stringify(task.task_output, null, 2)}
                                                                    </div>
                                                                {/if}
                                                            </div>
                                                        </div>
                                                    {/if}

                                                    {#if task.error}
                                                        <div>
                                                            <h5 class="text-sm font-semibold mb-2 text-red-600">Error</h5>
                                                            <div class="bg-red-50 p-4 rounded border border-red-200 whitespace-pre-wrap font-mono text-xs text-red-700">
                                                                {task.error}
                                                            </div>
                                                        </div>
                                                    {/if}

                                                    {#if task.task_details}
                                                        <div>
                                                            <h5 class="text-sm font-semibold mb-2">Details</h5>
                                                            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                                                {#each Object.entries(task.task_details) as [key, value]}
                                                                    {#if !['prompt', 'reasoning'].includes(key)}
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

                                                    {#if task.task_details}
                                                        {@const promptField = task.task_details?.prompt ? 'prompt' : 
                                                                            task.task_details?.reasoning ? 'reasoning' : null}
                                                        {#if promptField}
                                                            <div>
                                                                <h5 class="text-sm font-semibold mb-2">{promptField}</h5>
                                                                <details class="bg-white rounded border border-gray-200">
                                                                    <summary class="px-4 py-2 cursor-pointer hover:bg-gray-50 flex justify-between items-center">
                                                                        <span>View {promptField}</span>
                                                                        <div class="flex items-center space-x-2">
                                                                            <Switch id="prompt-markdown" bind:checked={showPromptMarkdown} />
                                                                            <Label for="prompt-markdown" class="text-sm">Markdown</Label>
                                                                        </div>
                                                                    </summary>
                                                                    <div class="p-4">
                                                                        {#if showPromptMarkdown}
                                                                            <div class="markdown-content">
                                                                                {@html marked(typeof task.task_details[promptField] === 'string' 
                                                                                    ? task.task_details[promptField]
                                                                                    : JSON.stringify(task.task_details[promptField], null, 2))}
                                                                            </div>
                                                                        {:else}
                                                                            <div class="whitespace-pre-wrap font-mono text-xs">
                                                                                {typeof task.task_details[promptField] === 'string' 
                                                                                    ? task.task_details[promptField]
                                                                                    : JSON.stringify(task.task_details[promptField], null, 2)}
                                                                            </div>
                                                                        {/if}
                                                                    </div>
                                                                </details>
                                                            </div>
                                                        {/if}
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
                                                    <div class="flex items-center mb-2">
                                                        <h4 class="font-semibold text-lg">
                                                            Evaluation
                                                            <span class="text-sm font-normal text-gray-800 ml-2">
                                                                {#if task.evaluated_at}
                                                                    (time: {formatTimeInterval(task.executed_at, task.evaluated_at)})
                                                                {:else}
                                                                    -
                                                                {/if}
                                                            </span>
                                                        </h4>
                                                        <div class="flex items-center gap-4 ml-auto">
                                                            <div class="text-sm text-gray-800">
                                                                Score: {(task.eval_score * 100).toFixed(0)}%
                                                            </div>
                                                            <div class={`px-4 py-1 rounded-lg font-semibold
                                                                ${task.eval_passed ? 'status-completed' : 'status-failed'}`}>
                                                                {task.eval_passed ? 'PASSED' : 'FAILED'}
                                                            </div>
                                                            <Button 
                                                                variant="primary" 
                                                                size="sm"
                                                                class="flex items-center gap-2 text-sm transition-colors"
                                                                on:click={() => handleRerunTaskClick(task)}
                                                            >
                                                                <Play class="h-3 w-3" />
                                                                Re-run
                                                            </Button>
                                                        </div>
                                                    </div>
                                                    
                                                    {#if task.eval_details?.evaluations}
                                                        <div>
                                                            <div class="flex items-center justify-between">
                                                                <h4 class="font-semibold text-lg">Evaluation Results</h4>
                                                                {#if (task.eval_details.evaluations.some((ev: {score: number}) => ev.score >= 1) && 
                                                                     task.eval_details.evaluations.some((ev: {score: number}) => ev.score < 1)) ||
                                                                     evaluationFilter != ""}
                                                                    <div class="flex gap-2">
                                                                        <Button
                                                                            variant="outline"
                                                                            size="sm"
                                                                            class={evaluationFilter === "" ? 'bg-gray-100 border-gray-200' : ''}
                                                                            on:click={() => evaluationFilter = ""}
                                                                        >
                                                                            All
                                                                        </Button>
                                                                        <Button
                                                                            variant="outline"
                                                                            size="sm"
                                                                            class={evaluationFilter === "passed" ? 'bg-green-50 border-green-200 text-green-700' : ''}
                                                                            on:click={() => evaluationFilter = "passed"}
                                                                        >
                                                                            Passed
                                                                        </Button>
                                                                        <Button
                                                                            variant="outline"
                                                                            size="sm"
                                                                            class={evaluationFilter === "failed" ? 'bg-red-50 border-red-200 text-red-700' : ''}
                                                                            on:click={() => evaluationFilter = "failed"}
                                                                        >
                                                                            Failed
                                                                        </Button>
                                                                    </div>
                                                                {/if}
                                                            </div>
                                                            <div class="mt-3">
                                                                <EvaluationResults 
                                                                    evaluations={task.eval_details.evaluations}
                                                                    evalSpec={task.eval_spec}
                                                                    filter={evaluationFilter}
                                                                />
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
