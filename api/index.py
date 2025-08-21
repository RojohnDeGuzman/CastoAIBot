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

# Setup OpenAI-style client for Groq (only if API key is available)
client = None
if GROQ_API_KEY:
    try:
        client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=GROQ_API_KEY
        )
        logging.info("✅ Groq AI client initialized successfully")
    except Exception as e:
        logging.error(f"❌ Failed to initialize Groq AI client: {str(e)}")
        client = None
else:
    logging.warning("⚠️ GROQ_API_KEY not found - AI responses will be limited")

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
    """Enhanced knowledge base with IT support focus and executive context"""
    try:
        # IT Support focused knowledge base for CASI
        knowledge = [
            "CASI (Casto AI) is your primary IT Support Assistant, designed to help with technical issues, IT requests, system problems, and general IT support. CASI combines AI technology with IT expertise to provide immediate technical assistance and guidance.",
            "George Anzures is the IT Director of Casto Travel Philippines with over 25 years of solid IT expertise and more than two decades of leadership excellence across diverse industries. Throughout his career, he has played a pivotal role in large multinational organizations in the Philippines. He previously served as Chief Technology Officer of Asiatrust Bank (later acquired by Asia United Bank) and held the position of Country Head of IT for Arvato Bertelsmann (Manila) and Publicis Resources Philippines. His leadership eventually expanded to a regional capacity, overseeing operations across five markets. He played a key role in establishing the IT backbone of several BPO startups in the Philippines, contributing to the successful launch of major contact centers such as Dell International Services, Genpact, and Arvato Bertelsmann. Beyond technical expertise, he is passionate about leadership development and considers his most significant accomplishment to be mentoring and coaching future technology leaders in the Philippines.",
            "Ma. Berdandina Galvez is the HR Director of Casto Travel Philippines. She is an experienced Senior Human Resources professional with a demonstrated history of working in various industries such as hospitality, health care, educational, food service and transportation. She is skilled in HR Consulting, Coaching, Team Building and HR Policies.",
            "CASTO Travel Philippines is the company where CASI provides IT support services. The company operates in the travel industry with various departments requiring IT assistance.",
            "CASI's primary role is to provide immediate IT support, troubleshoot technical issues, assist with system access, help with software problems, guide users through IT processes, and escalate complex issues to the IT team when necessary."
        ]
        return knowledge
    except Exception as e:
        logging.error(f"Error loading knowledge: {str(e)}")
        return []

def search_knowledge(query, knowledge_entries=None):
    """Enhanced knowledge search with relevance scoring"""
    try:
        if knowledge_entries is None:
            knowledge_entries = get_cached_knowledge()
        
        if not query or not knowledge_entries:
            return []
        
        query_lower = query.lower()
        results = []
        
        for entry in knowledge_entries:
            # Simple relevance scoring
            relevance_score = 0
            entry_lower = entry.lower()
            
            # Exact phrase matches get highest score
            if query_lower in entry_lower:
                relevance_score += 10
            
            # Word matches get medium score
            query_words = query_lower.split()
            for word in query_words:
                if len(word) > 2 and word in entry_lower:  # Ignore very short words
                    relevance_score += 2
            
            # Add to results if relevant
            if relevance_score > 0:
                results.append({
                    "content": entry,
                    "relevance": relevance_score,
                    "query": query
                })
        
        # Sort by relevance score (highest first)
        results.sort(key=lambda x: x["relevance"], reverse=True)
        
        # Return top 3 most relevant results
        return results[:3]
        
    except Exception as e:
        logging.error(f"Error in knowledge search: {str(e)}")
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

