# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design. 
- What classes did you include, and what responsibilities did you assign to each?

My initial UML design includes 4 classes, Owner, Pet, Task and Scheduler. The Owner class includes the owner id and owner name and a list of pets as a list of Pet objects.It also include a list of task which are all the tasks need to be done for the owners'pets ordered by priority level. The Owner can add/remove a pet and add/remove a task and change the order of the task. The Pet Class includes the pet id and the pet name as well as the Owner object. It also includes a routine dictionary which contains the tasks need to be done for this pet and the freqency of the task. The Pet class can also change the task. The Scheduler class will include a list of scheduled tasks in their priority order. It can add/remove a task. It can also change the priority level of a task.

3 core actions the user should be able to perform include adding a pet, scheduling a walk/groom, list a daily plan.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
