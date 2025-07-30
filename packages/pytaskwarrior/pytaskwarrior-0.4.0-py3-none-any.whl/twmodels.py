from __future__ import annotations
from datetime import datetime, timedelta
from uuid import UUID
from enum import Enum
from typing import Annotated, Optional, List, Union, get_origin, get_args

import isodate
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

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
    """Represents a TaskWarrior task.
    timedelta looks like `[±]P[DD]DT[HH]H[MM]M[SS]S` (ISO 8601 format for timedelta)"""

    description: Annotated[str, Field(..., description="Task description (required).")]
    status: Annotated[
        Optional[TaskStatus],
        Field(default=None, description="Current status of the task.")
    ]
    priority: Annotated[
        Optional[Priority],
        Field(default=None, description="Priority of the task (H, M, L, or empty).")
    ]
    due: Annotated[
        Optional[Union[datetime, timedelta]],
        Field(default=None, description="Due date and time for the task.")
    ]

    tags: Annotated[
        Optional[List[str]],
        Field(default_factory=list, description="List of tags associated with the task.")
    ]
    project: Annotated[
        Optional[str],
        Field(default=None, description="Project the task belongs to.")
    ]
    depends: Annotated[
        Optional[List[UUID]],
        Field(default_factory=list, description="List of UUIDs of tasks this task depends on.")
    ]
    parent: Annotated[
        Optional[UUID],
        Field(default=None, description="UUID of the template task")
    ]
    recur: Annotated[
        Optional[RecurrencePeriod],
        Field(default=None, description="Recurrence period for recurring tasks.")
    ]
    scheduled: Annotated[
        Optional[Union[datetime, timedelta]],
        Field(default=None, description="Schedule the earlier time the task can be done. Masked when using the `ready` filter")
    ]
    wait: Annotated[
        Optional[Union[datetime, timedelta]],
        Field(default=None, description="The task is hidden until the date.")
    ]
    until: Annotated[
        Optional[Union[datetime, timedelta]],
        Field(default=None, description="Expiration date for recurring tasks.")
    ]
    #annotations: List[Annotation ({'entry': datetime, 'description': str}] = Field(default_factory=list, description="List of annotations for the task.")
    context: Annotated[
        Optional[str],
        Field(default=None, description="Context filter for the task.")
    ]
    # Urgency should be readonly
    # urgency: Optional[float] = Field(default=None, description="Computed urgency score by TaskWarrior.")
#    udas: Dict[str, Any] = Field(default_factory=dict) #TODO: Review UDA usage

    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True,
        json_schema_extra={
            'examples': [
                {
                    'description': 'a task'
                },
                {
                    'description': 'a due task in two weeks for lambda project',
                    'due': 'P2W',
                    'project': 'lambda'
                },
            ]
        }
    )

    @field_validator("description")
    @classmethod
    def description_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Description cannot be empty")
        return v.strip()

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v):
        return [tag.strip() for tag in v if tag.strip()]

    @field_validator('*', mode='before')
    @classmethod
    def modify_date_format(cls, v, info):
        """Date converter"""
        # Get the field's type annotation
        field_type = cls.model_fields[info.field_name].annotation

        # Helper function to check if datetime is in the type (handles Union, Optional)
        def contains_datetime_or_timedelta(t):
            origin = get_origin(t)
            if origin in (Union, Optional):
                return any(contains_datetime_or_timedelta(arg) for arg in get_args(t))
            return t in (datetime, timedelta)

        # Check if the field involves datetime and the input is a string
        if contains_datetime_or_timedelta(field_type):# and isinstance(v, str):
            #        if (field_type == datetime or field_type == Union[datetime, timedelta]) and isinstance(v, str):
            if isinstance(v, (datetime, timedelta)):
                return v
            # Try parsing as datetime (format: yyyymmddThhmmssZ)
            try:
                return datetime.fromisoformat(v)
            except ValueError:
                # Try parsing as duration (example format: P21DT1H10M49S)
                try:
                    isodate.parse_duration(v)
                except isodate.ISO8601Error:
                    raise ValueError("Could not parse until as datetime or timedelta")
        return v


class TWTask(Task):
    index: Annotated[
        Optional[int],
        Field(default=None, alias='id', description="READONLY Task index of a task in the working set, which can change when tasks are completed or deleted.")
    ]
    uuid: Annotated[
        Optional[UUID],
        Field(default=None, description="READONLY Unique identifier for the task. Cannot be set when adding task")
    ]
    entry: Annotated[
        Optional[datetime],
        Field(default=None, description="READONLY Task creation date and time.")
    ]
    start: Annotated[
        Optional[datetime],
        Field(default=None, description="READONLY Task started date and time.")
    ]
    end: Annotated[
        Optional[datetime],
        Field(default=None, description="READONLY Task done date and time.")
    ]
    modified: Annotated[
        Optional[datetime],
        Field(default=None, description="READONLY Last modification date and time.")
    ]

    @field_serializer('uuid')
    def serialize_uuid(self, uuid: UUID, _info):
        return str(uuid)

