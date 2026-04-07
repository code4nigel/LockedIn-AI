# LockedIn - Presentation Outline

## Slide 1: Title Slide
- **Project Name:** LockedIn (7-Star Editor & AI Interviewer)
- **Subtitle:** An AI-powered proctoring and interview prep platform
- **Team Members:** [Insert Names]
- **Date:** [Insert Date]

## Slide 2: Problem Statement
- Traditional coding platforms lack real-time interview pressure.
- Candidates struggle with behavioral interviews and technical communication.
- Remote assessments suffer from poor proctoring and high cheating rates.

## Slide 3: Introduction
- **What is LockedIn?**
  - A comprehensive AI-driven platform for software engineering interview preparation.
- **Core Value Proposition:**
  - Combines a real-time coding editor with strict AI proctoring.
  - Offers immediate technical and behavioral feedback using Google's Gemini 2.0.

## Slide 4: Tech Stack
- **Frontend:** HTML, TailwindCSS, Monaco Editor, Chart.js
- **Backend:** Python, Flask
- **Database:** SQLite
- **AI & Computer Vision:** OpenCV, MediaPipe (Face Mesh), Google Gemini AI API

## Slide 5: Key Features
- **Real-time AI Proctoring:** Tracks face movement, tab switching, and audio levels.
- **Verbal Behavioral Interviews:** Voice-to-voice interaction with Gemini AI.
- **Skill Analytics Radar:** Visualizes mastery across different CS topics.
- **CS Aptitude Tests:** Quizzes on core computer science concepts.
- **Advanced Code Editor:** Multi-language support (Python, Java, JS) with keystroke dynamic monitoring.

## Slide 6: System Architecture Diagram
- Visualizing Frontend <-> Flask Backend <-> SQLite / Gemini API
```mermaid
graph TD
    A[Frontend Client - HTML/JS/Tailwind] -->|HTTP/REST| B(Flask Backend)
    B -->|SQL Queries| C[(SQLite Database)]
    B -->|API Calls| D[Google Gemini API]
    A -->|Video Stream| B
    B -->|MediaPipe Processing| E[Proctoring Engine]
    A -->|Web Speech API| B
```

## Slide 7: User Flow Diagram
- Login -> Select Mode -> Attempt Challenge -> AI Proctoring -> Final Assessment Report
```mermaid
graph LR
    A[Login/Register] --> B[Dashboard]
    B --> C{Select Session Type}
    C -->|Coding| D[Technical Coding Workspace]
    C -->|Aptitude| E[Aptitude Test]
    C -->|Behavioral| F[AI Verbal Interview]
    D --> G[AI Proctoring Active]
    G --> H[Submit Code]
    H --> I[AI Feedback & Report]
    E --> I
    F --> I
    I --> B
```

## Slide 8: Entity-Relationship (ER) Model
- Tables: Users, Sessions, Aptitude_Questions
```mermaid
erDiagram
    USERS {
        int id PK
        string username
        string password
        int total_points
        string rank
    }
    SESSIONS {
        int id PK
        int user_id FK
        int max_level
        int violations
        int syntax_errors
        int logic_errors
        string timestamp
        string violation_logs
        string level_times
        string categories_completed
        int aptitude_score
        string behavioral_feedback
    }
    APTITUDE_QUESTIONS {
        int id PK
        string question
        string option_a
        string option_b
        string option_c
        string option_d
        string correct_answer
        string category
    }
    USERS ||--o{ SESSIONS : "has many"
```

## Slide 9: Live Demo Highlights
- Discuss or show screenshots of:
  - Violation tracking (Red screen borders for audio/face violations).
  - AI chat window analyzing code.
  - Radar chart showing user skill progression.
  - Verbal interview interface.

## Slide 10: Future Scope & Conclusion
- **Future Enhancements:**
  - Integration with WebRTC for more seamless audio streaming.
  - Expanding language support in the compiler.
  - Multi-user mock interviews.
- **Conclusion:**
  - LockedIn effectively simulates high-pressure interview environments, bridging the gap between learning to code and successfully passing technical interviews.
