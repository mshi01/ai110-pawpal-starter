from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str = "medium"  # "low" | "medium" | "high"

    PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}

    @property
    def rank(self):
        return self.PRIORITY_RANK.get(self.priority, 1)


@dataclass
class Pet:
    name: str
    species: str
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task):
        self.tasks.append(task)


@dataclass
class Owner:
    name: str
    pets: list = field(default_factory=list)

    def add_pet(self, pet: Pet):
        self.pets.append(pet)

    def all_tasks(self):
        """Return (pet, task) pairs across all pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def build_schedule(self, day_start: datetime, day_end: datetime):
        """Sort tasks by priority and assign sequential time slots."""
        pairs = self.owner.all_tasks()
        sorted_pairs = sorted(pairs, key=lambda pt: -pt[1].rank)

        schedule = []
        cursor = day_start

        for pet, task in sorted_pairs:
            end = cursor + timedelta(minutes=task.duration_minutes)
            if end > day_end:
                break
            schedule.append({
                "pet": pet.name,
                "task": task.title,
                "priority": task.priority,
                "start": cursor,
                "end": end,
            })
            cursor = end

        return schedule
