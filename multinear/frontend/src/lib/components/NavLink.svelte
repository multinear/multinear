<script lang="ts">
    import { Button } from "$lib/components/ui/button";
    import { page } from "$app/stores";
    export let href: string;
    export let label: string;



    function checkIsActive(href: string, pathname: string): boolean {
        return (
            href === pathname ||
            href.split('#')[0].startsWith(`${pathname}`) ||
            `${href.split('#')[0]}/`.startsWith(`${pathname}`) ||
            (href === '/' && pathname.startsWith('/dashboard'))
        );
    }

    $: isActive = checkIsActive(href, $page.url.pathname);
</script>

<a {href} class="block">
    <Button
        variant="ghost"
        class="hover:bg-gray-700 text-gray-300 hover:text-gray-300 w-full {isActive ? 'active-nav' : ''}"
    >
        {label}
    </Button>
</a>
<style>
    :global(.active-nav) {
        text-decoration: underline;
        text-underline-offset: 2px;
    }
</style>

