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
from duckduckgo_search import DDGS
from newspaper import Article

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

# Define the website sources
WEBSITE_SOURCE = "https://www.travelpress.com/"
CASTO_TRAVEL_WEBSITE = "https://www.castotravel.ph/"
CASTO_WEBSITE = "https://www.casto.com.ph/"

# Additional Casto-related sources for enhanced learning
CASTO_SOURCES = [
    "https://www.casto.com.ph/",
    "https://www.castotravel.ph/",
    "https://www.facebook.com/castotravelphilippines",
    "https://www.linkedin.com/company/casto-travel-philippines",
    "https://www.instagram.com/castotravelph/",
    "https://www.youtube.com/@castotravelphilippines"
]

# Cache for website data (in-memory for serverless)
website_cache = {}
CACHE_DURATION = 300  # 5 minutes

# Conversation memory and context management (simplified for serverless)
conversation_memory = {}
CONVERSATION_TIMEOUT = 1800  # 30 minutes
MAX_CONVERSATION_HISTORY = 5  # Keep last 5 exchanges for serverless

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
                uni_parent = university_section.parent
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

def create_casto_direct_response(user_input, knowledge_entries, website_data):
    """Create a direct response for Casto Travel questions using knowledge base only."""
    user_input_lower = user_input.lower()
    
    # Check for incorrect CEO claims first
    is_incorrect_ceo, incorrect_name = check_incorrect_ceo_claims(user_input)
    if is_incorrect_ceo:
        return f"""As CASI, I need to CORRECT this information immediately!

{incorrect_name.title()} is NOT the CEO of Casto Travel Philippines. This is INCORRECT information.

The CORRECT information from our knowledge base is:
• **Founder**: Maryles Casto
• **Current CEO**: Marc Casto

Anyone claiming {incorrect_name.title()} is the CEO is providing outdated or wrong information. Marc Casto is the current CEO of Casto Travel Philippines, continuing the family legacy established by founder Maryles Casto."""
    
    # Check for CEO/founder questions first
    if any(word in user_input_lower for word in ["ceo", "founder", "who", "leader"]):
        if "casto" in user_input_lower:
            # Special handling for "who is maryles casto" questions
            if "maryles" in user_input_lower:
                return """As CASI, I can tell you that based on my knowledge base, Maryles Casto is the founder of Casto Travel Philippines. She started as a flight attendant and went on to own one of the top travel companies in Silicon Valley. 

Maryles Casto established the foundation for what would become Casto Travel Philippines, a leading travel and tourism company in the Philippines. The company has been making its mark in the travel industry for more than 35 years.

Today, the company is part of the unified CASTO brand, combining Casto Travel Philippines and MVC Solutions, with Marc Casto serving as the current CEO, continuing the family legacy of excellence in the travel industry."""
            
            return """As CASI, I can tell you that based on my knowledge base, Casto Travel Philippines was founded by Maryles Casto, who started as a flight attendant and went on to own one of the top travel companies in Silicon Valley. 

The current CEO is Marc Casto, who continues the family legacy of excellence in the travel industry. The company is now part of the unified CASTO brand, combining Casto Travel Philippines and MVC Solutions.

IMPORTANT: The current CEO is Marc Casto, NOT Michael S. Pastrana, NOT Ricardo Dickie Reyes, and NOT any other name. This is FACTUAL information from our knowledge base.

For the most current leadership information, please contact Casto Travel Philippines directly at https://www.casto.com.ph/"""
    
    # Check for company information
    if any(word in user_input_lower for word in ["what", "company", "business", "services"]):
        if "casto" in user_input_lower:
            return """As CASI (Casto Assistance and Support Intelligence), I can tell you that based on my knowledge base, Casto Travel Philippines is a leading travel and tourism company in the Philippines, part of the Casto Group. 

The company has been making its mark in the travel industry for more than 35 years. It's a Filipino-owned business that began in California's Silicon Valley and now has two offices in Metro Manila, plus expansion to Bacolod City.

Services include:
• Domestic and international travel packages
• Hotel bookings and reservations
• Tour packages and excursions
• Travel insurance and documentation
• Corporate travel management
• Group travel arrangements

For more detailed information, visit their official website: https://www.casto.com.ph/"""
    
    # Check for history questions
    if any(word in user_input_lower for word in ["history", "background", "when", "started"]):
        if "casto" in user_input_lower:
            return """Based on my knowledge base, Casto Travel Philippines has been making its mark in the travel industry for more than 35 years. 

It's a Filipino-owned business that began in California's Silicon Valley and now has two offices in the heart of Metro Manila. The company combines Casto Travel Philippines and MVC Solutions under the unified CASTO brand.

The company has expanded to bring highly skilled professionals to Bacolod City, known as the City of Smiles."""
    
    # Check for accreditation questions
    if any(word in user_input_lower for word in ["accreditation", "certification", "certified", "member"]):
        if "casto" in user_input_lower:
            return """Based on my knowledge base, Casto Travel Philippines holds multiple prestigious accreditations including:

• ISO 27001:2013 Certified by GICG and JAS-ANZ
• International Air Transport Associated Accredited Agent
• ASTA - American Society of Travel Advisors
• PCI-DSS Certified by Crossbow Labs
• Philippine Travel Agencies Association (PTAA) Accredited Member
• Philippine IATA Agency Association (PIATA) Member
• Philippine Tour Operators Association (PHILTOA) Accredited Member

This makes it one of the most certified travel agencies in the Philippines."""
    
    # If no specific match but it's a Casto question, provide general info
    if "casto" in user_input_lower:
        return """Based on my knowledge base, Casto Travel Philippines is a leading travel and tourism company in the Philippines, part of the Casto Group. 

The company was founded by Maryles Casto and has been serving the travel industry for more than 35 years. They offer comprehensive travel services including domestic and international packages, hotel bookings, tours, travel insurance, and corporate travel management.

For the most current and detailed information, please visit their official website: https://www.casto.com.ph/"""
    
    return None  # Let the AI model handle non-Casto questions

