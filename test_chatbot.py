import sys
from chatbot import HiringAssistant

def test_chatbot():
    bot = HiringAssistant()
    
    print(bot.get_greeting().encode('utf-8'))
    
    responses = [
        "John Doe",
        "john@email.com",
        "123-456-7890",
        "3 years",
        "Software Engineer",
        "New York",
        "Python, JavaScript, React, SQL"
    ]
    
    for response in responses:
        print(f"\nYou: {response}")
        bot_response = bot.process_message(response)
        print(f"Bot: {bot_response}")
    
    # Test technical questions
    print(f"\nYou: I'm ready")
    print(f"Bot: {bot.process_message('ready')}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    test_chatbot()