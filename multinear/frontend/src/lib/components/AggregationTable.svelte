<script lang="ts">
    import * as Table from "$lib/components/ui/table";
    import { Button } from "$lib/components/ui/button";
    import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-svelte';
    import type { AggregationResultResponse } from '$lib/api';

    export let aggregation: AggregationResultResponse;

    // Sorting state - default to sorting by field values (matching engine console output)
    let sortColumn: string | null = '_fieldValues';
    let sortDirection: 'asc' | 'desc' = 'asc';


    // Helper function to format field names
    function formatFieldName(field: string): string {
        return field
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    // Helper function to get score color class
    function getScoreColorClass(score: number): string {
        if (score >= 0.8) return 'text-green-600 font-medium';
        if (score >= 0.5) return 'text-yellow-600 font-medium';
        return 'text-red-600 font-medium';
    }

    // Helper function to get background color class for score
    function getScoreBackgroundClass(score: number): string {
        if (score >= 0.8) return 'bg-green-50';
        if (score >= 0.5) return 'bg-yellow-50';
        return 'bg-red-50';
    }

    // Helper function to get progress bar color class for score
    function getScoreProgressBarClass(score: number): string {
        if (score >= 0.8) return 'bg-green-400';
        if (score >= 0.5) return 'bg-yellow-400';
        return 'bg-red-400';
    }

    // Convert aggregation results to sortable array
    $: tableData = Object.entries(aggregation.results.results).map(([key, data]) => {
        // Split the key by '__' to get individual field values
        const fieldValues = aggregation.results.fields.length > 0 
            ? key.split('__')
            : [key];
        
        return {
            key,
            fieldValues,
            score: data.score,
            count: data.count,
            metadata: data.metadata || {}
        };
    });


    // Sort the table data
    $: sortedData = sortColumn 
        ? [...tableData].sort((a, b) => {
            let aValue, bValue;
            
            if (sortColumn === 'score') {
                aValue = a.score;
                bValue = b.score;
            } else if (sortColumn === 'count') {
                aValue = a.count;
                bValue = b.count;
            } else if (sortColumn === '_fieldValues') {
                // Sort by field values tuple (matching engine console output)
                // Compare lexicographically like Python tuple sorting
                for (let i = 0; i < Math.max(a.fieldValues.length, b.fieldValues.length); i++) {
                    const aVal = i < a.fieldValues.length ? a.fieldValues[i] : '';
                    const bVal = i < b.fieldValues.length ? b.fieldValues[i] : '';
                    const comparison = aVal.localeCompare(bVal);
                    if (comparison !== 0) {
                        return sortDirection === 'asc' ? comparison : -comparison;
                    }
                }
                return 0; // All field values are equal
            } else {
                // Field column
                const fieldIndex = aggregation.results.fields.indexOf(sortColumn);
                if (fieldIndex >= 0 && fieldIndex < a.fieldValues.length) {
                    aValue = a.fieldValues[fieldIndex];
                    bValue = b.fieldValues[fieldIndex];
                } else {
                    aValue = a.key;
                    bValue = b.key;
                }
            }
            
            if (typeof aValue === 'string' && typeof bValue === 'string') {
                const comparison = aValue.localeCompare(bValue);
                return sortDirection === 'asc' ? comparison : -comparison;
            } else {
                const comparison = (aValue as number) - (bValue as number);
                return sortDirection === 'asc' ? comparison : -comparison;
            }
        })
        : tableData;

    // Handle column sort
    function handleSort(column: string) {
        if (sortColumn === column) {
            sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            sortColumn = column;
            sortDirection = column === 'score' ? 'desc' : 'asc'; // Default to desc for score, asc for others
        }
    }

    // Get sort icon for column
    function getSortIcon(column: string) {
        // For field columns, check if we're sorting by field values tuple
        if (sortColumn === '_fieldValues' && aggregation.results.fields.includes(column)) {
            return sortDirection === 'asc' ? ArrowUp : ArrowDown;
        }
        if (sortColumn !== column) return ArrowUpDown;
        return sortDirection === 'asc' ? ArrowUp : ArrowDown;
    }

</script>

<!-- Table Container -->

    <!-- Table -->
    <div class="overflow-x-auto">
        <Table.Root>
        <Table.Header>
            <Table.Row>
                <!-- Dynamic field columns -->
                {#each aggregation.results.fields as field}
                    <Table.Head class="min-w-[120px]">
                        <Button
                            variant="ghost"
                            size="sm"
                            class="h-auto p-0 font-medium hover:bg-transparent"
                            on:click={() => handleSort(field)}
                        >
                            {formatFieldName(field)}
                            <svelte:component this={getSortIcon(field)} class="ml-1 h-3 w-3" />
                        </Button>
                    </Table.Head>
                {/each}
                
                <!-- Score column -->
                <Table.Head class="text-right min-w-[100px]">
                    <Button
                        variant="ghost"
                        size="sm"
                        class="h-auto p-0 font-medium hover:bg-transparent"
                        on:click={() => handleSort('score')}
                    >
                        Score
                        <svelte:component this={getSortIcon('score')} class="ml-1 h-3 w-3" />
                    </Button>
                </Table.Head>
                
                <!-- Count column -->
                <Table.Head class="text-right min-w-[80px]">
                    <Button
                        variant="ghost"
                        size="sm"
                        class="h-auto p-0 font-medium hover:bg-transparent"
                        on:click={() => handleSort('count')}
                    >
                        Count
                        <svelte:component this={getSortIcon('count')} class="ml-1 h-3 w-3" />
                    </Button>
                </Table.Head>
            </Table.Row>
        </Table.Header>
        <Table.Body>
            {#each sortedData as row}
                <Table.Row class="hover:bg-gray-50 h-10">
                    <!-- Field value columns -->
                    {#each aggregation.results.fields as field, fieldIndex}
                        <Table.Cell class="font-medium py-1">
                            {fieldIndex < row.fieldValues.length ? row.fieldValues[fieldIndex] : '-'}
                        </Table.Cell>
                    {/each}
                    
                    <!-- Score column -->
                    <Table.Cell class="text-right py-1">
                        <div class="inline-flex items-center gap-2">
                            <div class="w-16 bg-gray-200 rounded-full h-2">
                                <div 
                                    class="h-2 rounded-full transition-all duration-300 {getScoreProgressBarClass(row.score)}"
                                    style="width: {(row.score * 100).toFixed(1)}%"
                                ></div>
                            </div>
                            <span class="{getScoreColorClass(row.score)}">
                                {(row.score * 100).toFixed(1)}%
                            </span>
                        </div>
                    </Table.Cell>
                    
                    <!-- Count column -->
                    <Table.Cell class="text-right text-gray-600 py-1">
                        {row.count}
                    </Table.Cell>
                </Table.Row>
            {/each}
        </Table.Body>
    </Table.Root>
    </div>

    {#if sortedData.length === 0}
        <div class="text-center py-8 text-gray-500">
            <p>No data available for this aggregation.</p>
        </div>
    {/if}