def manage_conversation_context(user_id, user_input, response):
    """Manage conversation context and memory for better follow-up understanding."""
    current_time = time.time()
    
    # Initialize or get existing conversation
    if user_id not in conversation_memory:
        conversation_memory[user_id] = {
            'history': [],
            'last_updated': current_time,
            'topics': set(),
            'intent': None
        }
    
    conv = conversation_memory[user_id]
    
    # Clean old conversations
    if current_time - conv['last_updated'] > CONVERSATION_TIMEOUT:
        conv['history'] = []
        conv['topics'] = set()
        conv['intent'] = None
    
    # Add current exchange to history
    conv['history'].append({
        'user_input': user_input,
        'response': response,
        'timestamp': current_time
    })
    
    # Keep only recent history
    if len(conv['history']) > MAX_CONVERSATION_HISTORY:
        conv['history'] = conv['history'][-MAX_CONVERSATION_HISTORY:]
    
    # Update last activity
    conv['last_updated'] = current_time
    
    # Extract and track topics
    casto_keywords = ["casto", "travel", "philippines", "ceo", "founder", "services", "company"]
    detected_topics = [word for word in casto_keywords if word.lower() in user_input.lower()]
    conv['topics'].update(detected_topics)
    
    return conv

def understand_user_intent(user_input, conversation_context):
    """Analyze user intent and context for better responses."""
    user_input_lower = user_input.lower()
    
    # Check for Casto-related questions FIRST (highest priority)
    casto_keywords = [
        "casto", "marc casto", "maryles casto", "ceo", "founder", "leader", 
        "casto travel", "casto philippines", "casto group", "casto travel philippines"
    ]
    
    # Check for general knowledge questions SECOND (high priority)
    general_question_keywords = [
        "what is", "who is", "when is", "where is", "why is", "how is",
        "what are", "who are", "when are", "where are", "why are", "how are",
        "what does", "who does", "when does", "where does", "why does", "how does",
        "explain", "tell me about", "describe", "define", "what do you know about"
    ]
    
    # Check for travel/tourism questions THIRD (medium priority)
    travel_keywords = [
        "travel", "tourism", "vacation", "holiday", "trip", "booking", "hotel",
        "flight", "airline", "destination", "tour", "package", "philippines",
        "manila", "cebu", "boracay", "palawan", "visa", "passport"
    ]
    
    # If it's a Casto question, override other intent detection
    if any(keyword in user_input_lower for keyword in casto_keywords):
        return {
            'intent': 'casto_question',
            'context_clues': ['casto_focus'],
            'is_follow_up': False
        }
    
    # If it's a general knowledge question, give it high priority
    if any(keyword in user_input_lower for keyword in general_question_keywords):
        return {
            'intent': 'general_question',
            'context_clues': ['knowledge_seeking'],
            'is_follow_up': False
        }
    
    # If it's a travel/tourism question, give it medium priority
    if any(keyword in user_input_lower for keyword in travel_keywords):
        return {
            'intent': 'travel_question',
            'context_clues': ['travel_focus'],
            'is_follow_up': False
        }
    
    # Intent classification for non-Casto questions
    intents = {
        'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening'],
        'farewell': ['bye', 'goodbye', 'see you', 'thank you', 'thanks'],
        'question': ['what', 'who', 'when', 'where', 'why', 'how', 'tell me', 'explain'],
        'clarification': ['what do you mean', 'i don\'t understand', 'can you explain', 'clarify'],
        'follow_up': ['and', 'also', 'what about', 'how about', 'tell me more'],
        'comparison': ['difference', 'compare', 'versus', 'vs', 'better', 'best'],
        'request': ['help', 'assist', 'support', 'need', 'want', 'looking for']
    }
    
    detected_intent = 'general'
    for intent, keywords in intents.items():
        if any(keyword in user_input_lower for keyword in keywords):
            detected_intent = intent
            break
    
    # Context awareness
    context_clues = []
    if conversation_context and conversation_context['history']:
        last_exchange = conversation_context['history'][-1]
        last_topic = last_exchange.get('topics', set())
        
        # Check if this is a follow-up question
        if any(topic in user_input_lower for topic in last_topic):
            context_clues.append('follow_up')
        
        # Check for pronouns that refer to previous context
        pronouns = ['it', 'this', 'that', 'they', 'them', 'their', 'the company', 'the service']
        if any(pronoun in user_input_lower for pronoun in pronouns):
            context_clues.append('pronoun_reference')
    
    return {
        'intent': detected_intent,
        'context_clues': context_clues,
        'is_follow_up': 'follow_up' in context_clues or 'pronoun_reference' in context_clues
    }

