## Day 1 — Project Initialization & Core Decisions

### Problem

I realized that even though I spend time learning and working, I tend to forget what I actually did.
Tracking progress manually (writing notes/diary) felt time-consuming and unsustainable.

---

### Idea

To solve this, I decided to build an **AI-driven personal assistant** that:

* Accepts **voice input** (primary goal)
* Converts it into structured daily logs
* Stores it as a **journal/diary (Notion)**
* Acts as a **personal assistant** (future):

  * reminders
  * progress tracking
  * memory of past activities

---

### Initial Approach

* Built a simple UI using **Streamlit**
* Goal: create a fast interface to input daily activity

---

### LLM Decision

I needed an LLM to process raw input → clean diary entries.

#### Options considered:

* OpenAI / Gemini
  ❌ Paid / limited free usage
  ❌ Requires internet

#### Final choice:

* **Ollama + Llama3 (local LLM)**
  ✅ Free
  ✅ Runs locally
  ✅ No API dependency
  ✅ Better for learning system design

---

### First Issue Faced

The LLM generated incorrect dates (e.g., “March 12”) even when the input was from today.

---

### Root Cause

* LLM has **no real-time awareness**
* It guesses based on training data

---

### Key Design Decision

Initially considered:

* Letting LLM handle date/time via prompt ❌

Final decision:

* Handle date/time using **Python (`datetime`)** ✅

---

### Important Learning

Clear separation of responsibilities:

* **LLM → text processing only**
* **Python → system logic (date, time, control)**
* **External tools (Notion, DB) → storage**

---

### Architecture Direction (emerging)

```text
User Input → LLM (rewrite) → Python (adds metadata) → Storage (Notion)
```

---

### What I Learned Today

* LLMs are not aware of real-time data
* Prompt engineering is required to control output
* Local LLMs (Ollama) are powerful for zero-cost development
* Clean system design requires separating AI logic and application logic

---

### Next Steps

* Connect LLM output to Notion
* Store entries with proper date/time
* Build daily journal system
## Day 2 — LLM Integration, Control & System Design Corrections

### What I Did

* Integrated a **local LLM (Ollama + Llama 3)** into the Streamlit app
* Created a separate module (`core/llm.py`) to handle AI processing
* Connected UI (`app.py`) → LLM → output pipeline
* Successfully generated diary-style outputs from user input

---

### Problems I Faced

#### 1. LLM behaving like a chatbot

* Instead of rewriting input, the model:

  * gave advice
  * expanded content
  * added suggestions
* Realized that LLM defaults to “helpful assistant mode”

---

#### 2. Incorrect date generation

* LLM randomly generated dates (e.g., March 12)
* This broke the core requirement of accurate daily tracking

---

#### 3. Output length issues

* Responses were:

  * too long
  * unnecessarily expanded
  * sometimes cut off with “...”

---

#### 4. Loss of control over content

* LLM:

  * added new details ❌
  * changed tone ❌
  * removed or over-explained parts ❌

---

### Key Decisions Made

#### 1. Switched from API-based LLM → Local LLM

* Dropped OpenAI/Gemini due to:

  * cost
  * dependency on internet
* Chose **Ollama (local runtime)**:

  * free
  * offline
  * better for system-level understanding

---

#### 2. Introduced modular architecture

Separated responsibilities:

* `app.py` → UI
* `llm.py` → AI processing

---

#### 3. Fixed LLM behavior using prompt engineering

Refined prompt multiple times to enforce:

* no advice
* no hallucination
* no added content
* no shortening/expanding unnecessarily

Final behavior:

> Clean, natural diary-style rewriting with same meaning

---

#### 4. Corrected system design for date/time

Initial mistake:

* Tried to make LLM generate date/time ❌

Final decision:

* Use Python (`datetime`) as source of truth ✔️

---

### Important Learning

* LLMs are **not reliable for real-world facts (like time)**
* Prompt design directly controls system behavior
* LLM must be treated as:

  > a text processor, not a decision maker

---

### System Architecture (updated)

```text
User Input
   ↓
LLM (clean + normalize + diary style)
   ↓
Python (adds date & time)
   ↓
Display (UI)
   ↓
Next → Notion (storage)
```

---

### What I Achieved

* Built a working **AI-powered text normalization pipeline**
* Converted messy user input → structured diary-style entries
* Established clean separation between:

  * AI logic
  * system logic

---

### Next Step

* Integrate Notion API
* Store each processed entry with timestamp
* Build persistent daily diary system
