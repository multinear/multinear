<script lang="ts">
    import { selectedProjectId } from "$lib/stores/projects";
    import {
        handleStartExperiment,
        handleRerunTask,
        handleRunGroup,
        jobStore,
    } from "$lib/stores/jobs";
    import { Button } from "$lib/components/ui/button";
    import { Play, ChevronDown, ChevronRight } from "lucide-svelte";
    import { Loader2 } from "lucide-svelte";
    import * as DropdownMenu from "$lib/components/ui/dropdown-menu";
    import { getAvailableTasks } from "$lib/api";
    import type { Task, Group } from "$lib/api";
    
    export let reloadRecentRuns: () => Promise<void>;

    let availableTasks: Task[] = [];
    let availableGroups: Group[] = [];
    let tasksError: string | null = null;
    let isLoading = false;
    let open = false;

    // Track which group's dropdown is open
    let selectedGroupId: string | null = null;

    async function loadTasksAndGroups() {
        if (!$selectedProjectId) return;
        isLoading = true;
        tasksError = null;
        try {
            const response = await getAvailableTasks($selectedProjectId);
            availableTasks = response.tasks;
            availableGroups = response.groups;
        } catch (error) {
            console.error("Error loading tasks and groups:", error);
            tasksError =
                error instanceof Error ? error.message : "Unknown error";
        } finally {
            isLoading = false;
        }
    }

    $: if ($selectedProjectId) {
        loadTasksAndGroups();
    }

    function getTaskLabel(task: Task): string {
        if (task.name) return task.name;
        if (task.description) return task.description;
        if (task.id) {
            // If ID has a group prefix (group_id/task_id), show only the task_id part
            const parts = task.id.split("/");
            return parts.length > 1 ? parts[parts.length - 1] : task.id;
        }
        if (typeof task.input === "string")
            return task.input.slice(0, 30) + "...";
        return "Unnamed task";
    }

    function toggleGroup(groupId: string) {
        selectedGroupId = selectedGroupId === groupId ? null : groupId;
    }
</script>

