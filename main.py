from datetime import datetime
from pawpal_system import Task, Pet, Owner, Scheduler

# --- Setup ---
owner = Owner(name="Jordan")

mochi = Pet(name="Mochi", species="dog")
luna  = Pet(name="Luna",  species="cat")

owner.add_pet(mochi)
owner.add_pet(luna)

# --- Tasks for Mochi ---
mochi.add_task(Task(
    title="Morning Walk",
    description="30-minute walk around the block",
    duration_minutes=30,
    frequency="daily",
    priority="high",
))
mochi.add_task(Task(
    title="Breakfast",
    description="1 cup dry kibble",
    duration_minutes=10,
    frequency="daily",
    priority="high",
))

# --- Tasks for Luna ---
luna.add_task(Task(
    title="Medication",
    description="Administer 1 allergy tablet with food",
    duration_minutes=5,
    frequency="daily",
    priority="high",
))
luna.add_task(Task(
    title="Playtime",
    description="Interactive toy session",
    duration_minutes=20,
    frequency="daily",
    priority="low",
))

# --- Schedule ---
scheduler = Scheduler(owner)

day_start = datetime.now().replace(hour=8,  minute=0, second=0, microsecond=0)
day_end   = datetime.now().replace(hour=20, minute=0, second=0, microsecond=0)

schedule = scheduler.build_schedule(day_start, day_end)

# --- Print ---
print(f"\n{'='*45}")
print(f"  Today's Schedule for {owner.name}")
print(f"{'='*45}")

for slot in schedule:
    start = slot["start"].strftime("%I:%M %p")
    end   = slot["end"].strftime("%I:%M %p")
    print(f"\n{start} – {end}  |  {slot['task']} ({slot['pet']})")
    print(f"  {slot['description']}")
    print(f"  Priority: {slot['priority']}  |  Frequency: {slot['frequency']}")

print(f"\n{'='*45}")
print(f"  {len(schedule)} task(s) scheduled")
print(f"{'='*45}\n")
