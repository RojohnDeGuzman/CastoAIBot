from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging

# For Vercel serverless deployment
app = Flask(__name__)
CORS(app)

# Environment variables for Vercel
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# Setup logging
logging.basicConfig(level=logging.INFO)

@app.route("/", methods=["GET"])
def health_check():
    """Simple health check endpoint"""
    try:
        return jsonify({
            "status": "healthy", 
            "message": "CASI Backend API is running on Vercel",
            "api_key_configured": bool(GROQ_API_KEY),
            "endpoints": {
                "chat": "/chat",
                "knowledge": "/knowledge",
                "health": "/"
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/test", methods=["GET"])
def test_endpoint():
    """Simple test endpoint"""
    return jsonify({"message": "Test endpoint working!"})

@app.route('/knowledge', methods=['GET'])
def get_knowledge():
    """Get knowledge base entries"""
    try:
        return jsonify([])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/knowledge', methods=['POST'])
def add_knowledge():
    """Add knowledge base entry"""
    try:
        return jsonify({"success": True, "message": "Knowledge added successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/chat", methods=["POST"])
def chat():
    """Chat with the AI bot"""
    try:
        if not GROQ_API_KEY:
            return jsonify({"error": "GROQ_API_KEY not configured in Vercel"}), 500
        
        # For now, return a simple response
        return jsonify({"response": "Chat endpoint working! API key is configured."})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# For Vercel serverless deployment
app.debug = False

# Export the Flask app for Vercel
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9000)
