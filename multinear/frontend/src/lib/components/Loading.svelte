<script lang="ts">
    import { Loader2 } from "lucide-svelte";

    export let message: string = "Loading...";
</script>

<div class="flex items-center justify-center py-8 text-gray-500">
    <div class="flex items-center gap-2">
        <Loader2 class="h-6 w-6 animate-spin" />
        <span>{message}</span>
    </div>
</div>
