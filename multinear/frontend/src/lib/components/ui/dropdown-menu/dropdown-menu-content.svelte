<script lang="ts">
	import { DropdownMenu as DropdownMenuPrimitive } from "bits-ui";
	import { cn } from "$lib/utils/styles";
	import { fade } from "svelte/transition";

	export let align: "start" | "center" | "end" = "start";
	export let sideOffset = 4;
</script>

<DropdownMenuPrimitive.Content
	{align}
	{sideOffset}
	transition={fade}
	class={cn(
		"z-50 min-w-[8rem] overflow-hidden rounded-md border bg-popover p-1 text-popover-foreground shadow-md",
		$$props.class
	)}
	{...$$restProps}
>
	<slot />
</DropdownMenuPrimitive.Content> 