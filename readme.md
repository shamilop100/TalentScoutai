# 🤖 TalentScout AI Hiring Assistant Chatbot

An **intelligent Hiring Assistant chatbot** designed to automate the **initial technical screening** of candidates. The chatbot collects candidate information, generates tailored **technical questions** based on their tech stack, and evaluates responses in a conversational, professional manner.

---

## 🚀 Project Overview

The **TalentScout AI Assistant** is a smart, conversational recruitment chatbot built using **Python** and **Ollama’s LLaMA2 model**.  
It performs the following tasks:

- Collects essential candidate details (name, email, experience, location, etc.)
- Dynamically generates 5 technical questions tailored to the candidate’s **tech stack**
- Conducts a conversational Q&A session
- Evaluates responses and provides feedback
- Concludes with a warm, professional summary and next steps

This project demonstrates how **LLMs can enhance recruitment workflows** by providing context-aware, interactive screening.

---
##✨ Key Features

### 1. Information Collection
Collects candidate details: Name, Email, Phone, Experience, Position, Location, and Tech Stack (Languages, Frameworks, Databases, Tools).

### 2. AI-Generated Questions
Generates 5 smart, tech-specific questions with contextual follow-ups based on the candidate’s stack (e.g., Python, Django, React, PostgreSQL).

### 3. Conversational Intelligence
Understands natural language, maintains context, handles off-topic queries, and requests clarifications when needed.

### 4. User Experience
Includes progress tracking, categorized tech stack view, JSON export, responsive design, and a modern Streamlit UI.
## 🧠 Capabilities

- **Conversational Interaction**: Natural, human-like dialogue using LLM prompts  
- **Personalized Questioning**: Generates questions tailored to each candidate’s tech stack  
- **Validation & Correction**: Detects invalid inputs (e.g., wrong email formats)  
- **Fallback Handling**: Works even when LLM is unavailable (rule-based fallback)  
- **Graceful Exit**: Supports early exit and resumes conversation naturally  

---

## ⚙️ Installation Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/talentscout-chatbot.git
cd talentscout-chatbot

python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

pip install ollama




