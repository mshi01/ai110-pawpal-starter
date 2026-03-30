from __future__ import annotations
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta

PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}
BREAK_MINUTES = 5  # buffer inserted between back-to-back tasks


@dataclass
class Task:
    title: str
    description: str
    duration_minutes: int
    frequency: str = "daily"     # "once" | "daily" | "weekly"
    priority: str = "medium"     # "low" | "medium" | "high"
    status: str = "pending"      # "pending" | "completed" | "skipped"
    pet: Pet | None = field(default=None, repr=False)
    last_completed: datetime | None = field(default=None, repr=False)
    scheduled_time: datetime | None = field(default=None, repr=False)

    @property
    def rank(self):
        """Return the numeric priority rank for sorting."""
        return PRIORITY_RANK.get(self.priority, 1)

    def complete(self):
        """Mark this task as completed and record the time."""
        self.status = "completed"
        self.last_completed = datetime.now()

    def skip(self):
        """Mark this task as skipped."""
        self.status = "skipped"

    def reset(self):
        """Reset task back to pending (for reuse on a new day/week)."""
        self.status = "pending"
        self.last_completed = None
        self.scheduled_time = None

    def is_due(self, now: datetime) -> bool:
        """Return True if the task is due based on its frequency."""
        if self.status != "pending":
            return False
        if self.last_completed is None:
            return True
        if self.frequency == "once":
            return False
        if self.frequency == "daily":
            return self.last_completed.date() < now.date()
        if self.frequency == "weekly":
            days_since = (now.date() - self.last_completed.date()).days
            return days_since >= 7
        return True


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
        task.pet = self
        self.tasks.append(task)

    def remove_task(self, task: Task) -> bool:
        """Remove a task from this pet. Returns True if found and removed."""
        if task in self.tasks:
            self.tasks.remove(task)
            task.pet = None
            return True
        return False

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

    def build_schedule(
        self, day_start: datetime, day_end: datetime
    ) -> tuple[list[dict], list[tuple[str, str, str]]]:
        """
        Fit pending tasks into the day window using a greedy first-fit approach.

        Tasks are sorted by priority (desc) then pet name so each pet's tasks
        stay grouped. A BREAK_MINUTES gap is inserted between consecutive tasks.

        Returns:
            schedule:  list of scheduled task dicts
            skipped:   list of (pet_name, task_title, reason) for excluded tasks
        """
        sorted_pairs = sorted(
            self.get_pending_tasks(),
            key=lambda pt: (-pt[1].rank, pt[0].name),
        )

        available_minutes = (day_end - day_start).total_seconds() / 60
        total_needed = sum(t.duration_minutes for _, t in sorted_pairs)
        if total_needed > available_minutes:
            # caller can surface this as a warning
            pass  # individual overflow is handled per-task below

        schedule = []
        skipped: list[tuple[str, str, str]] = []
        cursor = day_start
        scheduled_titles = set()

        for pet, task in sorted_pairs:
            # Add break gap after the first scheduled task
            start = cursor + timedelta(minutes=BREAK_MINUTES) if schedule else cursor
            end = start + timedelta(minutes=task.duration_minutes)

            if end > day_end:
                skipped.append((pet.name, task.title, "not enough time remaining"))
                continue

            task.scheduled_time = start
            schedule.append({
                "pet": pet.name,
                "task": task.title,
                "description": task.description,
                "priority": task.priority,
                "frequency": task.frequency,
                "status": task.status,
                "start": start,
                "end": end,
            })
            scheduled_titles.add(task.title)
            cursor = end

        return schedule, skipped

    def detect_conflicts(self, schedule: list[dict]) -> list[str]:
        """
        Check a schedule (as returned by build_schedule) for overlapping tasks.

        Two entries conflict when their time windows overlap, i.e.:
            entry_a["start"] < entry_b["end"]  AND
            entry_b["start"] < entry_a["end"]

        Returns a list of human-readable warning strings — one per conflicting
        pair.  An empty list means no conflicts were found.  The method never
        raises; it is safe to call even if the schedule is empty or entries are
        missing time data.
        """
        warnings: list[str] = []

        for i, a in enumerate(schedule):
            for b in schedule[i + 1:]:
                a_start, a_end = a.get("start"), a.get("end")
                b_start, b_end = b.get("start"), b.get("end")

                if None in (a_start, a_end, b_start, b_end):
                    continue  # skip entries without time data

                if a_start < b_end and b_start < a_end:
                    warnings.append(
                        f"WARNING: Conflict between '{a['task']}' ({a['pet']}, "
                        f"{a_start.strftime('%H:%M')}–{a_end.strftime('%H:%M')}) "
                        f"and '{b['task']}' ({b['pet']}, "
                        f"{b_start.strftime('%H:%M')}–{b_end.strftime('%H:%M')})"
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
        instance to *pet* with its scheduled_time set to the next occurrence.

        Uses timedelta to calculate the next due date:
          - "daily"  → today + timedelta(days=1)
          - "weekly" → today + timedelta(days=7)

        Returns the newly created Task for recurring frequencies, or None for
        one-off tasks.
        """
        task.complete()

        if task.frequency == "daily":
            next_due = datetime.now() + timedelta(days=1)
        elif task.frequency == "weekly":
            next_due = datetime.now() + timedelta(days=7)
        else:
            return None  # "once" tasks are not rescheduled

        next_task = replace(
            task,
            status="pending",
            last_completed=None,
            scheduled_time=next_due,
        )
        pet.add_task(next_task)
        return next_task

    def sort_by_time(self) -> list[Task]:
        """
        Return all scheduled tasks across all pets sorted by scheduled_time.

        Tasks without a scheduled_time (not yet placed in a schedule) are
        appended at the end in their original order.
        """
        all_tasks = [task for _, task in self.owner.all_tasks()]
        return sorted(
            all_tasks,
            key=lambda t: (t.scheduled_time is None, t.scheduled_time),
        )
