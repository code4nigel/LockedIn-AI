# LockedIn - Future Ideas & Enhancement Backlog

These are backlog items that represent valuable architectural, content, or performance enhancements for the LockedIn project. They will be integrated in subsequent phases of development.

---

## 1. Multi-User Proctoring Session Support (Architecture)
* **Description**: Transition the active proctoring state from a single global dictionary in Python memory to a session-based or database-backed tracking structure.
* **Why**: Currently, multiple concurrent users would overwrite each other's proctoring flags, violations, and session timers. 
* **Proposed Implementation**: Use Flask sessions (`session['session_id']`) to map to unique active proctor states in a thread-safe registry, or serialize proctor logs directly into the `sessions` database table in real-time.

---

## 2. Expand the Coding Questions Database (Content)
* **Description**: Grow the coding challenge pool by introducing more data structures and algorithm questions categorized by difficulty and topic tags (e.g., Graphs, Trees, Heaps).
* **Why**: Offers a richer testing platform for candidates.
* **Proposed Implementation**: Update `backend/ai_proctor/questions.py` to define a broader array of standard algorithmic puzzles, including input boilerplates, custom test cases, and execution constraints.
