from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import logging
import time
import os
from functools import lru_cache

app = Flask(__name__)
CORS(app)

# Get API key from environment variable
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is required")

# Setup OpenAI-style client for Groq
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY
)

# Define the website source
WEBSITE_SOURCE = "https://www.travelpress.com/"

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Cache for website data
website_cache = {}
CACHE_DURATION = 300  # 5 minutes

# HTTP session for connection pooling
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
})

@lru_cache(maxsize=100)
def get_cached_knowledge():
    """Cache knowledge retrieval to avoid repeated queries"""
    try:
        with open('knowledge_base.json', 'r', encoding='utf-8') as f:
            import json
            data = json.load(f)
            return [entry.get('content', '') for entry in data if entry.get('content')]
    except Exception as e:
        logging.error(f"Error loading knowledge base: {str(e)}")
        return []

def fetch_website_data(url, query=None):
    """Fetch and parse data from a website with caching."""
    cache_key = f"{url}:{query}"
    current_time = time.time()
    
    # Check cache first
    if cache_key in website_cache:
        cached_data, timestamp = website_cache[cache_key]
        if current_time - timestamp < CACHE_DURATION:
            return cached_data
    
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract the title
        title = soup.title.string if soup.title else "No title found"
        
        # Search for the query in all paragraphs
        paragraphs = soup.find_all('p')
        if query:
            for paragraph in paragraphs:
                if query.lower() in paragraph.get_text().lower():
                    result = f"Title: {title}\nContent: {paragraph.get_text().strip()}"
                    website_cache[cache_key] = (result, current_time)
                    return result
        
        # If no relevant content is found, return a default message
        result = f"Title: {title}\nContent: No relevant information found on the website."
        website_cache[cache_key] = (result, current_time)
        return result
    except Exception as e:
        error_msg = f"Error fetching website data: {str(e)}"
        website_cache[cache_key] = (error_msg, current_time)
        return error_msg

@app.route("/chat", methods=["POST"])
def chat():
    """Chat with the AI bot - simple and clean like your on-premise version"""
    try:
        logging.info("Chat endpoint called")
        
        data = request.json
        user_input = data.get("message", "")
        
        logging.info(f"Received message: {user_input}")
        
        # Get knowledge base entries
        knowledge_entries = get_cached_knowledge()
        
        # Combine knowledge into a single string
        knowledge_context = "\n".join(knowledge_entries)
        system_prompt = "You are a helpful assistant named CASI. You are friendly, professional, and always ready to help."
        if knowledge_context:
            system_prompt += f"\n\nHere is some important knowledge you must always use when relevant:\n{knowledge_context}"

        # Step 1: Check if the question is relevant to the website
        website_keywords = ["CASTO", "mission", "vision", "services", "CEO", "about"]
        website_data = None
        if any(keyword.lower() in user_input.lower() for keyword in website_keywords):
            logging.info(f"Checking website ({WEBSITE_SOURCE}) for user query: {user_input}")
            website_data = fetch_website_data("https://www.casto.com.ph/", query=user_input)

        # Step 2: Get a response from the chatbot
        try:
            logging.info("Fetching response from the chatbot.")
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7
            )

            chatbot_message = response.choices[0].message.content
            logging.info("Answer fetched from the chatbot.")

            # Combine the chatbot's response with the website's response
            combined_response = chatbot_message
            if website_data and "No relevant information found" not in website_data:
                combined_response += f"\n\nAdditional Information from Website:\n{website_data}"

            return jsonify({"response": combined_response})
        
        except Exception as e:
            logging.error(f"Error during chatbot response: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    except Exception as e:
        logging.error(f"Unexpected error in chat endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/knowledge", methods=["GET"])
def get_knowledge():
    """Get knowledge base entries"""
    try:
        knowledge_entries = get_cached_knowledge()
        return jsonify({"knowledge": knowledge_entries})
    except Exception as e:
        logging.error(f"Error in get_knowledge: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/search", methods=["POST"])
def search():
    """Search knowledge base"""
    try:
        data = request.json
        query = data.get("query", "")
        
        if not query:
            return jsonify({"error": "No query provided"}), 400
        
        knowledge_entries = get_cached_knowledge()
        
        # Simple search through knowledge base
        results = []
        for entry in knowledge_entries:
            if query.lower() in entry.lower():
                results.append(entry)
        
        return jsonify({"results": results})
    except Exception as e:
        logging.error(f"Error in search: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "success",
        "message": "CASI Backend is running",
        "api_key_configured": bool(GROQ_API_KEY),
        "endpoints": {
            "chat": "POST /chat - General chat",
            "knowledge": "GET /knowledge - Knowledge base",
            "search": "POST /search - Search knowledge base",
            "health": "GET / - Health check"
        }
    })

@app.route("/test", methods=["GET"])
def test_endpoint():
    """Simple test endpoint for connectivity testing"""
    return jsonify({
        "status": "success",
        "message": "Backend is reachable and responding",
        "timestamp": time.time(),
        "endpoint": "/test"
    })

if __name__ == '__main__':
    print("🚀 Starting CASI Backend Server...")
    print("✅ Server will run on http://localhost:5000")
    print("✅ Simple and clean like your on-premise version")
    print("=" * 50)
    
    logging.info("✅ Backend is running at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
