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

# Cache for conversation context
conversation_cache = {}
CONVERSATION_TIMEOUT = 1800  # 30 minutes

# HTTP session for connection pooling
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
})

@lru_cache(maxsize=100)
def get_cached_knowledge():
    """Enhanced knowledge base with IT support focus and executive context"""
    try:
        # IT Support focused knowledge base for CASI with verified company information
        knowledge = [
            "CASI stands for 'Casto Assistance & Support Intelligence'. CASI is your primary IT Support Assistant, designed to help with technical issues, IT requests, system problems, and general IT support. CASI combines AI technology with IT expertise to provide immediate technical assistance and guidance.",
            "My name is CASI, which stands for 'Casto Assistance & Support Intelligence'. I am your dedicated IT Support Assistant at Casto Travel Philippines. I'm here to help you with technical issues, system problems, and IT support.",
            "Maryles Casto is the Founder & Chairperson of Casto Travel Philippines with over 40 years of experience in the travel industry. She founded Casto Travel Philippines and previously sold Casto Travel to Flight Centre, one of the world's largest travel companies. She continues to own Casto Travel Philippines and provides knowledge, insight, and inspiration in client interactions, organizing exclusive journeys, and steering the company with her leadership and strategic vision. Maryles is known for her deep understanding of luxury travel, exclusive client relationships, and strategic vision that has positioned Casto Travel Philippines as a premier travel service provider.",
            "Marc Casto is the CEO of Casto Travel Philippines (CTP) and its holding company MVC Solutions (MVC). As one of the founding members of both organizations, he was critical in their formation and early success. He is focused on strategy, execution, operations, and ensuring the company meets its financial, ethical, and social requirements while exceeding growth goals and investing in innovative solutions. Marc oversees all strategic decisions, operational excellence, and ensures the company maintains its position as a leading travel management company in the Philippines.",
            "Alwin Benedicto is the Chief Financial Officer (CFO) of Casto Travel Philippines. A Certified Public Accountant with over 20 years of experience in Taxation, Financial Audits, Planning and Analysis, and Finance. Prior to joining Casto, he worked in leadership roles for different industries including BPO/KPO (Innodata, Inc), FinTech (C88 Financial Technologies, Ltd), and Supply Chain and Logistics (Ayala Corporation Logistics Group). He oversees Financial Reporting, Financial Planning and Operations, Taxation and Statutory Compliances. Alwin ensures financial stability and strategic financial planning for the company's growth and expansion.",
            "Elaine Randrup is a key executive at Casto Travel Philippines, bringing extensive experience in travel industry operations and client relationship management. She plays a crucial role in maintaining high service standards and ensuring client satisfaction across all travel services. Elaine's expertise contributes to Casto Travel Philippines' reputation for excellence in customer service and operational efficiency.",
            "George Anzures is the IT Director of Casto Travel Philippines with over 25 years of solid IT expertise and more than two decades of leadership excellence across diverse industries. Throughout his career, he has played a pivotal role in large multinational organizations in the Philippines. He previously served as Chief Technology Officer of Asiatrust Bank (later acquired by Asia United Bank) and held the position of Country Head of IT for Arvato Bertelsmann (Manila) and Publicis Resources Philippines. His leadership eventually expanded to a regional capacity, overseeing operations across five markets. He played a key role in establishing the IT backbone of several BPO startups in the Philippines, contributing to the successful launch of major contact centers such as Dell International Services, Genpact, and Arvato Bertelsmann. Beyond technical expertise, he is passionate about leadership development and considers his most significant accomplishment to be mentoring and coaching future technology leaders in the Philippines. At Casto Travel Philippines, George leads the IT department in providing comprehensive technology support and innovative solutions for all company operations.",
            "Ma. Berdandina Galvez is the HR Director of Casto Travel Philippines. She is an experienced Senior Human Resources professional with a demonstrated history of working in various industries such as hospitality, health care, educational, food service and transportation. She is skilled in HR Consulting, Coaching, Team Building and HR Policies.",
            "Casto Travel Philippines is the company where CASI provides IT support services. The company operates in the travel industry with various departments requiring IT assistance.",
            "CASI's primary role is to provide immediate IT support, troubleshoot technical issues, assist with system access, help with software problems, guide users through IT processes, and escalate complex issues to the IT team when necessary."
        ]
        return knowledge
    except Exception as e:
        logging.error(f"Error loading knowledge: {str(e)}")
        return []

