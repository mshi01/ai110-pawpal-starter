from __future__ import annotations
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta

PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}


@dataclass
class Task:
    description: str
    time: datetime | None = field(default=None)          # scheduled time
    frequency: str = "daily"                              # "once" | "daily" | "weekly"
    status: str = "pending"                               # "pending" | "completed" | "skipped"
    priority: str = "medium"                              # "low" | "medium" | "high"

    @property
    def rank(self):
        """Return the numeric priority rank for sorting."""
        return PRIORITY_RANK.get(self.priority, 1)

    def complete(self):
        """Mark this task as completed."""
        self.status = "completed"

    def reset(self):
        """Reset task back to pending (for reuse on a new day/week)."""
        self.status = "pending"
        self.time = None

    def is_due(self, now: datetime) -> bool:
        """Return True if the task is pending and scheduled for today or earlier."""
        if self.status != "pending":
            return False
        if self.time is None:
            return True
        return self.time.date() <= now.date()


@dataclass
class Pet:
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)
    owner: Owner | None = field(default=None, repr=False)

    def add_task(self, task: Task):
        """Attach a task to this pet; ignores duplicates."""
        if task in self.tasks:
            return
        self.tasks.append(task)

    def remove_task(self, task: Task) -> bool:
        """Remove a task from this pet. Returns True if found and removed."""
        if task in self.tasks:
            self.tasks.remove(task)
            return True
        return False


@dataclass
class Owner:
    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet):
        """Register a pet under this owner and set its back-reference."""
        pet.owner = self
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> bool:
        """Remove a pet from this owner. Returns True if found and removed."""
        if pet in self.pets:
            self.pets.remove(pet)
            pet.owner = None
            return True
        return False

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
        """Return due pending (pet, task) pairs, filtered by frequency."""
        now = datetime.now()
        return [
            (pet, task)
            for pet, task in self.owner.all_tasks()
            if task.is_due(now)
        ]

    def build_schedule(self) -> list[tuple[Pet, Task]]:
        """
        Sort today's pending tasks by priority (high → low) then by scheduled
        time, print them, and return the sorted list.

        Tasks without a scheduled time are placed after timed tasks.
        """
        sorted_pairs = sorted(
            self.get_pending_tasks(),
            key=lambda pt: (-pt[1].rank, pt[1].time is None, pt[1].time),
        )

        print(f"Today's Schedule ({datetime.now().strftime('%Y-%m-%d')}):")
        if not sorted_pairs:
            print("  No pending tasks for today.")
        for pet, task in sorted_pairs:
            time_str = task.time.strftime("%H:%M") if task.time else "No time set"
            print(f"  [{task.priority.upper()}] {time_str} | {pet.name}: {task.description}")

        return sorted_pairs

    def detect_conflicts(self, schedule: list[tuple[Pet, Task]]) -> list[str]:
        """
        Check a schedule (as returned by build_schedule) for tasks at the same time.

        Two entries conflict when both have an identical non-None time value.

        Returns a list of human-readable warning strings — one per conflicting
        pair.  An empty list means no conflicts were found.
        """
        warnings: list[str] = []

        for i, (pet_a, task_a) in enumerate(schedule):
            for pet_b, task_b in schedule[i + 1:]:
                if task_a.time is None or task_b.time is None:
                    continue  # skip tasks without a scheduled time

                if task_a.time == task_b.time:
                    warnings.append(
                        f"WARNING: Conflict between '{task_a.description}' ({pet_a.name}) "
                        f"and '{task_b.description}' ({pet_b.name}) "
                        f"both scheduled at {task_a.time.strftime('%H:%M')}"
                    )

        return warnings

    def filter_by_status(self, status: str) -> list[tuple[Pet, Task]]:
        """Return all (pet, task) pairs whose task.status matches status."""
        return [
            (pet, task)
            for pet, task in self.owner.all_tasks()
            if task.status == status
        ]

    def filter_by_pet_name(self, pet_name: str) -> list[tuple[Pet, Task]]:
        """Return all (pet, task) pairs belonging to the named pet (case-insensitive)."""
        name_lower = pet_name.lower()
        return [
            (pet, task)
            for pet, task in self.owner.all_tasks()
            if pet.name.lower() == name_lower
        ]

    def mark_task_complete(self, pet: Pet, task: Task) -> Task | None:
        """
        Mark *task* as completed and, for recurring tasks, add a new pending
        instance to *pet* with its time set to the next occurrence.

        Uses timedelta to calculate the next due date:
          - "daily"  → today + timedelta(days=1)
          - "weekly" → today + timedelta(days=7)

        Returns the newly created Task for recurring frequencies, or None for
        one-off tasks.
        """
        task.complete()

        if task.frequency not in ("daily", "weekly"):
            return None  # "once" tasks are not rescheduled

        delta = timedelta(days=1) if task.frequency == "daily" else timedelta(days=7)
        next_time = task.time.replace(
            year=(datetime.now() + delta).year,
            month=(datetime.now() + delta).month,
            day=(datetime.now() + delta).day,
        ) if task.time else None

        next_task = replace(task, status="pending", time=next_time)
        pet.add_task(next_task)
        return next_task

    def sort_by_time(self) -> list[Task]:
        """
        Return all tasks across all pets sorted by time.

        Tasks without a time are appended at the end.
        """
        all_tasks = [task for _, task in self.owner.all_tasks()]
        return sorted(
            all_tasks,
            key=lambda t: (t.time is None, t.time),
        )
