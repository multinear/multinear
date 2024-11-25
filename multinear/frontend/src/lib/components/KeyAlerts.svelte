<script lang="ts">
    import * as Card from '$lib/components/ui/card';
    import * as Alert from '$lib/components/ui/alert';
    import { AlertCircle, CheckCircle2, XCircle } from 'lucide-svelte';
    import type { KeyAlert } from '$lib/types/alerts';

    export let alerts: KeyAlert[] = [];

    // const alerts: KeyAlert[] = [
    //     {
    //         type: "regression",
    //         message: "Regression detected in security tests for RUN-003",
    //     },
    //     {
    //         type: "security",
    //         message: "Potential security vulnerability found in RUN-002",
    //     },
    //     {
    //         type: "improvement",
    //         message: "Significant improvement in evaluation score for RUN-004",
    //     },
    // ] as const;
</script>

{#if alerts.length > 0}
    <Card.Root>
        <Card.Header>
            <Card.Title>Key Alerts and Notifications</Card.Title>
        </Card.Header>
        <Card.Content class="space-y-4">
            {#each alerts as alert, index (index)}
                <Alert.Root
                    variant={alert.type === "improvement" ? "default" : "destructive"}
                >
                    {#if alert.type === "regression"}
                        <AlertCircle class="h-4 w-4" />
                    {:else if alert.type === "security"}
                        <XCircle class="h-4 w-4" />
                    {:else if alert.type === "improvement"}
                        <CheckCircle2 class="h-4 w-4" />
                    {/if}
                    <Alert.Title>
                        {alert.type.charAt(0).toUpperCase() + alert.type.slice(1)}
                    </Alert.Title>
                    <Alert.Description>{alert.message}</Alert.Description>
                </Alert.Root>
            {/each}
        </Card.Content>
    </Card.Root>
{/if}
