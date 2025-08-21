from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import time

app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@app.route("/chat", methods=["POST"])
def chat():
    """Super simple chat endpoint - just hardcoded responses for testing"""
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
        
        # Super simple response logic - no external dependencies
        user_input_lower = user_input.lower()
        
        if "hello" in user_input_lower or "hi" in user_input_lower:
            response = "Hi there! I'm CASI! What can I do for you? 🎯"
        elif "who is casi" in user_input_lower:
            response = "Hello! I'm **CASI**, your AI virtual assistant. I'm here to help you with any questions or support you need! 😊"
        elif "george anzures" in user_input_lower:
            response = "George Anzures is the IT Director of Casto Travel Philippines with over 25 years of solid IT expertise and more than two decades of leadership excellence across diverse industries."
        elif "casto" in user_input_lower:
            response = "CASTO Travel Philippines is a travel company. I can help you with information about our services, team, or any other questions you might have!"
        elif "help" in user_input_lower:
            response = "I'm CASI, your helpful AI assistant! I'm here to help you with any questions or support you need. How can I assist you today? 😊"
        else:
            response = "I'm CASI, your AI assistant! I'm ready to help you with any questions about CASTO Travel, our team, or anything else you need. What would you like to know? 🚀"
        
        logging.info(f"Generated response: {response}")
        return jsonify({"response": response})
        
    except Exception as e:
        logging.error(f"Unexpected error in chat endpoint: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "success",
        "message": "CASI Minimal Test Backend is running",
        "note": "No KB integration, no website scraping - just simple responses",
        "endpoints": {
            "chat": "POST /chat - Simple chat with hardcoded responses",
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
            "note": "Super minimal backend - no external dependencies"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Backend error: {str(e)}",
            "timestamp": time.time(),
            "endpoint": "/test"
        }), 500

if __name__ == '__main__':
    print("🚀 Starting CASI Minimal Test Backend...")
    print("✅ Server will run on http://localhost:5000")
    print("✅ Super simple - no KB, no website scraping, just hardcoded responses")
    print("=" * 50)
    
    logging.info("✅ Backend is running at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
