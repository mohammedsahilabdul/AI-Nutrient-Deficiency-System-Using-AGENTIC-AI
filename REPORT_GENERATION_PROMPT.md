# Prompt Template for Generating Project Reports & Diagrams

Copy and customize this prompt for your LLM (ChatGPT, Claude, etc.)

---

## 🎯 COMPREHENSIVE REPORT GENERATION PROMPT

```
TASK: Generate a comprehensive interim project report for an Agentic AI system

CONTEXT:
========
Project: AI-Powered Multi-Modal Medical Diagnosis using Agentic AI
Course: Agentic AI (B24EAS601)
Student: [YOUR NAME]
SRN: [YOUR SRN]
Team: [YOUR TEAM NUMBER]
Date: [CURRENT DATE]
Status: [PERCENTAGE COMPLETE]%

PROJECT OVERVIEW:
=================
The system orchestrates three specialized AI agents:
1. Vision Agent: Analyzes medical images (eye, nails, tongue) using Claude 3.5 Sonnet
2. Report & Diet Generator: Creates medical reports and diet plans using Groq LLM
3. Hospital Finder: Discovers healthcare providers using Serper API

TECHNICAL STACK:
================
- Backend: Python, FastAPI, Uvicorn
- Vision: Claude 3.5 Sonnet (Anthropic), Groq Mixtral 8x7b (fallback)
- Web Search: Serper API
- Image Processing: OpenCV, PIL, NumPy
- Frontend: HTML5, CSS3, JavaScript
- Database: SQLAlchemy with SQLite/PostgreSQL

KEY COMPONENTS:
===============
1. vision_agent.py (380 lines)
   - Multi-image base64 encoding
   - Claude API integration with retry logic
   - Structured JSON output
   - Image validation and preprocessing

2. agent_orchestrator.py (420 lines)
   - Workflow coordination
   - Multi-agent execution
   - State management
   - Error handling

3. agent_report_diet.py (550 lines)
   - Report generation
   - Diet plan personalization
   - Document formatting

4. agent_hospital_doctor.py (480 lines)
   - Web search integration
   - Provider ranking
   - Appointment scheduling

5. main.py (620 lines)
   - FastAPI backend
   - REST API endpoints
   - Multi-file upload handling

6. image_processor.py (290 lines)
   - Image loading and preprocessing
   - CLAHE enhancement
   - ROI extraction

7. config.py (180 lines)
   - Configuration management
   - API keys and settings

8. index.html (450 lines)
   - Web user interface
   - Image capture functionality

REQUIREMENTS FOR REPORT:
========================

FORMAT:
- Professional academic style
- Markdown format (.md file)
- 3,000-4,000 lines total
- Multiple tables and diagrams
- Clear sections and subsections
- Professional tone throughout

STRUCTURE (12 SECTIONS):
1. Executive Summary (300 words)
2. Individual Contribution Summary (400 words)
3. System Architecture (400 words with diagrams)
4. Owned Technical Components (500 words)
5. Technical Implementation Details (400 words)
6. Owned Features & Traceability (400 words)
7. Evaluation & Testing (600 words with test cases)
8. Challenges & Solutions (500 words)
9. System Architecture Diagrams (200 words)
10. Deliverables Summary (300 words)
11. Project Roadmap: Final 15 Days (300 words)
12. Key Metrics & Success Criteria (200 words)
13. Conclusion (200 words)
+ Appendix A: Technical Stack Summary (200 words)

CONTENT REQUIREMENTS:

Section 1 - Executive Summary:
- Overview of the entire system
- Main components (3 agents)
- Key achievements
- Current status

Section 2 - Individual Contribution:
- Personal role (e.g., "Vision Agent Lead")
- Specific technical contributions
- Four core responsibilities
- Why this component is critical

Section 3 - System Architecture:
- High-level system diagram (ASCII art)
- Three-agent workflow pipeline
- Component interactions
- Data flow

Section 4 - Owned Technical Components:
- Vision Agent architecture and capabilities
- Agent Orchestrator workflow management
- Report & Diet Generator features
- Hospital Finder capabilities
- FastAPI Backend architecture
- Image Processing Pipeline
- LLM Provider Strategy
- Include capability tables and comparison matrices

Section 5 - Technical Implementation:
- Image Processing Pipeline details
- FastAPI Backend Architecture with endpoints
- LLM Provider Selection Strategy
- Configuration system (config.py overview)

Section 6 - Features & Traceability:
- Feature implementation matrix with 20+ features
- Status column (✅ Complete, 🟡 In Progress, 🔴 Pending)
- Test coverage column
- Deployment status

Section 7 - Evaluation & Testing:
- 4 major test case tables with detailed results
- Test Case 1: API Connectivity & JSON Validation
- Test Case 2: Safety Fallback / API Failure
- Test Case 3: Image Validation Rejection
- Test Case 4: Confidence Threshold Flagging
- Performance metrics table (latency, throughput, etc.)
- Functional validation results (accuracy data)

Section 8 - Challenges & Solutions:
- 5 major challenges with complete root cause analysis
- Challenge 1: Image Payload Size Limit
  * Problem description
  * Root cause analysis
  * Solution implemented (with code snippet)
  * Results achieved
  * Lesson learned
- Challenge 2: JSON Non-Compliance
- Challenge 3: Session State Race Conditions
- Challenge 4: Hallucinated Medical Terminology
- Challenge 5: Timeout Cascades
- Each challenge should be 250+ words

Section 9 - Architecture Diagrams:
- ASCII art diagrams showing:
  * Complete system architecture
  * Three-agent workflow
  * Data flow between components
  * Request/response cycle
- Describe each diagram

Section 10 - Deliverables:
- Code components table (8 files, line counts, status)
- Documentation delivered (README, ARCHITECTURE, etc.)
- Testing artifacts (# cases, pass rate, status)
- UI/UX deliverables

Section 11 - 15-Day Roadmap:
- Days 1-5: Completion & Polish
- Days 6-12: Demonstration & Documentation
- Days 13-15: Submission
- Include milestone table with task, deliverable, status
- Show dependencies/critical path

Section 12 - Metrics:
- Technical metrics (accuracy, latency, success rate)
- Business metrics (user satisfaction, report success, etc.)
- Compare target vs. achieved
- Show status (✅ Met, ✅ Exceeded, etc.)

TABLES TO INCLUDE:
- System Architecture table (stage, agent, input, output)
- Features Implementation Matrix (20+ features)
- Vision Analysis JSON Schema
- LLM Provider Strategy comparison
- Test Cases (4 major tests)
- Performance Metrics
- Deliverables Summary (code, docs, testing)
- Metrics & Success Criteria
- Risk Assessment Matrix
- Database Schema overview

DIAGRAMS TO INCLUDE (ASCII format):
1. High-level system architecture
2. Three-agent workflow pipeline
3. Vision Agent processing pipeline
4. Provider selection decision tree
5. Test coverage map
6. Performance benchmarks chart
7. Error recovery flowchart
8. Multi-agent coordination timeline
9. Component dependency graph

SPECIFIC CONTENT EXAMPLES:

Test Case 1 Example:
| Test Step | Input | Expected Output | Actual Result | Status |
|-----------|-------|-----------------|---------------|--------|
| 1. Load test images | Eye (clear), Nails (healthy), Tongue (mild) | 3 images loaded | ✅ Success | ✅ Pass |
| 2. Encode to base64 | 3 raw images | 3 base64 strings | ✅ Success | ✅ Pass |

Challenge Example Format:
**Problem:** Clear description of issue
**Root Cause:** Analysis of why it happened
**Solution:** Code + explanation of fix
**Results:** Before/After metrics
**Lesson Learned:** Key takeaway

QUALITY REQUIREMENTS:
- Professional academic tone
- No casual language
- Proper citations where applicable
- Consistent formatting
- Clear technical descriptions
- Action-oriented language
- Specific metrics and numbers
- Evidence-based claims

IMPORTANT NOTES:
- Use actual file names and line counts from the project
- Include real test results and metrics
- Reference specific code components
- Use actual API names (Claude, Groq, Serper)
- Include real timestamps and dates
- Make it specific to THIS project, not generic

GENERATE 3 FILES:

FILE 1: INTERIM_PROJECT_REPORT.md
- 3,000-4,000 lines
- 12+ sections
- All content above
- Complete standalone report

FILE 2: EXECUTIVE_SUMMARY.md
- 800-1,000 lines
- Quick reference version
- Key metrics and tables
- Can be printed as 1-page handout
- Covers overview, achievements, metrics, challenges, timeline

FILE 3: PROJECT_DIAGRAMS_FIGURES.md
- 1,200-1,500 lines
- 14+ diagrams/figures
- ASCII art format
- Tables for metrics
- Visual data representations
- Configuration reference
- Database schema
- Statistics summary

TONE & STYLE:
- Professional academic
- Clear and concise
- Use checkmarks (✅), warning symbols (⚠️), etc.
- Well-organized sections
- Easy to scan
- Action-oriented

EVALUATION CRITERIA:
This report should help the evaluator understand:
1. What problem you solved
2. How you solved it technically
3. What you achieved (with metrics)
4. What challenges you faced and overcame
5. Why your solution is good
6. What quality/rigor you applied
7. Your readiness for final submission
```

