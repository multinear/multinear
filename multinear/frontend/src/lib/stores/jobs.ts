import { writable, get } from 'svelte/store';
import { startExperiment, getJobStatus, startSingleTask } from '$lib/api';
import type { JobResponse } from '$lib/api';
import { goto } from '$app/navigation';

interface PendingRun {
    type: 'experiment' | 'task';
    projectId: string;
    challengeId?: string;
}

export const pendingRunStore = writable<PendingRun | null>(null);

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

export async function pollJobStatus(projectId: string, jobId: string, reloadRecentRuns: () => Promise<void>) {
    let status = 'started';
    while (!['completed', 'failed', 'not_found'].includes(status)) {
        await new Promise(r => setTimeout(r, 1000));
        try {
            const statusData = await getJobStatus(projectId, jobId);
            status = statusData.status;

            let counts: Record<string, number> = {};
            if (statusData.task_status_map && Object.keys(statusData.task_status_map).length > 0) {
                counts = Object.values(statusData.task_status_map).reduce((acc, status) => {
                    acc[status] = (acc[status] || 0) + 1;
                    return acc;
                }, {} as Record<string, number>);
            }

            // Check both top-level status and details.status for failure
            if (statusData.details?.status === 'failed' || statusData.details?.error) {
                status = 'failed';
                // Set the error in a way that JobStatus component will display it
                statusData.error = statusData.details.error;
            }

            jobStore.set({
                currentJob: jobId,
                jobStatus: status,
                jobDetails: statusData,
                taskStatusCounts: counts,
            });

            if (status === 'completed' && !statusData.details?.error) {
                await reloadRecentRuns();
            } else if (status === 'failed' || statusData.details?.error) {
                break;
            }
        } catch (error) {
            console.error('Error polling job status:', error);
            jobStore.set({
                currentJob: jobId,
                jobStatus: 'failed',
                jobDetails: {
                    project_id: projectId,
                    job_id: jobId,
                    status: 'failed',
                    total_tasks: 1,
                    current_task: 1,
                    task_status_map: {},
                    error: error instanceof Error ? error.message : 'Unknown error occurred'
                },
                taskStatusCounts: {},
            });
            break;
        }
    }
}

export async function handleStartExperiment(selectedProjectId: string, reloadRecentRuns: () => Promise<void>) {
    pendingRunStore.set({
        type: 'experiment',
        projectId: selectedProjectId
    });
    goto('/');
}

export async function handleRerunTask(projectId: string, challengeId: string, reloadRecentRuns: () => Promise<void>) {
    pendingRunStore.set({
        type: 'task',
        projectId,
        challengeId
    });
    goto('/');
}

export async function executePendingRun(reloadRecentRuns: () => Promise<void>) {
    const pendingRun = get(pendingRunStore);
    if (!pendingRun) return;
    
    try {
        const data = pendingRun.type === 'experiment' 
            ? await startExperiment(pendingRun.projectId)
            : await startSingleTask(pendingRun.projectId, pendingRun.challengeId!);
            
        const jobId = data.job_id;

        jobStore.update(state => ({
            ...state,
            currentJob: jobId,
            jobStatus: 'started',
            jobDetails: null,
            taskStatusCounts: {},
        }));

        await pollJobStatus(pendingRun.projectId, jobId, reloadRecentRuns);
    } catch (error) {
        console.error('Error executing pending run:', error);
        jobStore.set({
            currentJob: null,
            jobStatus: 'failed',
            jobDetails: {
                project_id: pendingRun.projectId,
                job_id: '',
                status: 'failed',
                total_tasks: 1,
                current_task: 1, // Set to 1 to show completion
                task_status_map: {},
                error: error instanceof Error ? error.message : 'Unknown error occurred'
            },
            taskStatusCounts: {},
        });
    } finally {
        pendingRunStore.set(null);
    }
}
