<script lang="ts">
    import StatusBadge from '$lib/components/StatusBadge.svelte';

    interface TaskStats {
        total: number;
        completed: number;
        failed: number;
        inProgress: number;
        avgScore: number;
    }

    export let runDetails: any;
    export let taskStats: TaskStats | null;
</script>

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

    <div class="grid grid-cols-2 md:grid-cols-4 gap-6 mb-6">
        <div>
            <h3 class="text-sm font-medium text-gray-500">Project</h3>
            <p class="mt-1 text-lg">{runDetails.project.name}</p>
        </div>
        <div>
            <h3 class="text-sm font-medium text-gray-500">Status</h3>
            <p class="mt-1">
                <StatusBadge status={runDetails.status} />
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