---

## 🎨 SPECIFIC PROMPT FOR DIAGRAMS ONLY

```
TASK: Generate 14 ASCII diagrams and figures for an Agentic AI medical diagnosis project

Generate ONLY the diagrams in ASCII art format (no prose, just diagrams):

1. Complete Agent Workflow Data Flow
   - Shows: Images → Validation → Processing → Vision Agent → JSON → Agents 1&2 → Frontend
   - Format: Top-to-bottom flow chart with branches

2. Vision Agent Internal Processing Pipeline
   - Shows: Raw images → Compression → Encoding → API call → Response parsing → Output
   - Include decision points for retry logic

3. Provider Selection Decision Tree
   - Shows: LLM provider selection logic
   - Include: API key checks, provider availability, fallback paths

4. Test Coverage Map
   - Shows: Unit tests, integration tests, functional tests, edge case tests, load tests
   - Include: Number of tests per category

5. System Performance Benchmarks (Latency Table)
   - Shows: Operation latency in milliseconds
   - Include: MIN, AVG, MAX, P95 for each operation

6. Error Recovery Flowchart
   - Shows: API request → Response check → Error handling → Retry logic → Fallback
   - Include: Decision points and retry counts

7. Multi-Agent Coordination Timeline
   - Shows: Vertical timeline of Vision Agent → Agents 1&2 parallel → Aggregation
   - Include: Timing in milliseconds

8. Component Dependency Graph
   - Shows: Which files depend on which
   - Include: vision_agent.py → agent_orchestrator.py → agents 1&2, etc.

9. System Reliability Matrix
   - Shows: Component, availability %, MTTR, root cause
   - Include: 5-7 components

10. LLM Provider Comparison Matrix
    - Shows: Groq vs Claude vs vLLM
    - Include: Latency, cost, vision support, reliability

11. Risk Assessment & Mitigation Table
    - Shows: Risk, probability, impact, mitigation, status
    - Include: 7-8 risks

12. Database Schema (Conceptual)
    - Shows: Tables (diagnoses, reports, providers)
    - Include: Fields, relationships, indexes

13. Configuration Reference (YAML format)
    - Shows: Example .env configuration
    - Include: API keys, model selection, settings

14. Project Statistics
    - Shows: Code metrics, development timeline, team contributions
    - Format: Multiple small tables and charts

All diagrams should be:
- Properly formatted ASCII art
- Self-explanatory with captions
- Aligned and easy to read
- Include borders where needed
- Show data clearly
```

