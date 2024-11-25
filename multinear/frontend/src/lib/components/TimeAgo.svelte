<script lang="ts">
    import { formatDistanceToNow } from "date-fns";
    import * as Tooltip from "$lib/components/ui/tooltip";

    export let date: Date | string;

    const dateObj = new Date(date);
    $: timeAgo = formatDistanceToNow(dateObj, { addSuffix: true })
        .replace("about ", "~")
        .replace("less than a minute ago", "just now");
    $: fullDate = dateObj.toLocaleString(undefined, {
        dateStyle: "medium",
        timeStyle: "short",
    });
</script>

<Tooltip.Root>
    <Tooltip.Trigger class="cursor-default">
        {timeAgo}
    </Tooltip.Trigger>
    <Tooltip.Content>
        <p>{fullDate}</p>
    </Tooltip.Content>
</Tooltip.Root>
