# LockedIn AI - Slide Presentation Speaker Notes

**Presentation Deck for Graduation Project**  
**Institution:** Lakshmi Narain College of Technology Excellence  
**Presenters:** Shivanshu Yadav & Uday Singh Prajapati  
**Target Duration:** 20 Minutes (approx. 1 minute per slide)  

---

## Slide 1: Title Slide
*   **Slide Title:** LockedIn AI: AI-Powered Adaptive Proctoring & Technical Interview Preparation Platform
*   **Visuals:** Dark blue/grey background, cyan accents, team names, and college affiliation.
*   **Speaking Role: Shivanshu Yadav**
*   **Script:**
    > *"Good morning, respected judges and faculty members. Welcome to our major project presentation. My name is Shivanshu Yadav, and along with my teammate Uday Singh Prajapati, we have developed 'LockedIn AI'—an adaptive, proctored coding and mock interview platform. This project was developed here at Lakshmi Narain College of Technology Excellence. Over the next twenty minutes, we will walk you through the architecture, algorithms, and live demonstration of our platform."*

---

## Slide 2: Project Hook & Vision
*   **Slide Title:** Bridging the Gap: Exam Integrity to Interview Readiness
*   **Visuals:** Dual icons showing a locked padlock (security) and a speaking human (behavioral prep).
*   **Speaking Role: Shivanshu Yadav**
*   **Script:**
    > *"Our vision is simple: to build a privacy-first, low-latency web application that simulates a secure exam room and a high-pressure interview panel. LockedIn AI enables educational institutions to hold secure coding tests while providing students with a realistic, AI-powered environment to practice both technical problem solving and verbal communication."*

---

## Slide 3: Problem Statement
*   **Slide Title:** The Challenges of Remote Testing and Career Preparation
*   **Visuals:** Graphic depicting a candidate looking away or using a mobile device, alongside bullet points highlighting high cheating rates and interview anxiety.
*   **Speaking Role: Uday Singh Prajapati**
*   **Script:**
    > *"Let's address the core problems. First, online exams suffer from high cheating rates. Traditional LMS platforms cannot detect eye-gaze deviation, secondary monitors, tab switching, or external speaking. Second, candidates often struggle with the verbal communication required in live interviews, even if they have strong technical skills. Existing proctoring tools are either invasive or expensive."*

---

## Slide 4: Proposed Solution
*   **Slide Title:** The LockedIn AI Ecosystem
*   **Visuals:** Diagram showing the three main modules: Monaco Code Workspace, AI Proctoring, and Interactive Behavioral Mock Interview.
*   **Speaking Role: Uday Singh Prajapati**
*   **Script:**
    > *"LockedIn AI addresses these challenges with three main modules. First, a Monaco-based coding workspace with real-time video/audio monitoring. Second, an adaptive difficulty engine that updates coding challenges as users submit correct solutions. Third, a voice-to-voice mock interview system that transcribes user speech, evaluates responses, and speaks back using browser speech APIs and the Gemini LLM."*

---

## Slide 5: System Architecture
*   **Slide Title:** Technical Architecture
*   **Visuals:** Diagram showing the client-server data flow, highlighting the connection between the frontend, Flask backend, MediaPipe, SQLite, and the Gemini API.
*   **Speaking Role: Shivanshu Yadav**
*   **Script:**
    > *"Here is our system architecture. The frontend is a single-page web app built with vanilla JS and TailwindCSS, incorporating the Monaco Editor. The backend is powered by Flask. When a user runs code, the Flask backend executes it in an isolated temporary directory via subprocesses. Proctoring frames are analyzed using MediaPipe Face Mesh, while behavioral interviews are routed through the Gemini API or a local Ollama fallback model."*

---

## Slide 6: Real-Time Proctoring Modules
*   **Slide Title:** Multi-Layered Proctoring
*   **Visuals:** Icons for Face Mesh tracking, PyAudio microphone monitoring, and tab visibility monitoring.
*   **Speaking Role: Uday Singh Prajapati**
*   **Script:**
    > *"Our proctoring system uses client-side algorithms to monitor three main channels. For vision, MediaPipe Face Mesh tracks facial landmarks to detect head rotation and eye deviation. For audio, a background thread calculates the RMS value of the microphone feed to identify noise violations. For browser activity, we monitor visibility change events to flag tab switching."*

