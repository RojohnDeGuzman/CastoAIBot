from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# For Vercel serverless deployment
app = Flask(__name__)
CORS(app)

# Environment variables for Vercel
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

@app.route("/", methods=["GET"])
def health_check():
    """Simple health check endpoint"""
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

@app.route("/test", methods=["GET"])
def test_endpoint():
    """Simple test endpoint"""
    return jsonify({"message": "Test endpoint working!"})

@app.route('/knowledge', methods=['GET'])
def get_knowledge():
    """Get knowledge base entries"""
    return jsonify([])

@app.route('/knowledge', methods=['POST'])
def add_knowledge():
    """Add knowledge base entry"""
    return jsonify({"success": True, "message": "Knowledge added successfully"})

@app.route("/chat", methods=["POST"])
def chat():
    """Chat with the AI bot"""
    try:
        if not GROQ_API_KEY:
            return jsonify({"error": "GROQ_API_KEY not configured in Vercel"}), 500
        
        # Get user input from request
        data = request.json
        if not data or "message" not in data:
            return jsonify({"error": "No message provided"}), 400
        
        user_input = data["message"]
        
        # For now, return a simple response until we confirm it's working
        return jsonify({
            "response": f"Hello! I'm CASI. You said: '{user_input}'. AI integration coming soon!"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# For Vercel serverless deployment
app.debug = False

# Export the Flask app for Vercel
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9000)