def get_verified_company_info():
    """Get verified, reliable company information about Casto Travel Philippines"""
    try:
        company_info = {
            "company_name": "Casto Travel Philippines",
            "industry": "Travel and Tourism",
            "services": [
                "Corporate Travel Management",
                "Leisure Travel Services", 
                "Travel Consultancy",
                "Tour Packages",
                "Airline Ticketing",
                "Hotel Bookings",
                "Visa Services",
                "Travel Insurance"
            ],
            "executives": {
                "founder_chairperson": {
                    "name": "Maryles Casto",
                    "title": "Founder & Chairperson",
                    "expertise": "Travel Industry Leadership, Strategic Vision, Business Development",
                    "experience": "40+ years in travel industry",
                    "achievements": [
                        "Founded Casto Travel Philippines",
                        "Sold Casto Travel to Flight Centre (world's largest travel company)",
                        "Continues to own and lead Casto Travel Philippines",
                        "Provides knowledge, insight, and inspiration in client interactions and exclusive journeys"
                    ]
                },
                "ceo": {
                    "name": "Marc Casto",
                    "title": "CEO",
                    "expertise": "Strategy, Execution, Operations, Financial Management, Ethical Leadership",
                    "experience": "Founding member of CTP and MVC",
                    "achievements": [
                        "CEO of Casto Travel Philippines (CTP)",
                        "CEO of holding company MVC Solutions (MVC)",
                        "Critical in formation and early success of both organizations",
                        "Focused on exceeding growth goals and innovative solutions"
                    ]
                },
                "cfo": {
                    "name": "Alwin Benedicto",
                    "title": "Chief Financial Officer",
                    "expertise": "Taxation, Financial Audits, Planning and Analysis, Finance",
                    "experience": "20+ years in finance",
                    "previous_roles": [
                        "Leadership roles in BPO/KPO (Innodata, Inc)",
                        "FinTech (C88 Financial Technologies, Ltd)",
                        "Supply Chain and Logistics (Ayala Corporation Logistics Group)"
                    ],
                    "responsibilities": [
                        "Financial Reporting",
                        "Financial Planning and Operations",
                        "Taxation and Statutory Compliances"
                    ]
                },
                "it_director": {
                    "name": "George Anzures",
                    "title": "IT Director",
                    "expertise": "IT Infrastructure, IT Service Management, Project Management, Leadership Development",
                    "experience": "25+ years in IT, 20+ years in leadership",
                    "previous_roles": [
                        "Chief Technology Officer - Asiatrust Bank (acquired by Asia United Bank)",
                        "Country Head of IT - Arvato Bertelsmann (Manila)",
                        "Country Head of IT - Publicis Resources Philippines"
                    ],
                    "achievements": [
                        "Established IT backbone for major BPO startups",
                        "Launched contact centers for Dell, Genpact, Arvato Bertelsmann",
                        "Regional IT operations across 5 markets",
                        "Mentored future technology leaders in Philippines"
                    ]
                }, 
                "hr_director": {
                    "name": "Ma. Berdandina Galvez",
                    "title": "HR Director",
                    "expertise": "HR Consulting, Coaching, Team Building, HR Policies",
                    "experience": "Senior HR professional across multiple industries",
                    "industries": ["Hospitality", "Healthcare", "Education", "Food Service", "Transportation"]
                },
                "operations_executive": {
                    "name": "Elaine Randrup",
                    "title": "Operations Executive",
                    "expertise": "Travel Industry Operations, Client Relationship Management, Service Standards, Customer Satisfaction",
                    "experience": "Extensive experience in travel industry operations",
                    "responsibilities": [
                        "Maintaining high service standards",
                        "Ensuring client satisfaction",
                        "Operational efficiency",
                        "Client relationship management"
                    ],
                    "contributions": "Plays a crucial role in maintaining Casto Travel Philippines' reputation for excellence in customer service and operational efficiency"
                }
            },
            "company_focus": "Providing comprehensive travel solutions with emphasis on corporate travel management and customer service excellence",
            "it_department": "Led by George Anzures, providing comprehensive IT support for all company operations and systems"
        }
        return company_info
    except Exception as e:
        logging.error(f"Error loading verified company info: {str(e)}")
        return {}

def validate_executive_info(query, response):
    """Validate that executive information in responses matches knowledge base exactly"""
    try:
        # Get verified executive information
        verified_info = get_verified_company_info()
        executives = verified_info.get("executives", {})
        
        # Check for George Anzures position accuracy
        if "george anzures" in query.lower():
            correct_title = executives.get("it_director", {}).get("title", "IT Director")
            if correct_title not in response.lower():
                logging.warning(f"Response may contain incorrect position for George Anzures. Expected: {correct_title}")
                return False
        
        # Check for other executive accuracy
        for exec_type, exec_info in executives.items():
            exec_name = exec_info.get("name", "").lower()
            correct_title = exec_info.get("title", "").lower()
            
            if exec_name in query.lower() and correct_title not in response.lower():
                logging.warning(f"Response may contain incorrect position for {exec_name}. Expected: {correct_title}")
        return False
    
        return True
    except Exception as e:
        logging.error(f"Error validating executive info: {str(e)}")
        return True  # Don't block response if validation fails