<div>
    {#if $jobStore.currentJob && $jobStore.jobStatus && !["completed", "failed", "error"].includes($jobStore.jobStatus)}
        <div class="flex items-center gap-2">
            <Loader2 class="h-4 w-4 animate-spin" />
            <span class="text-gray-500">{$jobStore.jobStatus}</span>
        </div>
    {:else}
        <div class="flex items-center gap-1">
            <Button
                variant="primary"
                on:click={() =>
                    handleStartExperiment($selectedProjectId, reloadRecentRuns)}
                class="flex items-center gap-2"
            >
                <Play class="h-4 w-4" />
                Run Experiment
            </Button>
            <DropdownMenu.Root bind:open>
                <DropdownMenu.Trigger>
                    <Button variant="primary" class="px-2">
                        <ChevronDown class="h-4 w-4" />
                    </Button>
                </DropdownMenu.Trigger>
                <DropdownMenu.Content
                    align="end"
                    class="w-80 bg-white border border-gray-200 shadow-lg rounded-md py-1 max-h-[80vh] overflow-hidden"
                >
                    {#if isLoading}
                        <DropdownMenu.Item disabled>
                            <Loader2 class="h-4 w-4 animate-spin mr-2" />
                            Loading...
                        </DropdownMenu.Item>
                    {:else if tasksError}
                        <DropdownMenu.Item disabled>
                            <span class="text-red-500">Error: {tasksError}</span
                            >
                        </DropdownMenu.Item>
                    {:else}
                        <!-- Groups Section -->
                        {#if availableGroups.length > 0}
                            <div
                                class="px-2 py-1 text-xs font-semibold text-gray-700 border-b border-gray-100 mb-1 sticky top-0 bg-white z-10"
                            >
                                Groups
                            </div>
                            <div
                                class="max-h-[calc(80vh-6rem)] overflow-y-auto"
                            >
                                {#each availableGroups as group}
                                    <!-- Group header -->
                                    <div class="flex items-center w-full">
                                        <div
                                            class="px-1 py-1 hover:bg-gray-100 cursor-pointer flex items-center flex-grow"
                                            on:click={() => toggleGroup(group.id)}
                                            on:keydown={(e) => {
                                                if (e.key === 'Enter' || e.key === ' ') {
                                                    e.preventDefault();
                                                    toggleGroup(group.id);
                                                }
                                            }}
                                            tabindex="0"
                                            role="button"
                                            aria-expanded={selectedGroupId === group.id}
                                            aria-controls={`group-${group.id}-content`}
                                        >
                                            {#if selectedGroupId === group.id}
                                                <ChevronDown class="h-3.5 w-3.5 mr-1 text-blue-600" />
                                            {:else}
                                                <ChevronRight class="h-3.5 w-3.5 mr-1 text-gray-600" />
                                            {/if}
                                            <span class="text-sm font-medium">{group.name || group.id}</span>
                                            <span class="text-xs text-gray-500 ml-1">({group.task_count} tasks)</span>
                                        </div>
                                        
                                        <!-- Run group button -->
                                        <button
                                            type="button"
                                            on:click={(e) => {
                                                e.stopPropagation(); // Prevent toggling the group
                                                handleRunGroup($selectedProjectId, group.id, reloadRecentRuns);
                                                open = false;
                                            }}
                                            class="px-2 py-1 hover:bg-gray-100 cursor-pointer flex items-center"
                                            aria-label={`Run all tasks in ${group.name || group.id} group`}
                                        >
                                            <svg 
                                                xmlns="http://www.w3.org/2000/svg" 
                                                width="14" 
                                                height="14" 
                                                viewBox="0 0 24 24" 
                                                fill="#16a34a" 
                                                stroke="none" 
                                                class="flex-shrink-0"
                                            >
                                                <polygon points="5 3 19 12 5 21 5 3" />
                                            </svg>
                                        </button>
                                    </div>

                                    {#if selectedGroupId === group.id}
                                        <div id={`group-${group.id}-content`}>
                                            <!-- Individual tasks in group (if expanded) -->
                                            {#if group.tasks && group.tasks.length > 0}
                                                <div class="max-h-[40vh] overflow-y-auto pl-4">
                                                    {#each group.tasks as task}
                                                        <button
                                                            type="button"
                                                            on:click={() => {
                                                                // Extract just the task ID part without the group prefix
                                                                const taskId = task.id.includes('/') 
                                                                    ? task.id.split('/').pop() || task.id 
                                                                    : task.id;
                                                                
                                                                handleRerunTask($selectedProjectId, taskId, reloadRecentRuns);
                                                                open = false;
                                                            }}
                                                            class="flex items-center py-1 w-full text-left hover:bg-gray-100 cursor-pointer"
                                                        >
                                                            <Play class="h-3.5 w-3.5 mr-1 text-green-600 flex-shrink-0" />
                                                            <span class="truncate text-sm">{getTaskLabel(task)}</span>
                                                        </button>
                                                    {/each}
                                                </div>
                                            {/if}
                                        </div>
                                    {/if}
                                {/each}
                            </div>

                            {#if availableTasks.length > 0}
                                <div class="h-px bg-gray-200 my-1"></div>
                            {/if}
                        {/if}

                        <!-- Individual Tasks Section -->
                        {#if availableTasks.length > 0}
                            <div
                                class="px-2 py-1 text-xs font-semibold text-gray-700 border-b border-gray-100 mb-1 sticky top-0 bg-white z-10"
                            >
                                Individual Tasks
                            </div>
                            <div class="max-h-[40vh] overflow-y-auto">
                                {#each availableTasks as task}
                                    <button
                                        type="button"
                                        on:click={() => {
                                            handleRerunTask(
                                                $selectedProjectId,
                                                task.id,
                                                reloadRecentRuns
                                            );
                                            open = false;
                                        }}
                                        class="flex items-center px-2 py-1 w-full text-left hover:bg-gray-100 cursor-pointer"
                                    >
                                        <Play
                                            class="h-3.5 w-3.5 mr-1 text-green-600 flex-shrink-0"
                                        />
                                        <span class="truncate text-sm"
                                            >{getTaskLabel(task)}</span
                                        >
                                    </button>
                                {/each}
                            </div>
                        {/if}

                        {#if availableTasks.length === 0 && availableGroups.length === 0}
                            <DropdownMenu.Item disabled>
                                No tasks available
                            </DropdownMenu.Item>
                        {/if}
                    {/if}
                </DropdownMenu.Content>
            </DropdownMenu.Root>
        </div>
    {/if}
</div>
