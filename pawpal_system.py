from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta

PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}


@dataclass
class Task:
    title: str
    description: str
    duration_minutes: int
    frequency: str = "daily"     # "once" | "daily" | "weekly"
    priority: str = "medium"     # "low" | "medium" | "high"
    status: str = "pending"      # "pending" | "completed" | "skipped"
    pet: Pet | None = field(default=None, repr=False)

    @property
    def rank(self):
        """Return the numeric priority rank for sorting."""
        return PRIORITY_RANK.get(self.priority, 1)

    def complete(self):
        """Mark this task as completed."""
        self.status = "completed"

    def skip(self):
        """Mark this task as skipped."""
        self.status = "skipped"


@dataclass
class Pet:
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)
    owner: Owner | None = field(default=None, repr=False)

    def add_task(self, task: Task):
        """Attach a task to this pet and add it to the task list."""
        task.pet = self
        self.tasks.append(task)

    def get_pending_tasks(self) -> list[Task]:
        """Return all tasks for this pet that are still pending."""
        return [t for t in self.tasks if t.status == "pending"]


@dataclass
class Owner:
    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet):
        """Register a pet under this owner and set its back-reference."""
        pet.owner = self
        self.pets.append(pet)

    def get_pet(self, name: str) -> Pet | None:
        """Return the pet with the given name, or None if not found."""
        return next((p for p in self.pets if p.name == name), None)

    def all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every (pet, task) pair across all owned pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


class Scheduler:
    def __init__(self, owner: Owner):
        """Initialize the scheduler for the given owner."""
        self.owner = owner

    def get_pending_tasks(self) -> list[tuple[Pet, Task]]:
        """Return all (pet, task) pairs where the task is still pending."""
        return [(pet, task) for pet, task in self.owner.all_tasks() if task.status == "pending"]

    def build_schedule(self, day_start: datetime, day_end: datetime) -> list[dict]:
        """Sort pending tasks by priority and fit them into the day window."""
        sorted_pairs = sorted(self.get_pending_tasks(), key=lambda pt: -pt[1].rank)

        schedule = []
        cursor = day_start

        for pet, task in sorted_pairs:
            end = cursor + timedelta(minutes=task.duration_minutes)
            if end > day_end:
                continue
            schedule.append({
                "pet": pet.name,
                "task": task.title,
                "description": task.description,
                "priority": task.priority,
                "frequency": task.frequency,
                "status": task.status,
                "start": cursor,
                "end": end,
            })
            cursor = end

        return schedule