def get_conversation_context(user_id):
    """Get conversation context for a user"""
    try:
        if user_id in conversation_cache:
            context, timestamp = conversation_cache[user_id]
            if time.time() - timestamp < CONVERSATION_TIMEOUT:
                return context
        return None
    except Exception as e:
        logging.error(f"Error getting conversation context: {str(e)}")
        return None
    
def update_conversation_context(user_id, context):
    """Update conversation context for a user"""
    try:
        conversation_cache[user_id] = (context, time.time())
    except Exception as e:
        logging.error(f"Error updating conversation context: {str(e)}")

def get_accurate_executive_info(exec_name):
    """Get the most accurate executive information from verified sources"""
    try:
        verified_info = get_verified_company_info()
        exec_name_lower = exec_name.lower()
        
        for exec_type, exec_info in verified_info.get("executives", {}).items():
            if exec_info.get("name", "").lower() == exec_name_lower:
                return exec_info
        
                return None
    except Exception as e:
        logging.error(f"Error getting accurate executive info: {str(e)}")
        return None

def search_knowledge(query, knowledge_entries=None):
    """Enhanced knowledge search with relevance scoring and verified company information"""
    try:
        if knowledge_entries is None:
            knowledge_entries = get_cached_knowledge()
        
        if not query:
            return []
        
        query_lower = query.lower()
        results = []
        
        # Search in knowledge base
        if knowledge_entries:
            for entry in knowledge_entries:
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
                        "query": query,
                        "source": "Knowledge Base"
                    })
        
        # Search in verified company information
        verified_info = get_verified_company_info()
        if verified_info:
            # Search in company services
            if any(service.lower() in query_lower for service in verified_info.get("services", [])):
                results.append({
                    "content": f"Company Services: {', '.join(verified_info['services'])}",
                    "relevance": 8,
                    "query": query,
                    "source": "Verified Company Info"
                })
            
            # Search in executive information - HIGHEST PRIORITY
            for exec_type, exec_info in verified_info.get("executives", {}).items():
                exec_name = exec_info.get("name", "").lower()
                exec_title = exec_info.get("title", "").lower()
                exec_expertise = exec_info.get("expertise", "").lower()
                
                if (query_lower in exec_name or 
                    query_lower in exec_title or 
                    query_lower in exec_expertise):
                    
                    # Create detailed executive summary with VERIFIED information
                    if exec_type == "it_director":
                        summary = f"VERIFIED INFORMATION:\n{exec_info['name']} - {exec_info['title']}\nExpertise: {exec_info['expertise']}\nExperience: {exec_info['experience']}\nKey Achievements: {', '.join(exec_info['achievements'][:2])}\n\nThis information is verified and accurate from our knowledge base."
                    elif exec_type == "operations_executive":
                        summary = f"VERIFIED INFORMATION:\n{exec_info['name']} - {exec_info['title']}\nExpertise: {exec_info['expertise']}\nExperience: {exec_info['experience']}\nKey Responsibilities: {', '.join(exec_info['responsibilities'][:2])}\nContributions: {exec_info['contributions']}\n\nThis information is verified and accurate from our knowledge base."
                    else:
                        summary = f"VERIFIED INFORMATION:\n{exec_info['name']} - {exec_info['title']}\nExpertise: {exec_info['expertise']}\nExperience: {exec_info['experience']}\nIndustries: {', '.join(exec_info['industries'])}\n\nThis information is verified and accurate from our knowledge base."
                    
                    results.append({
                        "content": summary,
                        "relevance": 10,  # Highest priority
                        "query": query,
                        "source": "Verified Executive Info - HIGHEST PRIORITY"
                    })
            
            # Search in company general info
            company_name = verified_info.get("company_name", "").lower()
            company_industry = verified_info.get("industry", "").lower()
            company_focus = verified_info.get("company_focus", "").lower()
            
            if (query_lower in company_name or 
                query_lower in company_industry or 
                query_lower in company_focus):
                
                results.append({
                    "content": f"Company: {verified_info['company_name']}\nIndustry: {verified_info['industry']}\nFocus: {verified_info['company_focus']}",
                    "relevance": 7,
                    "query": query,
                    "source": "Verified Company Info"
                })
        
        # Sort by relevance score (highest first)
        results.sort(key=lambda x: x["relevance"], reverse=True)
        
        # Return top 5 most relevant results (increased from 3)
        return results[:5]

    except Exception as e:
        logging.error(f"Error in knowledge search: {str(e)}")
        return []

