# CBSE 10th Smart Tutor

A professional, Retrieval-Augmented Generation (RAG) powered Q&A platform designed for comprehensive CBSE Class 10 board examination preparation.

This intelligent tutoring system leverages **FastAPI**, **NeonDB (pgvector)**, a **Vanilla JavaScript/HTML/CSS Frontend**, and **Groq LLaMA-3.3-70B** to provide students with precise, board-exam-optimized answers.

The platform's knowledge base is exhaustive, comprising complete NCERT textbooks, detailed chapter solutions, and an extensive collection of Past Year Questions (PYQs) from all previous years to ensure no topic is left uncovered.

---

## Project Structure

```
Gen-AI-Final-Project/
├── server/                         # FastAPI Backend
│   ├── main.py                     # Initializer and boot sequence
│   ├── requirements.txt            # Python dependencies
│   ├── railpack-plan.json          # Deployment configuration
│   ├── .env                        # Environment configurations
│   │
│   ├── api/
│   │   └── routes.py               # REST API endpoints
│   │
│   ├── agent/
│   │   └── groq_agent.py           # Core agent logic and prompt engineering
│   │
│   ├── database/
│   │   └── neon_db.py              # Vector database operations
│   │
│   └── ingestion/
│       └── pdf_loader.py           # Document embedding matrix
│
├── client/                         # Stateless Frontend Web Interface
│   ├── index.html                  # Core DOM structure
│   ├── style.css                   # Premium CSS stylesheets
│   ├── app.js                      # Asynchronous API logic
│   └── run_frontend.py             # Local development server script
```

---

## Technical Features

* **Comprehensive Knowledge Base:** Integrates comprehensive NCERT content and exhaustive all-year Past Year Questions (PYQ) across Mathematics, Science, English, and Social Science.
* **Stateless Deployment:** The server repository has been perfectly isolated. All PDF processing is run asynchronously off-deployment, allowing the server to utilize minimal memory.
* **Premium Client Architecture:** The frontend utilizes an ultra-fast, dependency-free vanilla technology stack. 
* **Dynamic Generation:** Answers are structurally mapped to match explicit CBSE board grading rubrics (Concept, Context, Step-by-Step Resolution, Marks Distribution).

---

## Local Development Setup

### 1. Backend Server Configuration
Navigate to the server directory, install the required packages, and start the FastAPI application:

```bash
cd server
pip install -r requirements.txt

# Ensure your .env file is populated with:
# DATABASE_URL=...
# GORQ_API_KEY=...

uvicorn main:app --reload --port 8000
```
The API documentation will be available at: http://localhost:8000/docs

### 2. Frontend Client Application
The frontend requires no package manager. Simply serve the directory locally using the provided python script:

```bash
cd client
python run_frontend.py
```
The User Interface will be available at: http://localhost:3000

---

## Deployment Architecture

The application is structured to be deployed efficiently using a decoupled microservice architecture:

1. **Backend Server (Web Service):**
   * Deploy the `server/` directory as a standard Web Service on Render or Railway.
   * Provide the `DATABASE_URL` and `GORQ_API_KEY` environmental arguments.
   * `railpack-plan.json` is provided to define explicit build phases if required.

2. **Frontend Website (Static Site):**
   * Deploy the `client/` directory as a completely free Static Site on Render.
   * The `app.js` file handles all backend routing asynchronously.

---

## System Workflow (RAG Pipeline)

```
Student Query
       |
       v
Context Embedding (MiniLM-L6-v2)
       |
       v
Vector Similarity Search (NeonDB via pgvector)
       |  (Retrieves highest-confidence chunks from PYQs and NCERT materials)
       v
Generative Resolution (Groq LLaMA-3.3-70B)
       |
       v
System Output:
  - Immediate Conceptual Overview
  - Methodical Board-Standard Answer Formulation
  - Expected Mark Breakdown and Examiner Expectations
```