def generate_contextual_response(user_input, intent_analysis, conversation_context, knowledge_entries):
    """Generate contextual responses based on conversation history and intent."""
    user_input_lower = user_input.lower()
    
    # Handle Casto questions FIRST (highest priority)
    if intent_analysis['intent'] == 'casto_question':
        # Let the main logic handle Casto questions with knowledge base
        return None
    
    # Handle general knowledge questions SECOND (high priority)
    if intent_analysis['intent'] == 'general_question':
        # Let the main logic handle general questions with web search
        return None
    
    # Handle travel/tourism questions THIRD (medium priority)
    if intent_analysis['intent'] == 'travel_question':
        # Let the main logic handle travel questions with enhanced search
        return None
    
    # Handle greetings
    if intent_analysis['intent'] == 'greeting':
        return """Hello! I'm CASI, your specialized AI assistant for Casto Travel Philippines information. 

I'm here to provide you with expert knowledge about Casto Travel Philippines, their services, leadership, and company details. How can I assist you today? 😊"""
    
    # Handle farewells
    if intent_analysis['intent'] == 'farewell':
        return """Thank you for chatting with me! I'm CASI, and I'm glad I could help you with information about Casto Travel Philippines. 

If you have more questions in the future, feel free to ask. Have a great day! 👋"""
    
    # Handle follow-up questions with context
    if intent_analysis['is_follow_up'] and conversation_context and conversation_context['history']:
        last_exchange = conversation_context['history'][-1]
        last_response = last_exchange['response']
        
        # Provide contextual follow-up information
        if 'casto' in user_input_lower:
            return f"""Based on our previous conversation, let me provide you with additional information about Casto Travel Philippines.

{get_casto_follow_up_info(user_input_lower, last_response)}"""
    
    # Handle clarification requests
    if intent_analysis['intent'] == 'clarification':
        return """I'd be happy to clarify! I'm CASI, and I want to make sure you get the information you need. Let me explain that in a different way. 

Could you please let me know what specific part you'd like me to clarify about Casto Travel Philippines?"""
    
    # Handle CASI meaning questions
    if check_casi_meaning_question(user_input):
        return """Great question! CASI stands for "Casto Assistance and Support Intelligence." 

I'm your specialized AI assistant designed to provide expert information about Casto Travel Philippines, their services, leadership, and company details. I'm here to help you with any questions you have about Casto Travel Philippines! 😊"""
    
    return None  # Let the main logic handle other cases

