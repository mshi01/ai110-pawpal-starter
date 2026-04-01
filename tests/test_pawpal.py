import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


def test_task_completion_changes_status():
    task = Task(description="Feed the pet")
    assert task.status == "pending"
    task.complete()
    assert task.status == "completed"


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="dog")
    assert len(pet.tasks) == 0
    task = Task(description="Walk the dog")
    pet.add_task(task)
    assert len(pet.tasks) == 1


# ── Sorting Correctness ───────────────────────────────────────────────────────

def test_sort_by_time_returns_chronological_order():
    """sort_by_time() must return tasks ordered earliest → latest."""
    owner = Owner(name="Alice")
    pet = Pet(name="Rex", species="dog")
    owner.add_pet(pet)

    t1 = Task(description="Morning walk",  time=datetime(2026, 3, 31, 7, 0))
    t2 = Task(description="Afternoon meds", time=datetime(2026, 3, 31, 13, 0))
    t3 = Task(description="Evening feed",  time=datetime(2026, 3, 31, 18, 0))

    # Add out of order
    pet.add_task(t3)
    pet.add_task(t1)
    pet.add_task(t2)

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time()

    assert sorted_tasks == [t1, t2, t3]


def test_sort_by_time_places_untimed_tasks_last():
    """Tasks without a scheduled time must appear after all timed tasks."""
    owner = Owner(name="Alice")
    pet = Pet(name="Rex", species="dog")
    owner.add_pet(pet)

    timed   = Task(description="Walk",  time=datetime(2026, 3, 31, 9, 0))
    untimed = Task(description="Groom", time=None)

    pet.add_task(untimed)
    pet.add_task(timed)

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time()

    assert sorted_tasks.index(timed) < sorted_tasks.index(untimed)


# ── Recurrence Logic ──────────────────────────────────────────────────────────

def test_completing_daily_task_creates_next_day_task():
    """Marking a daily task complete must add a new pending task for tomorrow."""
    owner = Owner(name="Bob")
    pet = Pet(name="Luna", species="cat")
    owner.add_pet(pet)

    today_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
    daily_task = Task(description="Morning feed", time=today_time, frequency="daily")
    pet.add_task(daily_task)

    scheduler = Scheduler(owner)
    next_task = scheduler.mark_task_complete(pet, daily_task)

    # Original task is completed
    assert daily_task.status == "completed"

    # A new task was returned and added to the pet
    assert next_task is not None
    assert next_task in pet.tasks
    assert next_task.status == "pending"
    assert next_task.frequency == "daily"

    # New task is scheduled for tomorrow
    expected_date = (datetime.now() + timedelta(days=1)).date()
    assert next_task.time.date() == expected_date


def test_completing_once_task_does_not_create_new_task():
    """One-off tasks must NOT generate a follow-up task."""
    owner = Owner(name="Bob")
    pet = Pet(name="Luna", species="cat")
    owner.add_pet(pet)

    one_off = Task(description="Vet visit", time=datetime.now(), frequency="once")
    pet.add_task(one_off)

    scheduler = Scheduler(owner)
    result = scheduler.mark_task_complete(pet, one_off)

    assert result is None
    assert len(pet.tasks) == 1  # no new task added


# ── Conflict Detection ────────────────────────────────────────────────────────

def test_detect_conflicts_flags_same_time_tasks():
    """Two tasks scheduled at the exact same time must produce a conflict warning."""
    owner = Owner(name="Carol")
    pet = Pet(name="Milo", species="dog")
    owner.add_pet(pet)

    shared_time = datetime(2026, 3, 31, 9, 0)
    task_a = Task(description="Bath",  time=shared_time)
    task_b = Task(description="Brush", time=shared_time)
    pet.add_task(task_a)
    pet.add_task(task_b)

    scheduler = Scheduler(owner)
    schedule = [(pet, task_a), (pet, task_b)]
    conflicts = scheduler.detect_conflicts(schedule)

    assert len(conflicts) == 1
    assert "Bath" in conflicts[0]
    assert "Brush" in conflicts[0]


def test_detect_conflicts_no_warning_for_different_times():
    """Tasks at different times must not produce any conflict warnings."""
    owner = Owner(name="Carol")
    pet = Pet(name="Milo", species="dog")
    owner.add_pet(pet)

    task_a = Task(description="Bath",  time=datetime(2026, 3, 31, 9, 0))
    task_b = Task(description="Brush", time=datetime(2026, 3, 31, 10, 0))
    pet.add_task(task_a)
    pet.add_task(task_b)

    scheduler = Scheduler(owner)
    schedule = [(pet, task_a), (pet, task_b)]
    conflicts = scheduler.detect_conflicts(schedule)

    assert conflicts == []


def test_detect_conflicts_ignores_untimed_tasks():
    """Tasks with no scheduled time must never be flagged as conflicting."""
    owner = Owner(name="Carol")
    pet = Pet(name="Milo", species="dog")
    owner.add_pet(pet)

    task_a = Task(description="Bath",  time=None)
    task_b = Task(description="Brush", time=None)
    pet.add_task(task_a)
    pet.add_task(task_b)

    scheduler = Scheduler(owner)
    schedule = [(pet, task_a), (pet, task_b)]
    conflicts = scheduler.detect_conflicts(schedule)

    assert conflicts == []
