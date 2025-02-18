<script lang="ts">
	import { DropdownMenu as DropdownMenuPrimitive } from "bits-ui";

	export let asChild = false;
</script>

<DropdownMenuPrimitive.Trigger {asChild} {...$$restProps}>
	<slot />
</DropdownMenuPrimitive.Trigger> 