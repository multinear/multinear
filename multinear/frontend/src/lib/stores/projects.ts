import { writable } from 'svelte/store';
import type { Project } from '$lib/api';

export const projects = writable<Project[]>([]);
export const projectsLoading = writable(true);
export const projectsError = writable<string | null>(null);
export const selectedProjectId = writable<string>('');
export const selectedRunId = writable<string>('');
export const selectedChallengeId = writable<string>('');
export const searchTerm = writable<string>('');

export function handlePageHashChange() {
    const hash = window.location.hash;
    const parts = hash ? hash.slice(1).split('/') : [];
    
    const projectId = parts[0] || '';
    selectedProjectId.set(projectId);
    
    const secondPart = parts[1] || '';
    const runId = secondPart.startsWith('r:') ? secondPart.slice(2) : '';
    const challengeId = secondPart.startsWith('c:') ? secondPart.slice(2) : '';
    const search = secondPart.startsWith('search:') ? secondPart.slice(7) : '';
    
    selectedRunId.set(runId);
    selectedChallengeId.set(challengeId);
    searchTerm.set(search);

    return { projectId, runId, challengeId, search };
}

export function setupHashChangeHandler() {
    const hashData = handlePageHashChange(); // Initial hash check
    window.addEventListener('hashchange', handlePageHashChange);
    return {
        ...hashData,
        cleanup: () => window.removeEventListener('hashchange', handlePageHashChange)
    };
}