def get_casto_follow_up_info(user_input, last_response):
    """Generate follow-up information based on previous context."""
    follow_up_info = """As CASI, here's some additional context that might be helpful:

• **Company Overview**: Casto Travel Philippines is part of the Casto Group
• **Leadership**: Founded by Maryles Casto, currently led by CEO Marc Casto  
• **Services**: Comprehensive travel packages, corporate management, accounting services
• **Locations**: Offices in Metro Manila and expanding to Bacolod City
• **Accreditations**: Multiple industry certifications including IATA, ASTA, PTAA

Is there a specific aspect you'd like to know more about?"""
    
    return follow_up_info

def smart_web_search(query):
    """Smart web search that automatically detects Casto vs general queries."""
    try:
        with DDGS() as ddgs:
            # Detect if this is a Casto-related query
            casto_keywords = [
                "casto", "casto travel", "casto travel philippines", 
                "maryles casto", "marc casto", "casto group",
                "casto philippines", "casto travel agency"
            ]
            
            user_query_lower = query.lower()
            is_casto_query = any(keyword in user_query_lower for keyword in casto_keywords)
            
            # Build search query based on type
            if is_casto_query:
                # For Casto queries, focus on Casto-specific information
                search_query = f"Casto Travel Philippines {query}"
                search_type = "Casto-Focused"
                logging.info(f"CASTO QUERY DETECTED: {query} -> {search_query}")
            else:
                # For general queries, search broadly
                search_query = query
                search_type = "General"
                logging.info(f"GENERAL QUERY: {query}")
            
            # Perform the search
            results = list(ddgs.text(search_query, max_results=5))
            
            if not results:
                return None
            
            # Process and format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'title': result.get('title', ''),
                    'snippet': result.get('body', ''),
                    'url': result.get('link', ''),
                    'source': 'Web Search',
                    'search_type': search_type,
                    'original_query': query,
                    'search_query_used': search_query
                })
            
            return formatted_results
    except Exception as e:
        logging.error(f"Smart web search error: {e}")
        return None

def web_search_casto_info(query):
    """Legacy function - now calls smart search for backward compatibility."""
    return smart_web_search(query)

