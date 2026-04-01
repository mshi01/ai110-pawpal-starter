# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design. 
- What classes did you include, and what responsibilities did you assign to each?

My initial UML design includes 4 classes, Owner, Pet, Task and Scheduler. The Owner class includes the owner name and a list of Pet objects. It also includes a function add_pet which can add a pet and a function all_tasks which can list all (pet, task) pairs across all the pets for the owner. The Pet Class includes the pet name, species and a list of tasks. It also has a function add_task to add tasks to the pet. The Task class includes the attributes title and duration_minutes and a priority level and a function rank which can return the rank of the priority of the task as an integer level. The Scheduler class includes the Owner object and a build_schedule function which can create a schedule for the owner with task title and assigned schedule slots, the tasks are sorted by the priority level.

3 core actions the user should be able to perform include adding a pet, scheduling a walk/groom, list a daily plan.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

AI helped me to identify the following missing ralationships in the original UML diagram: Task has no back-reference to its Pet	If you pass a Task around on its own, you can't tell which pet it belongs to; Pet has no back-reference to its Owner; Scheduler is not in the UML as owning Owner, Owner has no reference to its Scheduler.

AI also helped me to idenfify several logic bottlenecks. One of them is using "break" vs "continue" in build_schedule function. Using break stops at the first task that doesn't fit. If a 60-min low-priority task can't fit but a 5-min low-priority task after it could, it gets dropped silently. continue would be more correct. The other one is tasks: list is untyped (line 22)
list instead of list[Task] means nothing prevents adding non-Task objects to Pet.tasks, which would silently break Scheduler.build_schedule when it calls .rank. Another drawback we found out is there is no guard for an empty schedule window
If day_start >= day_end, build_schedule returns [] with no indication of why — could be confusing when wired to the UI.



---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?
Priority is the first constraints the scheduler considers, tasks with high priority will be picked up first. Time is also another important constraints. If the tasks of the same priority one is too long in duration, the another one with shorter time duration will be picked. Taks that dont fit are collected in a skipped list and not just silently dropped. Also, a break of 5 minutes were added between tasks to allow more feasible execution of the tasks.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
One tradeoff the scheduler makes is to group by pet not just priority. In theory, we need to prioritize tasks of higher priority. However, this might lead to frequent switching of the pets to be taken care of for the owner which might not be very practical and frequent swtiching of pets to perform task might take more time for the owner to take care on the pet. so in reality I think it would be more reasonable to group tasks also by pet, not jusst the priority level. 

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?
In the original design in app.py, AI suggeted to create a dufault owner named "Jordan" if the owner is not in session_state. I think instead of generating a default owner if would be better to create a form to collect owner info. 
I read through what the AI suggested and think about it whether it makes sense or not and accept the changes only if it makes seneses. 

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?
Test if sort_by_time works correctly. unscheduled tasks - none ones musht appear at the end. Deal with Two tasks with identical scheduled_time.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
This app implemented Smarter Scheduling. It can detect conflict. Takes the output of build_schedule and checks every pair of tasks for overlapping time windows using the interval overlap condition:


a.start < b.end  AND  b.start < a.end
Returns a list of human-readable warning strings instead of crashing. Works across pets and same-pet tasks alike. Also it performs auto-rescheduling on completion. When a recurring task is marked done, a new pending instance is automatically created for the next occurrence. It also implemented optimized time sorting. Replaced a two-pass split-and-concatenate approach with a single-pass sorted using a sentinel tuple key:


key=lambda t: (t.scheduled_time is None, t.scheduled_time)
Timed tasks sort first (False < True), unscheduled tasks fall to the end — no None comparison errors, no extra list allocations.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
