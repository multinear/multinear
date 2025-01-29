from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey,
    Float,
    Boolean,
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.types import JSON
from datetime import datetime, timezone
from contextlib import contextmanager
from typing import Dict, Optional, List
import uuid
from pathlib import Path
import yaml


Base = declarative_base()


class TaskStatus:
    """
    Enumeration of task statuses.
    """
    STARTING = "starting"
    RUNNING = "running"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    FAILED = "failed"


# Define SQLAlchemy models to represent database tables
class ProjectModel(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    folder = Column(String, nullable=False)
    jobs = relationship("JobModel", back_populates="project")

    @classmethod
    def list(cls) -> List["ProjectModel"]:
        """
        List all projects
        """
        with db_context() as db:
            return db.query(cls).all()

    @classmethod
    def find(cls, project_id: str) -> Optional["ProjectModel"]:
        """
        Find a project by ID
        """
        with db_context() as db:
            return db.query(cls).filter(cls.id == project_id).first()

    @classmethod
    def save(cls, id: str, name: str, description: str, folder: str) -> "ProjectModel":
        """
        Save or update a project
        """
        with db_context() as db:
            project = db.query(cls).filter(cls.id == id).first()
            if project:
                """
                Update existing project
                """
                project.name = name
                project.description = description
                project.folder = folder
            else:
                """
                Create a new project
                """
                project = cls(id=id, name=name, description=description, folder=folder)
                db.add(project)
            db.commit()
            return project

    def to_dict(self):
        """
        Convert the ProjectModel to a dictionary, excluding SQLAlchemy internals
        """
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}