def fetch_enhanced_casto_info(query):
    """Fetch enhanced information from multiple Casto sources."""
    enhanced_info = []
    
    try:
        # Web search for recent information
        web_results = web_search_casto_info(query)
        if web_results:
            enhanced_info.extend(web_results)
        
        # Fetch from Casto websites
        for source in CASTO_SOURCES[:2]:  # Limit to main websites
            try:
                website_data = fetch_website_data(source, query)
                if website_data:
                    enhanced_info.append({
                        'title': f'Information from {source}',
                        'snippet': website_data[:500] + '...' if len(website_data) > 500 else website_data,
                        'url': source,
                        'source': 'Casto Website'
                    })
            except Exception as e:
                logging.error(f"Error fetching from {source}: {e}")
                continue
        
        return enhanced_info
    except Exception as e:
        logging.error(f"Enhanced info fetch error: {e}")
        return None

def analyze_and_synthesize_info(knowledge_entries, enhanced_info, user_query):
    """Analyze and synthesize information from multiple sources."""
    if not enhanced_info:
        return knowledge_entries
    
    # Combine knowledge base with enhanced web information
    combined_info = []
    
    # Add knowledge base entries
    for entry in knowledge_entries:
        combined_info.append({
            'content': entry,
            'source': 'Knowledge Base',
            'reliability': 'High'
        })
    
    # Add enhanced web information
    for info in enhanced_info:
        combined_info.append({
            'content': f"{info['title']}: {info['snippet']}",
            'source': info['source'],
            'reliability': 'Medium' if info['source'] == 'Web Search' else 'High'
        })
    
    return combined_info

def check_casi_meaning_question(user_input):
    """Check if user is asking what CASI stands for."""
    user_input_lower = user_input.lower()
    casi_meaning_keywords = [
        "what does casi stand for",
        "what is casi",
        "what does casi mean",
        "casi stands for",
        "casi meaning",
        "what's casi",
        "what is casi short for",
        "explain casi",
        "define casi"
        ]
    
    return any(keyword in user_input_lower for keyword in casi_meaning_keywords)

