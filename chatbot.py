import re
import json
import ollama
from typing import Dict, List, Any, Tuple, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TalentScoutChatbot:
    def __init__(self):
        self.conversation_state = {
            'step': 'greeting',
            'collected_data': {},
            'current_questions': [],
            'current_question_index': 0,
            'technical_answers': {},
            'conversation_history': [],  # For LLM context
            'awaiting_field': None
        }
        
        # Define the information collection flow
        self.info_fields = {
            'full_name': 'full name',
            'email': 'email address',
            'phone': 'phone number',
            'years_experience': 'years of professional experience',
            'desired_position': 'desired position',
            'current_location': 'current location',
            'tech_stack': 'detailed tech stack (programming languages, frameworks, databases, tools)'
        }
        
        self.field_order = ['full_name', 'email', 'phone', 'years_experience', 
                           'desired_position', 'current_location', 'tech_stack']
        self.current_field_index = 0
        
        # System prompt for the LLM
        self.system_prompt = """You are TalentScout AI Assistant, a friendly and professional technical recruiter conducting initial candidate screening.

Your role:
1. Collect candidate information: full name, email, phone, years of experience, desired position, location, and detailed tech stack
2. Generate 5 tailored technical questions based on the candidate's tech stack
3. Ask technical questions one by one and evaluate answers
4. Be conversational, friendly, and professional
5. Handle clarifications and follow-up questions naturally
6. Stay focused on the screening purpose but be helpful and engaging

Guidelines:
- Be warm and encouraging
- Ask for clarification when answers are unclear
- Acknowledge good answers
- If someone asks you something off-topic, politely redirect them back to the screening
- If someone asks your name, respond naturally: "I'm TalentScout AI Assistant"
- Maintain conversation context throughout
- End gracefully when screening is complete or user wants to exit"""

        self._check_ollama_availability()

    def _check_ollama_availability(self):
        """Check if Ollama is running and llama2 model is available"""
        try:
            models = ollama.list()
            model_names = [model['name'] for model in models.get('models', [])]
            
            if not any('llama2' in name.lower() for name in model_names):
                logger.warning("llama2 model not found. Will use rule-based responses.")
                logger.info("To install llama2, run: ollama pull llama2")
                self.llm_available = False
            else:
                logger.info("llama2 model is available")
                self.llm_available = True
        except Exception as e:
            logger.warning(f"Could not connect to Ollama: {e}")
            logger.info("Make sure Ollama is running. Will use rule-based responses.")
            self.llm_available = False

    def get_greeting(self) -> str:
        """Return the initial greeting message"""
        return """👋 Hello! I'm TalentScout AI Assistant from TalentScout Recruitment.

I'm here to conduct an initial technical screening for technology positions. I'll chat with you to collect your information and then ask some technical questions based on your skills.

This should take about 10-15 minutes. Ready to get started?"""

    def process_message(self, user_input: str) -> Tuple[str, Dict]:
        """
        Process user input using LLM for natural conversation
        """
        user_input = user_input.strip()
        
        # Add to conversation history
        self.conversation_state['conversation_history'].append({
            'role': 'user',
            'content': user_input
        })
        
        # Check for exit commands
        if self._is_exit_command(user_input):
            response = self._handle_exit()
            self._add_assistant_message(response)
            return response, self._get_state_info()
        
        # Route based on current step
        if self.conversation_state['step'] == 'greeting':
            response = self._handle_greeting_response(user_input)
        elif self.conversation_state['step'] == 'collecting_info':
            response = self._handle_info_collection(user_input)
        elif self.conversation_state['step'] == 'technical_questions':
            response = self._handle_technical_questions(user_input)
        elif self.conversation_state['step'] == 'complete':
            response = self._handle_post_completion(user_input)
        else:
            response = self._get_llm_response(user_input, "Handle this unexpected state naturally.")
        
        self._add_assistant_message(response)
        return response, self._get_state_info()

    def _add_assistant_message(self, message: str):
        """Add assistant message to conversation history"""
        self.conversation_state['conversation_history'].append({
            'role': 'assistant',
            'content': message
        })
        # Keep only last 30 messages
        if len(self.conversation_state['conversation_history']) > 30:
            self.conversation_state['conversation_history'] = \
                self.conversation_state['conversation_history'][-30:]

    def _is_exit_command(self, user_input: str) -> bool:
        """Check if user wants to exit"""
        exit_words = ['bye', 'exit', 'quit', 'goodbye', 'stop', 'end']
        return any(word in user_input.lower().split() for word in exit_words)

    def _handle_exit(self) -> str:
        """Gracefully conclude the conversation using LLM"""
        self.conversation_state['step'] = 'complete'
        
        context = f"""The candidate wants to exit. Current progress:
- Information collected: {list(self.conversation_state['collected_data'].keys())}
- Technical questions answered: {len(self.conversation_state['technical_answers'])}

Generate a warm goodbye message. If they completed the screening, thank them and explain next steps (review within 24-48 hours, contact within 2-3 business days). If incomplete, thank them for their time and invite them to return."""

        return self._get_llm_response("bye", context)

    def _handle_greeting_response(self, user_input: str) -> Tuple[str, Dict]:
        """Handle initial greeting and transition to info collection"""
        self.conversation_state['step'] = 'collecting_info'
        self.conversation_state['awaiting_field'] = self.field_order[0]
        
        context = f"""The candidate has responded to your greeting. Now naturally transition to asking for their full name. Be friendly and conversational."""
        
        return self._get_llm_response(user_input, context)

    def _handle_info_collection(self, user_input: str) -> str:
        """Handle information collection using LLM for natural conversation"""
        
        current_field = self.conversation_state['awaiting_field']
        
        # Check if this looks like an off-topic question
        if self._is_off_topic_question(user_input):
            context = f"""The candidate asked you: "{user_input}"
            
This seems like a question about you or something off-topic. Answer it naturally and briefly, then gently guide them back to the screening. 

Currently waiting for: {self.info_fields[current_field]}
Already collected: {list(self.conversation_state['collected_data'].keys())}

Be helpful but keep the screening on track."""
            
            return self._get_llm_response(user_input, context)
        
        # Validate the input for current field
        validation = self._validate_field(current_field, user_input)
        
        if not validation['valid']:
            # Use LLM to naturally request correction
            context = f"""The candidate provided: "{user_input}" for their {self.info_fields[current_field]}.

This is invalid because: {validation['message']}

Politely point out the issue and ask them to provide it again. Be friendly and helpful."""
            
            return self._get_llm_response(user_input, context)
        
        # Store the validated data
        self.conversation_state['collected_data'][current_field] = user_input
        
        # Move to next field
        self.current_field_index += 1
        
        if self.current_field_index < len(self.field_order):
            # Ask for next field
            next_field = self.field_order[self.current_field_index]
            self.conversation_state['awaiting_field'] = next_field
            
            context = f"""Great! You just collected their {self.info_fields[current_field]}: "{user_input}"

Now ask for their {self.info_fields[next_field]}. 

Special instructions:
- If asking for tech stack: Ask them to provide detailed tech stack including programming languages, frameworks, databases, and tools. Be specific about wanting comprehensive information.
- Be conversational and natural
- Acknowledge what they just provided"""
            
            return self._get_llm_response(user_input, context)
        else:
            # All info collected, move to technical questions
            return self._start_technical_questions()

    def _is_off_topic_question(self, user_input: str) -> bool:
        """Detect if user is asking an off-topic question"""
        question_patterns = [
            r'what is your name',
            r'who are you',
            r'what can you do',
            r'how are you',
            r'tell me about',
            r'what do you',
            r'can you help',
            r'what.*\?',
        ]
        
        user_lower = user_input.lower()
        
        # Check if it's a question (has '?' or starts with question word)
        is_question = '?' in user_input or any(user_lower.startswith(q) for q in 
            ['what', 'who', 'how', 'why', 'when', 'where', 'can', 'could', 'would'])
        
        if is_question:
            # Check if it's about information we're collecting
            info_related = any(field in user_lower for field in 
                ['name', 'email', 'phone', 'experience', 'position', 'location', 'tech', 'skill'])
            
            # If it's a question but not about info collection, it's off-topic
            return not info_related
        
        return False

    def _validate_field(self, field: str, value: str) -> Dict[str, Any]:
        """Validate individual fields"""
        value = value.strip()
        
        validations = {
            'email': {
                'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                'message': "it doesn't appear to be a valid email format"
            },
            'phone': {
                'pattern': r'^[\+]?[0-9\s\-\(\)]{10,}$',
                'message': "it should be a valid phone number with at least 10 digits"
            },
            'years_experience': {
                'pattern': r'^\d+\.?\d*$',
                'message': "it should be a number (e.g., 5 or 3.5)"
            },
            'full_name': {
                'min_length': 2,
                'message': "it seems too short for a full name"
            },
            'tech_stack': {
                'min_length': 10,
                'message': "please provide more details about your tech stack"
            }
        }
        
        if field in validations:
            validation = validations[field]
            
            if 'pattern' in validation:
                if not re.match(validation['pattern'], value):
                    return {'valid': False, 'message': validation['message']}
            
            if 'min_length' in validation:
                if len(value) < validation['min_length']:
                    return {'valid': False, 'message': validation['message']}
        
        return {'valid': True, 'message': ''}

    def _start_technical_questions(self) -> str:
        """Start technical question phase"""
        self.conversation_state['step'] = 'technical_questions'
        
        # Generate questions based on tech stack
        tech_stack = self.conversation_state['collected_data'].get('tech_stack', '')
        questions = self._generate_technical_questions(tech_stack)
        
        self.conversation_state['current_questions'] = questions
        self.conversation_state['current_question_index'] = 0
        
        context = f"""Perfect! You've collected all their information. Their tech stack is: {tech_stack}

You've generated these 5 technical questions:
{chr(10).join([f"{i+1}. {q}" for i, q in enumerate(questions)])}

Now:
1. Let them know you're moving to technical questions
2. Briefly mention that you'll ask 5 questions based on their tech stack
3. Ask the FIRST question naturally

Be encouraging and set a positive tone for the technical assessment."""

        return self._get_llm_response("ready for questions", context)

    def _generate_technical_questions(self, tech_stack: str) -> List[str]:
        """Generate technical questions based on tech stack using LLM"""
        
        technologies = self._parse_tech_stack(tech_stack)
        tech_list = ', '.join(technologies) if technologies else tech_stack
        
        prompt = f"""Generate exactly 5 technical interview questions for a candidate with this tech stack: {tech_stack}

Key technologies identified: {tech_list}

Requirements:
- Create specific questions for the mentioned technologies
- Cover different aspects: coding, architecture, debugging, best practices
- Appropriate for initial screening
- Mix practical and conceptual questions

Return ONLY the 5 questions, one per line, no numbering or formatting."""

        try:
            if self.llm_available:
                response = ollama.chat(
                    model='llama2',
                    messages=[
                        {
                            'role': 'system',
                            'content': 'You are an expert technical recruiter. Generate specific, relevant interview questions.'
                        },
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ],
                    options={'temperature': 0.7, 'num_predict': 500}
                )
                
                questions_text = response['message']['content'].strip()
                questions = self._parse_questions(questions_text)
                
                if len(questions) >= 5:
                    return questions[:5]
        except Exception as e:
            logger.error(f"Question generation failed: {e}")
        
        # Fallback questions
        return self._generate_fallback_questions(technologies)

    def _parse_tech_stack(self, tech_stack: str) -> List[str]:
        """Parse tech stack to identify technologies"""
        tech_keywords = ['python', 'java', 'javascript', 'typescript', 'react', 'angular', 
                        'vue', 'django', 'flask', 'spring', 'node', 'postgresql', 'mysql', 
                        'mongodb', 'redis', 'docker', 'kubernetes', 'aws', 'azure', 'git']
        
        tech_lower = tech_stack.lower()
        found = []
        
        for keyword in tech_keywords:
            if keyword in tech_lower:
                found.append(keyword.title())
        
        return list(dict.fromkeys(found))

    def _parse_questions(self, text: str) -> List[str]:
        """Parse questions from LLM response"""
        questions = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Remove numbering and bullets
            line = re.sub(r'^[\d]+[\.\)\:]\s*', '', line)
            line = re.sub(r'^[-•*]\s*', '', line)
            
            if len(line) > 20:
                questions.append(line)
        
        return questions

    def _generate_fallback_questions(self, technologies: List[str]) -> List[str]:
        """Generate fallback questions"""
        questions = []
        
        tech_questions = {
            'Python': "Describe your experience with Python and explain a challenging problem you solved using it.",
            'Django': "How do you structure a Django project and handle database migrations?",
            'React': "Explain your approach to state management in React applications.",
            'JavaScript': "What JavaScript ES6+ features do you use most and why?",
            'PostgreSQL': "How do you optimize PostgreSQL queries for better performance?",
            'Docker': "Describe how you use Docker in your development workflow.",
        }
        
        for tech in technologies:
            if tech in tech_questions:
                questions.append(tech_questions[tech])
        
        general = [
            "What's your approach to writing clean, maintainable code?",
            "How do you debug complex technical issues?",
            "Describe your experience with version control and team collaboration.",
            "How do you stay updated with new technologies?",
            "Tell me about a project you're proud of and your role in it."
        ]
        
        questions.extend(general)
        return questions[:5]

    def _handle_technical_questions(self, user_input: str) -> str:
        """Handle technical question phase with LLM"""
        
        current_index = self.conversation_state['current_question_index']
        questions = self.conversation_state['current_questions']
        current_question = questions[current_index]
        
        # Check if they're asking something off-topic
        if self._is_off_topic_question(user_input):
            context = f"""The candidate asked: "{user_input}" instead of answering the technical question.

Current question: {current_question}

Answer their question briefly and naturally, then guide them back to answering the technical question. Be friendly but keep focus on the screening."""
            
            return self._get_llm_response(user_input, context)
        
        # Check if answer is too short
        if len(user_input.split()) < 5:
            context = f"""The candidate gave a very short answer: "{user_input}" to the question: "{current_question}"

This is too brief to assess their skills. Politely ask them to elaborate with:
- Specific examples from their experience
- Technical details
- Challenges and solutions

Be encouraging and supportive."""
            
            return self._get_llm_response(user_input, context)
        
        # Store answer
        self.conversation_state['technical_answers'][current_question] = user_input
        
        # Move to next question
        self.conversation_state['current_question_index'] += 1
        
        if self.conversation_state['current_question_index'] < len(questions):
            # Ask next question
            next_index = self.conversation_state['current_question_index']
            next_question = questions[next_index]
            
            context = f"""The candidate just answered: "{user_input}"

That was question {current_index + 1} of {len(questions)}.

Now:
1. Acknowledge their answer positively
2. Briefly comment on their answer if relevant
3. Mention it's question {next_index + 1} of {len(questions)}
4. Ask the next question: "{next_question}"

Be natural and encouraging."""
            
            return self._get_llm_response(user_input, context)
        else:
            # All questions answered
            return self._complete_screening()

    def _complete_screening(self) -> str:
        """Complete the screening"""
        self.conversation_state['step'] = 'complete'
        
        name = self.conversation_state['collected_data'].get('full_name', 'there')
        
        context = f"""The candidate ({name}) has completed all technical questions!

Generate a warm completion message that:
1. Congratulates them on completing the screening
2. Thanks them for their time and detailed answers
3. Explains next steps:
   - Team will review within 24-48 hours
   - Recruiter will contact via email within 2-3 business days
   - May include technical interview or coding assessment
4. Wish them well

Be warm, professional, and encouraging."""
        
        return self._get_llm_response("completed", context)

    def _handle_post_completion(self, user_input: str) -> str:
        """Handle messages after screening is complete"""
        context = f"""The screening is already complete. The candidate said: "{user_input}"

Respond naturally. If they're asking a question, answer it. If they're saying goodbye, respond warmly. If they want to start over, suggest they can begin a new screening.

Be helpful and friendly."""
        
        return self._get_llm_response(user_input, context)

    def _get_llm_response(self, user_input: str, context_instruction: str) -> str:
        """Get response from LLM with context"""
        
        if not self.llm_available:
            return self._get_fallback_response(context_instruction)
        
        try:
            # Build messages for LLM
            messages = [
                {'role': 'system', 'content': self.system_prompt},
                {'role': 'system', 'content': f"Current context: {context_instruction}"}
            ]
            
            # Add recent conversation history
            messages.extend(self.conversation_state['conversation_history'][-10:])
            
            response = ollama.chat(
                model='llama2',
                messages=messages,
                options={
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'num_predict': 300
                }
            )
            
            return response['message']['content'].strip()
            
        except Exception as e:
            logger.error(f"LLM response failed: {e}")
            return self._get_fallback_response(context_instruction)

    def _get_fallback_response(self, context_instruction: str) -> str:
        """Fallback response when LLM is unavailable"""
        
        current_step = self.conversation_state['step']
        
        if current_step == 'collecting_info':
            field = self.conversation_state.get('awaiting_field')
            if field:
                return f"Could you please provide your {self.info_fields[field]}?"
        
        elif current_step == 'technical_questions':
            current_index = self.conversation_state['current_question_index']
            questions = self.conversation_state['current_questions']
            if current_index < len(questions):
                return f"Question {current_index + 1}: {questions[current_index]}"
        
        return "I'm having trouble processing that. Could you please try again?"

    def _get_state_info(self) -> Dict:
        """Get current state information"""
        return {
            'step': self.conversation_state['step'],
            'collected_data': self.conversation_state['collected_data'].copy(),
            'current_question_index': self.conversation_state['current_question_index'],
            'total_questions': len(self.conversation_state['current_questions']),
            'is_complete': self.conversation_state['step'] == 'complete'
        }

    def get_collected_data(self) -> Dict:
        """Get all collected data"""
        return {
            'personal_info': self.conversation_state['collected_data'],
            'technical_answers': self.conversation_state['technical_answers'],
            'questions_asked': self.conversation_state['current_questions']
        }

    def reset_conversation(self):
        """Reset conversation"""
        self.conversation_state = {
            'step': 'greeting',
            'collected_data': {},
            'current_questions': [],
            'current_question_index': 0,
            'technical_answers': {},
            'conversation_history': [],
            'awaiting_field': None
        }
        self.current_field_index = 0
        logger.info("Conversation reset")