class JobModel(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    status = Column(String, nullable=False)
    total_tasks = Column(Integer, default=0)
    current_task = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    finished_at = Column(DateTime, nullable=True)
    project = relationship("ProjectModel", back_populates="jobs")
    tasks = relationship("TaskModel", back_populates="job")

    @classmethod
    def start(cls, project_id: str) -> str:
        """
        Start a new job for a project and return its ID.
        """
        job_id = str(uuid.uuid4())
        with db_context() as db:
            job = cls(id=job_id, project_id=project_id, status=TaskStatus.STARTING)
            db.add(job)
            db.commit()
            return job_id

    @classmethod
    def find(cls, job_id: str) -> Optional["JobModel"]:
        """
        Find a job by ID.
        """
        with db_context() as db:
            return db.query(cls).filter(cls.id == job_id).first()

    @classmethod
    def find_partial(cls, job_id: str) -> Optional["JobModel"]:
        """
        Find a job by partial ID.
        """
        with db_context() as db:
            return db.query(cls).filter(cls.id.like(f"%{job_id}")).first()

    def update(
        self,
        status: str = None,
        total_tasks: int = 0,
        current_task: Optional[int] = None,
        details: dict = None,
    ):
        """
        Update the job status and other fields.
        """
        with db_context() as db:
            job = db.query(JobModel).filter(JobModel.id == self.id).one()
            if status is not None:
                job.status = status
            if total_tasks is not None:
                job.total_tasks = total_tasks
            if current_task is not None:
                job.current_task = current_task
            if details is not None:
                current_details = job.details or {}
                merged_details = {**current_details, **details}
                job.details = merged_details
            db.commit()
            # Update the current instance
            if status is not None:
                self.status = status
            if total_tasks is not None:
                self.total_tasks = total_tasks
            if current_task is not None:
                self.current_task = current_task
            if details is not None:
                self.details = merged_details

    def finish(self, status: str = TaskStatus.COMPLETED):
        """
        Mark the job as finished.
        """
        finished_at = datetime.now(timezone.utc)
        with db_context() as db:
            job = db.query(JobModel).filter(JobModel.id == self.id).one()
            job.status = status
            job.finished_at = finished_at
            db.commit()
            # Update the current instance
            self.status = status
            self.finished_at = finished_at

    @classmethod
    def list_recent(
        cls, project_id: str, limit: int = 5, offset: int = 0
    ) -> List["JobModel"]:
        """
        List recent jobs for a project with pagination.
        """
        with db_context() as db:
            return (db.query(cls)
                    .filter(cls.project_id == project_id)
                    .order_by(cls.created_at.desc())
                    .offset(offset)
                    .limit(limit)
                    .all())

    @classmethod
    def get_status(cls, project_id: str, job_id: str) -> Optional["JobModel"]:
        """
        Get the status of a job, ensuring it belongs to the project.
        """
        with db_context() as db:
            return (db.query(cls)
                    .filter(cls.id == job_id, cls.project_id == project_id)
                    .first())

    def get_model_summary(self) -> str:
        """
        Get a summary of models used in this job's tasks.
        """
        with db_context() as db:
            tasks = db.query(TaskModel).filter(TaskModel.job_id == self.id).all()

            # Collect unique models from task details
            models = set()
            for task in tasks:
                if task.task_details and 'model' in task.task_details:
                    models.add(task.task_details['model'])

            # Return appropriate summary based on number of unique models
            if len(models) == 0:
                return "unknown"
            elif len(models) == 1:
                return models.pop()
            elif len(models) == 2:
                return " + ".join(sorted(models))
            else:
                return "multiple"

    @classmethod
    def count_jobs(cls, project_id: str) -> int:
        """
        Get the total count of jobs for a project.
        """
        with db_context() as db:
            return db.query(cls).filter(cls.project_id == project_id).count()


class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    challenge_id = Column(String, nullable=False)
    task_number = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    error = Column(String, nullable=True)
    task_input = Column(JSON, nullable=True)
    task_output = Column(JSON, nullable=True)
    task_details = Column(JSON, nullable=True)
    task_logs = Column(JSON, nullable=True)
    eval_spec = Column(JSON, nullable=True)
    eval_passed = Column(Boolean, nullable=True)
    eval_score = Column(Float, nullable=True)
    eval_details = Column(JSON, nullable=True)
    eval_logs = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    executed_at = Column(DateTime, nullable=True)
    evaluated_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    job = relationship("JobModel", back_populates="tasks")

    def to_dict(self):
        """
        Convert the TaskModel to a dictionary, excluding SQLAlchemy internals
        """
        data = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        for k, v in data.items():
            if isinstance(v, datetime):
                data[k] = v.isoformat()  # Convert datetime objects to ISO format strings
        return data

    @classmethod
    def start(cls, job_id: str, task_number: int, challenge_id: str) -> str:
        """
        Start a new task and return its ID.
        """
        task_id = str(uuid.uuid4())
        with db_context() as db:
            task = cls(
                id=task_id,
                job_id=job_id,
                task_number=task_number,
                status=TaskStatus.RUNNING,
                challenge_id=challenge_id
            )
            db.add(task)
            db.commit()
            return task_id

    @classmethod
    def executed(cls, task_id: str, input: any, output: any, details: dict, logs: dict):
        """
        Update the task as executed with results and logs.
        """
        with db_context() as db:
            task = db.query(cls).filter(cls.id == task_id).one()
            task.status = TaskStatus.EVALUATING
            task.task_input = input
            task.task_output = output
            task.task_details = details
            task.task_logs = logs
            task.executed_at = datetime.now(timezone.utc)
            db.commit()

    @classmethod
    def evaluated(
        cls,
        task_id: str,
        spec: dict,
        passed: bool,
        score: float,
        details: dict,
        logs: dict,
    ):
        """
        Update the task as evaluated and completed.
        """
        with db_context() as db:
            task = db.query(cls).filter(cls.id == task_id).one()
            task.status = TaskStatus.COMPLETED if passed else TaskStatus.FAILED
            task.eval_spec = spec
            task.eval_passed = passed
            task.eval_score = score
            task.eval_details = details
            task.eval_logs = logs
            task.evaluated_at = task.finished_at = datetime.now(timezone.utc)
            db.commit()

    @classmethod
    def fail(cls, task_id: str, error: str):
        """
        Mark the task as failed with an error message.
        """
        with db_context() as db:
            task = db.query(cls).filter(cls.id == task_id).one()
            task.status = TaskStatus.FAILED
            task.error = error
            task.finished_at = datetime.now(timezone.utc)
            db.commit()

    @classmethod
    def list(cls, job_id: str):
        """
        List all tasks associated with a job.
        """
        with db_context() as db:
            return db.query(cls).filter(cls.job_id == job_id).all()

    @classmethod
    def get_status_map(cls, job_id: str) -> Dict[str, str]:
        """
        Get a mapping of task IDs to their statuses for a job.
        """
        with db_context() as db:
            tasks = db.query(cls).filter(cls.job_id == job_id).all()
            return {task.id: task.status for task in tasks}

    @classmethod
    def find_same_tasks(
        cls, project_id: str, challenge_id: str, limit: int = 10, offset: int = 0
    ) -> List["TaskModel"]:
        """
        Find tasks with the same challenge ID within a project.
        """
        with db_context() as db:
            return (
                db.query(cls)
                .join(JobModel, cls.job_id == JobModel.id)
                .filter(
                    cls.challenge_id == challenge_id,
                    JobModel.project_id == project_id,
                    cls.finished_at.isnot(None)  # Only finished tasks
                )
                .order_by(cls.created_at.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )


# Database session management

# Global variable to store SessionLocal
_SessionLocal = None


def init_db():
    """
    Initialize the database engine and create tables if they don't exist.
    """
    DATABASE_URL = "sqlite:///./.multinear/multinear.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    global _SessionLocal
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create tables defined by the models
    Base.metadata.create_all(bind=engine)


def _create_session():
    """
    Internal function to create a new database session.
    """
    global _SessionLocal
    if _SessionLocal is None:
        init_db()
    return _SessionLocal()


@contextmanager
def db_context():
    """
    Provide a transactional scope around a series of operations.
    """
    db = _create_session()
    try:
        yield db
    finally:
        db.close()


def get_db():
    """
    Get a database session for FastAPI dependency injection.
    """
    with db_context() as db:
        yield db


def init_project_db(config_path: Optional[Path] = None):
    """
    Initialize the API by setting up the database and loading project configurations.

    This function performs the following steps:
    1. Initializes the database connection and creates necessary tables.
    2. Loads the project configuration from the specified config file or default .multinear/config.yaml.
    3. Extracts project details and saves or updates the project in the database.

    Args:
        config_path: Optional path to a custom config.yaml file. If not provided, uses default.
    """
    # Initialize the database and read the project configuration
    init_db()

    # Get the current working directory
    current_dir = Path.cwd()

    # Use provided config path or default
    if config_path is None:
        config_path = current_dir / ".multinear" / "config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Extract project details
    project_id = config["project"]["id"]
    project_data = {
        "id": project_id,
        "name": config["project"]["name"],
        "description": config["project"]["description"],
        "folder": str(current_dir)
    }

    # Update or create the project in the database on startup
    ProjectModel.save(
        id=project_id,
        name=project_data["name"],
        description=project_data["description"],
        folder=project_data["folder"]
    )
    return project_id
