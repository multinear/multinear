<script lang="ts">
    import { jobStore } from '$lib/stores/jobs';
    import { AlertCircle, Clock } from 'lucide-svelte';
    import * as Alert from '$lib/components/ui/alert';
    import { onMount, onDestroy } from 'svelte';
    import { intervalToDuration } from 'date-fns';

    // Timer state
    let elapsedTime = '';
    let timerInterval: ReturnType<typeof setInterval> | null = null;

    // Format time as (H:)MM:SS
    function formatElapsedTime(startTime: Date | null): string {
        if (!startTime) return '00:00';
        
        const now = new Date();
        const duration = intervalToDuration({ start: startTime, end: now });
        
        const hours = duration.hours || 0;
        const minutes = duration.minutes || 0;
        const seconds = duration.seconds || 0;
        
        if (hours > 0) {
            return `${hours}:${minutes}:${seconds.toString().padStart(2, '0')}`;
        } else {
            return `${minutes}:${seconds.toString().padStart(2, '0')}`;
        }
    }

    // Update timer every second
    function startTimer() {
        if (timerInterval) clearInterval(timerInterval);
        
        timerInterval = setInterval(() => {
            if ($jobStore.startTime) {
                elapsedTime = formatElapsedTime($jobStore.startTime);
            }
        }, 1000);
        
        // Initial update
        if ($jobStore.startTime) {
            elapsedTime = formatElapsedTime($jobStore.startTime);
        }
    }

    function stopTimer() {
        if (timerInterval) {
            clearInterval(timerInterval);
            timerInterval = null;
        }
    }

    // Start timer when component mounts
    onMount(() => {
        if ($jobStore.jobStatus !== 'completed' && $jobStore.jobStatus !== 'failed') {
            startTimer();
        } else if ($jobStore.startTime) {
            // Just set the final time without starting the timer
            elapsedTime = formatElapsedTime($jobStore.startTime);
        }
    });

    // Clean up timer when component is destroyed
    onDestroy(() => {
        stopTimer();
    });

    // Watch for job status changes
    $: {
        if ($jobStore.jobStatus === 'completed' || $jobStore.jobStatus === 'failed') {
            stopTimer();
        } else if ($jobStore.startTime && !timerInterval) {
            startTimer();
        }
    }
</script>

