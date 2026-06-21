# LockedIn Future Planning & Roadmap

Based on the current architecture (Flask, MediaPipe, Monaco Editor, SQLite) and the goal of creating a secure, AI-driven interview simulator, here is the strategic roadmap for the features we should add and the anti-features we should avoid.

## What SHOULD Be There (Planned Features)

1. **True Multi-Language Support**
   - **Why:** The UI currently has a dropdown for Python and Java, but the backend execution logic is currently hardcoded for Python.
   - **How:** Expand the local execution engine to compile and run Java, C++, and JavaScript with isolated test cases. We will continue to use local execution to ensure we maintain exact terminal outputs for syntax and logic errors in the UI, avoiding the limitations of external APIs like Judge0 or Piston.
2. **Advanced AI Proctoring**
   - **Why:** To make the "LockedIn" environment more robust against sophisticated cheating.
   - **How:** 
     - Object Detection (YOLO) to detect mobile phones in the frame.
     - Keystroke dynamics to detect unnatural typing speeds or large copy-paste dumps.
     - Optional browser extension for screen sharing/secondary monitor detection.
3. **Interactive AI Interviewer (LLM Integration)**
   - **Why:** To simulate a real interview rather than just an automated judge.
   - **How:** After the user passes all test cases, an LLM (like Gemini) analyzes the code's time/space complexity and asks a follow-up question via a chat interface or text-to-speech.
4. **Enhanced Dashboard Analytics**
   - **Why:** To provide actionable feedback to the user.
   - **How:** Tag questions by topic (e.g., Arrays, Dynamic Programming) and show heatmaps or radar charts of their strengths and weaknesses over time.

## What SHOULD NOT Be There (Anti-Features)

1. **External Execution APIs (Judge0/Piston API)**
   - **Why:** External APIs have limitations and often fail to return exact, raw terminal outputs for code errors (like specific syntax tracebacks) which are critical for our UI error reporting. We will maintain our local execution setup.
2. **Invasive Kernel-Level Anti-Cheat**
   - **Why:** We are an educational web app. Requiring users to install rootkits (like Vanguard) breaks cross-platform compatibility (Mac/Linux), destroys user trust, and is overkill.
3. **Manual Live Human Proctoring Dashboard**
   - **Why:** The core value proposition of LockedIn is *Automated AI Proctoring*. Building a heavy dashboard for human proctors to watch 50 live WebRTC streams simultaneously deviates from our unique selling point and adds massive server overhead.
4. **Heavy Frontend Framework Rewrite (React/Next.js)**
   - **Why:** The current Vanilla JS + Tailwind setup is lightweight and fast. Unless the UI state becomes unmanageable (e.g., adding real-time collaborative editing), rewriting the frontend is a waste of resources right now. Progressive enhancement is sufficient.
5. **Social Networking Features**
   - **Why:** While sharing scores is fine, building a full social feed, friends lists, and messaging distracts from the core loop: Practice, Test, Analyze.