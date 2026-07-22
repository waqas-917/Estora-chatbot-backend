from db import init_database, save_chat_message, fetch_chat_history
from chatbot import ask_question

# Test database
print("Testing MongoDB...")
init_database()

# Test chatbot
print("\nTesting Chatbot...")
try:
    response = ask_question("What properties are available?")
    print(f"Response: {response}")
except Exception as e:
    print(f"Error: {e}")