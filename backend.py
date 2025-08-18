from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from waitress import serve
import requests
from bs4 import BeautifulSoup
import logging
import sqlite3
from datetime import datetime, timedelta
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import threading
import time
from functools import lru_cache
from contextlib import contextmanager
import queue, os
import concurrent.futures

app = Flask(__name__)
CORS(app)

# Add Flask-Limiter for rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["60 per minute"]  # or whatever limit you want
)

# Get API key from environment variable for security
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# Setup OpenAI-style client for Groq
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY
)

# Define the website sources
WEBSITE_SOURCE = "https://www.travelpress.com/"
CASTO_TRAVEL_WEBSITE = "https://www.castotravel.ph/"
CASTO_WEBSITE = "https://www.casto.com.ph/"

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

DB_PATH = "conversations.db"

# Database connection pool
class DatabasePool:
    def __init__(self, db_path, max_connections=10):
        self.db_path = db_path
        self.max_connections = max_connections
        self.connections = queue.Queue(maxsize=max_connections)
        self._init_pool()
    
    def _init_pool(self):
        for _ in range(self.max_connections):
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self.connections.put(conn)
    
    @contextmanager
    def get_connection(self):
        conn = self.connections.get()
        try:
            yield conn
        finally:
            self.connections.put(conn)
    
    def close_all(self):
        while not self.connections.empty():
            conn = self.connections.get()
            conn.close()

# Initialize database pool
db_pool = DatabasePool(DB_PATH)

