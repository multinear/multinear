<script lang="ts">
    import ScoreCircle from './ScoreCircle.svelte';
    import type { AggregationResultResponse } from '$lib/api';

    export let aggregation: AggregationResultResponse;

    // Helper function to format field names
    function formatFieldName(field: string): string {
        return field
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    // Helper function to format group labels
    function formatGroupLabel(key: string, fields: string[]): string {
        if (fields.length === 0) {
            return key;
        }
        
        const fieldValues = key.split('__');
        if (fieldValues.length === 1) {
            return fieldValues[0];
        }
        
        // For multiple fields, create a hierarchical label
        return fieldValues.map((value, index) => {
            const fieldName = fields[index] || `Field ${index + 1}`;
            return value;
        }).join(' · ');
    }

    // Helper function to create subtitle from metadata
    function formatSubtitle(key: string, fields: string[]): string {
        if (fields.length <= 1) {
            return '';
        }
        
        const fieldValues = key.split('__');
        return fieldValues.map((value, index) => {
            const fieldName = fields[index] || `Field ${index + 1}`;
            return `${formatFieldName(fieldName)}: ${value}`;
        }).join('\n');
    }

    // Convert aggregation data to sorted array
    $: circleData = Object.entries(aggregation.results.results)
        .map(([key, data]) => ({
            key,
            label: formatGroupLabel(key, aggregation.results.fields),
            subtitle: formatSubtitle(key, aggregation.results.fields),
            score: data.score,
            count: data.count,
            metadata: data.metadata || {}
        }))
        .sort((a, b) => b.score - a.score); // Sort by score descending

    // Group data by score ranges for better organization
    $: groupedData = {
        excellent: circleData.filter(item => item.score >= 0.8),
        good: circleData.filter(item => item.score >= 0.5 && item.score < 0.8),
        needsImprovement: circleData.filter(item => item.score < 0.5)
    };
</script>

<div class="space-y-6">
    {#if circleData.length > 0}
        <!-- Score ranges with labels -->
        {#if groupedData.excellent.length > 0}
            <div>
                <h4 class="text-sm font-medium text-green-700 mb-3">Excellent Performance (≥80%)</h4>
                <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
                    {#each groupedData.excellent as item}
                        <div class="flex flex-col items-center space-y-2 p-3 rounded-lg hover:bg-green-50 transition-colors">
                            <ScoreCircle 
                                score={item.score} 
                                showMinScore={false}
                                size="lg"
                            />
                            <div class="text-center">
                                <div class="text-sm font-medium text-gray-900 break-words">
                                    {item.label}
                                </div>
                                {#if item.subtitle}
                                    <div class="text-xs text-gray-500 mt-1 whitespace-pre-line">
                                        {item.subtitle}
                                    </div>
                                {/if}
                                <div class="text-xs text-gray-400 mt-1">
                                    {item.count} tasks
                                </div>
                            </div>
                        </div>
                    {/each}
                </div>
            </div>
        {/if}

        {#if groupedData.good.length > 0}
            <div>
                <h4 class="text-sm font-medium text-yellow-700 mb-3">Good Performance (50-79%)</h4>
                <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
                    {#each groupedData.good as item}
                        <div class="flex flex-col items-center space-y-2 p-3 rounded-lg hover:bg-yellow-50 transition-colors">
                            <ScoreCircle 
                                score={item.score} 
                                showMinScore={false}
                                size="lg"
                            />
                            <div class="text-center">
                                <div class="text-sm font-medium text-gray-900 break-words">
                                    {item.label}
                                </div>
                                {#if item.subtitle}
                                    <div class="text-xs text-gray-500 mt-1 whitespace-pre-line">
                                        {item.subtitle}
                                    </div>
                                {/if}
                                <div class="text-xs text-gray-400 mt-1">
                                    {item.count} tasks
                                </div>
                            </div>
                        </div>
                    {/each}
                </div>
            </div>
        {/if}

        {#if groupedData.needsImprovement.length > 0}
            <div>
                <h4 class="text-sm font-medium text-red-700 mb-3">Needs Improvement (&lt;50%)</h4>
                <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
                    {#each groupedData.needsImprovement as item}
                        <div class="flex flex-col items-center space-y-2 p-3 rounded-lg hover:bg-red-50 transition-colors">
                            <ScoreCircle 
                                score={item.score} 
                                showMinScore={false}
                                size="lg"
                            />
                            <div class="text-center">
                                <div class="text-sm font-medium text-gray-900 break-words">
                                    {item.label}
                                </div>
                                {#if item.subtitle}
                                    <div class="text-xs text-gray-500 mt-1 whitespace-pre-line">
                                        {item.subtitle}
                                    </div>
                                {/if}
                                <div class="text-xs text-gray-400 mt-1">
                                    {item.count} tasks
                                </div>
                            </div>
                        </div>
                    {/each}
                </div>
            </div>
        {/if}

        <!-- Summary statistics -->
        <div class="mt-6 p-4 bg-gray-50 rounded-lg">
            <h4 class="text-sm font-medium text-gray-700 mb-3">Summary</h4>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                    <div class="text-gray-600">Total Groups</div>
                    <div class="text-lg font-semibold">{circleData.length}</div>
                </div>
                <div>
                    <div class="text-gray-600">Average Score</div>
                    <div class="text-lg font-semibold">
                        {(() => {
                            const avg = circleData.reduce((sum, item) => sum + item.score, 0) / circleData.length;
                            return (avg * 100).toFixed(1);
                        })()}%
                    </div>
                </div>
                <div>
                    <div class="text-gray-600">Total Tasks</div>
                    <div class="text-lg font-semibold">
                        {circleData.reduce((sum, item) => sum + item.count, 0)}
                    </div>
                </div>
                <div>
                    <div class="text-gray-600">Groups ≥80%</div>
                    <div class="text-lg font-semibold text-green-600">
                        {groupedData.excellent.length}
                    </div>
                </div>
            </div>
        </div>
    {:else}
        <div class="text-center py-8 text-gray-500">
            <p>No data available for score circle visualization.</p>
        </div>
    {/if}
</div>