{#if $jobStore.currentJob}
    <div class="border rounded-lg p-4 bg-gray-50">
        <div class="flex items-center gap-4">
            <span class="font-medium">Latest Run:</span>
            <span>{$jobStore.currentJob.slice(-8)}</span>
            <span class={`text-gray-500 ${$jobStore.jobStatus === 'failed' || $jobStore.jobStatus === 'error' ? 'text-red-500' : ''}`}>
                Status: {$jobStore.jobStatus}
            </span>
            <span class="ml-auto text-gray-500 flex items-center gap-1">
                <Clock class="h-4 w-4" /> {elapsedTime}
            </span>
        </div>
        {#if $jobStore.jobDetails}
            <div class="mt-2">
                {#if (!$jobStore.jobDetails.task_status_map || Object.keys($jobStore.jobDetails.task_status_map).length === 0) && !$jobStore.jobStatus}
                    <Alert.Root variant="destructive" class="mt-2">
                        <AlertCircle class="h-4 w-4" />
                        <Alert.Title>Experiment Failed</Alert.Title>
                        <Alert.Description>
                            No task status information available. The experiment may have failed to start properly.
                        </Alert.Description>
                    </Alert.Root>
                {:else}
                    <div class="w-full bg-gray-200 rounded-sm h-4 dark:bg-gray-700 relative overflow-hidden">
                        <div 
                            class={`h-4 transition-all duration-300 relative overflow-hidden rounded-r-sm ${$jobStore.jobStatus === 'failed' ? 'bg-red-500' : 'bg-blue-600 progress-stripe'}`}
                            style="width: {$jobStore.jobStatus === 'completed' || $jobStore.jobStatus === 'failed' ? '100' : ($jobStore.jobDetails.current_task! / $jobStore.jobDetails.total_tasks * 100)}%;"
                        ></div>
                        
                        {#if $jobStore.jobDetails.task_status_map}
                            {#each Object.entries($jobStore.jobDetails.task_status_map) as [taskId, status], index}
                                {#if status === 'failed'}
                                    <div 
                                        class="absolute top-0 h-4 bg-red-500"
                                        style="width: {100 / $jobStore.jobDetails.total_tasks}%; left: {(index / $jobStore.jobDetails.total_tasks) * 100}%"
                                    ></div>
                                {:else if status === 'evaluating'}
                                    <div 
                                        class="absolute top-0 h-4 bg-yellow-500 progress-stripe"
                                        style="width: {100 / $jobStore.jobDetails.total_tasks}%; left: {(index / $jobStore.jobDetails.total_tasks) * 100}%"
                                    ></div>
                                {:else if status === 'completed'}
                                    <div 
                                        class="absolute top-0 h-4 bg-green-600"
                                        style="width: {100 / $jobStore.jobDetails.total_tasks}%; left: {(index / $jobStore.jobDetails.total_tasks) * 100}%"
                                    ></div>
                                {/if}
                            {/each}
                        {/if}
                    </div>
                    <div class="flex justify-between mt-1 text-sm text-gray-500">
                        <div class="flex">
                            {#if $jobStore.jobDetails.task_status_map}
                                <div class="text-sm text-gray-500 flex flex-wrap gap-2">
                                    {#each Object.entries($jobStore.taskStatusCounts) as [status, count]}
                                        {#if count > 0}
                                            <span class="inline-flex items-center gap-1">
                                                <div class="w-2 h-2 rounded-full {
                                                    status === 'completed' ? 'bg-green-500' : 
                                                    status === 'running' ? 'bg-blue-500' :
                                                    status === 'evaluating' ? 'bg-yellow-500' :
                                                    status === 'failed' ? 'bg-red-500' : 'bg-gray-500'
                                                }"></div>
                                                {status}: {count}
                                            </span>
                                        {/if}
                                    {/each}
                                </div>
                            {/if}
                        </div>
                        <div class="flex gap-8">
                            <span>{$jobStore.jobDetails?.current_task || 0} / {$jobStore.jobDetails?.total_tasks || 0}</span>
                            <span>{$jobStore.jobStatus === 'completed' || $jobStore.jobStatus === 'failed' ? '100' : Math.round(($jobStore.jobDetails?.current_task || 0) / ($jobStore.jobDetails?.total_tasks || 1) * 100)}%</span>
                        </div>
                    </div>
                {/if}
            </div>
        {/if}

        {#if $jobStore.jobStatus === 'error' || $jobStore.jobStatus === 'failed'}
            <Alert.Root variant="destructive" class="mt-2">
                <AlertCircle class="h-4 w-4" />
                <Alert.Title>Run Failed</Alert.Title>
                <Alert.Description>
                    {#if $jobStore.jobDetails?.error}
                        {$jobStore.jobDetails.error}
                    {:else}
                        The experiment failed to complete. Check the task details for more information.
                    {/if}
                </Alert.Description>
            </Alert.Root>
        {/if}
    </div>
{/if}

<style>
    .progress-stripe {
        background-image: linear-gradient(
            45deg,
            rgba(255,255,255,0.15) 25%,
            transparent 25%,
            transparent 50%,
            rgba(255,255,255,0.15) 50%,
            rgba(255,255,255,0.15) 75%,
            transparent 75%,
            transparent
        );
        background-size: 16px 16px;
        animation: move 1s linear infinite;
    }

    @keyframes move {
        from {
            background-position: 0 0;
        }
        to {
            background-position: 16px 0;
        }
    }
</style>
