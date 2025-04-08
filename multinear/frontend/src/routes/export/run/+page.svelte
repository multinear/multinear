<script lang="ts">
    import { getRunDetails } from '$lib/api';
    // import { selectedRunId } from '$lib/stores/projects';
    // import * as Table from "$lib/components/ui/table";
    import { formatDuration, intervalToDuration } from 'date-fns';
    // import { getTaskStatus } from '$lib/utils/tasks';
    import { onMount } from 'svelte';
    import RunReportHeader from '$lib/components/RunReportHeader.svelte';
    import Loading from '$lib/components/Loading.svelte';
    import ErrorDisplay from '$lib/components/ErrorDisplay.svelte';
    import StatusBadge from '$lib/components/StatusBadge.svelte';
    import ScoreCircle from '$lib/components/ScoreCircle.svelte';
    import EvaluationResults from '$lib/components/EvaluationResults.svelte';
    import { truncateText } from '$lib/utils/scores';

    interface Task {
        id: string;
        status: string;
        eval_score: number | null;
    }

    let runDetails: any = null;
    let loading = true;
    let error: string | null = null;
    let runId: string | null = null;

    // Handle URL hash changes
    function handleHashChange() {
        const hash = window.location.hash.slice(1); // Remove the # character
        if (hash) {
            const [projectId, newRunId] = hash.split('/');
            if (projectId && newRunId) {
                runId = newRunId;
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

    function getScoreStyles(score: number): { color: string, border: string, text: string } {
        if (score >= 1) {
            return { 
                color: 'status-completed status-completed-border print:bg-green-50', 
                border: 'status-completed-border',
                text: 'text-green-600'
            };
        } else if (score >= 0.5) {
            return { 
                color: 'status-default status-default-border print:bg-yellow-50', 
                border: 'status-default-border',
                text: 'text-yellow-500'
            };
        }
        return { 
            color: 'status-failed status-failed-border print:bg-red-50', 
            border: 'status-failed-border',
            text: 'text-red-600'
        };
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
        <Loading message="Loading run details..." />
    {:else if error}
        <ErrorDisplay errorMessage={error} onRetry={() => loadRunDetails(runId!)} />
    {:else if runDetails}
        <RunReportHeader {runDetails} {taskStats} />
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
                            <StatusBadge status={task.status} className="px-3 py-1" />
                            {#if task.eval_score !== null}
                                <ScoreCircle 
                                    score={task.eval_score} 
                                    includePrintStyles={true}
                                    showMinScore={false}
                                />
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
                                                        {typeof value === 'string' 
                                                            ? (key === 'prompt' ? truncateText(value) : value)
                                                            : JSON.stringify(value, null, 2)}
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
                                    <!-- Old structure with direct evaluations -->
                                    <div>
                                        <h4 class="text-sm font-semibold mb-3">Evaluation Results</h4>
                                        <EvaluationResults 
                                            evaluations={task.eval_details.evaluations}
                                            evalSpec={task.eval_spec}
                                            includePrintStyles={true}
                                            filter={""}
                                        />
                                    </div>
                                {:else if task.eval_details?.metrics}
                                    <!-- New structure with metrics array -->
                                    <div>
                                        <h4 class="text-sm font-semibold mb-3">Evaluation Results</h4>
                                        {#each task.eval_details.metrics as metric}
                                            <div class="mb-4 border rounded-lg overflow-hidden">
                                                <div class="flex items-center justify-between bg-gray-100 p-3 border-b">
                                                    <h5 class="text-sm font-medium capitalize">{metric.metric_type}</h5>
                                                    <div class="flex items-center">
                                                        {#if metric.passed !== undefined}
                                                            <span class="mr-2 text-xs px-2 py-0.5 rounded-full {metric.passed ? 'bg-green-100 text-green-800 print:bg-green-50 border border-green-300' : 'bg-red-100 text-red-800 print:bg-red-50 border border-red-300'}">
                                                                {metric.passed ? 'Passed' : 'Failed'}
                                                            </span>
                                                        {/if}
                                                        <div>
                                                            <ScoreCircle 
                                                                score={metric.score} 
                                                                includePrintStyles={true}
                                                                showMinScore={false}
                                                            />
                                                        </div>
                                                    </div>
                                                </div>
                                                {#if metric.details?.evaluations}
                                                    <div class="p-3">
                                                        <EvaluationResults 
                                                            evaluations={metric.details.evaluations}
                                                            evalSpec={task.eval_spec}
                                                            includePrintStyles={true}
                                                            filter={""}
                                                        />
                                                    </div>
                                                {/if}
                                            </div>
                                        {/each}
                                    </div>
                                {/if}

                                {#if task.eval_details}
                                    <div>
                                        <h4 class="text-sm font-semibold mb-2">Evaluation Details</h4>
                                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                            {#each Object.entries(task.eval_details) as [key, value]}
                                                {#if key !== 'evaluations' && key !== 'metrics'}
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