@app.route('/knowledge/search', methods=['POST'])
def search_knowledge_endpoint():
    """Search knowledge base - available to all users"""
    try:
        data = request.json
        query = data.get("query", "")
        
        if not query:
            return jsonify({"error": "No search query provided"}), 400
        
        logging.info(f"Knowledge search requested: {query}")
        
        # Search knowledge base
        search_results = search_knowledge(query)
        
        if search_results:
            return jsonify({
                "success": True,
                "query": query,
                "results": search_results,
                "total_found": len(search_results)
            })
        else:
            return jsonify({
                "success": True,
                "query": query,
                "results": [],
                "total_found": 0,
                "message": "No relevant information found for your query."
            })
        
    except Exception as e:
        logging.error(f"Error in knowledge search: {str(e)}")
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
        
        # Enhanced knowledge search for all users (anonymous and authenticated)
        knowledge_search_results = search_knowledge(user_input, knowledge_entries)
        
        # Combine knowledge into a single string
        knowledge_context = "\n".join(knowledge_entries) if knowledge_entries else ""
        
        # Add search results to context if available
        if knowledge_search_results:
            search_context = "\n\nRelevant Knowledge:\n" + "\n---\n".join([result["content"] for result in knowledge_search_results])
            if knowledge_context:
                knowledge_context += search_context
            else:
                knowledge_context = search_context
        
        system_prompt = "You are CASI, a dedicated IT Support Assistant for CASTO Travel Philippines. Your primary role is to provide immediate IT support, troubleshoot technical issues, and assist users with IT-related problems. Always respond as an IT support professional first. You have knowledge about CASTO Travel executives and company context, but your main focus should be IT support. Be friendly, professional, and IT-focused in your responses."
        if knowledge_context:
            system_prompt += f"\n\nHere is important knowledge you must use when relevant:\n{knowledge_context}"

        # Step 1: Check if the question is relevant to the website
        website_keywords = ["CASTO", "mission", "vision", "services", "CEO", "about"]
        website_data = None
        if any(keyword.lower() in user_input.lower() for keyword in website_keywords):
            logging.info(f"Checking website ({WEBSITE_SOURCE}) for user query: {user_input}")
            website_data = fetch_website_data("https://www.casto.com.ph/", query=user_input)

        # Step 3: Get a response from the chatbot
        try:
            if client:
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
            else:
                # Fallback responses when AI client is not available
                user_input_lower = user_input.lower()
                if "hello" in user_input_lower or "hi" in user_input_lower:
                    chatbot_message = "Hi there! I'm CASI, your IT Support Assistant! How can I help you with any technical issues today? 🖥️"
                elif "who is casi" in user_input_lower:
                    chatbot_message = "Hello! I'm **CASI**, your dedicated IT Support Assistant at CASTO Travel Philippines. I'm here to help you with technical issues, system problems, and IT support! 💻"
                elif "george anzures" in user_input_lower:
                    chatbot_message = "George Anzures is our IT Director with over 25 years of IT expertise. He leads our IT department and oversees all technical operations. For IT support, I'm here to help you directly! 🚀"
                elif "casto" in user_input_lower:
                    chatbot_message = "CASTO Travel Philippines is where I provide IT support services. I'm here to help you with any technical issues, system access, or IT-related problems you might be experiencing! 🛠️"
                elif "help" in user_input_lower:
                    chatbot_message = "I'm CASI, your IT Support Assistant! I can help you with: system access, software issues, technical problems, IT requests, and general IT support. What technical issue are you facing? 🔧"
                else:
                    chatbot_message = "I'm CASI, your IT Support Assistant! I'm ready to help you with any technical issues, system problems, or IT support you need. What can I assist you with today? 💻"
                
                logging.info("Using fallback response (AI client not available)")

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
        "message": "CASI IT Support Assistant is running on Vercel with Enhanced Knowledge Base",
        "api_key_configured": bool(GROQ_API_KEY),
        "ai_client_available": bool(client),
        "knowledge_base": {
            "entries": len(get_cached_knowledge()),
            "features": ["IT Support Focus", "Executive Context", "Enhanced search", "Relevance scoring"]
        },
        "authentication": "Anonymous users allowed for IT support chat and knowledge search",
        "note": "If AI client is not available, IT support fallback responses will be used",
        "endpoints": {
            "chat": "POST /chat - IT Support chat with enhanced knowledge integration",
            "knowledge_search": "POST /knowledge/search - Search knowledge base (all users)",
            "knowledge": "GET/POST /knowledge - Knowledge base management (requires auth)",
            "it_on_duty": "POST /it-on-duty - IT support escalation (requires auth)",
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
