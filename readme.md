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

----

## 🚀 Installation
### Prerequisites

Python 3.8 or higher
Ollama (for running Llama2 locally)
Operating System: Windows, macOS, or Linux

 

---

## 📖 Usage

1. Start conversation - Greet the bot to begin
2. Provide information - Answer questions about name, email, experience, and tech stack
3. Answer technical questions - Bot generates 5 questions based on YOUR tech stack
4. Export data - Download screening results as JSON
   
---

### 🧠 Technical Stack

| **Component** | **Technology**          |
|----------------|-------------------------|
| **LLM**        | Llama2 (7B) via Ollama  |
| **Backend**    | Python 3.8+             |
| **Frontend**   | Streamlit               |
| **Data**       | JSON                    |

---

##🎨 Prompt Design
The chatbot uses carefully crafted prompts to guide Llama2:
System Prompt: Defines role as friendly technical recruiter
Context Injection: Each message includes current state and instructions
Off-Topic Handling: Answers questions naturally while staying on track
Question Generation: Generates 5 tech-specific questions using candidate's stack

---
### 📂 Project Structure

talentscout-ai-hiring-assistant/
├── app.py               # Streamlit UI
├── chatbot.py           # Core chatbot logic with LLM
├── requirements.txt     # Dependencies
└── README.md            # Project documentation


---

### requirements.txt:
 streamlit==1.28.0
 ollama==0.1.6

---

### 🚀 Installation & Setup

#### 1. Install Ollama
*Windows:
Download and install from https://ollama.ai/download






