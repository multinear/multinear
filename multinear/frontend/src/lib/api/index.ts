// const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_URL = import.meta.env.VITE_API_URL || '/api';

export interface Project {
    id: string;
    name: string;
    description: string;
}

export interface JobResponse {
    project_id: string;
    job_id: string;
    status: string;
    total_tasks: number;
    current_task?: number;
    task_status_map?: Record<string, string>;
    details?: Record<string, any>;
    error?: string;
}

export interface RecentRun {
    id: string;
    created_at: string;
    finished_at?: string;
    revision: string;
    model: string;
    score: number;
    totalTests: number;
    task_id?: string;
    pass: number;
    fail: number;
    regression: number;
    bookmarked?: boolean;
    noted?: boolean;
}

interface RecentRunsResponse {
    runs: RecentRun[];
    total: number;
}

export interface Task {
    id: string;
    name?: string;
    description?: string;
    input?: any;
}

export interface Group {
    id: string;
    name: string;
    description: string;
    task_count: number;
    tasks: Task[];
}

export interface TasksResponse {
    tasks: Task[];
    groups: Group[];
}

export async function getProjects(): Promise<Project[]> {
    const response = await fetch(`${API_URL}/projects`);
    if (!response.ok) {
        throw new Error(`Failed to fetch projects: ${response.statusText}`);
    }
    return response.json();
}

export async function startExperiment(projectId: string): Promise<JobResponse> {
    const response = await fetch(`${API_URL}/jobs/${projectId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    });
    if (!response.ok) {
        throw new Error(`Failed to start experiment: ${response.statusText}`);
    }
    return response.json();
}

export async function getJobStatus(projectId: string, jobId: string): Promise<JobResponse> {
    const response = await fetch(`${API_URL}/jobs/${projectId}/${jobId}/status`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    });
    if (!response.ok) {
        throw new Error(`Failed to fetch job status: ${response.statusText}`);
    }
    return response.json();
}

export async function getRecentRuns(projectId: string, limit: number = 5, offset: number = 0): Promise<RecentRunsResponse> {
    const response = await fetch(
        `${API_URL}/runs/${projectId}?limit=${limit}&offset=${offset}`,
        {
            headers: {
                'Content-Type': 'application/json',
            },
        }
    );

    if (!response.ok) {
        throw new Error(`Failed to fetch recent runs: ${response.statusText}`);
    }

    return response.json();
}

export async function getRunDetails(runId: string): Promise<any> {
    const response = await fetch(`${API_URL}/run-details/${runId}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch run details: ${response.statusText}`);
    }
    return response.json();
}

// TODO: TaskDetails
export async function getSameTasks(projectId: string, challengeId: string, limit: number = 10, offset: number = 0): Promise<any[]> {
    const response = await fetch(`${API_URL}/same-tasks/${projectId}/${challengeId}?limit=${limit}&offset=${offset}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch same tasks: ${response.statusText}`);
    }
    return response.json();
}

export async function startSingleTask(projectId: string, challengeId: string): Promise<JobResponse> {
    const response = await fetch(`${API_URL}/jobs/${projectId}/task/${challengeId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    });
    if (!response.ok) {
        throw new Error(`Failed to start task: ${response.statusText}`);
    }
    return response.json();
}

export async function getAvailableTasks(projectId: string): Promise<TasksResponse> {
    const response = await fetch(`${API_URL}/tasks/${projectId}`);
    if (!response.ok) {
        throw new Error(`Failed to get available tasks: ${response.statusText}`);
    }
    return response.json();
}

export async function startGroupRun(projectId: string, groupId: string): Promise<JobResponse> {
    const response = await fetch(`${API_URL}/jobs/${projectId}/group/${groupId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    });
    if (!response.ok) {
        throw new Error(`Failed to start group run: ${response.statusText}`);
    }
    return response.json();
}

// Aggregation interfaces
export interface AggregationResultData {
    score: number;
    count: number;
    metadata?: Record<string, any>;
}

export interface AggregationGroupResult {
    fields: string[];
    results: Record<string, AggregationResultData>;
}

export interface AggregationResultResponse {
    id: string;
    job_id: string;
    aggregation_type: string;
    results: AggregationGroupResult;
    created_at: string;
}

export interface AggregationSummaryResponse {
    job_id: string;
    aggregations: AggregationResultResponse[];
    task_count: number;
    total_tasks: number;
}

export async function getJobAggregations(jobId: string): Promise<AggregationSummaryResponse> {
    const response = await fetch(`${API_URL}/jobs/${jobId}/aggregations`);
    if (!response.ok) {
        throw new Error(`Failed to fetch job aggregations: ${response.statusText}`);
    }
    return response.json();
}

export async function getJobAggregationByType(jobId: string, aggregationType: string): Promise<AggregationResultResponse> {
    const response = await fetch(`${API_URL}/jobs/${jobId}/aggregations/${aggregationType}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch aggregation type ${aggregationType}: ${response.statusText}`);
    }
    return response.json();
}
