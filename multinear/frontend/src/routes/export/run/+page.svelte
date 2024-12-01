<script lang="ts">
    import { getRunDetails } from '$lib/api';
    import { selectedRunId } from '$lib/stores/projects';
    import * as Table from "$lib/components/ui/table";
    import { formatDuration, intervalToDuration } from 'date-fns';
    import { getTaskStatus } from '$lib/utils/tasks';
    import { onMount } from 'svelte';

    interface Task {
        id: string;
        status: string;
        eval_score: number | null;
    }

    let runDetails: any = null;
    let loading = true;
    let error: string | null = null;

    // Handle URL hash changes
    function handleHashChange() {
        const hash = window.location.hash.slice(1); // Remove the # character
        if (hash) {
            const [projectId, runId] = hash.split('/');
            if (projectId && runId) {
                loadRunDetails(runId);
            }
        }
    }

    onMount(() => {
        // Load run ID from URL hash on initial page load
        handleHashChange();

        // Listen for hash changes
        window.addEventListener('hashchange', handleHashChange);
        return () => {
            window.removeEventListener('hashchange', handleHashChange);
        };
    });

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

    // Calculate task statistics
    $: taskStats = runDetails?.tasks ? {
        total: runDetails.tasks.length,
        completed: runDetails.tasks.filter((t: Task) => t.status === 'completed').length,
        failed: runDetails.tasks.filter((t: Task) => t.status === 'failed').length,
        inProgress: runDetails.tasks.filter((t: Task) => !['completed', 'failed'].includes(t.status)).length,
        avgScore: runDetails.tasks.reduce((acc: number, t: Task) => acc + (t.eval_score || 0), 0) / runDetails.tasks.length
    } : null;

    function getScoreColor(score: number): string {
        if (score >= 0.9) return 'bg-green-100 text-green-800 border-green-300 print:bg-green-50';
        if (score > 0) return 'bg-yellow-100 text-yellow-800 border-yellow-300 print:bg-yellow-50';
        return 'bg-red-100 text-red-800 border-red-300 print:bg-red-50';
    }
</script>

<svelte:head>
    <!-- Remove default page elements and set print styles -->
    <style>
        @media screen {
            body {
                background: white;
                margin: 0;
                padding: 0;
            }
        }
        @media print {
            @page {
                margin: 1.5cm;
                size: A4;
            }
            body {
                margin: 0;
                padding: 0;
                color: black;
                background: white;
                font-size: 11pt;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }
            .no-print {
                display: none !important;
            }
            /* Ensure backgrounds and colors are printed */
            * {
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }
            /* Enhance borders for better print visibility */
            .border {
                border-width: 1.5px !important;
            }
            .border-b {
                border-bottom-width: 1.5px !important;
            }
            /* Enhance text contrast for print */
            .text-gray-500 {
                color: #4a5568 !important;
            }
            .text-gray-600 {
                color: #2d3748 !important;
            }
        }
        /* Hide header and footer */
        nav, footer, header {
            display: none !important;
        }
    </style>
</svelte:head>

