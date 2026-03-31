import streamlit as st
from datetime import datetime, time
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ── UI helpers ────────────────────────────────────────────────────────────────
SPECIES_EMOJI   = {"dog": "🐶", "cat": "🐱", "other": "🐾"}
PRIORITY_EMOJI  = {"high": "🔴", "medium": "🟡", "low": "🟢"}
FREQUENCY_EMOJI = {"daily": "🔁", "weekly": "📅", "once": "1️⃣"}
PRIORITY_COLOR  = {"high": "#ffd6d6", "medium": "#fff3cd", "low": "#d4edda"}
STATUS_BADGE    = {
    "pending":   '<span style="background:#fff3cd;color:#856404;padding:2px 8px;border-radius:10px;font-size:12px;">⏳ pending</span>',
    "completed": '<span style="background:#d4edda;color:#155724;padding:2px 8px;border-radius:10px;font-size:12px;">✅ completed</span>',
    "skipped":   '<span style="background:#e2e3e5;color:#383d41;padding:2px 8px;border-radius:10px;font-size:12px;">⏭ skipped</span>',
}

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
        st.caption(f"{SPECIES_EMOJI.get(pet.species, '🐾')} {pet.name} ({pet.species})")
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
    task_desc = st.text_input("Description", value="")
with col2:
    task_time = st.time_input("Scheduled time", value=time(8, 0))
with col3:
    frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])
with col4:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    if not task_desc.strip():
        st.error("Please enter a task description.")
    else:
        scheduled_dt = datetime.combine(datetime.today().date(), task_time)
        new_task = Task(
            description=task_desc.strip(),
            time=scheduled_dt,
            frequency=frequency,
            priority=priority,
        )
        active_pet.add_task(new_task)
        st.success(f"Added task '{task_desc.strip()}' to {active_pet.name}.")

if active_pet.tasks:
    species_icon = SPECIES_EMOJI.get(active_pet.species, "🐾")
    st.write(f"Tasks for {species_icon} **{active_pet.name}**:")
    for i, task in enumerate(active_pet.tasks):
        col_info, col_complete, col_remove = st.columns([5, 1, 1])
        with col_info:
            time_str = task.time.strftime("%H:%M") if task.time else "No time set"
            priority_icon = PRIORITY_EMOJI.get(task.priority, "")
            freq_icon = FREQUENCY_EMOJI.get(task.frequency, "")
            status_badge = STATUS_BADGE.get(task.status, task.status)
            st.markdown(
                f"{priority_icon} **{task.description}** &nbsp; {freq_icon} {task.frequency} &nbsp;"
                f"🕐 {time_str} &nbsp; {status_badge}",
                unsafe_allow_html=True,
            )
        with col_complete:
            if task.status != "completed":
                if st.button("✔ Complete", key=f"complete_task_{i}", use_container_width=True):
                    scheduler = Scheduler(owner)
                    scheduler.mark_task_complete(active_pet, task)
                    st.rerun()
            else:
                st.markdown("✅ Done")
        with col_remove:
            if st.button("🗑 Remove", key=f"remove_task_{i}", use_container_width=True):
                active_pet.remove_task(task)
                st.rerun()
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# ── Schedule generation ──────────────────────────────────────────────────────
st.subheader("Build Schedule")

def render_schedule(schedule, scheduler):
    rows_html = ""
    for pet, task in schedule:
        bg = PRIORITY_COLOR.get(task.priority, "#ffffff")
        time_str = task.time.strftime("%H:%M") if task.time else "No time set"
        priority_icon = PRIORITY_EMOJI.get(task.priority, "")
        freq_icon = FREQUENCY_EMOJI.get(task.frequency, "")
        species_icon = SPECIES_EMOJI.get(pet.species, "🐾")
        status_badge = STATUS_BADGE.get(task.status, task.status)
        td = 'style="padding:8px 10px;"'
        rows_html += (
            f'<tr style="background-color:{bg}; border-bottom:1px solid #ddd;">'
            f"<td {td}>{species_icon} {pet.name}</td>"
            f"<td {td}>{task.description}</td>"
            f"<td {td}>{priority_icon} {task.priority.capitalize()}</td>"
            f"<td {td}>🕐 {time_str}</td>"
            f"<td {td}>{freq_icon} {task.frequency}</td>"
            f"<td {td}>{status_badge}</td>"
            f"</tr>"
        )
    th = 'style="padding:8px 10px; background:#f0f2f6; text-align:left;"'
    st.markdown(
        f"""
        <table style="width:100%; border-collapse:collapse; font-size:14px; border:1px solid #ddd; border-radius:8px; overflow:hidden;">
          <thead>
            <tr>
              <th {th}>Pet</th>
              <th {th}>Description</th>
              <th {th}>Priority</th>
              <th {th}>Time</th>
              <th {th}>Frequency</th>
              <th {th}>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows_html}
          </tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )
    conflicts = scheduler.detect_conflicts(schedule)
    if conflicts:
        st.markdown("**⚠️ Conflicts detected:**")
        for warning in conflicts:
            st.warning(warning)

if st.button("Generate schedule"):
    has_pending = any(
        t.status == "pending"
        for p in owner.pets
        for t in p.tasks
    )
    if not has_pending:
        st.warning("Add at least one pet and one pending task first.")
    else:
        scheduler = Scheduler(owner)
        schedule = scheduler.build_schedule()
        if schedule:
            st.session_state["schedule"] = schedule
            st.session_state["scheduler"] = scheduler
        else:
            st.info("No pending tasks for today.")

if "schedule" in st.session_state:
    schedule = st.session_state["schedule"]
    scheduler = st.session_state["scheduler"]
    completed = sum(1 for _, t in schedule if t.status == "completed")
    st.success(f"🗓 Schedule — {len(schedule)} task(s) · {completed} completed")
    render_schedule(schedule, scheduler)
