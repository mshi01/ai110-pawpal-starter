import streamlit as st
from datetime import datetime, time
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# ── Session-state "vault" ────────────────────────────────────────────────────
# "owner" is only stored after the user explicitly submits the setup form.
# Until then, the rest of the app is hidden behind an early return so the user
# is never looking at stale placeholder data.

if "owner" not in st.session_state:
    st.subheader("Welcome! Let's get you set up.")
    with st.form("setup_form"):
        owner_name = st.text_input("Your name")
        pet_name   = st.text_input("Pet name")
        species    = st.selectbox("Species", ["dog", "cat", "other"])
        submitted  = st.form_submit_button("Create profile")

    if submitted:
        if not owner_name.strip() or not pet_name.strip():
            st.error("Please fill in both your name and your pet's name.")
        else:
            new_owner = Owner(name=owner_name.strip())
            new_owner.add_pet(Pet(name=pet_name.strip(), species=species))
            st.session_state["owner"] = new_owner
            st.rerun()

    st.stop()   # nothing below renders until setup is complete

owner: Owner = st.session_state["owner"]

# ── Owner / Pet info (editable after setup) ──────────────────────────────────
with st.expander("Owner & Pet settings"):
    col_o = st.columns(1)[0]
    with col_o:
        owner_name = st.text_input("Owner name", value=owner.name)
    if st.button("Update owner name"):
        owner.name = owner_name.strip()
        st.success("Owner name updated.")

    st.markdown("---")
    st.markdown("**Your pets**")

    for i, pet in enumerate(list(owner.pets)):
        col_p, col_s, col_upd, col_del = st.columns([2, 2, 1, 1])
        with col_p:
            new_pet_name = st.text_input("Name", value=pet.name, key=f"pet_name_{i}")
        with col_s:
            new_species = st.selectbox(
                "Species",
                ["dog", "cat", "other"],
                index=["dog", "cat", "other"].index(pet.species),
                key=f"pet_species_{i}",
            )
        with col_upd:
            st.write("")  # vertical alignment spacer
            if st.button("Update", key=f"update_pet_{i}"):
                pet.name = new_pet_name.strip()
                pet.species = new_species
                st.success(f"Updated {pet.name}.")
        with col_del:
            st.write("")
            if st.button("Remove", key=f"remove_pet_{i}", type="secondary"):
                owner.remove_pet(pet)
                st.rerun()

    st.markdown("---")
    st.markdown("**Add another pet**")
    with st.form("add_pet_form"):
        new_name    = st.text_input("Pet name", key="new_pet_name")
        new_species = st.selectbox("Species", ["dog", "cat", "other"], key="new_pet_species")
        add_submitted = st.form_submit_button("Add pet")

    if add_submitted:
        if not new_name.strip():
            st.error("Please enter a pet name.")
        elif owner.get_pet(new_name.strip()) is not None:
            st.error(f"A pet named '{new_name.strip()}' already exists.")
        else:
            owner.add_pet(Pet(name=new_name.strip(), species=new_species))
            st.success(f"Added {new_name.strip()}!")
            st.rerun()

st.divider()

# ── Task entry ───────────────────────────────────────────────────────────────
st.subheader("Tasks")

if not owner.pets:
    st.info("Add at least one pet in the settings above to manage tasks.")
    st.stop()

# Pet selector — only show the dropdown when there is more than one pet
if len(owner.pets) == 1:
    active_pet = owner.pets[0]
else:
    pet_names  = [p.name for p in owner.pets]
    chosen     = st.selectbox("Select pet", pet_names, key="active_pet_select")
    active_pet = owner.get_pet(chosen)

st.caption(f"Tasks are attached to **{active_pet.name}** and persist across reruns.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    task_desc = st.text_input("Description", value="")
with col3:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
with col4:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    new_task = Task(
        title=task_title,
        description=task_desc,
        duration_minutes=int(duration),
        priority=priority,
    )
    active_pet.add_task(new_task)
    st.success(f"Added task '{task_title}' to {active_pet.name}.")

if active_pet.tasks:
    st.write(f"Current tasks for **{active_pet.name}**:")
    for i, task in enumerate(active_pet.tasks):
        col_info, col_btn = st.columns([5, 1])
        with col_info:
            st.markdown(
                f"**{task.title}** · {task.priority} priority · "
                f"{task.duration_minutes} min · *{task.status}*"
            )
        with col_btn:
            if st.button("Remove", key=f"remove_task_{i}"):
                active_pet.remove_task(task)
                st.rerun()
else:
    st.info("No tasks yet. Add one above.")

if active_pet.tasks:
    if st.button("Reset daily tasks", key="reset_daily"):
        for task in active_pet.tasks:
            if task.frequency == "daily":
                task.reset()
        st.success("Daily tasks reset to pending.")
        st.rerun()

st.divider()

# ── Schedule generation ──────────────────────────────────────────────────────
st.subheader("Build Schedule")

col_start, col_end = st.columns(2)
with col_start:
    day_start_time = st.time_input("Day start", value=time(8, 0))
with col_end:
    day_end_time = st.time_input("Day end", value=time(20, 0))

if st.button("Generate schedule"):
    has_pending = any(
        t.status == "pending"
        for p in owner.pets
        for t in p.tasks
    )
    if not has_pending:
        st.warning("Add at least one pet and one pending task first.")
    else:
        today = datetime.today().date()
        day_start = datetime.combine(today, day_start_time)
        day_end = datetime.combine(today, day_end_time)

        available_minutes = (day_end - day_start).total_seconds() / 60
        from pawpal_system import BREAK_MINUTES
        pending_pairs = Scheduler(owner).get_pending_tasks()
        total_needed = sum(t.duration_minutes for _, t in pending_pairs)
        if total_needed > available_minutes:
            st.warning(
                f"Tasks total {total_needed} min but only {int(available_minutes)} min available — "
                "some tasks will be excluded."
            )

        scheduler = Scheduler(owner)
        schedule, skipped = scheduler.build_schedule(day_start, day_end)

        if schedule:
            st.success(f"Schedule built — {len(schedule)} task(s) fit in the day.")
            st.table(
                [
                    {
                        "pet": entry["pet"],
                        "task": entry["task"],
                        "priority": entry["priority"],
                        "start": entry["start"].strftime("%H:%M"),
                        "end": entry["end"].strftime("%H:%M"),
                        "duration (min)": int(
                            (entry["end"] - entry["start"]).total_seconds() / 60
                        ),
                    }
                    for entry in schedule
                ]
            )
        else:
            st.warning("No tasks fit in the selected time window.")

        if skipped:
            st.markdown("**Tasks excluded from schedule:**")
            for pet_name, task_title, reason in skipped:
                st.caption(f"- {pet_name} / {task_title}: {reason}")
