<script lang="ts">
    import { selectedProjectId } from '$lib/stores/projects';
    import { handleStartExperiment, handleRerunTask, jobStore } from '$lib/stores/jobs';
    import { Button } from '$lib/components/ui/button';
    import { Play, ChevronDown } from 'lucide-svelte';
    import { Loader2 } from 'lucide-svelte';
    import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
    import { getAvailableTasks } from '$lib/api';
    import type { Task } from '$lib/api';
    import { onMount } from 'svelte';

    export let reloadRecentRuns: () => Promise<void>;

    let availableTasks: Task[] = [];
    let tasksError: string | null = null;
    let tasksLoading = false;
    let open = false;

    async function loadTasks() {
        if (!$selectedProjectId) return;
        tasksLoading = true;
        tasksError = null;
        try {
            const response = await getAvailableTasks($selectedProjectId);
            availableTasks = response.tasks;
        } catch (error) {
            console.error('Error loading tasks:', error);
            tasksError = error instanceof Error ? error.message : 'Unknown error';
        } finally {
            tasksLoading = false;
        }
    }

    $: if ($selectedProjectId) {
        loadTasks();
    }

    function getTaskLabel(task: Task): string {
        if (task.id) return task.id;
        if (task.name) return task.name;
        if (task.description) return task.description;
        if (typeof task.input === 'string') return task.input.slice(0, 30) + '...';
        return task.id.slice(0, 8);
    }
</script>

<div>
    {#if $jobStore.currentJob && $jobStore.jobStatus && !['completed', 'failed', 'error'].includes($jobStore.jobStatus)}
        <div class="flex items-center gap-2">
            <Loader2 class="h-4 w-4 animate-spin" />
            <span class="text-gray-500">{$jobStore.jobStatus}</span>
        </div>
    {:else}
        <div class="flex items-center gap-1">
            <Button variant="primary" on:click={() => handleStartExperiment($selectedProjectId, reloadRecentRuns)} class="flex items-center gap-2">
                <Play class="h-4 w-4" />
                Run Experiment
            </Button>
            <DropdownMenu.Root bind:open>
                <DropdownMenu.Trigger>
                    <Button variant="primary" class="px-2">
                        <ChevronDown class="h-4 w-4" />
                    </Button>
                </DropdownMenu.Trigger>
                <DropdownMenu.Content align="end">
                    {#if tasksLoading}
                        <DropdownMenu.Item disabled>
                            <Loader2 class="h-4 w-4 animate-spin mr-2" />
                            Loading tasks...
                        </DropdownMenu.Item>
                    {:else if tasksError}
                        <DropdownMenu.Item disabled>
                            <span class="text-red-500">Error: {tasksError}</span>
                        </DropdownMenu.Item>
                    {:else if availableTasks.length === 0}
                        <DropdownMenu.Item disabled>
                            No tasks available
                        </DropdownMenu.Item>
                    {:else}
                        {#each availableTasks as task}
                            <DropdownMenu.Item
                                on:click={() => {
                                    handleRerunTask($selectedProjectId, task.id, reloadRecentRuns);
                                    open = false;
                                }}
                            >
                                <Play class="h-4 w-4 mr-2" />
                                {getTaskLabel(task)}
                            </DropdownMenu.Item>
                        {/each}
                    {/if}
                </DropdownMenu.Content>
            </DropdownMenu.Root>
        </div>
    {/if}
</div>