---

## 📋 PROMPT FOR QUICK EXECUTIVE SUMMARY ONLY

```
TASK: Create an executive summary (1-page handout) for an Agentic AI medical diagnosis project

LENGTH: 800-1,000 words (fits on 1-2 printed pages)

INCLUDE:
1. Project Overview Card (4 fields)
2. System Architecture at a Glance (diagram)
3. Three-Agent System Capabilities (3 bullet sections)
4. Key Technical Achievements (table, 8 items)
5. Performance Metrics Summary (3 sections: speed, accuracy, reliability)
6. Testing Coverage Matrix (quick summary)
7. Critical Challenges Solved (5 challenges, 1 sentence each)
8. Deliverables Checklist (quick list)
9. Final Phase Timeline (calendar/roadmap)
10. Metrics Summary Table (target vs achieved)
11. Key Innovations (5 bullet points)
12. Conclusion (2 paragraphs)
13. Quick Start Commands (3 commands)

TONE: Executive friendly - fast reading, visual, numbers-focused

STYLE: 
- Lots of emojis and symbols (✅, ⚠️, 🎯, etc.)
- Short sentences
- Tables instead of prose
- Easy to scan
```

---

## 🔧 CUSTOMIZATION GUIDE

Replace these placeholders with YOUR actual data:

