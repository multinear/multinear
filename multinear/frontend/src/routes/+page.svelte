<script lang="ts">
    import * as Card from "$lib/components/ui/card";
    import { Button } from "$lib/components/ui/button";
    import { goto } from '$app/navigation';
    import { projects, projectsLoading, projectsError } from '$lib/stores/projects';

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
            <Card.Root class="border-red-200 bg-red-50">
                <Card.Header>
                    <Card.Title class="text-red-800">Error</Card.Title>
                    <Card.Description class="text-red-600">
                        {$projectsError}
                        <p class="pt-1">Check if API is running</p>
                    </Card.Description>
                </Card.Header>
                <Card.Footer class="flex justify-end">
                    <Button 
                        variant="outline" 
                        class="border-red-200 text-red-800 hover:bg-red-100"
                        on:click={() => window.location.reload()}
                    >
                        Try Again
                    </Button>
                </Card.Footer>
            </Card.Root>
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