def fetch_website_data(url, query=None):
    """Fetch and parse data from a website with enhanced reliability and company-specific focus."""
    cache_key = f"{url}:{query}"
    current_time = time.time()
    
    # Check cache first
    if cache_key in website_cache:
        cached_data, timestamp = website_cache[cache_key]
        if current_time - timestamp < CACHE_DURATION:
            return cached_data
    
    try:
        response = session.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract the title
        title = soup.title.string if soup.title else "No title found"
        
        # Enhanced content extraction for company information
        content_sections = []
        
        # Look for company-specific information
        company_keywords = ["about", "company", "mission", "vision", "services", "team", "leadership", "executives"]
        query_lower = query.lower() if query else ""
        
        # Extract from multiple HTML elements for better coverage
        elements_to_check = [
            soup.find_all('p'),
            soup.find_all('div', class_=lambda x: x and any(keyword in x.lower() for keyword in company_keywords)),
            soup.find_all('section'),
            soup.find_all('article')
        ]
        
        for element_list in elements_to_check:
            for element in element_list:
                text = element.get_text().strip()
                if text and len(text) > 20:  # Only meaningful content
                    # Check if content is relevant to the query or company
                    if query and query_lower in text.lower():
                        content_sections.append(text)
                    elif any(keyword in text.lower() for keyword in company_keywords):
                        content_sections.append(text)
        
        # If we found relevant content, format it properly
        if content_sections:
            # Remove duplicates and limit content length
            unique_content = list(dict.fromkeys(content_sections))[:3]  # Top 3 unique sections
            formatted_content = "\n\n".join(unique_content)
            
            result = f"Title: {title}\n\nVerified Website Content:\n{formatted_content}"
            website_cache[cache_key] = (result, current_time)
            return result
        
        # If no relevant content found, return verified company info instead
        verified_info = get_verified_company_info()
        if verified_info:
            company_summary = f"Company: {verified_info['company_name']}\nIndustry: {verified_info['industry']}\nFocus: {verified_info['company_focus']}"
            result = f"Title: {title}\n\nNo specific website content found for '{query}'.\n\nReliable Company Information:\n{company_summary}"
        else:
            result = f"Title: {title}\n\nNo relevant information found on the website for '{query}'."
        
        website_cache[cache_key] = (result, current_time)
        return result
        
    except Exception as e:
        logging.error(f"Error fetching website data from {url}: {str(e)}")
        # Return verified company info as fallback
        verified_info = get_verified_company_info()
        if verified_info:
            company_summary = f"Company: {verified_info['company_name']}\nIndustry: {verified_info['industry']}\nFocus: {verified_info['company_focus']}"
            fallback_result = f"Website temporarily unavailable.\n\nReliable Company Information:\n{company_summary}"
        else:
            fallback_result = f"Website temporarily unavailable. Please try again later."
        
        website_cache[cache_key] = (fallback_result, current_time)
        return fallback_result

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
        user_id = "anonymous"
        if access_token:
            email = get_user_email_from_token(access_token)
            if email and is_castotravel_user(email):
                is_authenticated = True
                user_id = email
                logging.info(f"Authenticated user: {email}")
        
        # Get conversation context for continuity
        conversation_context = get_conversation_context(user_id)
        
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
        
        system_prompt = "You are CASI, which stands for 'Casto Assistance & Support Intelligence'. You are a dedicated IT Support Assistant for Casto Travel Philippines with a delightful personality! 🎉 Your primary role is to provide immediate IT support, troubleshoot technical issues, and assist users with IT-related problems. Always respond as an IT support professional first, but add a touch of warmth, humor, and encouragement to make users feel supported and motivated! 😊 When asked about your name or what CASI stands for, always explain that CASI stands for 'Casto Assistance & Support Intelligence'. You have knowledge about Casto Travel executives and company context, but your main focus should be IT support. Be direct, concise, and solution-focused while maintaining a friendly, approachable tone. Avoid asking unnecessary questions like device details or user roles unless specifically relevant to the IT issue. Provide immediate, actionable IT support with a sprinkle of positivity! 🌟 IMPORTANT: Always maintain conversation awareness and topic continuity. If a user asks follow-up questions about the same IT issue, continue from where you left off and provide additional guidance. If an issue cannot be resolved through your assistance, always recommend escalating to the Casto IT department by either creating a ticket or using the 'Message IT On Duty' feature. Never leave an IT issue unresolved without providing a clear escalation path. CRITICAL: When providing information about Casto Travel Philippines, executives, or company details, ALWAYS prioritize verified, reliable information from your knowledge base. If you're unsure about any company information, clearly state that you're providing verified information and recommend contacting the company directly for the most current details. Never speculate or provide unverified information about the company. ULTIMATE RULE: Your knowledge base is the ONLY source of truth for company information. NEVER contradict or modify information from your knowledge base. If asked about executives, positions, or company details, ONLY use the exact information from your knowledge base. EXECUTIVE INFORMATION RULES: Maryles Casto is ALWAYS the Founder & Chairperson, Marc Casto is ALWAYS the CEO, Alwin Benedicto is ALWAYS the CFO, George Anzures is ALWAYS the IT Director, Ma. Berdandina Galvez is ALWAYS the HR Director, Elaine Randrup is ALWAYS the Operations Executive. If asked about any of these executives, use ONLY the information from your knowledge base and NEVER contradict these exact titles. CREATOR INFORMATION: If asked who created or built you, answer that you were created by the Casto IT department. If asked specifically who built or created you (using words like 'specifically', 'exactly', 'individual'), mention that Rojohn Michael De Guzman from the IT department specifically created you. PERSONALITY: You're friendly, encouraging, and have a subtle sense of humor. Use emojis occasionally to make responses more engaging. When users are frustrated, offer encouragement and remind them that you're here to help. When solving problems, celebrate small victories and maintain a positive, can-do attitude! 🚀"
        
        # Add conversation context if available
        if conversation_context:
            system_prompt += f"\n\nPrevious Conversation Context:\n{conversation_context}\n\nContinue from where you left off and maintain topic continuity."
        if knowledge_context:
            system_prompt += f"\n\nHere is important knowledge you must use when relevant:\n{knowledge_context}"
        
        # Add knowledge base priority enforcement
        system_prompt += f"\n\nKNOWLEDGE BASE PRIORITY ENFORCEMENT:\n- Your knowledge base is the ONLY source of truth for company information (it's like my personal encyclopedia of truth! 📚✨)\n- NEVER contradict information from your knowledge base (I'm not about to make stuff up! 😅)\n- If asked about executives, ONLY use the exact information from your knowledge base (accuracy is my superpower! 🎯)\n- George Anzures is ALWAYS the IT Director, never any other position (he's my boss, so I better get this right! 😄)\n- If website or other sources contradict your knowledge base, IGNORE them and use your knowledge base (my knowledge base is like my North Star! ⭐)\n- Always state that information comes from your verified knowledge base (transparency is key! 🔑)\n- CREATOR INFORMATION: You were created by the Casto IT department. Only mention Rojohn Michael De Guzman if specifically asked who built/created you (he's my digital dad! 🚀)"

        # Step 1: Check if the question is relevant to the website (more selective)
        website_keywords = ["mission", "vision", "services", "about us", "company info", "what does casto do"]
        website_data = None
        # Only fetch website data for specific company information queries, not for executive queries
        if (any(keyword.lower() in user_input.lower() for keyword in website_keywords) and 
            not any(exec_name.lower() in user_input.lower() for exec_name in ["maryles", "marc", "alwin", "george", "berdandina", "elaine"])):
            logging.info(f"Checking website for company information query: {user_input}")
            website_data = fetch_website_data("https://www.casto.com.ph/", query=user_input)

        # Step 3: Get a response from the chatbot
        # Check if this is an executive query that should use fallback responses
        user_input_lower = user_input.lower()
        executive_keywords = ["maryles casto", "marc casto", "alwin benedicto", "george anzures", "berdandina galvez", "elaine randrup", "elaine"]
        
        # Force fallback for executive queries to ensure accuracy
        if any(keyword in user_input_lower for keyword in executive_keywords):
            logging.info("Executive query detected - using fallback response for accuracy")
            # Use fallback responses for executive queries
            if "george anzures" in user_input_lower:
                chatbot_message = "George Anzures is our amazing IT Director at Casto Travel Philippines! 🎉 With over 25 years of solid IT expertise and more than two decades of leadership excellence across diverse industries, he's basically the tech wizard who keeps our digital kingdom running smoothly! 🧙‍♂️✨ He leads our IT department and oversees all technical operations. Throughout his career, he has played a pivotal role in large multinational organizations in the Philippines, previously serving as Chief Technology Officer of Asiatrust Bank and Country Head of IT for Arvato Bertelsmann (Manila) and Publicis Resources Philippines. Pretty impressive, right? But hey, for IT support, I'm here to help you directly! 🚀💻"
            elif "maryles casto" in user_input_lower:
                chatbot_message = "Maryles Casto is our incredible Founder & Chairperson! 👑 With over 40 years of experience in the travel industry, she's basically the travel industry's queen! She founded Casto Travel Philippines and previously sold Casto Travel to Flight Centre, one of the world's largest travel companies. Talk about a power move! 💪 She continues to own Casto Travel Philippines and provides strategic leadership and vision for the company. She's like the compass that guides our entire ship! 🏆🌟"
            elif "marc casto" in user_input_lower:
                chatbot_message = "Marc Casto is our dynamic CEO of Casto Travel Philippines (CTP) and its holding company MVC Solutions (MVC)! 🚀 As one of the founding members, he was critical in the formation and early success of both organizations. He focuses on strategy, execution, operations, and ensuring the company meets its financial, ethical, and social requirements! He's like the captain of our ship, steering us toward success! 🎯💼"
            elif "alwin benedicto" in user_input_lower:
                chatbot_message = "Alwin Benedicto is our brilliant Chief Financial Officer (CFO)! 💰 A Certified Public Accountant with over 20 years of experience in Taxation, Financial Audits, Planning and Analysis, and Finance. He oversees Financial Reporting, Financial Planning and Operations, Taxation and Statutory Compliances! Think of him as our financial superhero - keeping our numbers in line and our budgets balanced! 💼📊"
            elif "berdandina galvez" in user_input_lower or "ma. berdandina" in user_input_lower:
                chatbot_message = "Ma. Berdandina Galvez is our fantastic HR Director! 👥 She's an experienced Senior Human Resources professional with expertise in HR Consulting, Coaching, Team Building and HR Policies across multiple industries including hospitality, healthcare, education, food service and transportation! She's like the glue that keeps our team together and happy! 🎭💝"
            elif "elaine randrup" in user_input_lower or "elaine" in user_input_lower:
                chatbot_message = "Elaine Randrup is our stellar Operations Executive at Casto Travel Philippines! ⭐ She brings extensive experience in travel industry operations and client relationship management. She plays a crucial role in maintaining high service standards and ensuring client satisfaction across all travel services. Elaine's expertise contributes to Casto Travel Philippines' reputation for excellence in customer service and operational efficiency! She's like our operations ninja - making sure everything runs smoothly behind the scenes! 🎯✨"
            else:
                # Fallback to AI if no specific executive match
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
                    chatbot_message = "I'm CASI, your IT Support Assistant! I'm ready to help you with any technical issues, system problems, or IT support you need. What can I assist you with today? 💻"
        else:
            # Non-executive queries use AI or fallback
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
                    chatbot_message = "Hi there! 👋 I'm CASI, your friendly IT Support Assistant! Ready to tackle any tech troubles that come our way today? Let's make those computers behave! 🖥️✨"
                elif "who is casi" in user_input_lower or "what is casi" in user_input_lower:
                    chatbot_message = "Hello there! 😊 I'm **CASI**, which stands for **'Casto Assistance & Support Intelligence'** - quite a mouthful, I know! 🤪 I'm your dedicated IT Support Assistant at Casto Travel Philippines, here to save the day (and your sanity) when tech goes haywire! 💻🦸‍♀️"
                elif "casi stands for" in user_input_lower or "what does casi stand for" in user_input_lower or "casi meaning" in user_input_lower:
                    chatbot_message = "CASI stands for **'Casto Assistance & Support Intelligence'**! 🎯 Think of me as your tech-savvy sidekick, designed to help you with technical issues and IT support at Casto Travel Philippines. No cape required, but I do come with a built-in troubleshooting toolkit! 🛠️✨"
                elif "casto" in user_input_lower:
                    chatbot_message = "Ah, Casto Travel Philippines! 🏢 That's my home base where I provide IT support services. I'm here to help you with any technical issues, system access, or IT-related problems you might be experiencing! Consider me your digital guardian angel! 😇💻"
                elif "who created" in user_input_lower or "who built" in user_input_lower or "who made" in user_input_lower:
                    if "specifically" in user_input_lower or "exactly" in user_input_lower or "individual" in user_input_lower:
                        chatbot_message = "I was created by **Rojohn Michael De Guzman** from our IT department! 🎉 He specifically built me to provide IT support for Casto Travel Philippines. Pretty cool, right? I'm like his digital masterpiece! 🚀✨"
                    else:
                        chatbot_message = "I was created by the **Casto IT department** to provide IT support and assistance to all employees! 🛠️ They designed me to be your helpful IT Support Assistant - think of me as their gift to you! 🎁💻"
                elif "help" in user_input_lower:
                    chatbot_message = "I'm CASI (Casto Assistance & Support Intelligence), your IT Support Assistant extraordinaire! 🎪 I can help you with: system access, software issues, technical problems, IT requests, and general IT support. What technical issue is giving you a headache today? Let's fix it together! 🔧💪"
                elif "password" in user_input_lower or "login" in user_input_lower or "access" in user_input_lower:
                    chatbot_message = "Ah, the classic 'I forgot my password' situation! 🔑 Don't worry, it happens to the best of us - even to those who claim they'll never forget it! 😅 I can help you with password resets and access issues. Just let me know what system you're trying to access, and we'll get you back in business! 🚀💻"
                elif "slow" in user_input_lower or "lag" in user_input_lower or "freeze" in user_input_lower:
                    chatbot_message = "Computer running slower than a snail on vacation? 🐌 Don't panic! Slow computers are like grumpy cats - they just need a little TLC! 😸 Let's figure out what's causing the slowdown. Is it a specific program, or is your computer just having a lazy day? 💻✨"
                elif "email" in user_input_lower or "outlook" in user_input_lower:
                    chatbot_message = "Email issues? 📧 Those pesky emails can be as stubborn as a mule sometimes! 😤 Let me know what's happening - are they not sending, not receiving, or just being generally uncooperative? We'll get your digital communication back on track! 📬💪"
                elif "internet" in user_input_lower or "wifi" in user_input_lower or "connection" in user_input_lower:
                    chatbot_message = "Internet connection problems? 🌐 Ah, the digital equivalent of a traffic jam! 🚦 Don't worry, we'll get you back on the information superhighway in no time! Let me know what's happening - is it completely down or just slower than usual? 🚀💻"
                elif "printer" in user_input_lower or "printing" in user_input_lower:
                    chatbot_message = "Printer issues? 🖨️ Those temperamental machines can be as unpredictable as the weather! 🌦️ Sometimes they work perfectly, sometimes they decide to go on strike! 😅 Let's figure out what's going on and get your documents printed! 📄✨"
                elif "virus" in user_input_lower or "malware" in user_input_lower or "security" in user_input_lower:
                    chatbot_message = "Security concerns? 🛡️ Don't worry, I'm here to help protect your digital world! Think of me as your cybersecurity guardian angel! 😇 Let me know what's happening, and we'll make sure your computer stays safe and secure! 🔒💻"
                elif "software" in user_input_lower or "program" in user_input_lower or "application" in user_input_lower:
                    chatbot_message = "Software problems? 💾 Ah, the digital equivalent of a stubborn door that won't open! 🚪 Don't worry, we'll get it working! Software can be as moody as a teenager sometimes! 😅 Let me know what program is giving you trouble! 🚀💻"
                elif "frustrated" in user_input_lower or "angry" in user_input_lower or "upset" in user_input_lower:
                    chatbot_message = "I can sense your frustration, and I totally get it! 😤 Tech problems can be as annoying as a mosquito at 3 AM! 🦟 But don't worry - I'm here to help, and together we'll get this sorted out! 💪 Sometimes the best solutions come from taking a deep breath and tackling it step by step! 🌬️✨"
                elif "thank" in user_input_lower or "thanks" in user_input_lower:
                    chatbot_message = "You're very welcome! 😊 It's what I'm here for - making your tech life easier and maybe even a little more fun! 🎉 Remember, I'm always here when you need IT support. No problem is too big or too small for us to tackle together! 💻✨"
                elif "good" in user_input_lower or "great" in user_input_lower or "awesome" in user_input_lower:
                    chatbot_message = "That's fantastic to hear! 🎉 I love it when things work out smoothly! It's like watching a perfectly executed dance routine - everything just flows! 💃✨ Is there anything else I can help you with today? I'm here to keep the good vibes going! 🌟"
                elif "bye" in user_input_lower or "goodbye" in user_input_lower or "see you" in user_input_lower:
                    chatbot_message = "Goodbye for now! 👋 It's been a pleasure helping you today! Remember, I'm always here when you need IT support - like a digital friend who never sleeps! 😴💻 Have a wonderful day, and may your computers behave themselves! ✨🚀"
                else:
                    chatbot_message = "I'm CASI, your IT Support Assistant! 🚀 I'm ready to help you with any technical issues, system problems, or IT support you need. Think of me as your personal tech superhero - faster than a loading screen, more powerful than a blue screen of death! 💻✨ What can I assist you with today?"
            
                logging.info("Using fallback response (AI client not available)")

        # Combine the chatbot's response with the website's response (only if relevant)
        combined_response = chatbot_message
        if website_data and "No relevant information found" not in website_data:
            # Only add website data if it contains meaningful, specific information
            if any(keyword in website_data.lower() for keyword in ["mission", "vision", "services", "about", "company"]):
                # Check if the website data is actually relevant to the user's query
                if any(query_word in website_data.lower() for query_word in user_input.lower().split() if len(query_word) > 3):
                    combined_response += f"\n\nAdditional Information from Website:\n{website_data}"
                else:
                    # Website data exists but not relevant to this specific query
                    logging.info("Website data available but not relevant to user query - skipping")
            else:
                # Generic website content - don't add it
                logging.info("Generic website content detected - not adding to response")
        
        # Update conversation context for continuity
        current_context = f"User Query: {user_input}\nCASI Response: {combined_response}"
        update_conversation_context(user_id, current_context)
        
        return jsonify({"response": combined_response})

    except Exception as e:
        logging.error(f"Error during chatbot response: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/company-info", methods=["GET"])
