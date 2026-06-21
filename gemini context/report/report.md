# LockedIn Project Report Structure

## 1. Title Page & Abstract
- **Project Title**
- **Student Details**
- **Abstract:** A brief summary of the LockedIn project, its objectives (improving interview skills via AI proctoring and feedback), the technology stack, and the overall outcome.

## 2. Introduction
- **2.1 Background:** The need for comprehensive interview prep tools.
- **2.2 Objectives:** What LockedIn aims to solve (proctoring, realistic environment, AI feedback).
- **2.3 Scope of the Project:** Supported features (Coding, Aptitude, Behavioral).

## 3. Problem Formulation & Proposed Solution
- **3.1 Current System Drawbacks:** Lack of pressure in LeetCode, lack of proctoring in self-assessments.
- **3.2 Proposed System:** LockedIn as an all-in-one solution with a strict environment.

## 4. System Architecture & Tech Stack Details
- **Frontend:** HTML, TailwindCSS, Monaco Editor (for VS Code-like experience), Chart.js (analytics).
- **Backend:** Flask (Python server), subprocess module for isolated code execution.
- **Database:** SQLite (lightweight, relational data mapping).
- **AI & ML:** MediaPipe (Face Mesh for tracking), OpenCV, Google Gemini 2.0 API (Code analysis and behavioral interview).

## 5. Implementation Details
- **5.1 AI Proctoring Module:**
  - Face tracking (calculating nose and iris ratios using MediaPipe).
  - Audio monitoring (volume thresholding using pyaudio/sounddevice).
  - Tab switching detection via JavaScript Visibility API.
- **5.2 Coding Environment:**
  - Keystroke dynamics and copy-paste detection to prevent cheating.
  - Real-time compilation using Python subprocesses.
- **5.3 AI Interviewer:**
  - Integration with Gemini 2.0 to provide code feedback and act as a voice-based behavioral interviewer.
- **5.4 Analytics Dashboard:**
  - Radar charts summarizing skill proficiency based on completed categories.
  - Detailed session reports with violation history.

## 6. Required Diagrams

### 6.1 Use Case Diagram
```mermaid
usecaseDiagram
    actor User
    actor AI_Proctor
    actor AI_Interviewer
    
    User --> (Register / Login)
    User --> (Take Technical Test)
    User --> (Take Aptitude Test)
    User --> (Take Behavioral Interview)
    User --> (View Dashboard & Analytics)
    
    (Take Technical Test) <.. (Monitor Face & Audio) : <<include>>
    AI_Proctor --> (Monitor Face & Audio)
    
    (Take Behavioral Interview) <.. (Evaluate Responses) : <<include>>
    AI_Interviewer --> (Evaluate Responses)
    (Take Technical Test) <.. (Evaluate Code) : <<include>>
    AI_Interviewer --> (Evaluate Code)
```
*(Note: Mermaid use case syntax is better represented using graph LR or flowchart, but standard UML representations can be drawn from this logic.)*

Alternative Use Case Flowchart:
```mermaid
flowchart LR
    U[User] --> L[Login]
    U --> D[Dashboard]
    U --> TT[Technical Test]
    U --> AT[Aptitude Test]
    U --> BI[Behavioral Interview]
    P[AI Proctor] --> M[Monitor Session]
    TT -.-> M
    I[Gemini AI] --> EC[Evaluate Code]
    I --> EV[Evaluate Verbal]
    TT -.-> EC
    BI -.-> EV
```

### 6.2 Data Flow Diagram (Level 0 and Level 1)
**Level 0 (Context Diagram):**
```mermaid
graph TD
    User([User]) -- "Credentials, Code, Voice" --> System[LockedIn System]
    System -- "Video/Audio Stream" --> AI_Models[MediaPipe & OpenCV]
    System -- "Prompts & Context" --> Gemini[Google Gemini API]
    Gemini -- "Feedback & Responses" --> System
    System -- "Dashboard & Reports" --> User
```

**Level 1 DFD:**
```mermaid
graph TD
    U([User]) --> |Login Data| P1(Auth Process)
    P1 --> |Verify| D1[(Users DB)]
    U --> |Select Session| P2(Session Manager)
    P2 --> |Start Proctoring| P3(Proctor Engine)
    U --> |Video/Audio| P3
    P3 --> |Log Violations| D2[(Sessions DB)]
    U --> |Submit Code/Voice| P4(AI Interview Process)
    P4 --> |Prompt| G[Gemini API]
    G --> |Response| P4
    P4 --> |Save Results| D2
    P2 --> |Fetch History| D1 & D2
    P2 --> |Show Dashboard| U
```

### 6.3 Entity-Relationship (ER) Diagram
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

### 6.4 Sequence Diagram (Code Submission to AI Evaluation flow)
```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant FlaskServer
    participant Subprocess
    participant GeminiAPI
    participant Database

    User->>Frontend: Clicks 'Submit Code'
    Frontend->>FlaskServer: POST /run_code (code, lang)
    FlaskServer->>Subprocess: Execute code via temp file
    Subprocess-->>FlaskServer: Return stdout/stderr
    FlaskServer-->>Frontend: Display test results
    
    User->>Frontend: Clicks 'Practice Interview'
    Frontend->>FlaskServer: POST /ai_interview (code, history)
    FlaskServer->>GeminiAPI: Send Prompt with Code
    GeminiAPI-->>FlaskServer: Return AI Feedback
    FlaskServer-->>Frontend: Display AI Feedback to User
    
    User->>Frontend: Stops Session
    Frontend->>FlaskServer: POST /stop_test
    FlaskServer->>Database: Save Session logs, violations, stats
    Database-->>FlaskServer: OK
    FlaskServer-->>Frontend: Show Final Report Modal
```

## 7. Results & Testing
- **Unit Testing:** Validating code execution environment for Python, Java, JS.
- **Proctoring Accuracy:** Precision of face tracking in detecting "looking away" events and capturing audio spikes.
- **Edge Cases Handled:** Syntax vs. Logic errors differentiation, timeout enforcement on infinite loops.

## 8. Conclusion & Future Work
- Summarize the effectiveness of the AI proctor and the value of Gemini feedback.
- Outline next steps (e.g., cloud-based compilation sandbox, multiplayer interviews).

## 9. References
- Flask Documentation
- MediaPipe Face Mesh Research
- Google Gemini API Docs
- Chart.js documentation
