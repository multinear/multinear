<script lang="ts">
    import * as Table from "$lib/components/ui/table";
    import type { AggregationResultResponse } from '$lib/api';

    export let aggregation: AggregationResultResponse;

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

    // Convert aggregation results to sorted array (same as vertical table)
    $: sortedData = Object.entries(aggregation.results.results)
        .map(([key, data]) => {
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
        })
        .sort((a, b) => {
            // Sort lexicographically by field values (same as vertical table)
            for (let i = 0; i < Math.max(a.fieldValues.length, b.fieldValues.length); i++) {
                const aVal = i < a.fieldValues.length ? a.fieldValues[i] : '';
                const bVal = i < b.fieldValues.length ? b.fieldValues[i] : '';
                const comparison = aVal.localeCompare(bVal);
                if (comparison !== 0) {
                    return comparison;
                }
            }
            return 0;
        });

    // Create hierarchical headers structure
    $: headerStructure = (() => {
        if (aggregation.results.fields.length === 0) {
            return { rows: [], totalColumns: sortedData.length };
        }

        const numFields = aggregation.results.fields.length;
        const rows: any[][] = [];
        
        // Initialize rows for each field level
        for (let i = 0; i < numFields; i++) {
            rows.push([]);
        }

        // Track current position for each level
        let currentPositions: { [level: number]: string } = {};
        let columnSpans: { [level: number]: { value: string, start: number, count: number } } = {};

        sortedData.forEach((item, index) => {
            for (let level = 0; level < numFields; level++) {
                const fieldValue = level < item.fieldValues.length ? item.fieldValues[level] : '';
                
                // Check if this field value is different from the previous column
                if (currentPositions[level] !== fieldValue) {
                    // Close previous span if exists
                    if (columnSpans[level]) {
                        rows[level].push({
                            value: columnSpans[level].value,
                            colspan: columnSpans[level].count,
                            start: columnSpans[level].start
                        });
                    }
                    
                    // Start new span
                    columnSpans[level] = {
                        value: fieldValue,
                        start: index,
                        count: 1
                    };
                    currentPositions[level] = fieldValue;
                    
                    // Reset all deeper levels when a higher level changes
                    for (let resetLevel = level + 1; resetLevel < numFields; resetLevel++) {
                        if (columnSpans[resetLevel]) {
                            rows[resetLevel].push({
                                value: columnSpans[resetLevel].value,
                                colspan: columnSpans[resetLevel].count,
                                start: columnSpans[resetLevel].start
                            });
                        }
                        currentPositions[resetLevel] = '';
                        delete columnSpans[resetLevel];
                    }
                } else {
                    // Same field value, increment count
                    columnSpans[level].count++;
                }
            }
        });

        // Close remaining spans
        for (let level = 0; level < numFields; level++) {
            if (columnSpans[level]) {
                rows[level].push({
                    value: columnSpans[level].value,
                    colspan: columnSpans[level].count,
                    start: columnSpans[level].start
                });
            }
        }

        return { rows, totalColumns: sortedData.length };
    })();
</script>

<div class="w-full">
    {#if sortedData.length > 0}
        <div class="overflow-x-auto">
            <Table.Root>
                <Table.Header>
                    <!-- Hierarchical field value headers -->
                    {#each headerStructure.rows as row, rowIndex}
                        <Table.Row class="bg-gray-50">
                            {#each row as header}
                                <Table.Head 
                                    class="text-center border-r border-gray-300 px-2 py-1 text-sm font-medium"
                                    colspan={header.colspan}
                                >
                                    <div class="min-w-[60px]">
                                        {header.value}
                                    </div>
                                </Table.Head>
                            {/each}
                        </Table.Row>
                    {/each}
                    
                </Table.Header>
                
                <Table.Body>
                    <!-- Score values row -->
                    <Table.Row class="hover:bg-gray-50">
                        {#each sortedData as item}
                            <Table.Cell class="text-center border-r border-gray-300 px-2 py-2 {getScoreBackgroundClass(item.score)}">
                                <div class="flex flex-col items-center gap-1">
                                    <span class="{getScoreColorClass(item.score)} font-medium text-sm">
                                        {(item.score * 100).toFixed(1)}%
                                    </span>
                                    <div class="text-xs text-gray-500">
                                        {item.count} tasks
                                    </div>
                                </div>
                            </Table.Cell>
                        {/each}
                    </Table.Row>
                </Table.Body>
            </Table.Root>
        </div>
        
        <!-- Summary -->
        <div class="mt-4 text-xs text-gray-500 text-center">
            {sortedData.length} groups total • Sorted by {aggregation.results.fields.map(formatFieldName).join(' → ')}
        </div>
    {:else}
        <div class="text-center py-8 text-gray-500">
            <p>No data available for horizontal table view.</p>
        </div>
    {/if}
</div>