from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
import json
from datetime import datetime
from db import fetch_chat_history


load_dotenv()

# 1. LOAD PROPERTIES FROM JSON FILE 
def load_properties(json_file="properties.json"):
    try:
        with open(json_file, 'r') as f:
            properties = json.load(f)
        
        # Convert properties to plain text
        property_texts = []
        for prop in properties:
            text = f"""
Property ID: {prop.get('id', 'N/A')}
Title: {prop.get('title', 'N/A')}
Type: {prop.get('property_type', 'N/A')}
Price: ${prop.get('price', 'N/A')}
Location: {prop.get('location', 'N/A')}
Bedrooms: {prop.get('bedrooms', 'N/A')}
Bathrooms: {prop.get('bathrooms', 'N/A')}
Square Feet: {prop.get('sqft', 'N/A')}
Description: {prop.get('description', 'N/A')}
Features: {', '.join(prop.get('features', []))}
Status: {prop.get('status', 'N/A')}
"""
            property_texts.append(text)
        
        plain_properties = " ".join(property_texts)
        return plain_properties
        
    except FileNotFoundError:
        print("Properties file not found")
        return ""

# Load property data
property_data = load_properties("properties.json")
# print(property_data)

# 2. CHUNKING (same as your code)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=900,
    chunk_overlap=100,
)

# create_documents requires a list of strings, so we wrap property_data in a list
# remember to use [] format instead of list() to avoid errors,

chunks = splitter.create_documents([property_data])
print(f"Created {len(chunks)} chunks")

# 3. EMBEDDING AND VECTOR STORE 
embedding_model = GoogleGenerativeAIEmbeddings(model='models/gemini-embedding-001')
vector_store = FAISS.from_documents(chunks, embedding_model)

# 4. RETRIEVER 
retriever = vector_store.as_retriever(search_type="similarity", kwargs={"k": 3})

# 5. CHAT HISTORY FUNCTIONS
chat_history = []
history_file = "chat_history.json"

def load_history():
    global chat_history
    try:
        with open(history_file, 'r') as f:
            chat_history = json.load(f)
        print(f"Loaded {len(chat_history)} chat entries")
    except FileNotFoundError:
        chat_history = []
        print("No existing history found")

def save_history():
    with open(history_file, 'w') as f:
        json.dump(chat_history, f, indent=2)


def get_history_context(user_id="anonymous"):
    history = fetch_chat_history(user_id, limit=5)
    history_text = ""
    for msg in reversed(history):  # Show oldest first
        history_text += f"User: {msg['user_message']}\nBot: {msg['bot_response']}\n"
    return history_text

def add_to_history(question, answer):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "answer": answer
    }
    chat_history.append(entry)
    save_history()

# Load existing history
load_history()

# 6. AUGMENTATION (modified to include history)
chat_model = ChatGoogleGenerativeAI(model='gemini-3.5-flash')

prompt = PromptTemplate(
    template="""You are a helpful real estate assistant. If the customer is in coversation mode, chat with them. But if they ask about properties, answer ONLY from the provided property context. If the context is insufficient, just say you don't know.

    Previous conversation: {history}

    Context from properties:
    {context} 
    Question: {question} """,
    
    input_variables=["history", "context", "question"]
)

# 7. CHAINING 
def format_doc(docs):
    context = " ".join(doc.page_content for doc in docs)
    return context

parallel_chain = RunnableParallel(
    {
        "history": RunnableLambda(get_history_context),
        "context": retriever | RunnableLambda(format_doc),
        "question": RunnablePassthrough()
    }
)

parser = StrOutputParser()
main_chain = parallel_chain | prompt | chat_model | parser

# 8. GENERATION 
def ask_question(question):
    # Get answer from chain
    result = main_chain.invoke(question)
    
    # Store in history
    add_to_history(question, result)
    
    return result



