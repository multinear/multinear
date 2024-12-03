<script lang="ts">
    export let status: string;
    export let className: string = '';
</script>

<span class={`inline-flex items-center px-2.5 py-0.5 rounded-full text-sm font-medium border
    ${status === 'completed' ? 'status-completed status-completed-border' : 
    status === 'failed' ? 'status-failed status-failed-border' : 
    'status-default status-default-border'} ${className}`}>
    {status}
</span>
