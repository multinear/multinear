<script lang="ts">
	import { DropdownMenu as DropdownMenuPrimitive } from "bits-ui";
	import { cn } from "$lib/utils/styles";

	export let inset = false;
	export let disabled = false;
</script>

<DropdownMenuPrimitive.Item>
	<button
		class={cn(
			"relative flex w-full cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground data-[highlighted]:bg-accent data-[highlighted]:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50",
			inset && "pl-8",
			$$props.class
		)}
		{disabled}
		on:click
		{...$$restProps}
	>
		<slot />
	</button>
</DropdownMenuPrimitive.Item> 