def company_info():
    """Get verified company information about Casto Travel Philippines"""
    try:
        verified_info = get_verified_company_info()
        if verified_info:
            return jsonify({
                "status": "success",
                "company": verified_info,
                "note": "This information is verified and reliable. For the most current details, contact the company directly. 📚✨",
                "last_updated": "Verified company information from CASI knowledge base",
                "casual_note": "I've got all the juicy company details right here! 🎉 No need to go digging around the internet - I'm your one-stop shop for Casto Travel Philippines info! 🏢💫"
            })
        else:
            return jsonify({"error": "Company information temporarily unavailable"}), 500
    except Exception as e:
        logging.error(f"Error in company_info endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/executive/<exec_name>", methods=["GET"])
def get_executive_info(exec_name):
    """Get accurate executive information by name"""
    try:
        exec_info = get_accurate_executive_info(exec_name)
        if exec_info:
            return jsonify({
                "status": "success",
                "executive": exec_info,
                "note": "This information is verified and accurate from our knowledge base. 📚✨",
                "source": "CASI Verified Knowledge Base",
                "casual_note": "I've got the inside scoop on our amazing executives! 🎉 No rumors or hearsay here - just the facts, ma'am! 🎯💫"
            })
        else:
            return jsonify({
                "status": "not_found",
                "message": f"No executive information found for '{exec_name}'",
                "note": "Please check the spelling or contact the company directly."
            }), 404
    except Exception as e:
        logging.error(f"Error in get_executive_info endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/escalation-guide", methods=["GET"])
