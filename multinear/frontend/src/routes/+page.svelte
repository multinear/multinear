<script lang="ts">
    import * as Card from "$lib/components/ui/card";
    import { goto } from '$app/navigation';
    import { projects, projectsLoading, projectsError } from '$lib/stores/projects';
    import ErrorDisplay from '$lib/components/ErrorDisplay.svelte';

    // If there is only one project, redirect to it
    $: if (!$projectsLoading && !$projectsError && $projects.length === 1) {
        handleProjectSelect($projects[0].id);
    }

    function handleProjectSelect(projectId: string) {
        goto(`/dashboard/#${projectId}`);
    }
</script>

<div class="container mx-auto flex-1 flex items-center justify-center p-4">
    <div class="w-96 max-w-2xl space-y-8">
        <h1 class="text-3xl font-bold text-center mb-8">Projects</h1>

        {#if $projectsLoading}
            <div class="text-center text-gray-500">Loading projects...</div>
        {:else if $projectsError}
            <ErrorDisplay errorMessage={$projectsError} onRetry={() => window.location.reload()} />
        {:else if $projects.length === 0}
            <div class="text-center text-gray-500">No projects found</div>
        {:else}
            <div class="grid gap-4">
                {#each $projects as project (project.id)}
                    <Card.Root class="hover:bg-gray-50 transition-colors">
                        <button
                            class="w-full text-left"
                            on:click={() => handleProjectSelect(project.id)}
                        >
                            <Card.Header>
                                <Card.Title>{project.name}</Card.Title>
                                <Card.Description class="pb-4">{project.description}</Card.Description>
                            </Card.Header>
                        </button>
                    </Card.Root>
                {/each}
            </div>
        {/if}
    </div>
</div>