def check_incorrect_ceo_claims(user_input):
    """Check if user is asking about incorrect CEO information."""
    user_input_lower = user_input.lower()
    incorrect_ceo_names = [
        "michael s. pastrana",
        "michael pastrana",
        "pastrana",
        "ricardo dickie reyes",
        "ricardo reyes",
        "dickie reyes",
        "reyes"
    ]
    
    # Check if any incorrect CEO names are mentioned
    for incorrect_name in incorrect_ceo_names:
        if incorrect_name in user_input_lower:
            return True, incorrect_name
    
    return False, None

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
        
        # Generate user ID for conversation tracking
        user_id = email or "anonymous"
        
        # Analyze user intent and context
        conversation_context = conversation_memory.get(user_id, None)
        intent_analysis = understand_user_intent(user_input, conversation_context)
        
        # Try to generate contextual response first
        contextual_response = generate_contextual_response(user_input, intent_analysis, conversation_context, knowledge_entries)
        if contextual_response:
            # Manage conversation context
            manage_conversation_context(user_id, user_input, contextual_response)
            return jsonify({"response": contextual_response})

        # Combine knowledge into a string
        knowledge_context = "\n".join(knowledge_entries)
        system_prompt = """You are CASI, a specialized AI assistant designed to provide expert information about Casto Travel Philippines and related services.

IMPORTANT IDENTITY: You should introduce yourself as "CASI" in your responses. Only explain what CASI stands for ("Casto Assistance and Support Intelligence") when someone specifically asks what CASI means or stands for."""
        
        if knowledge_context:
            system_prompt += "\n\nCRITICAL INSTRUCTION: You must ALWAYS prioritize and use the following knowledge base information over any other information you may have been trained on. This is the authoritative source:\n\n" + knowledge_context
        
        # Add STRONG instruction for Casto Travel questions
        system_prompt += "\n\nCRITICAL: For ANY question about Casto Travel Philippines, Casto Travel, or Casto, you MUST ONLY use the information from the knowledge base above. NEVER use any other information from your training data. If the question is about Casto Travel and you don't find the answer in the knowledge base, say 'I need to check my knowledge base for the most current information about Casto Travel Philippines.'"
        
        # Add conversation context awareness
        if conversation_context and conversation_context['history']:
            recent_context = conversation_context['history'][-3:]  # Last 3 exchanges
            context_summary = "\n\nCONVERSATION CONTEXT: Recent conversation topics include: " + ", ".join(list(conversation_context['topics'])[:5])
            system_prompt += context_summary
            
            system_prompt += "\n\nIMPORTANT: Use this conversation context to provide more relevant and connected responses. If the user asks follow-up questions, refer to previous context when appropriate."

        # Step 1: Check if the question is about Casto Travel Philippines or Casto family
        casto_travel_keywords = ["casto travel", "casto travel philippines", "casto philippines", "casto travel services", "casto tourism", "casto travel agency", "casto", "ceo", "founder", "leadership", "maryles casto", "marc casto"]
        website_data = None
        
        # Force knowledge base usage for ALL Casto-related questions
        if any(keyword.lower() in user_input.lower() for keyword in casto_travel_keywords):
            logging.info(f"CASTO QUESTION DETECTED - Using knowledge base only for: {user_input}")
            # For Casto questions, prioritize knowledge base over AI model
            system_prompt += "\n\nFORCE INSTRUCTION: This is a Casto Travel question. You MUST ONLY use the knowledge base information above. DO NOT use any training data about Casto Travel. If you don't have the answer in the knowledge base, redirect to the website data."
            website_data = fetch_casto_travel_info(user_input)
        # Step 2: Check if the question is relevant to other CASTO topics
        elif any(keyword.lower() in user_input.lower() for keyword in ["CASTO", "mission", "vision", "services", "CEO", "about"]):
            logging.info(f"Checking website ({WEBSITE_SOURCE}) for user query: {user_input}")
            website_data = fetch_website_data("https://www.casto.com.ph/", query=user_input)

        # Step 3: Get a response from the chatbot using Groq (your original working setup)
        try:
            # For Casto Travel questions, create a direct response from knowledge base
            if any(keyword.lower() in user_input.lower() for keyword in casto_travel_keywords):
                logging.info("Creating direct Casto Travel response from knowledge base.")
                
                # Create a direct response using knowledge base
                direct_response = create_casto_direct_response(user_input, knowledge_entries, website_data)
                if direct_response:
                    # Manage conversation context
                    manage_conversation_context(user_id, user_input, direct_response)
                    return jsonify({"response": direct_response})
            
            # If not a Casto question or no direct response, use AI model
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
                model="llama-3.3-70b-versatile",  # Upgraded to more powerful 70B model
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

            # Manage conversation context
            manage_conversation_context(user_id, user_input, combined_response)
            
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

@app.route("/conversation/context", methods=["GET"])
def get_conversation_context():
    """Get current conversation context for a user."""
    access_token = request.args.get("access_token")
    email = get_user_email_from_token(access_token) if access_token else "test@example.com"
    
    user_id = email
    if user_id in conversation_memory:
        conv = conversation_memory[user_id]
        return jsonify({
            "user_id": user_id,
            "topics": list(conv['topics']),
            "conversation_count": len(conv['history']),
            "last_updated": conv['last_updated'],
            "recent_topics": list(conv['topics'])[:5]
        })
    else:
        return jsonify({"message": "No conversation history found"})

@app.route("/conversation/clear", methods=["POST"])
def clear_conversation_context():
    """Clear conversation context for a user."""
    access_token = request.json.get("access_token") if request.json else None
    email = get_user_email_from_token(access_token) if access_token else "test@example.com"
    
    user_id = email
    if user_id in conversation_memory:
        del conversation_memory[user_id]
        return jsonify({"message": "Conversation context cleared successfully"})
    else:
        return jsonify({"message": "No conversation context to clear"})

