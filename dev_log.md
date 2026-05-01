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