<div class="min-h-screen bg-white">
    {#if loading}
        <div class="text-center text-gray-500 p-8">Loading run details...</div>
    {:else if error}
        <div class="text-red-600 p-8">{error}</div>
    {:else if runDetails}
        <!-- Run Header with Status -->
        <div class="p-8 border-b">
            <div class="flex justify-between items-start mb-6">
                <div>
                    <h1 class="text-4xl font-bold mb-2">Run Report: {runDetails.id.slice(-8)}</h1>
                    <div class="text-gray-600">
                        Generated on {new Date().toLocaleString()}
                    </div>
                </div>
                {#if taskStats}
                    <div class={`text-center px-6 py-4 rounded-lg ${
                        taskStats.failed === 0 ? 'bg-green-50 border-2 border-green-200' : 
                        'bg-red-50 border-2 border-red-200'
                    }`}>
                        <div class="text-2xl font-bold mb-1">
                            <span class={taskStats.failed === 0 ? 'text-green-600' : 'text-red-600'}>
                                {taskStats.completed}/{taskStats.total}
                            </span>
                        </div>
                        <div class={`text-sm ${taskStats.failed === 0 ? 'text-green-600' : 'text-red-600'}`}>
                            Tasks Passed
                        </div>
                        <div class="text-sm text-gray-500 mt-1">
                            Avg Score: {(taskStats.avgScore * 100).toFixed(0)}%
                        </div>
                    </div>
                {/if}
            </div>

            <!-- Summary Grid -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-6 mb-6">
                <div>
                    <h3 class="text-sm font-medium text-gray-500">Project</h3>
                    <p class="mt-1 text-lg">{runDetails.project.name}</p>
                </div>
                <div>
                    <h3 class="text-sm font-medium text-gray-500">Status</h3>
                    <p class="mt-1">
                        <span class={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium
                            ${runDetails.status === 'completed' ? 'bg-green-100 text-green-800' : 
                            runDetails.status === 'failed' ? 'bg-red-100 text-red-800' : 
                            'bg-gray-100 text-gray-800'}`}>
                            {runDetails.status}
                        </span>
                    </p>
                </div>
                <div>
                    <h3 class="text-sm font-medium text-gray-500">Created</h3>
                    <p class="mt-1 text-lg">{new Date(runDetails.date).toLocaleString()}</p>
                </div>
                <div>
                    <h3 class="text-sm font-medium text-gray-500">Model</h3>
                    <p class="mt-1 text-lg">{runDetails.details.model || 'N/A'}</p>
                </div>
            </div>

            <!-- Task Statistics -->
            {#if taskStats}
                <div class="flex gap-1 h-2 rounded-full overflow-hidden bg-gray-100 w-full">
                    <div class="bg-green-500" style="width: {(taskStats.completed / taskStats.total * 100)}%"></div>
                    <div class="bg-red-500" style="width: {(taskStats.failed / taskStats.total * 100)}%"></div>
                    <div class="bg-gray-300" style="width: {(taskStats.inProgress / taskStats.total * 100)}%"></div>
                </div>
                <div class="flex gap-6 text-sm mt-2">
                    <div class="flex items-center gap-2">
                        <div class="w-3 h-3 rounded-full bg-green-500"></div>
                        <span>{taskStats.completed} completed</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <div class="w-3 h-3 rounded-full bg-red-500"></div>
                        <span>{taskStats.failed} failed</span>
                    </div>
                    {#if taskStats.inProgress > 0}
                        <div class="flex items-center gap-2">
                            <div class="w-3 h-3 rounded-full bg-gray-300"></div>
                            <span>{taskStats.inProgress} in progress</span>
                        </div>
                    {/if}
                </div>
            {/if}
        </div>

        <!-- Tasks Section -->
        <div class="p-8">
            <h2 class="text-2xl font-bold mb-6">Tasks</h2>
            {#each runDetails.tasks as task}
                <div class="task-card mb-8 border rounded-lg overflow-hidden">
                    <!-- Task Header -->
                    <div class={`p-4 flex justify-between items-center
                        ${task.status === 'completed' ? 'bg-green-50 border-b-2 border-green-200 print:border-green-300' :
                        task.status === 'failed' ? 'bg-red-50 border-b-2 border-red-200 print:border-red-300' :
                        'bg-gray-50 border-b-2 border-gray-200 print:border-gray-300'}`}>
                        <div>
                            <h3 class="text-lg font-bold">Task {task.id.slice(-8)}</h3>
                            <div class="text-sm text-gray-500 mt-1">
                                {new Date(task.created_at).toLocaleString()}
                                {#if task.finished_at}
                                    · {formatDuration(
                                        intervalToDuration({
                                            start: new Date(task.created_at),
                                            end: new Date(task.finished_at)
                                        }),
                                        { format: ['minutes', 'seconds'] }
                                    )}
                                {/if}
                                {#if task.task_details?.model}
                                    · {task.task_details.model}
                                {/if}
                            </div>
                        </div>
                        <div class="flex items-center gap-4">
                            <span class={`px-3 py-1 rounded-full text-sm font-medium border
                                ${task.status === 'completed' ? 'bg-green-100 text-green-800 border-green-300' : 
                                task.status === 'failed' ? 'bg-red-100 text-red-800 border-red-300' : 
                                'bg-gray-100 text-gray-800 border-gray-300'}`}>
                                {task.status}
                            </span>
                            {#if task.eval_score !== null}
                                <div class="flex-none flex items-center justify-center w-9 h-9 rounded-full border
                                    {getScoreColor(task.eval_score)}">
                                    <span class="text-xs font-medium leading-none">
                                        {(task.eval_score * 100).toFixed(0)}%
                                    </span>
                                </div>
                            {/if}
                        </div>
                    </div>

                    <!-- Task Content -->
                    <div class="p-6">
                        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                            <!-- Left Column: Input/Output -->
                            <div class="space-y-6">
                                {#if task.task_input}
                                    <div>
                                        <h4 class="text-sm font-semibold mb-2">Input</h4>
                                        <div class="bg-gray-50 p-4 rounded border border-gray-200 whitespace-pre-wrap font-mono text-xs">
                                            {typeof task.task_input === 'object' && 'str' in task.task_input 
                                                ? task.task_input.str 
                                                : JSON.stringify(task.task_input, null, 2)}
                                        </div>
                                    </div>
                                {/if}

                                {#if task.task_output}
                                    <div>
                                        <h4 class="text-sm font-semibold mb-2">Output</h4>
                                        <div class="bg-gray-50 p-4 rounded border border-gray-200 whitespace-pre-wrap font-mono text-xs">
                                            {typeof task.task_output === 'object' && 'str' in task.task_output 
                                                ? task.task_output.str 
                                                : JSON.stringify(task.task_output, null, 2)}
                                        </div>
                                    </div>
                                {/if}

                                {#if task.task_details}
                                    <div>
                                        <h4 class="text-sm font-semibold mb-2">Details</h4>
                                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                            {#each Object.entries(task.task_details) as [key, value]}
                                                <div>
                                                    <div class="text-sm font-medium text-gray-600 mb-1">{key}</div>
                                                    <div class="bg-gray-50 p-3 rounded border border-gray-200 whitespace-pre-wrap font-mono text-xs">
                                                        {typeof value === 'string' ? value : JSON.stringify(value, null, 2)}
                                                    </div>
                                                </div>
                                            {/each}
                                        </div>
                                    </div>
                                {/if}
                            </div>

                            <!-- Right Column: Evaluation -->
                            <div class="space-y-6 lg:border-l lg:pl-8">
                                {#if task.eval_details?.evaluations}
                                    <div>
                                        <h4 class="text-sm font-semibold mb-3">Evaluation Results</h4>
                                        <div class="space-y-4 divide-y divide-gray-100">
                                            {#each task.eval_details.evaluations as ev}
                                                <div class="print:break-inside-avoid pt-4 first:pt-0">
                                                    <div class="flex items-center gap-3">
                                                        <div class="flex-none flex items-center justify-center w-9 h-9 rounded-full border
                                                            {getScoreColor(ev.score)}">
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
                                        <h4 class="text-sm font-semibold mb-2">Evaluation Details</h4>
                                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                            {#each Object.entries(task.eval_details) as [key, value]}
                                                {#if key !== 'evaluations'}
                                                    <div>
                                                        <div class="text-sm font-medium text-gray-600 mb-1">{key}</div>
                                                        <div class="bg-gray-50 p-3 rounded border border-gray-200 whitespace-pre-wrap font-mono text-xs">
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
                    </div>
                </div>
            {/each}
        </div>

        <!-- Print Button (visible only on screen) -->
        <div class="fixed bottom-4 right-4 no-print">
            <button
                class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded shadow"
                on:click={() => window.print()}
            >
                Print Report
            </button>
        </div>
    {:else}
        <div class="text-center text-gray-500 p-8">No run found</div>
    {/if}
</div>
