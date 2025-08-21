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

# Get API key from environment variable for Vercel
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
    """Cache knowledge retrieval - simplified for Vercel"""
    try:
        # For Vercel, we'll use a simple knowledge base
        knowledge = [
            "George Anzures is the IT Director of Casto Travel Philippines with over 25 years of solid IT expertise and more than two decades of leadership excellence across diverse industries.",
            "CASTO Travel Philippines is a travel company providing various travel services.",
            "CASI is your AI virtual assistant, always ready to help with any questions or support you need."
        ]
        return knowledge
    except Exception as e:
        logging.error(f"Error loading knowledge: {str(e)}")
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

def search_web(query):
    """Simulate a web search and parse results."""
    return ["Web search is disabled for testing."]

def get_user_email_from_token(access_token):
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        user_response = session.get("https://graph.microsoft.com/v1.0/me", headers=headers, timeout=10)
        if user_response.status_code == 200:
            user_json = user_response.json()
            email = user_json.get("mail") or user_json.get("userPrincipalName") or ""
            return email
    except Exception as e:
        pass
    return None

def is_castotravel_user(email):
    return email.lower().endswith("@castotravel.ph")

@app.route('/knowledge', methods=['POST'])
def add_knowledge():
    """Add knowledge base entry - simplified for Vercel"""
    try:
        access_token = request.json.get("access_token")
        content = request.json.get("content")
        
        if not access_token:
            return jsonify({"error": "Authentication required"}), 401
            
        email = get_user_email_from_token(access_token)
        if email != "rojohn.deguzman@castotravel.ph":
            return jsonify({"error": "Unauthorized: Only rojohn.deguzman@castotravel.ph can add knowledge."}), 403
        
        if not content:
            return jsonify({"error": "No content provided"}), 400
        
        # For Vercel, we'll just acknowledge the request
        logging.info(f"Knowledge addition requested by {email}: {content}")
        
        return jsonify({"success": True, "message": "Knowledge addition acknowledged (Vercel mode)"})
        
    except Exception as e:
        logging.error(f"Error in add_knowledge: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/knowledge', methods=['GET'])
def get_knowledge():
    """Get knowledge base entries - simplified for Vercel"""
    try:
        access_token = request.args.get("access_token")
        
        if not access_token:
            return jsonify({"error": "Authentication required"}), 401
            
        email = get_user_email_from_token(access_token)
        if not email or not is_castotravel_user(email):
            return jsonify({"error": "Unauthorized: Only castotravel.ph users allowed"}), 403
        
        # Return cached knowledge for Vercel
        knowledge_entries = get_cached_knowledge()
        return jsonify([{"id": i, "timestamp": time.time(), "content": entry} for i, entry in enumerate(knowledge_entries)])
        
    except Exception as e:
        logging.error(f"Error in get_knowledge: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/chat", methods=["POST"])
def chat():
    """Chat with the AI bot - allows anonymous users"""
    try:
        logging.info("Chat endpoint called")
        
        data = request.json
        user_input = data.get("message", "")
        access_token = data.get("access_token")
        
        logging.info(f"Received message: {user_input}")
        logging.info(f"Access token provided: {bool(access_token)}")
        
        # Check if user is authenticated
        email = None
        is_authenticated = False
        if access_token:
            email = get_user_email_from_token(access_token)
            if email and is_castotravel_user(email):
                is_authenticated = True
                logging.info(f"Authenticated user: {email}")
        
        # Use cached knowledge retrieval (only for authenticated users)
        knowledge_entries = []
        if is_authenticated:
            knowledge_entries = get_cached_knowledge()
        
        # Combine knowledge into a single string
        knowledge_context = "\n".join(knowledge_entries)
        system_prompt = "You are a helpful assistant named CASI."
        if knowledge_context:
            system_prompt += f"\nHere is some important knowledge you must always use:\n{knowledge_context}"

        # Step 1: Check if the question is relevant to the website
        website_keywords = ["CASTO", "mission", "vision", "services", "CEO", "about"]
        website_data = None
        if any(keyword.lower() in user_input.lower() for keyword in website_keywords):
            logging.info(f"Checking website ({WEBSITE_SOURCE}) for user query: {user_input}")
            website_data = fetch_website_data("https://www.casto.com.ph/", query=user_input)

        # Step 3: Get a response from the chatbot
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

@app.route("/it-on-duty", methods=["POST"])
def it_on_duty():
    """Endpoint for IT on Duty messages - requires authentication"""
    try:
        data = request.json
        access_token = data.get("access_token")
        
        if not access_token:
            return jsonify({"error": "Authentication required for IT support requests"}), 401
        
        email = get_user_email_from_token(access_token)
        if not email or not is_castotravel_user(email):
            return jsonify({"error": "Unauthorized: Only castotravel.ph users allowed"}), 403
        
        concern = data.get("concern", "")
        if not concern:
            return jsonify({"error": "Concern description is required"}), 400
        
        # Here you would typically send the message to your IT support system
        # For now, we'll just acknowledge receipt
        logging.info(f"IT on Duty request from {email}: {concern}")
        
        return jsonify({
            "success": True,
            "message": "IT support request received successfully",
            "user_email": email
        })
    except Exception as e:
        logging.error(f"Error in IT on Duty endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "success",
        "message": "CASI Backend is running on Vercel",
        "api_key_configured": bool(GROQ_API_KEY),
        "authentication": "Anonymous users allowed for chat",
        "endpoints": {
            "chat": "POST /chat - General chat (anonymous users allowed)",
            "it_on_duty": "POST /it-on-duty - IT support (requires auth)",
            "knowledge": "GET/POST /knowledge - Knowledge base (requires auth)",
            "test": "GET /test - Connectivity test"
        }
    })

@app.route("/test", methods=["GET"])
def test_endpoint():
    """Simple test endpoint for connectivity testing"""
    return jsonify({
        "status": "success",
        "message": "Backend is reachable and responding",
        "timestamp": time.time(),
        "endpoint": "/test",
        "note": "Running on Vercel with your working code"
    })

if __name__ == '__main__':
    print("🚀 Starting CASI Backend Server...")
    print("✅ Server will run on http://localhost:5000")
    print("✅ Anonymous users allowed for general chat")
    print("✅ IT support requires Office 365 authentication")
    print("=" * 50)
    
    logging.info("✅ Backend is running at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