---

## Slide 7: Sandbox Code Compiler
*   **Slide Title:** Isolated Subprocess Execution
*   **Visuals:** Process flow diagram showing the creation of a temporary directory, code execution, timeout protection, and exit code capture.
*   **Speaking Role: Shivanshu Yadav**
*   **Script:**
    > *"To compile and test user code safely without relying on third-party APIs, we build an isolated local sandbox. For every submission, the server creates a temporary directory, writes the code along with pre-defined assertions, and executes it via a subprocess. We enforce a 5-second execution timeout to prevent infinite loops, capture compiler error outputs, and update syntax and logic error counts accordingly."*

---

## Slide 8: Generative AI & Model Fallback
*   **Slide Title:** Hybrid Cloud-Local LLM Routing
*   **Visuals:** Flowchart showing API requests routing to the Gemini API, with an automatic fallback to local Ollama endpoints in offline environments.
*   **Speaking Role: Shivanshu Yadav**
*   **Script:**
    > *"For interactive feedback and behavioral interviews, we use Google Gemini 2.5 Flash. However, if the user is offline or the API key is unavailable, our system automatically routes prompts to a local Ollama instance running a lightweight model like Llama-3.2-1b. This hybrid architecture ensures the application remains functional in different network environments."*

---

## Slide 9: Database Schema
*   **Slide Title:** SQLite Database Design
*   **Visuals:** ER diagram showing the relationships between the `users`, `sessions`, and `aptitude_questions` tables.
*   **Speaking Role: Uday Singh Prajapati**
*   **Script:**
    > *"Our database is managed using SQLite. The users table tracks credentials, ranks, and total points. The sessions table logs metrics for each attempt, including violations, syntax and logic errors, and JSON arrays for level times and violation logs. The aptitude questions table stores our multiple-choice question pool."*

---

## Slide 10: System Workflow
*   **Slide Title:** Step-by-Step System Flow
*   **Visuals:** Sequence diagram showing the flow of a user starting a test, submitting code, receiving feedback, and reviewing dashboard analytics.
*   **Speaking Role: Uday Singh Prajapati**
*   **Script:**
    > *"This diagram shows the complete session workflow. When the user starts a session, the backend initializes the webcam and audio monitoring thread. Code submissions are run in the sandbox, and final session statistics are saved to the database. The frontend then updates the dashboard to show the user's progress."*

---

## Slide 11: Gaze and Audio Algorithms
*   **Slide Title:** Gaze Tracking & Audio RMS Calculations
*   **Visuals:** Formulations for gaze ratios and audio Root Mean Square values.
*   **Speaking Role: Uday Singh Prajapati**
*   **Script:**
    > *"Let's look at the tracking math. For gaze tracking, we calculate the ratio of the iris center relative to the eye corners. Ratios outside the 0.35 to 0.65 range indicate deviation. For audio monitoring, we calculate the Root Mean Square of the microphone input buffer. If this value exceeds 150, an audio violation is flagged."*

---

## Slide 12: Security & Sandboxing
*   **Slide Title:** Secure Process Isolation
*   **Visuals:** Diagram showing security controls like `shell=False` execution, password hashing, and thread safety locks.
*   **Speaking Role: Shivanshu Yadav**
*   **Script:**
    > *"Security is a key focus. To prevent code injection, we run subprocesses with shell execution disabled. We also use thread locks to coordinate camera access, preventing concurrent access crashes, and hash passwords using PBKDF2 with SHA-256."*

---

## Slide 13: Performance and Scalability
*   **Slide Title:** Performance Optimization
*   **Visuals:** Latency bar chart showing MediaPipe frame analysis, Web Speech API response times, and JPEG compression sizes.
*   **Speaking Role: Uday Singh Prajapati**
*   **Script:**
    > *"We optimized the application for performance. MediaPipe frame analysis takes 12 to 18 milliseconds, enabling a smooth 25 to 30 FPS stream. We also compress frame sizes to JPEG format with 80% quality to reduce network load, and use lightweight fallback models to keep CPU usage low."*

