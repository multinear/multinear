<script lang="ts">
    import { Button } from "$lib/components/ui/button";
    import { Label } from "$lib/components/ui/label";

    export let statusFilter: string = "";
    export let statusCounts: Record<string, number> = {};
    export let totalCount: number;
    export let selectedFilter: boolean = false;
    export let selectedCount: number | null = null;

    $: availableStatuses = Object.entries(statusCounts)
        .filter(([_, count]) => count > 0)
        .map(([status]) => status);

    function handleFilterClick(newStatus: string, newSelectedFilter: boolean) {
        statusFilter = newStatus;
        selectedFilter = newSelectedFilter;
    }
</script>

<div class="flex flex-col space-y-1.5">
    <Label>Filter</Label>
    <div class="flex gap-2">
        <Button
            variant="outline"
            size="sm"
            class={statusFilter === "" && !selectedFilter ? 'bg-gray-100 border-gray-200' : ''}
            on:click={() => handleFilterClick("", false)}
        >
            All tasks ({totalCount})
        </Button>

        {#if selectedCount !== null && selectedCount > 0}
            <Button
                variant="outline"
                size="sm"
                class={selectedFilter ? 'bg-blue-50 border-blue-200 text-blue-700' : ''}
                on:click={() => handleFilterClick("", true)}
            >
                Selected ({selectedCount})
            </Button>
        {/if}

        {#each availableStatuses as status}
            <Button
                variant="outline"
                size="sm"
                class={`
                    ${status === 'completed' ? 'text-green-700' : 
                      status === 'failed' ? 'text-red-700' : 
                      'text-gray-700'}
                    ${statusFilter === status && !selectedFilter ? 
                      status === 'completed' ? 'bg-green-50 border-green-200' :
                      status === 'failed' ? 'bg-red-50 border-red-200' :
                      'bg-gray-50 border-gray-200' : ''}
                `}
                on:click={() => handleFilterClick(status, false)}
            >
                {status} ({statusCounts[status]})
            </Button>
        {/each}
    </div>
</div> 