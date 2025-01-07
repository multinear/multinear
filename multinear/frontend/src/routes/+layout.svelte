<script lang="ts">
	import '../app.css';
	import '../lib/styles/styles.css';
	// import { Input } from '$lib/components/ui/input';
	import { Button } from '$lib/components/ui/button';
	import logo from '$lib/assets/logo.png';
	import NavLink from '$lib/components/NavLink.svelte';
	import { Book } from 'lucide-svelte';
	import { onMount } from 'svelte';
	import { getProjects } from '$lib/api';
	import { projects, projectsLoading, projectsError, selectedProjectId, selectedChallengeId } from '$lib/stores/projects';
	import { page } from '$app/stores';
	import { setupHashChangeHandler } from '$lib/stores/projects';
	import { afterNavigate } from '$app/navigation';

	let { children } = $props();

	const baseNavLinks = [
		{ href: '/', label: 'Home' },
	];

	// Dynamically add links based on the current page
	const navLinks = $derived.by(() => {
		const pathname = $page.url.pathname;
		let links = [...baseNavLinks];
		if ($selectedProjectId) {
			links.push({ href: `/experiments#${$selectedProjectId}`, label: 'Experiments' });
		}
		if (pathname.startsWith('/run')) {
			links.push({ href: pathname + $page.url.hash, label: 'Run' });
		}
		if (pathname.startsWith('/compare') || $selectedChallengeId) {
			links.push({ 
				href: `/compare#${$selectedProjectId}/c:${$selectedChallengeId}`, 
				label: 'Compare' 
			});
		}
		return links;
	});

	onMount(() => {
		const { cleanup: hashCleanup } = setupHashChangeHandler();
		
		// Re-run hash handler after navigation
		afterNavigate(() => {
			setupHashChangeHandler();
		});

		const loadProjects = async () => {
			try {
				const response = await getProjects();
				if (!response) {
					projectsError.set("Invalid response from server");
					return;
				}
				projects.set(response);
			} catch (e) {
				projectsError.set(e instanceof Error ? e.message : "Failed to load projects");
				console.error(e);
			} finally {
				projectsLoading.set(false);
			}
		};

		loadProjects();

		return () => {
			hashCleanup();
		};
	});
</script>

<!-- Top Navigation Bar -->
<div class="min-h-screen flex flex-col">
	<nav class="bg-gray-800 p-4">
		<div class="container mx-auto flex justify-between items-center">
			<!-- Left side: Logo and Links -->
			<!-- space-x-4 -->
			<div class="flex items-center">
				<a href="/" class="flex items-center">
					<img src={logo} alt="Logo" class="h-8 w-10 mr-4" />
					<div class="text-lg text-white font-bold pr-8">Multinear</div>
				</a>
				{#each navLinks as link}
					<NavLink href={link.href} label={link.label} />
				{/each}
			</div>
			<!-- Right side: Search and Login -->
			<!-- <div class="flex items-center space-x-4">
				<Input type="search" placeholder="Search..." class="h-9 md:w-[100px] lg:w-[300px]" />
				<NavLink href="/settings" label="Settings" />
			</div> -->
		</div>
	</nav>

	<!-- Main Content -->
	<main class="flex-1 flex">
		{@render children()}
	</main>

	<!-- Footer -->
	<footer class="bg-gray-800 p-4">
		<div class="container mx-auto flex justify-between items-center text-gray-300">
			<!-- Left side: © symbol -->
			<div>
				<a href="https://multinear.com" target="_blank" rel="noopener noreferrer">
					&copy; 2025 Multinear.
				</a>
			</div>

			<!-- Right side: Links -->
			<div class="flex items-center">
				<!-- Documentation link -->
				<a href="https://multinear.com" target="_blank" rel="noopener noreferrer" class="">
					<Button variant="ghost" class="hover:bg-gray-700 text-gray-300 hover:text-gray-300 w-full flex items-center space-x-2">
						<Book class="h-6 w-6" />
						<span>Documentation</span>
					</Button>
				</a>
				<!-- GitHub link -->
				<a href="https://github.com/multinear" target="_blank" rel="noopener noreferrer" class="">
					<Button variant="ghost" class="hover:bg-gray-700 text-gray-300 hover:text-gray-300 w-full flex items-center space-x-2">
					<!-- GitHub SVG Logo -->
					<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="h-6 w-6">
						<path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.438 9.8 8.205 11.385.6.11.82-.26.82-.577v-2.17c-3.338.726-4.042-1.61-4.042-1.61-.546-1.387-1.333-1.756-1.333-1.756-1.09-.745.083-.73.083-.73 1.205.084 1.84 1.237 1.84 1.237 1.07 1.835 2.807 1.305 3.492.997.108-.775.42-1.305.763-1.605-2.665-.3-5.467-1.332-5.467-5.93 0-1.31.467-2.38 1.235-3.22-.123-.303-.535-1.523.117-3.176 0 0 1.007-.322 3.3 1.23.957-.266 1.983-.398 3.003-.403 1.02.005 2.046.137 3.003.403 2.29-1.552 3.297-1.23 3.297-1.23.653 1.653.24 2.873.118 3.176.77.84 1.233 1.91 1.233 3.22 0 4.61-2.807 5.625-5.48 5.92.43.37.823 1.102.823 2.222v3.293c0 .32.22.694.825.576C20.565 21.8 24 17.3 24 12c0-6.63-5.37-12-12-12z"/>
					</svg>
					<span>GitHub</span>
				</Button>
				</a>
			</div>
		</div>
	</footer>
</div>
