import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet


def test_task_completion_changes_status():
    task = Task(title="Feed", description="Feed the pet", duration_minutes=5)
    assert task.status == "pending"
    task.complete()
    assert task.status == "completed"


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="dog")
    assert len(pet.tasks) == 0
    task = Task(title="Walk", description="Walk the dog", duration_minutes=30)
    pet.add_task(task)
    assert len(pet.tasks) == 1