---

## Slide 14: Challenges and Solutions
*   **Slide Title:** Technical Challenges Faced
*   **Visuals:** Split comparison showing initial issues (e.g. thread conflicts, PyAudio crashes) and implemented solutions.
*   **Speaking Role: Shivanshu Yadav**
*   **Script:**
    > *"During development, we resolved several technical challenges. We addressed webcam access conflicts using thread locks, made audio monitoring fail-safe on devices without microphones, and optimized local model routing to prevent CPU lockups during offline mode."*

---

## Slide 15: Comparison with Existing Solutions
*   **Slide Title:** Competitive Analysis
*   **Visuals:** Table comparing LockedIn AI with LeetCode, HackerRank, and traditional LMS platforms across features like gaze tracking and sandbox compilation.
*   **Speaking Role: Uday Singh Prajapati**
*   **Script:**
    > *"Compared to traditional systems, LockedIn AI integrates coding challenges, real-time proctoring, gaze tracking, audio monitoring, and vocal prep into a single, locally hostable application, offering a comprehensive and cost-effective preparation tool."*

---

## Slide 16: Innovation Highlights
*   **Slide Title:** Key Innovations
*   **Visuals:** Highlight cards showing edge computer vision, hybrid cloud-local routing, and sandbox compilation.
*   **Speaking Role: Shivanshu Yadav**
*   **Script:**
    > *"Our main innovations include performing gaze calculations locally on the edge, implementing hybrid LLM routing to handle offline preparation, and compiling code locally in sandboxed subprocesses."*

---

## Slide 17: Live Demonstration
*   **Slide Title:** Live Demonstration Walkthrough
*   **Visuals:** Screen layout showing the coding workspace, active proctoring feed, and dashboard charts.
*   **Speaking Role: Shivanshu Yadav & Uday Singh Prajapati**
*   **Script:**
    > *"(Shivanshu): Let's start the live demonstration. First, we log in and access the dashboard. When we start a coding session, the camera and microphone track our activity. (Uday): If we turn away or speak, the system flags the violation immediately. Finally, we complete a behavioral interview and view the updated radar chart on the dashboard."*

---

## Slide 18: Version 3.0 Platform Updates
*   **Slide Title:** Version 3.0 Updates: Profile Customization & Rich Analytics
*   **Visuals:** UI elements showcasing the Edit Profile dialog, custom Base64 avatar preview, 6-axis Radar skill chart, and the level-by-level cumulative Performance Line Chart.
*   **Speaking Role: Shivanshu Yadav**
*   **Script:**
    > *"In our latest Version 3.0 release, we introduced several user-centric features. First, profile customization: users can now change their username, password, and upload a custom profile picture, which is stored securely in the database as a Base64-encoded string. Second, we updated our analytics: we replaced simple bar charts with a 6-axis Radar chart to measure skills like Syntax, Coding, Speed, and Integrity, and we added a continuous level-by-level cumulative Line Graph compared against developer benchmarks. We also implemented automatic starting and stopping of the local Ollama backend process to optimize system CPU/memory resources."*

---

## Slide 19: Future Roadmap
*   **Slide Title:** Future Enhancements
*   **Visuals:** Roadmap showing plans for Flask session integration, C++ compiler support, and WebRTC video migration.
*   **Speaking Role: Uday Singh Prajapati**
*   **Script:**
    > *"Our roadmap includes migrating the global proctor state to Flask sessions, expanding coding questions, adding C++ compilation support, and migrating video capture to WebRTC to improve backend scalability."*

---

## Slide 20: Conclusion
*   **Slide Title:** Project Summary & Impact
*   **Visuals:** Summary points detailing academic integrity, interview preparation, and the project's overall value.
*   **Speaking Role: Shivanshu Yadav**
*   **Script:**
    > *"In conclusion, LockedIn AI combines real-time edge computer vision and generative AI to offer a secure, accessible testing and interview preparation platform. Thank you for your time, and we are happy to take any questions."*

