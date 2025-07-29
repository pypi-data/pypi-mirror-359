import subprocess
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4
import json
import os

# Enums for TaskWarrior-specific fields
class TaskStatus(str, Enum):
    """Task status as defined by TaskWarrior."""
    PENDING = "pending"
    COMPLETED = "completed"
    DELETED = "deleted"
    WAITING = "waiting"
    RECURRING = "recurring"

class Priority(str, Enum):
    """Task priority levels in TaskWarrior."""
    HIGH = "H"
    MEDIUM = "M"
    LOW = "L"
    NONE = ""

class RecurrencePeriod(str, Enum):
    """Supported recurrence periods for tasks."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    QUARTERLY = "quarterly"
    SEMIANNUALLY = "semiannually"

# Pydantic Models
class Task(BaseModel):
    """Represents a TaskWarrior task as per the Task RFC."""
    id: Optional[int] = Field(default=None, description="Task ID assigned by TaskWarrior (None for new tasks).")
    uuid: UUID = Field(default_factory=uuid4, description="Unique identifier for the task.")
    description: str = Field(..., description="Task description (required).")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current status of the task.")
    priority: Priority = Field(default=Priority.NONE, description="Priority of the task (H, M, L, or empty).")
    due: Optional[datetime] = Field(default=None, description="Due date and time for the task.")
    entry: datetime = Field(default_factory=datetime.now, description="Task creation date and time.")
    modified: Optional[datetime] = Field(default=None, description="Last modification date and time.")
    tags: List[str] = Field(default_factory=list, description="List of tags associated with the task.")
    project: Optional[str] = Field(default=None, description="Project the task belongs to.")
    depends: List[UUID] = Field(default_factory=list, description="List of UUIDs of tasks this task depends on.")
    recur: Optional[RecurrencePeriod] = Field(default=None, description="Recurrence period for recurring tasks.")
    until: Optional[datetime] = Field(default=None, description="Expiration date for recurring tasks.")
    annotations: List[str] = Field(default_factory=list, description="List of annotations for the task.")
    context: Optional[str] = Field(default=None, description="Context filter for the task.")
    urgency: Optional[float] = Field(default=None, description="Computed urgency score by TaskWarrior.")

    @validator("description")
    def description_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Description cannot be empty")
        return v.strip()

    @validator("tags")
    def validate_tags(cls, v):
        return [tag.strip() for tag in v if tag.strip()]

    class Config:
        use_enum_values = True  # Store enum values as strings
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str,
        }

class TaskWarriorAPI:
    """A Python API wrapper for TaskWarrior, interacting via CLI commands."""

    def __init__(self, taskrc_path: Optional[str] = None):
        """
        Initialize the TaskWarrior API.

        Args:
            taskrc_path: Optional path to the .taskrc file. If None, uses default.
        """
        # self.taskrc = taskrc_path
        self.taskrc = os.environ['TASKRC']
        self.base_command = ["task"] if not self.taskrc else ["task", f"rc:{taskrc_path}"]

    def _run_task_command(self, args: List[str]) -> subprocess.CompletedProcess:
        """
        Execute a TaskWarrior command via subprocess.

        Args:
            args: List of command arguments to append to the base task command.

        Returns:
            subprocess.CompletedProcess: Result of the command execution.

        Raises:
            RuntimeError: If the command fails.
        """
        print(
                self.base_command + args,
            )

        try:
            result = subprocess.run(
                self.base_command + args,
                capture_output=True,
                text=True,
                check=True,
            )
            return result
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"TaskWarrior command failed: {e.stderr}")

    def add_task(self, task: Task) -> Task:
        """
        Add a new task to TaskWarrior.

        Args:
            task: Task object to add.

        Returns:
            Task: Updated task object with ID and UUID from TaskWarrior.
        """
        args = ["add", task.description]
        if task.priority:
            args.extend(["priority:" + task.priority])
        if task.due:
            args.extend(["due:" + task.due.isoformat()])
        if task.project:
            args.extend(["project:" + task.project])
        if task.tags:
            args.extend([f"+{tag}" for tag in task.tags])
        if task.recur:
            args.extend(["recur:" + task.recur])
        if task.until:
            args.extend(["until:" + task.until.isoformat()])
        if task.depends:
            args.extend(["depends:" + ",".join(str(uuid) for uuid in task.depends)])
        if task.context:
            args.extend(["context:" + task.context])

        result = self._run_task_command(args)
        # Extract task ID and UUID from output
        task_id = None
        uuid = task.uuid
        for line in result.stdout.splitlines():
            print(line)
            if "Created task" in line:
                task_id = line.removeprefix('Created task ').split()[0] #int(line.split()[-1].strip("."))
            if "UUID" in line:
                uuid = UUID(line.split()[-1])

        return task.copy(update={"id": task_id, "uuid": uuid, "modified": datetime.now()})

    def modify_task(self, task: Task) -> Task:
        """
        Modify an existing task in TaskWarrior.

        Args:
            task: Task object with updated fields.

        Returns:
            Task: Updated task object.

        Raises:
            ValueError: If task ID or UUID is missing.
        """
        if not task.id and not task.uuid:
            raise ValueError("Task ID or UUID required to modify a task")

        args = [str(task.id) or str(task.uuid), "modify"]
        if task.description:
            args.extend(["description:" + task.description])
        if task.priority:
            args.extend(["priority:" + task.priority])
        if task.due:
            args.extend(["due:" + task.due.isoformat()])
        if task.project:
            args.extend(["project:" + task.project])
        if task.tags:
            args.extend([f"+{tag}" for tag in task.tags])
        if task.recur:
            args.extend(["recur:" + task.recur])
        if task.until:
            args.extend(["until:" + task.until.isoformat()])
        if task.depends:
            args.extend(["depends:" + ",".join(str(uuid) for uuid in task.depends)])
        if task.context:
            args.extend(["context:" + task.context])

        self._run_task_command(args)
        return task.copy(update={"modified": datetime.now()})

    def delete_task(self, task_id_or_uuid: str) -> None:
        """
        Delete a task by ID or UUID.

        Args:
            task_id_or_uuid: Task ID or UUID to delete.
        """
        self._run_task_command([task_id_or_uuid, "delete"])

    def complete_task(self, task_id_or_uuid: str) -> None:
        """
        Mark a task as completed.

        Args:
            task_id_or_uuid: Task ID or UUID to complete.
        """
        self._run_task_command([task_id_or_uuid, "done"])

    def list_tasks(self, status: TaskStatus = TaskStatus.PENDING) -> List[Task]:
        """
        List tasks filtered by status.

        Args:
            status: Task status to filter by (default: pending).

        Returns:
            List[Task]: List of Task objects.
        """
        args = ["export", f"status:{status}"]
        result = self._run_task_command(args)
        tasks_data = json.loads(result.stdout)
        return [Task(**data) for data in tasks_data]

    def add_annotation(self, task_id_or_uuid: str, annotation: str) -> None:
        """
        Add an annotation to a task.

        Args:
            task_id_or_uuid: Task ID or UUID.
            annotation: Annotation text to add.
        """
        self._run_task_command([task_id_or_uuid, "annotate", annotation])

    def set_context(self, context_name: str) -> None:
        """
        Set the current context for task filtering.

        Args:
            context_name: Name of the context to set.
        """
        self._run_task_command(["context", context_name])

    def get_task(self, task_id_or_uuid: str) -> Task:
        """
        Retrieve a task by ID or UUID.

        Args:
            task_id_or_uuid: Task ID or UUID.

        Returns:
            Task: Task object.

        Raises:
            RuntimeError: If task is not found.
        """
        result = self._run_task_command([task_id_or_uuid, "export"])
        tasks_data = json.loads(result.stdout)
        if not tasks_data:
            raise RuntimeError(f"Task {task_id_or_uuid} not found")
        return Task(**tasks_data[0])

# Example Usage
if __name__ == "__main__":
    api = TaskWarriorAPI('api_taskrc')

    # Create a new task
    new_task = Task(
        description="Finish API implementation",
        priority=Priority.HIGH,
        due=datetime(2025, 6, 30, 17, 0),
        tags=["work", "coding"],
        project="API_Development",
        recur=RecurrencePeriod.WEEKLY,
        context="work"
    )
    created_task = api.add_task(new_task)
    print(f"Created task: {created_task.id}, UUID: {created_task.uuid}")

    # List pending tasks
    tasks = api.list_tasks(status=TaskStatus.PENDING)
    for task in tasks:
        print(f"Task {task.id}: {task.description} (Due: {task.due})")

    # Modify a task
    created_task.description = "Finish and test API implementation"
    updated_task = api.modify_task(created_task)
    print(f"Updated task: {updated_task.description}")

    # Add an annotation
    api.add_annotation(created_task.id, "Added unit tests")

    # Complete a task
    api.complete_task(created_task.id)

    # Set context
    api.set_context("work")