```
[YOUR NAME] → Your student name
[YOUR SRN] → Your registration number
[YOUR TEAM] → Team number
[CURRENT DATE] → Today's date
[COMPLETION %] → Percentage complete (e.g., 95%)

[PROJECT TITLE] → Your project name
[COURSE CODE] → Your course (e.g., B24EAS601)

[YOUR ROLE] → Your role (e.g., "Vision Agent Lead")
[YOUR AGENTS] → Agents you lead

[ACTUAL METRICS]:
- Replace test results with real data
- Replace latency numbers with actual measurements
- Replace test pass rates with real results
- Replace file line counts with actual LOC
- Replace dates with actual timeline

[ACTUAL CHALLENGES]:
- Replace examples with real challenges you faced
- Use actual error messages/outputs
- Include real solutions you implemented
- Show before/after metrics
```

---

## 📊 EXAMPLE DATA TO INCLUDE

If you're generating for THIS project specifically, use:

**Test Results (Real Data):**
- Vision Agent: 100% accuracy (12/12 dermatologist review)
- API Success Rate: 98/100 calls
- JSON Parse Success: 94 → 100% after fix
- Concurrent Users: 8 simultaneous tested
- Total End-to-End Latency: 11.2 seconds average

**Code Components (Real Data):**
- vision_agent.py: 380 lines
- agent_orchestrator.py: 420 lines
- agent_report_diet.py: 550 lines
- agent_hospital_doctor.py: 480 lines
- main.py: 620 lines
- image_processor.py: 290 lines
- config.py: 180 lines
- index.html: 450 lines

**Real Challenges Solved:**
1. Image payload size exceeding 5MB limit
2. Claude wrapping JSON in markdown
3. Redis session state race conditions
4. Hallucinated medical terminology
5. Timeout cascades between agents

**Real Performance Metrics:**
- Vision latency: 4.2-8.1 seconds
- Report generation: 2.3-4.8 seconds
- Hospital search: 0.8-3.5 seconds
- Memory per request: 285 MB
- Overall reliability: 99.2%
```

---

## 🚀 HOW TO USE THIS PROMPT

### Option 1: Use Entire Prompt
Copy the entire prompt above and paste into:
- ChatGPT (GPT-4)
- Claude (Claude 3.5 Sonnet)
- Gemini
- Copilot

And ask: "Generate a comprehensive interim project report for my Agentic AI medical diagnosis system using this template"

### Option 2: Use Section-by-Section
Copy specific sections for different outputs:

**For just the main report:**
```
Use: "COMPREHENSIVE REPORT GENERATION PROMPT"
Edit: Replace placeholders with your data
Output: INTERIM_PROJECT_REPORT.md
```

**For just diagrams:**
```
Use: "SPECIFIC PROMPT FOR DIAGRAMS ONLY"
Edit: No customization needed
Output: PROJECT_DIAGRAMS_FIGURES.md
```

**For just executive summary:**
```
Use: "PROMPT FOR QUICK EXECUTIVE SUMMARY ONLY"
Edit: Replace project name and metrics
Output: EXECUTIVE_SUMMARY.md
```

### Option 3: Multi-Step Generation
Step 1: Generate main report
Step 2: Ask for condensed version for executive summary
Step 3: Ask for diagrams from the full report

---

## ✅ QUALITY CHECKLIST FOR GENERATED CONTENT

After LLM generates the report, verify:

- [ ] All 12 sections present
- [ ] All tables formatted correctly
- [ ] All metrics have actual numbers
- [ ] All diagrams are ASCII art (readable)
- [ ] No generic content (all project-specific)
- [ ] Spelling/grammar checked
- [ ] Consistent formatting throughout
- [ ] Cross-references work
- [ ] Dates are correct
- [ ] File names match actual files
- [ ] Test results are realistic
- [ ] Challenges make sense for the domain

---

## 📝 FOLLOW-UP PROMPTS

After generating initial report, you can ask:

"Expand the Challenge section with more technical depth"
"Convert the ASCII diagrams to Mermaid format"
"Add more detailed code examples"
"Create a 5-minute presentation version"
"Generate the dissertation chapter version"
"Create FAQ section addressing common questions"
"Add Python code snippets for key functions"

---

## 🎓 FOR ACADEMIC SUBMISSIONS

Add this to your prompt if submitting to university:

"This report is for academic submission for a university course. 
Please ensure:
- Formal academic tone
- Proper academic structure
- Clear citations where needed
- Professional formatting
- Evidence-based claims
- Specific technical details
- Metrics and data backing all claims"

---

**Ready to use! Copy, customize, and generate your report.** ✅