def init_db():
    with db_pool.get_connection() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            timestamp TEXT,
            content TEXT
        )''')
        conn.commit()

init_db()

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
    """Cache knowledge retrieval to avoid repeated DB queries"""
    with db_pool.get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT content FROM knowledge ORDER BY timestamp DESC")
        return [row[0] for row in c.fetchall()]

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

def fetch_casto_travel_info(query=None):
    """Fetch comprehensive information about Casto Travel Philippines from casto.com.ph."""
    cache_key = f"casto_travel:{query}"
    current_time = time.time()
    
    # Check cache first
    if cache_key in website_cache:
        cached_data, timestamp = website_cache[cache_key]
        if current_time - timestamp < CACHE_DURATION:
            return cached_data
    
    try:
        # Fetch from Casto main website
        response = session.get(CASTO_WEBSITE, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else "Casto - Growth Reimagined"
            
            # Extract comprehensive information
            comprehensive_info = []
            comprehensive_info.append(f"# {title}")
            comprehensive_info.append("")
            
            # Company Overview
            company_news = soup.find(string=lambda text: 'COMPANY NEWS:' in str(text))
            if company_news:
                news_parent = company_news.parent
                if news_parent:
                    news_text = news_parent.get_text().strip()
                    comprehensive_info.append("## Company News")
                    comprehensive_info.append(news_text)
                    comprehensive_info.append("")
            
            # Main Services
            comprehensive_info.append("## Core Services")
            
            # Agency Support
            agency_support = soup.find(string=lambda text: 'TRAVEL AGENCY SUPPORT' in str(text))
            if agency_support:
                support_section = agency_support.find_parent()
                if support_section:
                    support_text = support_section.get_text().strip()
                    comprehensive_info.append("### Travel Agency Support")
                    comprehensive_info.append(support_text)
                    comprehensive_info.append("")
            
            # Agent & Concierge Services
            agent_services = soup.find(string=lambda text: 'AGENT & CONCIERGE SERVICES' in str(text))
            if agent_services:
                agent_section = agent_services.find_parent()
                if agent_section:
                    agent_text = agent_section.get_text().strip()
                    comprehensive_info.append("### Agent & Concierge Services")
                    comprehensive_info.append(agent_text)
                    comprehensive_info.append("")
            
            # Accounting Services
            accounting_services = soup.find(string=lambda text: 'ACCOUNTING SERVICES' in str(text))
            if accounting_services:
                accounting_section = accounting_services.find_parent()
                if accounting_section:
                    accounting_text = accounting_section.get_text().strip()
                    comprehensive_info.append("### Accounting Services")
                    comprehensive_info.append(accounting_text)
                    comprehensive_info.append("")
            
            # Company Description
            company_desc = soup.find(string=lambda text: 'We use our experience, technology and global partnerships' in str(text))
            if company_desc:
                desc_parent = company_desc.parent
                if desc_parent:
                    desc_text = desc_parent.get_text().strip()
                    comprehensive_info.append("## Company Description")
                    comprehensive_info.append(desc_text)
                    comprehensive_info.append("")
            
            # Casto University
            university_section = soup.find(string=lambda text: 'Casto University' in str(text))
            if university_section:
                uni_parent = university_section.find_parent()
                if uni_parent:
                    uni_text = uni_parent.get_text().strip()
                    comprehensive_info.append("## Casto University")
                    comprehensive_info.append(uni_text)
                    comprehensive_info.append("")
            
            # Client Reviews
            comprehensive_info.append("## What Our Clients Say")
            reviews_section = soup.find(string=lambda text: 'WHAT OUR CLIENTS SAY ABOUT US' in str(text))
            if reviews_section:
                reviews_parent = reviews_section.parent
                if reviews_parent:
                    # Find review text
                    review_texts = reviews_parent.find_all(string=True)
                    for text in review_texts:
                        if text.strip() and len(text.strip()) > 20:
                            comprehensive_info.append(f"• {text.strip()}")
                    comprehensive_info.append("")
            
            # Local Footprint
            footprint_section = soup.find(string=lambda text: 'EXPANDING OUR LOCAL FOOTPRINT' in str(text))
            if footprint_section:
                footprint_parent = footprint_section.parent
                if footprint_parent:
                    footprint_text = footprint_parent.get_text().strip()
                    comprehensive_info.append("## Local Footprint")
                    comprehensive_info.append(footprint_text)
                    comprehensive_info.append("")
            
            # Accreditations
            comprehensive_info.append("## Accreditations & Certifications")
            accreditations = [
                "ISO 27001:2013 Certified by GICG and JAS-ANZ",
                "International Air Transport Associated Accredited Agent",
                "ASTA - American Society of Travel Advisors",
                "PCI-DSS Certified by Crossbow Labs",
                "Philippine Travel Agencies Association (PTAA) Accredited Member",
                "Philippine IATA Agency Association (PIATA) Member",
                "Philippine Tour Operators Association (PHILTOA) Accredited Member"
            ]
            for acc in accreditations:
                comprehensive_info.append(f"• {acc}")
            comprehensive_info.append("")
            
            # Founder Information
            founder_section = soup.find(string=lambda text: 'Our founder, Maryles Casto' in str(text))
            if founder_section:
                founder_parent = founder_section.parent
                if founder_parent:
                    founder_text = founder_parent.get_text().strip()
                    comprehensive_info.append("## Founder")
                    comprehensive_info.append(founder_text)
                    comprehensive_info.append("")
            
            # Contact Information
            comprehensive_info.append("## Contact Information")
            comprehensive_info.append("Website: https://www.casto.com.ph/")
            comprehensive_info.append("")
            
            # Combine all information
            if len(comprehensive_info) > 2:  # More than just title
                result = "\n".join(comprehensive_info)
            else:
                # Fallback to basic extraction
                paragraphs = soup.find_all('p')
                basic_info = []
                for paragraph in paragraphs[:20]:
                    para_text = paragraph.get_text().strip()
                    if para_text and len(para_text) > 20:
                        basic_info.append(para_text)
                
                if basic_info:
                    result = f"Title: {title}\n\nCasto Travel Philippines Information:\n\n" + "\n\n".join(basic_info[:10])
                else:
                    result = f"Title: {title}\n\nCasto Travel Philippines - Comprehensive travel services and support."
            
            website_cache[cache_key] = (result, current_time)
            return result
            
    except Exception as e:
        logging.error(f"Error fetching Casto information: {str(e)}")
    
    # Return comprehensive default information if all else fails
    default_info = """# Casto Travel Philippines

## Company Overview
Casto Travel Philippines is a leading travel and tourism company in the Philippines, part of the Casto Group. The company has been making its mark in the travel industry for more than 35 years.

## Company News
Casto Travel Philippines and MVC Solutions are now unified under one brand—CASTO!

## Core Services

### Travel Agency Support
Behind the scenes support for your frontline agents. Our travel agents are ready to support your frontline agents from behind the scenes to ensure reservations are ticketed and confirmed, including special requests.

### Agent & Concierge Services
With over 10 years of experience, our travel consultants provide high-quality customer service while ensuring travel policy compliance, 24 hours a day, 7 days a week.

### Accounting Services
Accounting professionals trained in travel accounting operations, with multi GDS and varied accounting system experience, deliver high level accounting services.

## Company Description
We use our experience, technology and global partnerships to bring travel management companies the best possible travel industry services.

## Casto University
With our years of experience, leadership, and emphasis on training, we set out to pioneer a travel university.

## Local Footprint
We have been making our mark in the travel industry for more than 35 years. Our Filipino-owned business, with beginnings in California's Silicon Valley, has two offices in the heart of Metro Manila. We now bring this company of highly skilled professionals to the City of Smiles - BACOLOD!

## Accreditations & Certifications
• ISO 27001:2013 Certified by GICG and JAS-ANZ
• International Air Transport Associated Accredited Agent
• ASTA - American Society of Travel Advisors
• PCI-DSS Certified by Crossbow Labs
• Philippine Travel Agencies Association (PTAA) Accredited Member
• Philippine IATA Agency Association (PIATA) Member
• Philippine Tour Operators Association (PHILTOA) Accredited Member

## Founder
Our founder, Maryles Casto, has written a book all about her travel industry experiences...from flight attendant to owning one of the top travel companies in Silicon Valley!

## Contact Information
Website: https://www.casto.com.ph/

For the most current information and to access their services, please visit their official website or contact them directly."""
    
    website_cache[cache_key] = (default_info, current_time)
    return default_info

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
@limiter.limit("30 per minute")
def add_knowledge():
    access_token = request.json.get("access_token")
    content = request.json.get("content")
    email = get_user_email_from_token(access_token)
    if email != "rojohn.deguzman@castotravel.ph":
        return jsonify({"error": "Unauthorized: Only rojohn.deguzman@castotravel.ph can add knowledge."}), 403
    if not content:
        return jsonify({"error": "No content provided"}), 400
    
    with db_pool.get_connection() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO knowledge (user_id, timestamp, content) VALUES (?, ?, ?)",
                  (email, datetime.utcnow().isoformat(), content))
        conn.commit()
    
    # Clear knowledge cache to force refresh
    get_cached_knowledge.cache_clear()
    return jsonify({"success": True})

@app.route('/knowledge', methods=['GET'])
@limiter.limit("30 per minute")
def get_knowledge():
    access_token = request.args.get("access_token")
    email = get_user_email_from_token(access_token)
    if not email or not is_castotravel_user(email):
        return jsonify({"error": "Unauthorized"}), 403
    
    with db_pool.get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT id, timestamp, content FROM knowledge ORDER BY timestamp DESC")
        rows = c.fetchall()
    
    return jsonify([{"id": r[0], "timestamp": r[1], "content": r[2]} for r in rows])

@app.route("/chat", methods=["POST"])
@limiter.limit("60 per minute")
def chat():
    data = request.json
    user_input = data.get("message", "")
    access_token = data.get("access_token")
    email = get_user_email_from_token(access_token)
    if not email or not is_castotravel_user(email):
        return jsonify({"error": "Unauthorized: Only castotravel.ph users allowed"}), 403

    # Use cached knowledge retrieval
    knowledge_entries = get_cached_knowledge()

    # Combine knowledge into a single string
    knowledge_context = "\n".join(knowledge_entries)
    system_prompt = "You are a helpful assistant named CASI."
    if knowledge_context:
        system_prompt += "\nHere is some important knowledge you must always use:\n" + knowledge_context

    # Step 1: Check if the question is about Casto Travel Philippines
    casto_travel_keywords = ["casto travel", "casto travel philippines", "casto philippines", "casto travel services", "casto tourism", "casto travel agency"]
    website_data = None
    
    if any(keyword.lower() in user_input.lower() for keyword in casto_travel_keywords):
        logging.info(f"Fetching Casto Travel Philippines information for user query: {user_input}")
        website_data = fetch_casto_travel_info(user_input)
    # Step 2: Check if the question is relevant to other CASTO topics
    elif any(keyword.lower() in user_input.lower() for keyword in ["CASTO", "mission", "vision", "services", "CEO", "about"]):
        logging.info(f"Checking website ({WEBSITE_SOURCE}) for user query: {user_input}")
        website_data = fetch_website_data("https://www.casto.com.ph/", query=user_input)

    # Step 3: Get a response from the chatbot
    try:
        logging.info("Fetching response from the chatbot.")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Upgraded to more powerful 70B model
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
        # If an error occurs, return an error message
        logging.error(f"Error during chatbot response: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Cleanup function for graceful shutdown
def cleanup():
    """Cleanup resources on shutdown"""
    session.close()
    db_pool.close_all()
    # Clear caches
    get_cached_knowledge.cache_clear()
    website_cache.clear()

if __name__ == '__main__':
    logging.info("✅ Backend is running at http://172.16.11.69:9000")
    try:
        serve(app, host='172.16.11.69', port=9000)
    except KeyboardInterrupt:
        cleanup()
        logging.info("Backend shutdown complete")