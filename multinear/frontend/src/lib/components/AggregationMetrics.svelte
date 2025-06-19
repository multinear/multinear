<script lang="ts">
    import { onMount } from 'svelte';
    import * as Card from "$lib/components/ui/card";
    import { Button } from "$lib/components/ui/button";
    import { Input } from "$lib/components/ui/input";
    import * as Select from "$lib/components/ui/select";
    import { ChevronDown, ChevronRight, BarChart3, Table, Table2, Circle, Filter, X } from 'lucide-svelte';
    import { getJobAggregations, type AggregationSummaryResponse, type AggregationResultResponse } from '$lib/api';
    import Loading from './Loading.svelte';
    import ErrorDisplay from './ErrorDisplay.svelte';
    import AggregationTable from './AggregationTable.svelte';
    import AggregationBarChart from './AggregationBarChart.svelte';
    import AggregationScoreCircles from './AggregationScoreCircles.svelte';
    import AggregationHorizontalTable from './AggregationHorizontalTable.svelte';

    export let runId: string;

    // Component state
    let isExpanded = false;
    let loading = false;
    let error: string | null = null;
    let aggregationData: AggregationSummaryResponse | null = null;
    let selectedTabIndex = 0;
    let selectedDisplayType = "table";

    // Filtering state (shared across all views)
    let showFilters = false;
    let fieldFilters: Record<string, string> = {};
    let scoreFilter = { min: '', max: '' };
    let countFilter = { min: '', max: '' };

    // Display type options
    const displayTypes = [
        { value: "table", label: "Table", icon: Table },
        { value: "horizontal", label: "Horizontal Table", icon: Table2 },
        { value: "chart", label: "Bar Chart", icon: BarChart3 },
        { value: "circles", label: "Score Circles", icon: Circle }
    ];

    // Helper function to format aggregation type names
    function formatAggregationType(type: string): string {
        return type
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    // Helper function to format field names
    function formatFieldName(field: string): string {
        return field
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    // Load aggregation data when expanded for the first time
    async function loadAggregationData() {
        if (aggregationData) return; // Already loaded
        
        loading = true;
        error = null;
        
        try {
            aggregationData = await getJobAggregations(runId);
        } catch (e) {
            error = e instanceof Error ? e.message : "Failed to load aggregation data";
            console.error('Error loading aggregations:', e);
        } finally {
            loading = false;
        }
    }

    // Toggle expansion and load data if needed
    async function toggleExpanded() {
        isExpanded = !isExpanded;
        if (isExpanded && !aggregationData && !loading) {
            await loadAggregationData();
        }
    }

    // Handle keyboard shortcut
    function handleKeydown(event: KeyboardEvent) {
        if (event.target instanceof HTMLInputElement || 
            event.target instanceof HTMLTextAreaElement) {
            return;
        }
        
        // Use 'g' key to avoid conflict with existing shortcuts
        if (event.key === 'g' || event.key === 'G') {
            toggleExpanded();
        }
    }

    // Clear all filters
    function clearFilters() {
        fieldFilters = {};
        scoreFilter = { min: '', max: '' };
        countFilter = { min: '', max: '' };
    }

    // Check if any filters are active
    $: hasActiveFilters = Object.values(fieldFilters).some(v => v.trim()) || 
                         scoreFilter.min || scoreFilter.max || 
                         countFilter.min || countFilter.max;

    // Get current aggregation data for selected tab
    $: currentAggregation = aggregationData?.aggregations[selectedTabIndex] || null;
    $: hasAggregations = aggregationData && aggregationData.aggregations.length > 0;

    // Apply filters to current aggregation data
    $: filteredAggregation = currentAggregation ? (() => {
        if (!hasActiveFilters) return currentAggregation;

        const filteredResults: Record<string, any> = {};
        
        Object.entries(currentAggregation.results.results).forEach(([key, data]) => {
            const fieldValues = currentAggregation.results.fields.length > 0 
                ? key.split('__')
                : [key];
            
            // Apply field filters
            let passesFieldFilters = true;
            for (let i = 0; i < currentAggregation.results.fields.length; i++) {
                const field = currentAggregation.results.fields[i];
                const filterValue = fieldFilters[field];
                if (filterValue && filterValue.trim()) {
                    const fieldValue = i < fieldValues.length ? fieldValues[i] : '';
                    if (!fieldValue.toLowerCase().includes(filterValue.toLowerCase())) {
                        passesFieldFilters = false;
                        break;
                    }
                }
            }
            
            if (!passesFieldFilters) return;

            // Apply score filter
            if (scoreFilter.min && data.score < parseFloat(scoreFilter.min) / 100) {
                return;
            }
            if (scoreFilter.max && data.score > parseFloat(scoreFilter.max) / 100) {
                return;
            }

            // Apply count filter
            if (countFilter.min && data.count < parseInt(countFilter.min)) {
                return;
            }
            if (countFilter.max && data.count > parseInt(countFilter.max)) {
                return;
            }

            filteredResults[key] = data;
        });

        return {
            ...currentAggregation,
            results: {
                ...currentAggregation.results,
                results: filteredResults
            }
        };
    })() : null;

    onMount(() => {
        // Optional: Auto-expand if there are aggregations (for testing)
        // You can remove this for production to keep collapsed by default
    });
</script>

<svelte:window on:keydown={handleKeydown} />

<Card.Root class="mb-6">
    <Card.Header class="pb-2">
        <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
                <Button 
                    variant="ghost" 
                    size="sm" 
                    class="h-6 w-6 p-0"
                    on:click={toggleExpanded}
                >
                    <ChevronRight 
                        class="h-4 w-4 transition-transform duration-200 text-gray-600 {isExpanded ? 'rotate-90' : ''}"
                    />
                </Button>
                <Card.Title class="text-lg">Aggregated Metrics</Card.Title>
                {#if aggregationData}
                    <span class="text-sm text-gray-500">
                        ({aggregationData.task_count} evaluated / {aggregationData.total_tasks} total tasks)
                    </span>
                {/if}
            </div>
            {#if !isExpanded}
                <span class="text-xs text-gray-400">Press 'g' to expand</span>
            {/if}
        </div>
    </Card.Header>

    {#if isExpanded}
        <Card.Content class="pt-0">
            {#if loading}
                <Loading message="Loading aggregation metrics..." />
            {:else if error}
                <ErrorDisplay errorMessage={error} onRetry={loadAggregationData} />
            {:else if hasAggregations}
                <!-- Tabs for different aggregation types -->
                <div class="space-y-4">
                    <div class="flex flex-wrap gap-1 sm:gap-2 border-b border-gray-200 overflow-x-auto">
                        {#each aggregationData.aggregations as aggregation, index}
                            <button
                                class="px-3 sm:px-4 py-2 text-xs sm:text-sm font-medium rounded-t-lg transition-colors whitespace-nowrap
                                    {selectedTabIndex === index 
                                        ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50' 
                                        : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'}"
                                on:click={() => selectedTabIndex = index}
                            >
                                {formatAggregationType(aggregation.aggregation_type)}
                            </button>
                        {/each}
                    </div>

                    {#if currentAggregation}
                        <!-- Filter Controls -->
                        <div class="flex items-center justify-between">
                            <div class="flex items-center gap-2">
                                <Button
                                    variant="outline"
                                    size="sm"
                                    class="h-8 {showFilters ? 'bg-blue-50 border-blue-200' : ''}"
                                    on:click={() => showFilters = !showFilters}
                                >
                                    <Filter class="h-3 w-3 mr-1" />
                                    Filters
                                    {#if hasActiveFilters}
                                        <span class="ml-1 bg-blue-100 text-blue-800 text-xs px-1.5 py-0.5 rounded-full">
                                            {Object.values(fieldFilters).filter(v => v.trim()).length + 
                                             (scoreFilter.min || scoreFilter.max ? 1 : 0) +
                                             (countFilter.min || countFilter.max ? 1 : 0)}
                                        </span>
                                    {/if}
                                </Button>
                                {#if hasActiveFilters}
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        class="h-8 text-gray-500"
                                        on:click={clearFilters}
                                    >
                                        <X class="h-3 w-3 mr-1" />
                                        Clear
                                    </Button>
                                {/if}
                            </div>
                            <div class="text-sm text-gray-500">
                                Showing {Object.keys(filteredAggregation?.results.results || {}).length} of {Object.keys(currentAggregation.results.results).length} groups
                            </div>
                        </div>

                        <!-- Filter Panel -->
                        {#if showFilters}
                            <div class="bg-gray-50 p-4 rounded-lg border">
                                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                    <!-- Field Filters -->
                                    {#each currentAggregation.results.fields as field}
                                        <div>
                                            <label for="filter-{field}" class="block text-sm font-medium text-gray-700 mb-1">
                                                {formatFieldName(field)}
                                            </label>
                                            <Input
                                                id="filter-{field}"
                                                type="text"
                                                placeholder="Filter..."
                                                class="h-8"
                                                bind:value={fieldFilters[field]}
                                            />
                                        </div>
                                    {/each}

                                    <!-- Score Filter -->
                                    <div>
                                        <label for="score-filter" class="block text-sm font-medium text-gray-700 mb-1">
                                            Score Range (%)
                                        </label>
                                        <div class="flex gap-2">
                                            <Input
                                                id="score-filter"
                                                type="number"
                                                placeholder="Min"
                                                min="0"
                                                max="100"
                                                class="h-8"
                                                bind:value={scoreFilter.min}
                                            />
                                            <Input
                                                type="number"
                                                placeholder="Max"
                                                min="0"
                                                max="100"
                                                class="h-8"
                                                bind:value={scoreFilter.max}
                                            />
                                        </div>
                                    </div>

                                    <!-- Count Filter -->
                                    <div>
                                        <label for="count-filter" class="block text-sm font-medium text-gray-700 mb-1">
                                            Task Count Range
                                        </label>
                                        <div class="flex gap-2">
                                            <Input
                                                id="count-filter"
                                                type="number"
                                                placeholder="Min"
                                                min="0"
                                                class="h-8"
                                                bind:value={countFilter.min}
                                            />
                                            <Input
                                                type="number"
                                                placeholder="Max"
                                                min="0"
                                                class="h-8"
                                                bind:value={countFilter.max}
                                            />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        {/if}

                        <!-- Display type selector -->
                        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                            <div class="flex items-center gap-2">
                                <span class="text-sm font-medium text-gray-700">View as:</span>
                                <div class="flex gap-1">
                                    {#each displayTypes as type}
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            class="h-8 px-2 sm:px-3 text-xs {selectedDisplayType === type.value ? 'bg-gray-100 border-gray-300' : ''}"
                                            on:click={() => selectedDisplayType = type.value}
                                        >
                                            <svelte:component this={type.icon} class="h-3 w-3 sm:mr-1" />
                                            <span class="hidden sm:inline">{type.label}</span>
                                        </Button>
                                    {/each}
                                </div>
                            </div>
                            <div class="text-xs text-gray-500">
                                {Object.keys(currentAggregation.results.results).length} groups
                                {#if currentAggregation.results.fields.length > 0}
                                    <span class="hidden sm:inline">• Grouped by: {currentAggregation.results.fields.map(formatFieldName).join(', ')}</span>
                                {/if}
                            </div>
                        </div>

                        <!-- Content area -->
                        <div class="mt-4">
                            {#if selectedDisplayType === "table"}
                                <AggregationTable aggregation={filteredAggregation} />
                            {:else if selectedDisplayType === "horizontal"}
                                <AggregationHorizontalTable aggregation={filteredAggregation} />
                            {:else if selectedDisplayType === "chart"}
                                <AggregationBarChart aggregation={filteredAggregation} />
                            {:else if selectedDisplayType === "circles"}
                                <AggregationScoreCircles aggregation={filteredAggregation} />
                            {/if}
                        </div>
                    {/if}
                </div>
            {:else}
                <div class="text-center py-8 text-gray-500">
                    <p>No aggregation metrics available for this run.</p>
                    <p class="text-sm mt-1">Aggregations may not be configured for this experiment.</p>
                </div>
            {/if}
        </Card.Content>
    {/if}
</Card.Root>