@app.route("/search", methods=["POST"])
@limiter.limit("30 per minute")
def web_search():
    """Perform smart web search that automatically detects Casto vs general queries."""
    try:
        data = request.json
        query = data.get("query", "") if data else ""
        
        if not query:
            return jsonify({"error": "No query provided"}), 400
        
        # Perform smart web search
        search_results = smart_web_search(query)
        
        if search_results:
            # Determine search type for response
            search_type = search_results[0].get('search_type', 'Unknown') if search_results else 'Unknown'
            
            return jsonify({
                "success": True,
                "results": search_results,
                "query": query,
                "search_type": search_type,
                "message": f"Smart search completed - {search_type} mode"
            })
        else:
            return jsonify({
                "success": False,
                "message": "No search results found",
                "query": query
            })
    
    except Exception as e:
        logging.error(f"Smart web search error: {e}")
        return jsonify({"error": "Search service temporarily unavailable"}), 500

@app.route("/sources", methods=["GET"])
@limiter.limit("30 per minute")
def get_available_sources():
    """Get list of available information sources."""
    return jsonify({
        "sources": CASTO_SOURCES,
        "description": "Available information sources for Casto Travel Philippines"
    })

@app.route("/search/general", methods=["POST"])
@limiter.limit("30 per minute")
def general_web_search():
    """Perform general web search for any topic."""
    try:
        data = request.json
        query = data.get("query", "") if data else ""
        
        if not query:
            return jsonify({"error": "No query provided"}), 400
        
        # Force general search mode
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=8))  # More results for general search
            
            if results:
                formatted_results = []
                for result in results:
                    formatted_results.append({
                        'title': result.get('title', ''),
                        'snippet': result.get('body', ''),
                        'url': result.get('link', ''),
                        'source': 'General Web Search',
                        'search_type': 'General',
                        'original_query': query
                    })
                
                return jsonify({
                    "success": True,
                    "results": formatted_results,
                    "query": query,
                    "search_type": "General",
                    "message": "General web search completed"
                })
            else:
                return jsonify({
                    "success": False,
                    "message": "No general search results found",
                    "query": query
                })
    
    except Exception as e:
        logging.error(f"General web search error: {e}")
        return jsonify({"error": "General search service temporarily unavailable"}), 500

@app.route("/search/knowledge", methods=["POST"])
@limiter.limit("30 per minute")
def knowledge_web_search():
    """Perform knowledge-focused web search for general questions."""
    try:
        data = request.json
        query = data.get("query", "") if data else ""
        
        if not query:
            return jsonify({"error": "No query provided"}), 400
        
        # Use smart search for knowledge questions
        search_results = smart_web_search(query)
        
        if search_results:
            return jsonify({
                "success": True,
                "results": search_results,
                "query": query,
                "search_type": "Knowledge",
                "message": "Knowledge search completed with smart detection"
            })
        else:
            return jsonify({
                "success": False,
                "message": "No knowledge search results found",
                "query": query
            })
    
    except Exception as e:
        logging.error(f"Knowledge web search error: {e}")
        return jsonify({"error": "Knowledge search service temporarily unavailable"}), 500

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
            "conversation_memory": True,
            "intent_recognition": True,
            "context_awareness": True,
            "web_search": True,
            "multiple_sources": True,
            "authentication": "disabled (temporary)",
            "rate_limiting": True
        },
        "endpoints": {
            "test": "/test",
            "chat": "/chat",
            "knowledge": "/knowledge",
            "conversation_context": "/conversation/context",
            "conversation_clear": "/conversation/clear",
            "search": "/search",
            "search_general": "/search/general",
            "search_knowledge": "/search/knowledge",
            "sources": "/sources",
            "health": "/"
        },
        "note": "Authentication is temporarily disabled for testing. Will be re-enabled once Microsoft Graph API integration is working."
    })

# For Vercel serverless deployment
app.debug = False

# Export the Flask app for Vercel
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9000)