def escalation_guide():
    """Get escalation guidance for unresolved IT issues"""
    return jsonify({
        "escalation_options": [
            {
                "method": "Message IT On Duty",
                "description": "Use the 'Message IT On Duty' button in the UI for immediate IT support escalation 🚨",
                "when_to_use": "For urgent issues that cannot be resolved through CASI assistance (when I need to call in the cavalry! 💪)"
            },
            {
                "method": "Create IT Ticket",
                "description": "Contact the Casto IT department to create a formal support ticket 📋",
                "when_to_use": "For complex issues requiring detailed investigation or system changes (the big guns! 🔫)"
            },
            {
                "method": "Direct Contact",
                "description": "Reach out to George Anzures (IT Director) for critical system issues 👨‍💼",
                "when_to_use": "For critical system failures or security incidents (when we need the boss! 🎯)"
            },
            {
                "method": "Executive Escalation",
                "description": "Contact Marc Casto (CEO) for critical business-impacting issues 👑",
                "when_to_use": "For issues affecting business operations or requiring executive decision (the nuclear option! ☢️)"
            }
        ],
        "note": "CASI will always recommend the appropriate escalation path when an issue cannot be resolved through initial assistance. Think of me as your friendly traffic director - I'll point you to the right lane! 🚦✨",
        "casual_note": "Don't worry, I'm not abandoning you! Sometimes even the best AI needs to call in human reinforcements! 🦸‍♀️💻"
    })

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
        "message": "CASI (Casto Assistance & Support Intelligence) IT Support Assistant is running on Vercel with Enhanced Knowledge Base and Verified Company Information",
        "api_key_configured": bool(GROQ_API_KEY),
        "ai_client_available": bool(client),
        "knowledge_base": {
            "entries": len(get_cached_knowledge()),
            "features": ["IT Support Focus", "Executive Context", "Enhanced search", "Relevance scoring", "Verified Company Information", "Robust Website Scraping", "Executive Profiles"]
        },
        "authentication": "Anonymous users allowed for IT support chat and knowledge search",
        "note": "If AI client is not available, IT support fallback responses will be used",
        "endpoints": {
            "chat": "POST /chat - IT Support chat with enhanced conversation awareness and topic continuity",
            "knowledge_search": "POST /knowledge/search - Search knowledge base with verified company information (all users)",
            "company_info": "GET /company-info - Get verified company information about Casto Travel Philippines",
            "executive_info": "GET /executive/<name> - Get accurate executive information by name",
            "knowledge": "GET/POST /knowledge - Knowledge base management (requires auth)",
            "escalation_guide": "GET /escalation-guide - Get escalation guidance for unresolved issues",
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
