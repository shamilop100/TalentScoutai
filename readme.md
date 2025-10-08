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


