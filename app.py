import streamlit as st
import json
import logging
import time
from datetime import datetime
from chatbot import TalentScoutChatbot

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="TalentScout AI - Technical Screening",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

class ChatInterface:
    def __init__(self):
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize all session state variables"""
        if 'chatbot' not in st.session_state:
            try:
                st.session_state.chatbot = TalentScoutChatbot()
                logger.info("✅ Chatbot initialized successfully with Llama2")
            except Exception as e:
                logger.error(f"❌ Error initializing chatbot: {e}")
                st.error("Failed to initialize chatbot. Please ensure Ollama is running with llama2 model.")
                st.info("Run: `ollama pull llama2` to install the model")
                st.stop()
        
        if 'messages' not in st.session_state:
            st.session_state.messages = []
            self.add_bot_message(st.session_state.chatbot.get_greeting())
        
        if 'conversation_active' not in st.session_state:
            st.session_state.conversation_active = True
        
        if 'state_info' not in st.session_state:
            st.session_state.state_info = {
                'step': 'greeting',
                'collected_data': {},
                'current_question_index': 0,
                'total_questions': 0,
                'is_complete': False
            }
        
        if 'session_start_time' not in st.session_state:
            st.session_state.session_start_time = datetime.now()
    
    def add_bot_message(self, message):
        """Add a bot message to the chat history"""
        st.session_state.messages.append(("assistant", message))
    
    def add_user_message(self, message):
        """Add a user message to the chat history"""
        st.session_state.messages.append(("user", message))
    
    def display_chat_messages(self):
        """Display all chat messages maintaining conversation context"""
        for speaker, message in st.session_state.messages:
            if speaker == "assistant":
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(message)
            else:
                with st.chat_message("user", avatar="👤"):
                    st.markdown(message)
    
    def handle_user_input(self, user_input):
        """
        Process user input and generate bot response
        Maintains context and provides fallback for unexpected inputs
        """
        if not user_input.strip():
            return
        
        # Add user message to chat
        self.add_user_message(user_input)
        
        try:
            # Get bot response with context handling
            bot_response, state_info = st.session_state.chatbot.process_message(user_input)
            
            # Update state info for UI
            st.session_state.state_info = state_info
            
            # Add bot response to chat
            self.add_bot_message(bot_response)
            
            # Check if conversation completed or ended
            if state_info.get('is_complete', False):
                st.session_state.conversation_active = False
                logger.info("✅ Screening completed successfully")
            elif any(word in bot_response.lower() for word in ['have a great day', 'goodbye']):
                st.session_state.conversation_active = False
                logger.info("👋 Conversation ended by user")
        
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            error_message = "⚠️ I encountered an error. Please try rephrasing your response or type 'bye' to exit."
            self.add_bot_message(error_message)
    
    def reset_conversation(self):
        """Reset the conversation to start fresh"""
        try:
            st.session_state.chatbot.reset_conversation()
            st.session_state.messages = []
            st.session_state.conversation_active = True
            st.session_state.state_info = {
                'step': 'greeting',
                'collected_data': {},
                'current_question_index': 0,
                'total_questions': 0,
                'is_complete': False
            }
            st.session_state.session_start_time = datetime.now()
            self.add_bot_message(st.session_state.chatbot.get_greeting())
            logger.info("🔄 Conversation reset to initial state")
        except Exception as e:
            logger.error(f"❌ Error resetting conversation: {e}")
            st.error("Failed to reset. Please refresh the page.")
    
    def export_data_as_json(self):
        """Export collected data as JSON for recruitment team"""
        collected_data = st.session_state.chatbot.get_collected_data()
        
        # Add metadata
        export_data = {
            'metadata': {
                'screening_date': st.session_state.session_start_time.strftime("%Y-%m-%d %H:%M:%S"),
                'completion_status': 'Complete' if st.session_state.state_info.get('is_complete') else 'Incomplete',
                'total_questions': len(collected_data['questions_asked']),
                'answered_questions': len(collected_data['technical_answers'])
            },
            'candidate_data': collected_data
        }
        
        return json.dumps(export_data, indent=2)
    
    def render_sidebar(self):
        """Render sidebar with candidate info, progress, and controls"""
        with st.sidebar:
            st.markdown("# 🎯 TalentScout AI")
            st.caption("Technical Screening Assistant")
            st.caption("*Powered by Llama2 via Ollama*")
            st.markdown("---")
            
            # Conversation controls
            st.subheader("⚙️ Controls")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 New", use_container_width=True, help="Start a new screening"):
                    self.reset_conversation()
                    st.rerun()
            
            with col2:
                collected_data = st.session_state.chatbot.get_collected_data()
                if collected_data['personal_info'] or collected_data['technical_answers']:
                    if st.button("💾 Export", use_container_width=True, help="Export candidate data"):
                        st.session_state.show_export = True
            
            # Export modal
            if hasattr(st.session_state, 'show_export') and st.session_state.show_export:
                st.markdown("---")
                with st.expander("📋 Export Candidate Data", expanded=True):
                    json_data = self.export_data_as_json()
                    
                    candidate_name = st.session_state.state_info['collected_data'].get('full_name', 'candidate')
                    filename = f"screening_{candidate_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json"
                    
                    st.download_button(
                        label="📥 Download JSON",
                        data=json_data,
                        file_name=filename,
                        mime="application/json",
                        use_container_width=True
                    )
                    
                    with st.expander("View Data"):
                        st.code(json_data, language="json")
                    
                    if st.button("✖️ Close", use_container_width=True):
                        st.session_state.show_export = False
                        st.rerun()
            
            st.markdown("---")
            
            # Candidate Profile Section
            st.subheader("👤 Candidate Profile")
            collected_data = st.session_state.chatbot.get_collected_data()
            
            if collected_data['personal_info']:
                personal_info = collected_data['personal_info']
                
                # Candidate name
                if 'full_name' in personal_info:
                    st.markdown(f"### {personal_info['full_name']}")
                    st.caption(f"Screening started: {st.session_state.session_start_time.strftime('%I:%M %p')}")
                
                # Contact information
                if 'email' in personal_info:
                    st.text(f"✉️ {personal_info['email']}")
                
                if 'phone' in personal_info:
                    st.text(f"📞 {personal_info['phone']}")
                
                st.markdown("---")
                
                # Professional details
                if 'desired_position' in personal_info:
                    st.info(f"**🎯 Position:** {personal_info['desired_position']}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'years_experience' in personal_info:
                        st.metric("Experience", f"{personal_info['years_experience']} yrs")
                
                with col2:
                    if 'current_location' in personal_info:
                        location = personal_info['current_location']
                        display_location = location[:12] + "..." if len(location) > 12 else location
                        st.metric("Location", display_location)
                
                # Tech Stack - Prominently displayed as per requirements
                if 'tech_stack' in personal_info:
                    st.markdown("---")
                    st.subheader("💻 Tech Stack")
                    with st.expander("View Technologies", expanded=True):
                        tech_stack = personal_info['tech_stack']
                        
                        # Parse and display as organized list
                        categories = {
                            'Languages': ['python', 'java', 'javascript', 'typescript', 'c++', 'go', 'rust'],
                            'Frameworks': ['django', 'react', 'angular', 'vue', 'flask', 'spring', 'express'],
                            'Databases': ['postgresql', 'mysql', 'mongodb', 'redis', 'cassandra'],
                            'Tools': ['docker', 'kubernetes', 'aws', 'git', 'jenkins', 'terraform']
                        }
                        
                        tech_lower = tech_stack.lower()
                        categorized = {cat: [] for cat in categories}
                        uncategorized = []
                        
                        # Split tech stack
                        items = [item.strip() for item in tech_stack.replace('\n', ',').split(',')]
                        
                        for item in items:
                            if not item:
                                continue
                            
                            categorized_flag = False
                            for category, keywords in categories.items():
                                if any(keyword in item.lower() for keyword in keywords):
                                    categorized[category].append(item)
                                    categorized_flag = True
                                    break
                            
                            if not categorized_flag:
                                uncategorized.append(item)
                        
                        # Display categorized
                        for category, items_list in categorized.items():
                            if items_list:
                                st.markdown(f"**{category}:**")
                                st.markdown(", ".join([f"`{item}`" for item in items_list]))
                        
                        if uncategorized:
                            st.markdown("**Other:**")
                            st.markdown(", ".join([f"`{item}`" for item in uncategorized]))
                
                # Progress indicator
                total_questions = len(collected_data['questions_asked'])
                answered_questions = len(collected_data['technical_answers'])
                
                if total_questions > 0:
                    st.markdown("---")
                    st.subheader("📊 Progress")
                    
                    progress = answered_questions / total_questions
                    st.progress(progress)
                    st.caption(f"Questions: {answered_questions}/{total_questions}")
                    
                    # Completion status
                    if st.session_state.state_info.get('is_complete', False):
                        st.success("✅ Screening Complete!")
                    elif answered_questions > 0:
                        remaining = total_questions - answered_questions
                        st.info(f"🔄 In Progress ({remaining} remaining)")
                    else:
                        st.warning("⏳ Starting technical assessment...")
                
                # Technical questions and answers
                if collected_data['technical_answers']:
                    st.markdown("---")
                    with st.expander(f"📝 Answers ({len(collected_data['technical_answers'])})", expanded=False):
                        for i, (question, answer) in enumerate(collected_data['technical_answers'].items(), 1):
                            st.markdown(f"**Q{i}:** {question}")
                            
                            # Show truncated answer
                            if len(answer) > 150:
                                with st.expander(f"View Answer {i}"):
                                    st.markdown(f"*{answer}*")
                            else:
                                st.markdown(f"*{answer}*")
                            
                            if i < len(collected_data['technical_answers']):
                                st.markdown("---")
            
            else:
                st.info("💡 No data collected yet.\n\nStart the conversation to begin screening!")
            
            st.markdown("---")
            
            # System status
            with st.expander("🔧 System Info"):
                state = st.session_state.state_info
                
                status_data = {
                    "Current Step": state.get('step', 'unknown').replace('_', ' ').title(),
                    "Active": "✅ Yes" if st.session_state.conversation_active else "❌ No",
                    "Complete": "✅ Yes" if state.get('is_complete', False) else "⏳ In Progress",
                    "Questions": f"{state.get('current_question_index', 0)}/{state.get('total_questions', 0)}"
                }
                
                for key, value in status_data.items():
                    st.text(f"{key}: {value}")
    
    def render_main_interface(self):
        """Render the main chat interface"""
        # Custom CSS
        st.markdown("""
        <style>
        .main-title {
            text-align: center;
            color: #1E3A8A;
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        .sub-title {
            text-align: center;
            color: #64748B;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        .highlight-box {
            background-color: #F0F9FF;
            border-left: 4px solid #3B82F6;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Header
        st.markdown('<h1 class="main-title">🤖 TalentScout AI Assistant</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">Technical Screening with AI-Generated Questions</p>', unsafe_allow_html=True)
        
        # Current step indicator
        state = st.session_state.state_info
        step_name = state.get('step', 'greeting').replace('_', ' ').title()
        
        if state.get('step') == 'collecting_info':
            st.info(f"📝 Current Step: **{step_name}** - Collecting your information")
        elif state.get('step') == 'technical_questions':
            progress = state.get('current_question_index', 0)
            total = state.get('total_questions', 0)
            st.info(f"💻 Current Step: **Technical Assessment** - Question {progress}/{total}")
        elif state.get('is_complete'):
            st.success(f"✅ Screening Complete! Thank you for your time.")
        
        # Display chat messages
        chat_container = st.container()
        with chat_container:
            self.display_chat_messages()
        
        # User input section with context-aware placeholder
        if st.session_state.conversation_active:
            # Determine placeholder based on current step
            placeholders = {
                'greeting': "Type 'start' or 'hello' to begin...",
                'collecting_info': "Type your answer here...",
                'technical_questions': "Provide a detailed answer with specific examples...",
            }
            
            placeholder = placeholders.get(state.get('step', 'greeting'), "Type your response...")
            
            user_input = st.chat_input(placeholder)
            if user_input:
                self.handle_user_input(user_input)
                st.rerun()
        else:
            # Different message based on completion
            if st.session_state.state_info.get('is_complete', False):
                st.success("✅ **Screening Completed!** Click 'New' in the sidebar to start another screening.")
            else:
                st.info("💡 **Conversation Ended.** Click 'New' in the sidebar to begin a new screening.")
    
    def render_instructions(self):
        """Render usage instructions emphasizing tech stack and question generation"""
        with st.expander("ℹ️ How This Screening Works", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ### 📋 Information Collection
                
                We'll collect:
                - **Full Name**
                - **Email** (for contact)
                - **Phone Number**
                - **Years of Experience**
                - **Desired Position**
                - **Current Location**
                - **Tech Stack** (detailed)
                """)
            
            with col2:
                st.markdown("""
                ### 💻 Tech Stack Assessment
                
                **Specify your skills in:**
                - Programming Languages
                - Frameworks & Libraries
                - Databases (SQL/NoSQL)
                - Tools & Technologies
                - Cloud Platforms
                - DevOps Tools
                """)
            
            st.markdown("---")
            
            st.markdown("""
            ### 🤖 AI-Generated Technical Questions
            
            Based on YOUR specific tech stack, our AI (Llama2) will generate **3-5 tailored questions** to assess:
            
            - **Proficiency** in each declared technology
            - **Practical experience** and problem-solving
            - **Best practices** and architecture understanding
            - **Real-world application** of your skills
            
            **Example:** If you list *Python, Django, React, PostgreSQL*, you'll get specific questions about:
            - Python programming concepts
            - Django framework features
            - React state management
            - PostgreSQL optimization
            """)
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ### 🎯 Tips for Success
                
                ✅ **Be specific** about technologies  
                ✅ **List all relevant** skills  
                ✅ **Provide detailed** answers  
                ✅ **Use examples** from experience  
                ✅ **Take your time** to think  
                """)
            
            with col2:
                st.markdown("""
                ### 📞 Next Steps
                
                After completion:
                
                1. ⏱️ Review within **24-48 hours**
                2. 📧 Email contact in **2-3 days**
                3. 📞 Technical interview if qualified
                4. 💼 Coding assessment (if needed)
                """)
            
            st.markdown("---")
            st.info("💡 **Note:** The more detailed your tech stack, the more relevant and targeted your technical questions will be!")
    
    def render_footer(self):
        """Render footer with attribution"""
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #64748B; padding: 1rem; font-size: 0.9rem;'>
            <p><strong>Powered by Llama2 via Ollama</strong> | Built with Streamlit</p>
            <p style='font-size: 0.8rem;'>© 2024 TalentScout Recruitment. All rights reserved.</p>
            <p style='font-size: 0.75rem; margin-top: 0.5rem;'>
                This chatbot uses AI to generate contextual technical questions based on your declared tech stack.<br>
                All responses are confidential and reviewed by our recruitment team.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def run(self):
        """Main method to run the application"""
        self.render_sidebar()
        self.render_main_interface()
        self.render_instructions()
        self.render_footer()


def main():
    """Main application entry point"""
    try:
        # Display ollama check warning if needed
        try:
            import ollama
            ollama.list()
        except Exception as e:
            st.warning("⚠️ Ollama connection issue detected. Questions will use fallback mode.")
            st.info("Ensure Ollama is running: `ollama serve` and model is installed: `ollama pull llama2`")
        
        # Initialize and run the chat interface
        chat_interface = ChatInterface()
        chat_interface.run()
        
    except Exception as e:
        st.error(f"❌ Application Error: {e}")
        logger.error(f"Application error: {e}", exc_info=True)
        
        st.markdown("""
        ### 🔧 Troubleshooting
        
        **Please ensure:**
        1. Ollama is installed and running: `ollama serve`
        2. Llama2 model is downloaded: `ollama pull llama2`
        3. Python dependencies are installed: `pip install streamlit ollama`
        
        **Then refresh this page.**
        """)


if __name__ == "__main__":
    main()