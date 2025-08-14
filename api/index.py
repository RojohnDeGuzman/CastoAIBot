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
        
        # Try to import OpenAI client
        try:
            from openai import OpenAI
        except ImportError as e:
            return jsonify({
                "error": "OpenAI library not available",
                "details": str(e),
                "message": "Please check if 'openai' is in requirements.txt"
            }), 500
        
        # Initialize OpenAI client for Groq
        try:
            client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=GROQ_API_KEY
            )
        except Exception as e:
            return jsonify({
                "error": "Failed to initialize OpenAI client",
                "details": str(e)
            }), 500
        
        # Get AI response from Groq
        try:
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant named CASI."},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            return jsonify({"response": ai_response})
            
        except Exception as e:
            return jsonify({
                "error": "Failed to get AI response from Groq",
                "details": str(e)
            }), 500
        
    except Exception as e:
        return jsonify({
            "error": "Unexpected error in chat endpoint",
            "details": str(e)
        }), 500

# For Vercel serverless deployment
app.debug = False

# Export the Flask app for Vercel
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9000)
