<script lang="ts">
    import * as Card from '$lib/components/ui/card';
    import { Button } from "$lib/components/ui/button";

    export let errorMessage: string;
    export let onRetry: (() => void) | null = null;
    export let className: string = '';
</script>

<Card.Root class={`border-red-200 bg-red-50 ${className}`}>
    <Card.Header>
        <Card.Title class="text-red-800">Error</Card.Title>
        <Card.Description class="text-red-600 pt-2 pb-4">
            {errorMessage}
        </Card.Description>
    </Card.Header>
    <Card.Footer class="flex justify-end">
        {#if onRetry}
            <Button 
                variant="outline" 
                class="border-red-200 text-red-800 hover:bg-red-100"
                on:click={onRetry}
            >
                Try Again
            </Button>
        {/if}
    </Card.Footer>
</Card.Root>
