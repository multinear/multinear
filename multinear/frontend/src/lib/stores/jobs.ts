import { writable } from 'svelte/store';
import { startExperiment, getJobStatus } from '$lib/api';
import type { JobResponse } from '$lib/api';


export interface JobState {
    currentJob: string | null;
    jobStatus: string | null;
    jobDetails: JobResponse | null;
    taskStatusCounts: Record<string, number>;
}

export const jobStore = writable<JobState>({
    currentJob: null,
    jobStatus: null,
    jobDetails: null,
    taskStatusCounts: {},
});

export async function handleStartExperiment(selectedProjectId: string, reloadRecentRuns: () => Promise<void>) {
    try {
        const data = await startExperiment(selectedProjectId);
        const jobId = data.job_id;

        jobStore.update(state => ({
            ...state,
            currentJob: jobId,
            jobStatus: 'started',
            jobDetails: null,
            taskStatusCounts: {},
        }));

        // Polling for job status
        let status = 'started';
        while (!['completed', 'failed', 'not_found'].includes(status)) {
            await new Promise(r => setTimeout(r, 1000));
            const statusData = await getJobStatus(selectedProjectId, jobId);
            status = statusData.status;

            let counts: Record<string, number> = {};
            if (statusData.task_status_map && Object.keys(statusData.task_status_map).length > 0) {
                counts = Object.values(statusData.task_status_map).reduce((acc, status) => {
                    acc[status] = (acc[status] || 0) + 1;
                    return acc;
                }, {} as Record<string, number>);
            }

            jobStore.set({
                ...jobStore,
                currentJob: jobId,
                jobStatus: status,
                jobDetails: statusData,
                taskStatusCounts: counts,
            });

            if (status === 'completed') {
                await reloadRecentRuns();
            } else if (status === 'failed') {
                break;
            }
        }
    } catch (error) {
        console.error('Error:', error);
        jobStore.update(state => ({
            ...state,
            jobStatus: 'error',
        }));
    }
}
