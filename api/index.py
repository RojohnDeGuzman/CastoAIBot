from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import logging
import os
from datetime import datetime, timedelta
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time
from functools import lru_cache

# NOTE: Authentication has been temporarily disabled for testing purposes.
# Authentication will be re-enabled once the Microsoft Graph API integration is working properly.

# For Vercel serverless deployment
app = Flask(__name__)
CORS(app)

# Add Flask-Limiter for rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["60 per minute"]
)

# Environment variables for Vercel
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Define the website source
WEBSITE_SOURCE = "https://www.travelpress.com/"

# Cache for website data (in-memory for serverless)
website_cache = {}
CACHE_DURATION = 300  # 5 minutes

# HTTP session for connection pooling
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
})

@lru_cache(maxsize=100)
def get_cached_knowledge():
    """Cache knowledge retrieval - simplified for Vercel hosting"""
    # For Vercel, return empty knowledge base
    # You can implement cloud database integration later
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
    """Add knowledge base entry"""
    try:
        logging.info("Add knowledge endpoint called")
        access_token = request.json.get("access_token")
        content = request.json.get("content")
        
        logging.info(f"Content provided: {bool(content)}")
        logging.info(f"Access token provided: {bool(access_token)}")
        
        # Temporarily disable authentication for testing
        # email = get_user_email_from_token(access_token)
        # if email != "rojohn.deguzman@castotravel.ph":
        #     return jsonify({"error": "Unauthorized: Only rojohn.deguzman@castotravel.ph can add knowledge."}), 403
        
        if not content:
            return jsonify({"error": "No content provided"}), 400
        
        # For Vercel hosting, return success without database storage
        # You can implement cloud database integration later
        logging.info("Knowledge added successfully (placeholder)")
        return jsonify({"success": True, "message": "Knowledge added successfully"})
        
    except Exception as e:
        logging.error(f"Error in add_knowledge: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/knowledge', methods=['GET'])
def get_knowledge():
    """Get knowledge base entries"""
    try:
        logging.info("Get knowledge endpoint called")
        access_token = request.args.get("access_token")
        
        logging.info(f"Access token provided: {bool(access_token)}")
        
        # Temporarily disable authentication for testing
        # email = get_user_email_from_token(access_token)
        # if not email or not is_castotravel_user(email):
        #     return jsonify({"error": "Unauthorized"}), 403
        
        # For Vercel hosting, return empty knowledge base
        # You can implement cloud database integration later
        logging.info("Returning empty knowledge base (placeholder)")
        return jsonify([])
        
    except Exception as e:
        logging.error(f"Error in get_knowledge: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/chat", methods=["POST"])
def chat():
    """Chat with the AI bot"""
    try:
        logging.info("Chat endpoint called")
        
        if not GROQ_API_KEY:
            logging.error("GROQ_API_KEY not configured")
            return jsonify({"error": "GROQ_API_KEY not configured in Vercel"}), 500
        
        data = request.json
        user_input = data.get("message", "")
        access_token = data.get("access_token")
        
        logging.info(f"Received message: {user_input}")
        logging.info(f"Access token provided: {bool(access_token)}")
        
        # Temporarily disable authentication for testing
        # email = get_user_email_from_token(access_token)
        # if not email or not is_castotravel_user(email):
        #     return jsonify({"error": "Unauthorized: Only castotravel.ph users allowed"}), 403
        
        # For now, allow all users to test the chat functionality
        email = "test@example.com"  # Placeholder for testing
        logging.info(f"Using test email: {email}")

        # Use cached knowledge retrieval
        knowledge_entries = get_cached_knowledge()

        # Combine knowledge into a single string
        knowledge_context = "\n".join(knowledge_entries)
        system_prompt = "You are a helpful assistant named CASI."
        if knowledge_context:
            system_prompt += "\nHere is some important knowledge you must always use:\n" + knowledge_context

        # Step 1: Check if the question is relevant to the website
        website_keywords = ["CASTO", "mission", "vision", "services", "CEO", "about"]
        website_data = None
        if any(keyword.lower() in user_input.lower() for keyword in website_keywords):
            logging.info(f"Checking website ({WEBSITE_SOURCE}) for user query: {user_input}")
            website_data = fetch_website_data("https://www.casto.com.ph/", query=user_input)

        # Step 3: Get a response from the chatbot using Groq (your original working setup)
        try:
            # Import OpenAI client in isolation to avoid any conflicts
            import openai
            
            # Setup OpenAI-style client for Groq with isolated initialization
            try:
                # Create client with minimal parameters for version 1.66.3
                client = openai.OpenAI(
                    api_key=GROQ_API_KEY,
                    base_url="https://api.groq.com/openai/v1"
                )
                
            except Exception as e:
                logging.error(f"Failed to create OpenAI client: {e}")
                return jsonify({"error": f"Client initialization failed: {str(e)}"}), 500
            
            logging.info("Fetching response from Groq.")
            response = client.chat.completions.create(
                model="llama3-8b-8192",  # or "mixtral-8x7b-32768"
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7
            )

            chatbot_message = response.choices[0].message.content
            logging.info("Answer fetched from Groq.")

            # Combine the chatbot's response with the website's response
            combined_response = chatbot_message
            if website_data and "No relevant information found" not in website_data:
                combined_response += f"\n\nAdditional Information from Website:\n{website_data}"

            return jsonify({"response": combined_response})
        
        except Exception as e:
            # If an error occurs, return an error message
            logging.error(f"Error during Groq response: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    except Exception as e:
        logging.error(f"Unexpected error in chat endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/test", methods=["GET"])
def test_endpoint():
    """Simple test endpoint for connectivity testing"""
    return jsonify({
        "status": "success",
        "message": "Backend is reachable and responding",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoint": "/test"
    })

@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "message": "CASI Backend API is running on Vercel",
        "api_key_configured": bool(GROQ_API_KEY),
        "authentication": "TEMPORARILY DISABLED FOR TESTING",
        "features": {
            "ai_chat": True,
            "website_scraping": True,
            "knowledge_base": "placeholder (cloud DB needed)",
            "authentication": "disabled (temporary)",
            "rate_limiting": True
        },
        "endpoints": {
            "test": "/test",
            "chat": "/chat",
            "knowledge": "/knowledge",
            "health": "/"
        },
        "note": "Authentication is temporarily disabled for testing. Will be re-enabled once Microsoft Graph API integration is working."
    })

# For Vercel serverless deployment
app.debug = False

# Export the Flask app for Vercel
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9000)
