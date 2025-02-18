import { DropdownMenu as DropdownMenuPrimitive } from "bits-ui";
import Content from "./dropdown-menu-content.svelte";
import Item from "./dropdown-menu-item.svelte";
import Root from "./dropdown-menu.svelte";
import Trigger from "./dropdown-menu-trigger.svelte";

const DropdownMenu = DropdownMenuPrimitive.Root;

export {
	Root,
	Content,
	Item,
	Trigger,
	//
	Root as DropdownMenu,
	Content as DropdownMenuContent,
	Item as DropdownMenuItem,
	Trigger as DropdownMenuTrigger
}; 