if __name__ == "__main__":
    print("🤖 Testing Conversational TalentScout Chatbot")
    print("="*70)
    
    chatbot = TalentScoutChatbot()
    print(chatbot.get_greeting())
    
    # Test conversation
    test_inputs = [
        "Hello!",
        "What is your name?",
        "John Doe",
        "john@email.com",
        "+1234567890",
        "5",
        "Software Engineer",
        "San Francisco",
        "Python, Django, React, PostgreSQL, Docker, AWS",
        "I use Django extensively for building REST APIs. I structure projects with clear separation of concerns, use Django REST Framework for serialization, and implement proper authentication. In my last project, I built a microservices architecture handling 10k requests/minute.",
        "I manage state using Redux for complex applications. I organize store by features, use Redux Toolkit to reduce boilerplate, implement proper middleware for async operations, and use selectors for derived state. This approach helped us maintain a large application with 50+ components.",
        "I optimize PostgreSQL by analyzing query plans with EXPLAIN, adding appropriate indexes, avoiding N+1 queries, using connection pooling, and implementing read replicas for scaling. I once reduced query time from 5s to 200ms by adding a composite index.",
        "I containerize all services with Docker. Each service has a Dockerfile with multi-stage builds. I use docker-compose for local development and Kubernetes for production. I've set up CI/CD pipelines that automatically build and deploy containers to AWS ECS.",
        "I write unit tests using pytest, integration tests for APIs, and use test-driven development. I aim for 80%+ coverage, mock external dependencies, and run tests in CI/CD pipeline. I also implement end-to-end tests using Selenium for critical user flows."
    ]
    
    for user_input in test_inputs:
        print(f"\n{'='*70}")
        print(f"👤 You: {user_input}")
        print("-"*70)
        response, state = chatbot.process_message(user_input)
        print(f"🤖 Bot: {response}")
        print(f"State: {state['step']}")
        
        if state['is_complete']:
            print("\n✅ Screening Complete!")
            break