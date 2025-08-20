from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import time
import os

app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@app.route("/chat", methods=["POST"])
def chat():
    """Simple chat endpoint for testing - no external API calls"""
    try:
        logging.info("Chat endpoint called")
        
        data = request.json
        if not data:
            logging.error("No JSON data received")
            return jsonify({"error": "No data received"}), 400
            
        user_input = data.get("message", "")
        if not user_input:
            logging.error("No message in request")
            return jsonify({"error": "No message provided"}), 400
        
        logging.info(f"Received message: {user_input}")
        
        # Simple response logic without external API
        if "hello" in user_input.lower() or "hi" in user_input.lower():
            response = "Hi there! I'm CASI! What can I do for you? 🎯"
        elif "who is casi" in user_input.lower():
            response = "Hello! I'm **CASI**, your AI virtual assistant. I'm here to help you with any questions or support you need! 😊"
        elif "george anzures" in user_input.lower():
            response = "George Anzures is the IT Director of Casto Travel Philippines with over 25 years of solid IT expertise and more than two decades of leadership excellence across diverse industries."
        elif "casto" in user_input.lower():
            response = "CASTO Travel Philippines is a travel company. I can help you with information about our services, team, or any other questions you might have!"
        else:
            response = "I'm CASI, your helpful AI assistant! I'm here to help you with any questions or support you need. How can I assist you today? 😊"
        
        logging.info(f"Generated response: {response}")
        return jsonify({"response": response})
        
    except Exception as e:
        logging.error(f"Unexpected error in chat endpoint: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/knowledge", methods=["GET"])
def get_knowledge():
    """Get knowledge base entries"""
    try:
        # Return some basic knowledge for testing
        knowledge = [
            "George Anzures is the IT Director with 25+ years of IT expertise",
            "CASTO Travel Philippines provides travel services",
            "CASI is your AI virtual assistant"
        ]
        return jsonify({"knowledge": knowledge})
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
        
        # Simple search through basic knowledge
        knowledge = [
            "George Anzures is the IT Director with 25+ years of IT expertise",
            "CASTO Travel Philippines provides travel services",
            "CASI is your AI virtual assistant"
        ]
        
        results = []
        for entry in knowledge:
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
    try:
        return jsonify({
            "status": "success",
            "message": "Backend is reachable and responding",
            "timestamp": time.time(),
            "endpoint": "/test",
            "note": "This is a simplified test backend"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Backend error: {str(e)}",
            "timestamp": time.time(),
            "endpoint": "/test"
        }), 500

if __name__ == '__main__':
    print("🚀 Starting CASI Test Backend Server...")
    print("✅ Server will run on http://localhost:5000")
    print("✅ Simplified backend for testing - no external API calls")
    print("=" * 50)
    
    logging.info("✅ Backend is running at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
