from pydantic import BaseModel, Field
from typing import Optional, Dict, List


class Project(BaseModel):
    """
    Schema representing a project.
    """
    id: str
    name: str
    description: str


class JobDetails(BaseModel):
    """
    Schema representing job details and status.
    """
    project_id: str
    job_id: str
    status: str
    total_tasks: int
    current_task: Optional[int] = None
    task_status_map: Optional[Dict] = None
    details: Optional[Dict] = None


class RecentRun(BaseModel):
    """
    Schema representing a recent run summary.
    """
    id: str
    revision: str
    model: str
    score: float
    totalTests: int
    task_id: Optional[str] = None
    pass_: int = Field(alias='pass')  # 'pass' is a Python keyword, so we use an alias
    fail: int
    regression: int
    bookmarked: Optional[bool] = False
    noted: Optional[bool] = False
    created_at: str
    finished_at: Optional[str] = None


class TaskDetails(BaseModel):
    """
    Schema representing detailed information about a task.
    """
    id: str
    challenge_id: str
    job_id: str
    status: str
    error: Optional[str] = None
    task_input: Optional[Dict] = None
    task_output: Optional[Dict] = None
    task_details: Optional[Dict] = None
    task_logs: Optional[Dict] = None
    eval_spec: Optional[Dict] = None
    eval_passed: Optional[bool] = None
    eval_score: Optional[float] = None
    eval_details: Optional[Dict] = None
    eval_logs: Optional[Dict] = None
    created_at: str
    executed_at: Optional[str] = None
    evaluated_at: Optional[str] = None
    finished_at: Optional[str] = None


class FullRunDetails(BaseModel):
    """
    Schema representing all details of a run, including tasks.
    """
    id: str
    project: Project
    details: Dict
    date: str
    status: str
    tasks: List[TaskDetails]


class RecentRunsResponse(BaseModel):
    """
    Schema representing the response for recent runs API.
    """
    runs: List[RecentRun]
    total: int


class AggregationResultData(BaseModel):
    """
    Schema representing individual aggregation result data.
    """
    score: float
    count: int
    metadata: Optional[Dict] = None


class AggregationGroupResult(BaseModel):
    """
    Schema representing aggregation results for a specific grouping.
    """
    fields: List[str]
    results: Dict[str, AggregationResultData]


class AggregationResultResponse(BaseModel):
    """
    Schema representing a single aggregation result.
    """
    id: str
    job_id: str
    aggregation_type: str
    results: AggregationGroupResult
    created_at: str


class AggregationSummaryResponse(BaseModel):
    """
    Schema representing all aggregation results for a job.
    """
    job_id: str
    aggregations: List[AggregationResultResponse]
    task_count: int
    total_tasks: int
