# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design. 
- What classes did you include, and what responsibilities did you assign to each?

The system is built around 4 classes: Owner, Pet, Task, and Scheduler.

- Owner stores the owner's name and a list of Pet objects, with methods to add a pet (add_pet) and retrieve all (pet, task) pairs across every pet (all_tasks).
- Pet stores the pet's name, species, and a list of Task objects, with an add_task method to attach tasks to the pet.
- Task stores a title, duration in minutes, and a priority level, with a rank method that returns the priority as an integer for sorting.
- Scheduler holds an Owner object and a build_schedule method that generates a daily schedule by sorting tasks by priority rank and assigning them to time slots.

Core User Actions
There are 3 key actions a user can perform:

- Add a pet — register a new pet under the owner's profile.
- Schedule a task — create and assign a task to a specific pet.
- View the daily plan — generate and display a prioritized schedule of tasks across all pets.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Through AI-assisted review, several missing relationships in the original UML diagram were identified:

- Task has no back-reference to its parent Pet, making it impossible to determine which pet a task belongs to when the task is passed around in isolation.
- Pet has no back-reference to its parent Owner.
- Scheduler is not modeled as owning an Owner, and conversely, Owner holds no reference to its Scheduler.

Several logic bottlenecks were also surfaced. For example, the handling of recurring tasks — specifically how mark_task_complete was implemented — did not account for auto-recreating tasks after completion. Also, using an untyped list instead of list[Task] for Pet.tasks places no restriction on what gets added, meaning non-Task objects could silently enter the list and cause Scheduler.build_schedule to break when it attempts to call .rank on them.


---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler orders tasks based on two constraints. Priority is considered first — high-priority tasks are always scheduled before lower-priority ones. Time is the second constraint, used as a tiebreaker when tasks share the same priority level; among those, tasks are ordered chronologically by their scheduled start time. And if two tasks have conflicting start times, the scheduler surfaces a warning to the user.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff in the scheduler's conflict detection is that it only checks for exact start time matches rather than overlapping durations. A duration-based approach would require each Task to carry an estimated completion time — which is inherently imprecise, since actual task durations can vary. By limiting conflict detection to exact time matches, the algorithm stays simple and the code remains easy to read and maintain.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

AI was used throughout the development process for brainstorming, UML class design, debugging, refactoring, writing docstrings, and generating test cases. The most effective prompting strategy was asking specific, targeted questions with direct references to relevant files or line numbers.


**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

Not all AI suggestions were accepted as-is — each was evaluated for whether it aligned with the intended design. Two examples illustrate this.

First, when initializing app.py, AI suggested creating a default owner named "Jordan" if no owner was found in session state. This was reconsidered in favor of a setup form that explicitly collects owner information from the user, which is a more appropriate approach for a real application.

Second, AI initially misunderstood the purpose of the Scheduler, designing it to accept start and end times as inputs and align tasks based on durations. After clarifying the intended behavior, AI revised the implementation to match what was actually needed.

A general lesson from this process is that AI can sometimes over-engineer solutions beyond what is necessary. Reviewing suggestions incrementally — rather than accepting large changes all at once — helps catch these cases early before they compound into larger issues.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

Three areas of core functionality were tested to verify the app behaves as intended.

First, task sorting was validated to confirm that tasks are ordered by priority (highest first) and then chronologically by scheduled time when priorities are equal.

Second, the recurrence logic was tested by verifying that marking a daily task complete via mark_task_complete() automatically creates a new pending copy of that task scheduled for the following day, while a once task produces no follow-up after completion.

Third, conflict detection was tested to confirm that detect_conflicts() emits a warning for every pair of tasks sharing an identical scheduled time, and returns an empty list when all times are distinct or when tasks have no scheduled time set.
These tests are important because they directly cover the app's core scheduling behavior.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

The scheduler works as intended, earning a confidence rating of 4 out of 5. Given more time, one area worth exploring further is handling tasks with overlapping durations — both designing the logic for how the scheduler should deal with this scenario and adding tests to cover it.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The app implements smarter scheduling by sorting tasks by priority and time, detecting scheduling conflicts, and automatically re-queuing recurring tasks after completion — all through a clean, user-friendly interface.


**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

A natural next step would be adding a duration attribute to each Task and incorporating estimated durations into the scheduling logic. This would also open the door to inserting buffer time between back-to-back tasks, making the generated schedule more realistic and practical.


**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Starting with a minimal design and incrementally adding complexity leads to more manageable development. When working with AI, it is important to fully read and understand each suggestion before accepting it, and to verify that it aligns with the intended behavior rather than introducing unnecessary complexity.
