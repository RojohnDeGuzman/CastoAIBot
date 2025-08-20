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
# Removed heavy dependencies for Vercel deployment
# from duckduckgo_search import DDGS
# from newspaper import Article

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

# Debug mode toggle - set to True to see debug info in terminal
DEBUG_MODE = True  # Change to False to disable terminal debug output

# Local debug echo - sends debug info back to client for local terminal display
LOCAL_DEBUG_ECHO = True  # Set to True to echo debug info to client

# Define the website sources
WEBSITE_SOURCE = "https://www.travelpress.com/"
CASTO_TRAVEL_WEBSITE = "https://www.castotravel.ph/"
CASTO_WEBSITE = "https://www.casto.com.ph/"
CASTO_ABOUT_US = "https://www.casto.com.ph/about-us"

# Additional Casto-related sources for enhanced learning
CASTO_SOURCES = [
    "https://www.casto.com.ph/",
    "https://www.casto.com.ph/",
    "https://www.facebook.com/castotravelphilippines",
    "https://www.linkedin.com/company/casto-travel-philippines",
    "https://www.instagram.com/castotravelph/",
    "https://www.youtube.com/@castotravelphilippines"
]

# Cache for website data (in-memory for serverless)
website_cache = {}
CACHE_DURATION = 300  # 5 minutes

# Conversation memory and context management (enhanced for persistent focus)
conversation_memory = {}
CONVERSATION_TIMEOUT = 3600  # Increased to 1 hour for better persistence
MAX_CONVERSATION_HISTORY = 15  # Increased to 15 exchanges for better context
ACTIVE_ISSUE_TIMEOUT = 7200  # 2 hours for active issues to remain open

# HTTP session for connection pooling
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
})

@lru_cache(maxsize=100)
def get_cached_knowledge():
    """Cache knowledge retrieval - load from embedded knowledge base for Vercel hosting"""
    # For Vercel, return embedded knowledge base since we can't access local files
    embedded_knowledge = [
        {
            "question": "How do I reset my password?",
            "answer": "To reset your password, go to the login page and click on 'Forgot Password'. Follow the instructions sent to your email."
        },
        {
            "question": "Why is my internet not working?",
            "answer": "Check if the network cable is properly connected or restart your router. You can also run the Windows Network Troubleshooter."
        },
        {
            "question": "How do I connect to the VPN?",
            "answer": "Use the company VPN client and enter your credentials. Make sure you are connected to the internet before attempting to connect."
        },
        {
            "question": "What is Casto Travel Philippines?",
            "answer": "Casto Travel Philippines is a leading travel and tourism company in the Philippines, part of the Casto Group. They offer domestic and international travel packages, hotel bookings, tour packages, travel insurance, corporate travel management, and group travel arrangements."
        },
        {
            "question": "What services does Casto Travel offer?",
            "answer": "Casto Travel Philippines offers comprehensive travel services including domestic and international travel packages, hotel reservations, tour packages and excursions, travel insurance and documentation, corporate travel management, and group travel arrangements for both business and leisure travelers."
        },
        {
            "question": "How can I contact Casto Travel Philippines?",
            "answer": "You can contact Casto Travel Philippines through their official website at https://www.casto.com.ph/ or visit their office locations. They provide professional travel consultation and booking services for all your travel needs in the Philippines and abroad."
        },
        {
            "question": "Who is the CEO of Casto Travel Philippines?",
            "answer": "The current CEO of Casto Travel Philippines is Marc Casto. Maryles Casto is the founder, and Marc Casto continues the family legacy of excellence in the travel industry. The company is now part of the unified CASTO brand, combining Casto Travel Philippines and MVC Solutions."
        },
        {
            "question": "What is Casto Travel's company history?",
            "answer": "Casto Travel Philippines has been making its mark in the travel industry for more than 35 years. It's a Filipino-owned business that began in California's Silicon Valley and now has two offices in Metro Manila, plus expansion to Bacolod City. The company combines Casto Travel Philippines and MVC Solutions under the unified CASTO brand."
        },
        {
            "question": "What are Casto Travel's accreditations?",
            "answer": "Casto Travel Philippines holds multiple prestigious accreditations including ISO 27001:2013 certification, IATA accreditation, ASTA membership, PCI-DSS certification, and is an accredited member of PTAA, PIATA, and PHILTOA - making it one of the most certified travel agencies in the Philippines."
        },
        {
            "question": "Who is Ricardo Dickie Reyes?",
            "answer": "I don't have information about Ricardo 'Dickie' Reyes in relation to Casto Travel Philippines. The founder of Casto Travel Philippines is Maryles Casto, and the current CEO is Marc Casto."
        },
        {
            "question": "Who is the current CEO of Casto Travel?",
            "answer": "The current CEO of Casto Travel Philippines is Marc Casto. He continues the family legacy of excellence in the travel industry, building upon the foundation established by founder Maryles Casto. The company is now part of the unified CASTO brand, combining Casto Travel Philippines and MVC Solutions."
        },
        {
            "question": "Who is Marc Casto?",
            "answer": "Marc Casto is the current CEO of Casto Travel Philippines. He is part of the Casto family legacy, continuing the tradition of excellence established by founder Maryles Casto. Under Marc Casto's leadership, the company continues to provide comprehensive travel services and maintain its position as one of the leading travel agencies in the Philippines."
        },
        {
            "question": "Who is Michael S. Pastrana?",
            "answer": "I don't have information about Michael S. Pastrana in relation to Casto Travel Philippines. The current CEO of Casto Travel Philippines is Marc Casto, and the founder is Maryles Casto."
        },
        {
            "question": "Is Michael S. Pastrana the CEO of Casto Travel?",
            "answer": "No, Michael S. Pastrana is not the CEO of Casto Travel Philippines. The current CEO is Marc Casto, and the founder is Maryles Casto."
        },
        {
            "question": "Who is Maryles Casto?",
            "answer": "MARYLES CASTO - Founder & Chairperson. After 40+ years of traversing through the travel industry's ebbs and flows; and changes in Silicon Valley, Maryles sold Casto Travel to Flight Centre, one of the world's largest travel companies. She continues to own Casto Travel Philippines, providing knowledge, insight, and inspiration in several capacities, including client interactions, organizing exclusive journeys, and steering the company with her leadership and strategic vision."
        },
        {
            "question": "Tell me about Maryles Casto",
            "answer": "MARYLES CASTO - Founder & Chairperson. After 40+ years of traversing through the travel industry's ebbs and flows; and changes in Silicon Valley, Maryles sold Casto Travel to Flight Centre, one of the world's largest travel companies. She continues to own Casto Travel Philippines, providing knowledge, insight, and inspiration in several capacities, including client interactions, organizing exclusive journeys, and steering the company with her leadership and strategic vision."
        },
        {
            "question": "Who is the founder of Casto Travel?",
            "answer": "MARYLES CASTO is the Founder & Chairperson of Casto Travel Philippines. After 40+ years of traversing through the travel industry's ebbs and flows; and changes in Silicon Valley, Maryles sold Casto Travel to Flight Centre, one of the world's largest travel companies. She continues to own Casto Travel Philippines, providing knowledge, insight, and inspiration in several capacities, including client interactions, organizing exclusive journeys, and steering the company with her leadership and strategic vision."
        },
        {
            "question": "Tell me about Marc Casto",
            "answer": "MARC CASTO is the CEO of Casto Travel Philippines (CTP) as well as its holding company MVC Solutions (MVC). Marc is assiduously focused upon the strategy, execution, and operations of the company all while ensuring it is in accord with its financial, ethical, and social requirements. He is highly driven and consistently intent upon exceeding growth goals while investing in innovative solutions to propel the industry forwards. As one of the founding members of CTP and MVC, Marc was critical in the formation of the organizations and propelling its early success."
        },
        {
            "question": "Who is Elaine Randrup?",
            "answer": "ELAINE RANDRUP is the Vice President of Operations at Casto Travel Philippines. Elaine, VP of Operations, leads our Travel and Fulfillment Center operations. Educated in Business Administration, Elaine found her passion for the travel industry beginning as a Travel Counselor for Peoplesupport and American Express Travel Singapore. Her move back to the Philippines brings Casto years of experience as a travel expert as well as client services and operations management."
        },
        {
            "question": "Tell me about Elaine Randrup",
            "answer": "ELAINE RANDRUP is the Vice President of Operations at Casto Travel Philippines. Elaine, VP of Operations, leads our Travel and Fulfillment Center operations. Educated in Business Administration, Elaine found her passion for the travel industry beginning as a Travel Counselor for Peoplesupport and American Express Travel Singapore. Her move back to the Philippines brings Casto years of experience as a travel expert as well as client services and operations management."
        },
        {
            "question": "Who is Alwin Benedicto?",
            "answer": "ALWIN BENEDICTO, CPA is the Chief Financial Officer of Casto Travel Philippines. A Certified Public Accountant, duly accredited Public Accounting Practitioner by the Philippine Board of Accountancy, and accredited Tax Practitioner by the Bureau of Internal Revenue. Alwin brings more than 20 years of experience in the fields of Taxation, Financial Audits, Planning and Analysis, and different areas of Finance. Prior to joining Casto, he worked in leadership roles for different industries, including BPO/KPO (Innodata, Inc), FinTech (C88 Financial Technologies, Ltd), Supply Chain and Logistics (Ayala Corporation Logistics Group). He oversees Financial Reporting, Financial Planning and Operations, Taxation and Statutory Compliances for Casto."
        },
        {
            "question": "Tell me about Alwin Benedicto",
            "answer": "ALWIN BENEDICTO, CPA is the Chief Financial Officer of Casto Travel Philippines. A Certified Public Accountant, duly accredited Public Accounting Practitioner by the Philippine Board of Accountancy, and accredited Tax Practitioner by the Bureau of Internal Revenue. Alwin brings more than 20 years of experience in the fields of Taxation, Financial Audits, Planning and Analysis, and different areas of Finance. Prior to joining Casto, he worked in leadership roles for different industries, including BPO/KPO (Innodata, Inc), FinTech (C88 Financial Technologies, Ltd), Supply Chain and Logistics (Ayala Corporation Logistics Group). He oversees Financial Reporting, Financial Planning and Operations, Taxation and Statutory Compliances for Casto."
        },
        {
            "question": "Who is George Anzures?",
            "answer": "GEORGE ANZURES is the IT Director of Casto Travel Philippines."
        },
        {
            "question": "Tell me about George Anzures",
            "answer": "GEORGE ANZURES is the IT Director of Casto Travel Philippines."
        },
        {
            "question": "Who is Ma. Berdandina Galvez?",
            "answer": "MA. BERDANDINA GALVEZ is the HR Director of Casto Travel Philippines."
        },
        {
            "question": "Tell me about Ma. Berdandina Galvez",
            "answer": "MA. BERDANDINA GALVEZ is the HR Director of Casto Travel Philippines."
        },
        {
            "question": "Who are the key leaders at Casto Travel Philippines?",
            "answer": "The key leadership team at Casto Travel Philippines includes: MARYLES CASTO (Founder & Chairperson), MARC CASTO (CEO), ELAINE RANDRUP (Vice President of Operations), ALWIN BENEDICTO, CPA (Chief Financial Officer), GEORGE ANZURES (IT Director), and MA. BERDANDINA GALVEZ (HR Director). Each brings extensive experience and expertise to their respective roles, contributing to the company's continued success in the travel industry."
        },
        {
            "question": "What is the leadership structure at Casto Travel?",
            "answer": "The leadership structure at Casto Travel Philippines includes: MARYLES CASTO as Founder & Chairperson, MARC CASTO as CEO, ELAINE RANDRUP as Vice President of Operations, ALWIN BENEDICTO, CPA as Chief Financial Officer, GEORGE ANZURES as IT Director, and MA. BERDANDINA GALVEZ as HR Director. This team provides strategic direction and operational excellence across all aspects of the company."
        },
        {
            "question": "Who is Luz Bagtas?",
            "answer": "LUZ BAGTAS is the President and Chief Operating Officer (COO) of Casto Travel Philippines. One of the longest serving members of Casto Travel Philippines, Luz is a CPA who served in various capacities in accounting and management information systems (MIS) at Casto U.S. before being transferred to the Philippines. Her in-depth knowledge of the U.S. travel agency accounting systems is unrivaled and gives her incredible insights into today's clients' accounting services."
        },
        {
            "question": "Tell me about Luz Bagtas",
            "answer": "LUZ BAGTAS is the President and Chief Operating Officer (COO) of Casto Travel Philippines. One of the longest serving members of Casto Travel Philippines, Luz is a CPA who served in various capacities in accounting and management information systems (MIS) at Casto U.S. before being transferred to the Philippines. Her in-depth knowledge of the U.S. travel agency accounting systems is unrivaled and gives her incredible insights into today's clients' accounting services."
        },
        {
            "question": "Who is Berlin Torres?",
            "answer": "BERLIN TORRES is the HR Director of Casto Travel Philippines. Berlin holds a bachelor's degree in Psychology and spent the last twenty years at BPO and technology firms such as Concentrix, Pearson Management, and Human Edge Software Technology. He is very well versed in recruitment, employee relations, employee engagement, mobility, payroll, health services, and HR operations."
        },
        {
            "question": "Tell me about Berlin Torres",
            "answer": "BERLIN TORRES is the HR Director of Casto Travel Philippines. Berlin holds a bachelor's degree in Psychology and spent the last twenty years at BPO and technology firms such as Concentrix, Pearson Management, and Human Edge Software Technology. He is very well versed in recruitment, employee relations, employee engagement, mobility, payroll, health services, and HR operations."
        },
        {
            "question": "Who is Voltaire Villaflores?",
            "answer": "VOLTAIRE 'VICTOR' VILLAFLORES is the Director of Casto University at Casto Travel Philippines. Victor started working in the BPO in 2005 with a travel account and has loved it ever since. He joined Casto Travel Philippines as a travel consultant in 2012. Educated in computer programming, he advanced his knowledge and skillset by joining the Systems Department, enhancing and creating GDS scripts, back-end setup, and programming to provide efficiency to agents, accounting, and clients. He then joined the training team where he created and re-designed training curricula. Being in the industry for over 17 years in different roles, he is currently the Director of Casto University where he aims to produce great talents for the travel industry."
        },
        {
            "question": "Tell me about Victor Villaflores",
            "answer": "VOLTAIRE 'VICTOR' VILLAFLORES is the Director of Casto University at Casto Travel Philippines. Victor started working in the BPO in 2005 with a travel account and has loved it ever since. He joined Casto Travel Philippines as a travel consultant in 2012. Educated in computer programming, he advanced his knowledge and skillset by joining the Systems Department, enhancing and creating GDS scripts, back-end setup, and programming to provide efficiency to agents, accounting, and clients. He then joined the training team where he created and re-designed training curricula. Being in the industry for over 17 years in different roles, he is currently the Director of Casto University where he aims to produce great talents for the travel industry."
        },
        {
            "question": "Who is the COO of Casto Travel?",
            "answer": "LUZ BAGTAS is the President and Chief Operating Officer (COO) of Casto Travel Philippines. One of the longest serving members of Casto Travel Philippines, Luz is a CPA who served in various capacities in accounting and management information systems (MIS) at Casto U.S. before being transferred to the Philippines. Her in-depth knowledge of the U.S. travel agency accounting systems is unrivaled and gives her incredible insights into today's clients' accounting services."
        },
        {
            "question": "Who is the HR Director of Casto Travel?",
            "answer": "BERLIN TORRES is the HR Director of Casto Travel Philippines. Berlin holds a bachelor's degree in Psychology and spent the last twenty years at BPO and technology firms such as Concentrix, Pearson Management, and Human Edge Software Technology. He is very well versed in recruitment, employee relations, employee engagement, mobility, payroll, health services, and HR operations."
        },
        {
            "question": "Who is the Director of Casto University?",
            "answer": "VOLTAIRE 'VICTOR' VILLAFLORES is the Director of Casto University at Casto Travel Philippines. Victor started working in the BPO in 2005 with a travel account and has loved it ever since. He joined Casto Travel Philippines as a travel consultant in 2012. Educated in computer programming, he advanced his knowledge and skillset by joining the Systems Department, enhancing and creating GDS scripts, back-end setup, and programming to provide efficiency to agents, accounting, and clients. He then joined the training team where he created and re-designed training curricula. Being in the industry for over 17 years in different roles, he is currently the Director of Casto University where he aims to produce great talents for the travel industry."
        },
        {
            "question": "Who are the key leaders at Casto Travel Philippines?",
            "answer": "The key leadership team at Casto Travel Philippines includes: MARYLES CASTO (Founder & Chairperson), MARC CASTO (CEO), LUZ BAGTAS (President and COO), ELAINE RANDRUP (Vice President of Operations), ALWIN BENEDICTO, CPA (Chief Financial Officer), BERLIN TORRES (HR Director), GEORGE ANZURES (IT Director), MA. BERDANDINA GALVEZ (HR Director), and VOLTAIRE 'VICTOR' VILLAFLORES (Director of Casto University). Each brings extensive experience and expertise to their respective roles, contributing to the company's continued success in the travel industry."
        },
        {
            "question": "What is the leadership structure at Casto Travel?",
            "answer": "The leadership structure at Casto Travel Philippines includes: MARYLES CASTO as Founder & Chairperson, MARC CASTO as CEO, LUZ BAGTAS as President and COO, ELAINE RANDRUP as Vice President of Operations, ALWIN BENEDICTO, CPA as Chief Financial Officer, BERLIN TORRES as HR Director, GEORGE ANZURES as IT Director, MA. BERDANDINA GALVEZ as HR Director, and VOLTAIRE 'VICTOR' VILLAFLORES as Director of Casto University. This team provides strategic direction and operational excellence across all aspects of the company."
        },
        {
            "question": "What are Casto Travel's company values?",
            "answer": "Casto Travel Philippines operates with the following core values: Own It (owning and resolving complaints), One Team (success contingent on everyone's success), Exceptional Service (delivering exceptional experiences), Continuous Improvement (striving to improve), Celebrate Success (recognizing achievements), Clients for Life (long-term commitment), Ethics in Travel (operating ethically), Creative Solutions (finding solutions to problems), Casto Professional (maintaining professionalism), and Kindness (leaving more kindness in the world)."
        },
        {
            "question": "What is Casto University?",
            "answer": "Casto University is Casto Travel Philippines' training and development division, led by Director Voltaire 'Victor' Villaflores. It aims to produce great talents for the travel industry through comprehensive training curricula, GDS scripts development, back-end setup, and programming. The university focuses on streamlining processes and timelines while providing efficiency to agents, accounting, and clients through enhanced training programs."
        }
    ]
    return embedded_knowledge

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

        if query:
            # Search across all text, not just <p>
            page_text = soup.get_text().lower()
            q = query.lower()
            if q in page_text:
                relevant = []

                # Headings with following siblings
                for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                    if q in h.get_text().lower():
                        heading_text = h.get_text().strip()
                        sib = h.find_next_sibling()
                        if sib:
                            relevant.append(f"{heading_text}: {sib.get_text().strip()}")
                        else:
                            relevant.append(heading_text)

                # Paragraphs
                for p in soup.find_all('p'):
                    pt = p.get_text().strip()
                    if q in pt.lower():
                        relevant.append(pt)

                # Other containers
                for div in soup.find_all('div'):
                    dt = div.get_text().strip()
                    if q in dt.lower() and len(dt) > 20:
                        relevant.append(dt)

                if relevant:
                    content = "\n\n".join(relevant[:3])
                    result = f"Title: {title}\nContent: {content}"
                    website_cache[cache_key] = (result, current_time)
                    return result

        # Default when not found
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
    
    logging.info(f"Creating direct Casto response for: {user_input}")
    logging.info(f"Knowledge entries available: {len(knowledge_entries) if knowledge_entries else 0}")
    
    # Check for incorrect CEO claims first
    is_incorrect_ceo, incorrect_name = check_incorrect_ceo_claims(user_input)
    if is_incorrect_ceo:
        response_text = f"""As CASI, I can provide you with the correct information about Casto Travel Philippines leadership.

Based on our knowledge base:
• **Founder**: Maryles Casto
• **Current CEO**: Marc Casto

I don't have information about {incorrect_name.title()} in relation to Casto Travel Philippines."""
        
        return make_links_clickable(response_text)
    
    # Check for CEO/founder questions first
    if any(word in user_input_lower for word in ["ceo", "founder", "who", "leader"]):
        if "casto" in user_input_lower:
            # Special handling for "who is maryles casto" questions (including variations like "maryle")
            if any(name in user_input_lower for name in ["maryles", "maryle", "maryl"]):
                # Use knowledge base instead of hardcoded response
                knowledge_response = check_knowledge_base_for_person(user_input, knowledge_entries)
                if knowledge_response:
                    return f"""As CASI, {knowledge_response}"""
                else:
                    return """As CASI, I can tell you that based on my knowledge base, Maryles Casto is the founder of Casto Travel Philippines. She started as a flight attendant and went on to own one of the top travel companies in Silicon Valley. 

Maryles Casto established the foundation for what would become Casto Travel Philippines, a leading travel and tourism company in the Philippines. The company has been making its mark in the travel industry for more than 35 years.

Today, the company is part of the unified CASTO brand, combining Casto Travel Philippines and MVC Solutions, with Marc Casto serving as the current CEO, continuing the family legacy of excellence in the travel industry."""
            
            # Use knowledge base for other CEO/founder questions
            knowledge_response = check_knowledge_base_for_person(user_input, knowledge_entries)
            if knowledge_response:
                return f"""As CASI, {knowledge_response}"""
            else:
                response_text = """As CASI, I can tell you that based on my knowledge base, Casto Travel Philippines was founded by Maryles Casto, who started as a flight attendant and went on to own one of the top travel companies in Silicon Valley. 

The current CEO is Marc Casto, who continues the family legacy of excellence in the travel industry. The company is now part of the unified CASTO brand, combining Casto Travel Philippines and MVC Solutions.

For the most current leadership information, please contact Casto Travel Philippines directly at https://www.casto.com.ph/"""
                
                return make_links_clickable(response_text)
    
    # Check for company information
    if any(word in user_input_lower for word in ["what", "company", "business", "services"]):
        if "casto" in user_input_lower:
            # Use knowledge base for company questions
            knowledge_response = check_knowledge_base_for_person(user_input, knowledge_entries)
            if knowledge_response:
                return f"""As CASI, {knowledge_response}"""
            else:
                response_text = """As CASI (Casto Assistance and Support Intelligence), I can tell you that based on my knowledge base, Casto Travel Philippines is a leading travel and tourism company in the Philippines, part of the Casto Group. 

The company has been making its mark in the travel industry for more than 35 years. It's a Filipino-owned business that began in California's Silicon Valley and now has two offices in Metro Manila, plus expansion to Bacolod City.

Services include:
• Domestic and international travel packages
• Hotel bookings and reservations
• Tour packages and excursions
• Travel insurance and documentation
• Corporate travel management
• Group travel arrangements

For more detailed information, visit their official website: https://www.casto.com.ph/"""
                
                return make_links_clickable(response_text)
    
    # Check for history questions
    if any(word in user_input_lower for word in ["history", "background", "when", "started"]):
        if "casto" in user_input_lower:
            # Use knowledge base for history questions
            knowledge_response = check_knowledge_base_for_person(user_input, knowledge_entries)
            if knowledge_response:
                return f"""As CASI, {knowledge_response}"""
            else:
                return """Based on my knowledge base, Casto Travel Philippines has been making its mark in the travel industry for more than 35 years. 

It's a Filipino-owned business that began in California's Silicon Valley and now has two offices in the heart of Metro Manila. The company combines Casto Travel Philippines and MVC Solutions under the unified CASTO brand.

The company has expanded to bring highly skilled professionals to Bacolod City, known as the City of Smiles."""
    
    # Check for accreditation questions
    if any(word in user_input_lower for word in ["accreditation", "certification", "certified", "member"]):
        if "casto" in user_input_lower:
            # Use knowledge base for accreditation questions
            knowledge_response = check_knowledge_base_for_person(user_input, knowledge_entries)
            if knowledge_response:
                return f"""As CASI, {knowledge_response}"""
            else:
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
        # Use knowledge base for general Casto questions
        knowledge_response = check_knowledge_base_for_person(user_input, knowledge_entries)
        if knowledge_response:
            return f"""As CASI, {knowledge_response}"""
        else:
            response_text = """Based on my knowledge base, Casto Travel Philippines is a leading travel and tourism company in the Philippines, part of the Casto Group. 

The company was founded by Maryles Casto and has been serving the travel industry for more than 35 years. They offer comprehensive travel services including domestic and international packages, hotel bookings, tours, travel insurance, and corporate travel management.

For the most current and detailed information, please visit their official website: https://www.casto.com.ph/"""
            
            return make_links_clickable(response_text)
    
    return None  # Let the AI model handle non-Casto questions

def manage_conversation_context(user_id, user_input, response):
    """Enhanced conversation context and memory management for better follow-up understanding."""
    current_time = time.time()
    
    # Initialize or get existing conversation
    if user_id not in conversation_memory:
        conversation_memory[user_id] = {
            'history': [],
            'last_updated': current_time,
            'topics': set(),
            'intent': None,
            'current_focus': None,
            'current_subject': None,  # Track current subject being discussed
            'subject_start_time': None,  # When current subject started
            'resolution_status': 'ongoing',  # ongoing, resolved, abandoned
            'conversation_depth': 0,
            'related_questions': [],
            'user_preferences': set(),
            'context_chain': []  # Chain of related exchanges
        }
    
    conv = conversation_memory[user_id]
    
    # Clean old conversations but preserve active subjects
    if current_time - conv['last_updated'] > CONVERSATION_TIMEOUT:
        # Only clear if no active subject or subject is very old
        if not conv.get('current_subject') or \
           (conv.get('subject_start_time') and 
            current_time - conv['subject_start_time'] > ACTIVE_ISSUE_TIMEOUT):
            conv['history'] = []
            conv['topics'] = set()
            conv['intent'] = None
            conv['current_focus'] = None
            conv['current_subject'] = None
            conv['subject_start_time'] = None
            conv['resolution_status'] = 'ongoing'
            conv['conversation_depth'] = 0
            conv['related_questions'] = []
            conv['user_preferences'] = set()
            conv['context_chain'] = []
    
    # Extract current subject from input
    current_subject = extract_subject_from_input(user_input, conv)
    
    # Update subject tracking
    if current_subject != conv.get('current_subject'):
        # New subject started
        conv['current_subject'] = current_subject
        conv['subject_start_time'] = current_time
        conv['resolution_status'] = 'ongoing'
        conv['context_chain'] = []
    else:
        # Same subject continues
        conv['context_chain'].append({
            'input': user_input,
            'response': response,
            'timestamp': current_time
        })
    
    # Check if issue is resolved
    if detect_conversation_resolution(user_input, response, conv) == "resolved":
        conv['resolution_status'] = 'resolved'
    
    # Add current exchange to history with enhanced metadata
    exchange_data = {
        'user_input': user_input,
        'response': response,
        'timestamp': current_time,
        'intent': analyze_exchange_intent(user_input),
        'topics': extract_topics_from_text(user_input),
        'entities': extract_entities_from_text(user_input),
        'subject': current_subject,
        'resolution_status': conv['resolution_status']
    }
    
    conv['history'].append(exchange_data)
    
    # Keep more history for better context (increased to 15)
    if len(conv['history']) > MAX_CONVERSATION_HISTORY:
        conv['history'] = conv['history'][-MAX_CONVERSATION_HISTORY:]
    
    # Update last activity
    conv['last_updated'] = current_time
    
    # Enhanced topic tracking
    new_topics = extract_topics_from_text(user_input)
    conv['topics'].update(new_topics)
    
    # Track conversation focus and depth
    if len(conv['history']) > 1:
        conv['conversation_depth'] = len(conv['history'])
        conv['current_focus'] = determine_conversation_focus(conv['history'])
    
    # Track related questions for better follow-up suggestions
    if is_follow_up_question(user_input, conv['history']):
        conv['related_questions'].append(user_input)
        if len(conv['related_questions']) > 5:
            conv['related_questions'] = conv['related_questions'][-5:]
    
    # Extract user preferences and interests
    user_prefs = extract_user_preferences(user_input, response)
    conv['user_preferences'].update(user_prefs)
    
    return conv

def analyze_exchange_intent(user_input):
    """Analyze the intent of a single exchange."""
    user_input_lower = user_input.lower()
    
    if any(word in user_input_lower for word in ["who", "what", "when", "where", "why", "how"]):
        return "question"
    elif any(word in user_input_lower for word in ["thank", "thanks", "appreciate"]):
        return "gratitude"
    elif any(word in user_input_lower for word in ["yes", "no", "okay", "ok", "sure"]):
        return "confirmation"
    elif any(word in user_input_lower for word in ["more", "tell me more", "explain", "elaborate"]):
        return "elaboration_request"
    else:
        return "statement"

def extract_topics_from_text(text):
    """Extract relevant topics from text."""
    text_lower = text.lower()
    topics = set()
    
    # Casto-related topics
    casto_topics = ["casto", "travel", "philippines", "ceo", "founder", "leadership", 
                    "services", "company", "business", "tourism", "agency"]
    
    # Personnel topics
    personnel_topics = ["maryles casto", "marc casto", "elaine randrup", 
                       "alwin benedicto", "george anzures", "berdandina galvez"]
    
    # Service topics
    service_topics = ["booking", "hotel", "flight", "tour", "package", "insurance", 
                     "corporate", "group", "domestic", "international"]
    
    # IT troubleshooting topics
    it_topics = ["internet", "slow", "connection", "vpn", "password", "computer", 
                "troubleshoot", "problem", "issue", "help", "router", "network", 
                "speed", "fiber", "cable", "dsl", "wireless", "wifi"]
    
    # Check for topics in text
    for topic in casto_topics + personnel_topics + service_topics + it_topics:
        if topic in text_lower:
            topics.add(topic)
    
    return topics

def extract_entities_from_text(text):
    """Extract named entities and key information from text."""
    text_lower = text.lower()
    entities = set()
    
    # Check for company names
    if "casto" in text_lower:
        entities.add("Casto Travel Philippines")
    
    # Check for personnel names
    personnel = ["maryles casto", "marc casto", "elaine randrup", 
                "alwin benedicto", "george anzures", "berdandina galvez"]
    
    for person in personnel:
        if person in text_lower:
            entities.add(person.title())
    
    # Check for locations
    locations = ["philippines", "manila", "bacolod", "silicon valley", "california"]
    for location in locations:
        if location in text_lower:
            entities.add(location.title())
    
    return entities

def extract_subject_from_input(user_input, conversation_context):
    """Extract the main subject/topic from user input."""
    # If we have an ongoing subject, check if this is related
    if conversation_context and conversation_context.get('current_subject'):
        if should_continue_subject(user_input, conversation_context):
            return conversation_context['current_subject']
    
    # Extract new subject from input
    user_input_lower = user_input.lower()
    
    # Travel-related subjects
    travel_subjects = [
        "travel planning", "vacation", "trip", "booking", "hotel", "flight",
        "tour package", "travel insurance", "visa", "passport", "destination",
        "itinerary", "budget", "accommodation", "transportation"
    ]
    
    # Casto-related subjects
    casto_subjects = [
        "casto travel", "company", "services", "personnel", "leadership",
        "about casto", "casto history", "casto team", "casto offerings"
    ]
    
    # Check for specific subjects
    for subject in travel_subjects + casto_subjects:
        if subject in user_input_lower:
            return subject
    
    # Check for question words that indicate a new subject
    question_words = ["what", "how", "when", "where", "why", "who"]
    if any(word in user_input_lower for word in question_words):
        # Extract the main topic after the question word
        words = user_input_lower.split()
        for i, word in enumerate(words):
            if word in question_words and i + 1 < len(words):
                return " ".join(words[i+1:i+3])  # Take next 2 words as subject
    
    return "general inquiry"

def determine_conversation_focus(history):
    """Determine the main focus of the conversation based on history."""
    if not history:
        return None
    
    # Count topic frequencies
    topic_counts = {}
    for exchange in history:
        for topic in exchange.get('topics', []):
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
    
    # Return the most frequent topic
    if topic_counts:
        return max(topic_counts, key=topic_counts.get)
    return None

def is_follow_up_question(user_input, history):
    """Determine if the current input is a follow-up question."""
    if not history:
        return False
    
    user_input_lower = user_input.lower()
    
    # Follow-up indicators
    follow_up_indicators = [
        "and", "also", "what about", "how about", "tell me more", "explain",
        "elaborate", "can you", "could you", "would you", "more details",
        "in addition", "furthermore", "moreover", "besides", "additionally"
    ]
    
    # Check for follow-up indicators
    if any(indicator in user_input_lower for indicator in follow_up_indicators):
        return True
    
    # Check for pronouns that refer to previous context
    pronouns = ["it", "this", "that", "they", "them", "their", "the company", 
                "the service", "the person", "he", "she", "his", "her"]
    
    if any(pronoun in user_input_lower for pronoun in pronouns):
        return True
    
    # Check if input is very short (likely a follow-up)
    if len(user_input.split()) <= 3:
        return True
    
    return False

def extract_user_preferences(user_input, response):
    """Extract user preferences and interests from the exchange."""
    user_input_lower = user_input.lower()
    preferences = set()
    
    # Travel preferences
    if any(word in user_input_lower for word in ["domestic", "local", "philippines"]):
        preferences.add("domestic_travel")
    if any(word in user_input_lower for word in ["international", "abroad", "overseas"]):
        preferences.add("international_travel")
    if any(word in user_input_lower for word in ["business", "corporate", "work"]):
        preferences.add("business_travel")
    if any(word in user_input_lower for word in ["leisure", "vacation", "holiday", "tour"]):
        preferences.add("leisure_travel")
    
    # Information depth preferences
    if any(word in user_input_lower for word in ["detailed", "comprehensive", "full", "complete"]):
        preferences.add("detailed_info")
    if any(word in user_input_lower for word in ["brief", "summary", "overview", "quick"]):
        preferences.add("brief_info")
    
    return preferences

def generate_follow_up_suggestions(user_input, conversation_context, current_response):
    """Generate contextual follow-up suggestions based on conversation context."""
    if not conversation_context:
        return []
    
    suggestions = []
    current_focus = conversation_context.get('current_focus', 'general')
    recent_topics = conversation_context.get('topics', set())
    user_preferences = conversation_context.get('user_preferences', set())
    current_subject = conversation_context.get('current_subject', 'general inquiry')
    resolution_status = conversation_context.get('resolution_status', 'ongoing')
    
    # Subject-specific follow-up suggestions
    if current_subject and current_subject != 'general inquiry':
        if 'travel planning' in current_subject.lower():
            if resolution_status == 'ongoing':
                suggestions.extend([
                    "What's your budget for this trip?",
                    "How many people will be traveling?",
                    "Do you have any specific dates in mind?",
                    "What type of accommodation do you prefer?"
                ])
            else:
                suggestions.extend([
                    "Would you like to start planning another trip?",
                    "Can I help you with travel insurance for your upcoming trip?",
                    "Do you need help with visa applications?"
                ])
        
        elif 'hotel' in current_subject.lower():
            if resolution_status == 'ongoing':
                suggestions.extend([
                    "What's your preferred hotel category (budget, mid-range, luxury)?",
                    "Do you need airport transfer services?",
                    "Would you like to see nearby attractions?",
                    "What amenities are important to you?"
                ])
        
        elif 'flight' in current_subject.lower():
            if resolution_status == 'ongoing':
                suggestions.extend([
                    "What's your preferred airline?",
                    "Do you need flexible booking options?",
                    "Would you like to add travel insurance?",
                    "Do you need help with seat selection?"
                ])
        
        elif 'casto travel' in current_subject.lower():
            if resolution_status == 'ongoing':
                suggestions.extend([
                    "What specific services are you interested in?",
                    "Would you like to know about Casto's accreditations?",
                    "Can I tell you about Casto's leadership team?",
                    "What makes Casto Travel different from competitors?"
                ])
    
    # Casto Travel Philippines focused suggestions
    if 'casto' in recent_topics or 'travel' in recent_topics:
        if 'leadership' in recent_topics or 'ceo' in recent_topics:
            suggestions.extend([
                "What services does Casto Travel Philippines offer?",
                "Can you tell me more about Casto's history and background?",
                "What are Casto Travel's accreditations and certifications?"
            ])
        
        if 'services' in recent_topics:
            suggestions.extend([
                "Who are the key leaders at Casto Travel Philippines?",
                "What makes Casto Travel different from other agencies?",
                "Can you provide contact information for Casto Travel?"
            ])
        
        if 'personnel' in recent_topics or any(person in str(recent_topics) for person in ['maryles', 'marc', 'elaine', 'alwin', 'george', 'berdandina']):
            suggestions.extend([
                "What is the organizational structure of Casto Travel?",
                "Can you tell me about Casto's company culture and values?",
                "What are Casto Travel's future plans and expansion?"
            ])
    
    # Travel service focused suggestions
    if 'travel' in recent_topics and 'casto' not in recent_topics:
        suggestions.extend([
            "What are the best travel destinations in the Philippines?",
            "Can you help with travel planning and booking information?",
            "What travel insurance options are available?"
        ])
    
    # General knowledge suggestions
    if 'philippines' in recent_topics:
        suggestions.extend([
            "What are the visa requirements for visiting the Philippines?",
            "Can you tell me about Philippine culture and traditions?",
            "What are the best times to visit the Philippines?"
        ])
    
    # Personalized suggestions based on user preferences
    if 'domestic_travel' in user_preferences:
        suggestions.append("What are the top domestic travel packages available?")
    
    if 'international_travel' in user_preferences:
        suggestions.append("What international destinations does Casto Travel specialize in?")
    
    if 'business_travel' in user_preferences:
        suggestions.append("What corporate travel management services are offered?")
    
    # Resolution-based suggestions
    if resolution_status == 'resolved':
        suggestions.extend([
            "Is there anything else I can help you with?",
            "Would you like to explore other Casto Travel services?",
            "Can I assist you with a different travel inquiry?"
        ])
    elif resolution_status == 'ongoing':
        suggestions.extend([
            "Do you need more details about this?",
            "Would you like me to clarify anything?",
            "Is there a specific aspect you'd like me to focus on?"
        ])
    
    # Default suggestions if no specific context
    if not suggestions:
        suggestions = [
            "What services does Casto Travel Philippines offer?",
            "Can you tell me about Casto's leadership team?",
            "What makes Casto Travel unique in the industry?"
        ]
    
    # Limit to 3-4 suggestions and ensure uniqueness
    unique_suggestions = list(dict.fromkeys(suggestions))[:4]
    
    return unique_suggestions

def understand_user_intent(user_input, conversation_context):
    """Enhanced user intent analysis with conversation context awareness."""
    user_input_lower = user_input.lower()
    
    # Check for Casto-related questions FIRST (highest priority)
    casto_keywords = [
        "casto", "marc casto", "maryles casto", "ceo", "founder", "leader", 
        "casto travel", "casto philippines", "casto group", "casto travel philippines"
    ]
    
    # Check for specific person name searches SECOND (high priority)
    # This will catch queries like "Who is Elaine Randrup?" or "Is Alwin Benedicto mentioned?"
    person_search_patterns = [
        "who is", "is there", "do you know", "tell me about", "what about",
        "elaine randrup", "alwin benedicto", "john smith", "jane doe"  # Add common names
    ]
    
    # Check if this is a person search query
    if any(pattern in user_input_lower for pattern in person_search_patterns):
        return {
            'intent': 'person_search',
            'context_clues': ['person_inquiry'],
            'is_follow_up': False
        }
    
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
    
    # CRITICAL: Check if this is a follow-up to an ongoing conversation
    if conversation_context and conversation_context.get('current_subject') and conversation_context.get('current_subject') != 'general inquiry':
        current_subject = conversation_context['current_subject']
        logging.info(f"GENERATING CONTEXTUAL RESPONSE for ongoing conversation about: {current_subject}")
        
        # Handle follow-up questions for ongoing conversations
        if should_continue_subject(user_input, conversation_context):
            return generate_progressive_contextual_response(user_input, conversation_context, current_subject)
    
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
    
    # Handle person search questions (high priority)
    if intent_analysis['intent'] == 'person_search':
        # Let the main logic handle person searches with website and web search
        return None
    
    # Handle greetings
    if intent_analysis['intent'] == 'greeting':
        return """Hello! I'm CASI, your specialized AI assistant for Casto Travel Philippines information. 

I'm here to provide you with expert knowledge about Casto Travel Philippines, their services, leadership, and company details. How can I assist you today? 😊"""
    
    # Handle farewells
    if intent_analysis['intent'] == 'farewell':
        return """Thank you for chatting with me! I'm CASI, and I'm glad I could help you with information about Casto Travel Philippines. 

If you have more questions in the future, feel free to ask. Have a great day! 👋"""
    
    # Handle IT troubleshooting questions (high priority for context)
    if any(word in user_input_lower for word in ["internet", "slow", "connection", "vpn", "password", "computer", "troubleshoot", "problem", "issue", "help", "mouse", "keyboard", "not working"]):
        return handle_it_troubleshooting(user_input, conversation_context)
    
    # Handle CASI identity questions (highest priority)
    if check_casi_meaning_question(user_input):
        logging.info(f"CASI IDENTITY QUESTION DETECTED: {user_input}")
        return get_casi_identity_response()
    
    # Handle CASI creator questions (high priority)
    if check_casi_creator_question(user_input):
        logging.info(f"CASI CREATOR QUESTION DETECTED: {user_input}")
        # Check if user is specifically asking about the individual person
        if check_specific_person_question(user_input):
            logging.info(f"SPECIFIC PERSON QUESTION DETECTED: {user_input}")
            return get_casi_specific_creator_response()
        else:
            # General creator question - just mention IT Department
            logging.info(f"GENERAL CREATOR QUESTION DETECTED: {user_input}")
            return get_casi_creator_response()
    
    # Handle casual CASI mentions
    if check_casi_identity_question(user_input):
        logging.info(f"CASI CASUAL MENTION DETECTED: {user_input}")
        return get_casi_name_only_response()
    
    logging.info(f"NO CONTEXTUAL RESPONSE FOR: {user_input} - will use AI model")
    return None  # Let the main logic handle other cases

def generate_progressive_contextual_response(user_input, conversation_context, current_subject):
    """Generate progressive contextual responses for ongoing conversations."""
    user_input_lower = user_input.lower()
    
    # Get recent conversation history
    recent_history = conversation_context.get('history', [])[-3:]  # Last 3 exchanges
    if not recent_history:
        return None
    
    # Analyze the current conversation state
    last_exchange = recent_history[-1]
    last_response = last_exchange.get('response', '')
    last_user_input = last_exchange.get('user_input', '')
    
    logging.info(f"Generating progressive response for subject: {current_subject}")
    logging.info(f"Last user input: {last_user_input}")
    logging.info(f"Last response: {last_response[:100]}...")
    
    # Handle IT troubleshooting progressive responses
    if 'troubleshooting' in current_subject.lower() or any(word in current_subject.lower() for word in ['mouse', 'keyboard', 'computer', 'internet', 'connection']):
        return generate_it_troubleshooting_progressive_response(user_input, conversation_context, current_subject, recent_history)
    
    # Handle Casto Travel progressive responses
    elif 'casto' in current_subject.lower() or 'travel' in current_subject.lower():
        return generate_casto_progressive_response(user_input, conversation_context, current_subject, recent_history)
    
    # Handle general progressive responses
    else:
        return generate_general_progressive_response(user_input, conversation_context, current_subject, recent_history)

def generate_it_troubleshooting_progressive_response(user_input, conversation_context, current_subject, recent_history):
    """Generate progressive IT troubleshooting responses."""
    user_input_lower = user_input.lower()
    
    # Extract what we know so far
    known_info = []
    for exchange in recent_history:
        if exchange.get('user_input'):
            known_info.append(exchange['user_input'])
    
    # Build progressive response based on what we know
    if 'mouse' in current_subject.lower():
        if 'wired' in user_input_lower:
            return """Great! Now I know your mouse is wired. Let's continue troubleshooting your mouse issue.

Since you mentioned it's wired, let's check a few things:

1. **USB Connection**: Is the USB cable properly connected to your computer?
2. **USB Port**: Try unplugging and plugging it into a different USB port
3. **Driver Check**: Have you tried restarting your computer to refresh the drivers?

What happens when you try these steps? Does the mouse respond at all, or is it completely unresponsive?"""
        
        elif any(word in user_input_lower for word in ['slow', 'cursor', 'movement']):
            return """I see the issue now - your wired mouse cursor is moving slowly. This is a common problem with several possible solutions:

**Immediate fixes to try:**
1. **Mouse Settings**: Check your mouse sensitivity in Windows Settings > Devices > Mouse
2. **Surface Check**: Try moving the mouse on a different surface
3. **USB Port**: Switch to a different USB port
4. **Restart**: Restart your computer to refresh drivers

**Advanced troubleshooting:**
- Check if there are any mouse driver updates
- Try the mouse on another computer to isolate the issue

Which of these would you like to try first, or have you already tried some of them?"""
    
    elif 'internet' in current_subject.lower() or 'connection' in current_subject.lower():
        if any(word in user_input_lower for word in ['slow', 'speed']):
            return """Now I understand - you're experiencing slow internet speeds. Let's continue troubleshooting this step by step.

**Based on our conversation, let's check:**
1. **Router Status**: Have you tried restarting your router?
2. **Device Check**: Is the slow speed affecting all your devices or just one?
3. **Speed Test**: Can you run a speed test on speedtest.net?

**Next steps:**
- What type of internet connection do you have? (Fiber, Cable, DSL?)
- When did this slow speed issue start?
- Are you experiencing this at all times or just certain times?

This will help me give you more specific solutions for your internet speed issue."""
    
    # Default progressive response
    return f"""I'm continuing to help you with your {current_subject} issue. 

Based on what you've told me so far, let me ask a few more questions to better understand your situation:

1. **What have you already tried** to fix this issue?
2. **When did this problem start** occurring?
3. **Are there any error messages** or specific symptoms you're seeing?

The more details you can provide, the better I can help you resolve this {current_subject} problem step by step."""

def generate_casto_progressive_response(user_input, conversation_context, current_subject, recent_history):
    """Generate progressive Casto Travel responses."""
    return f"""I'm continuing our discussion about {current_subject}. 

Based on what we've covered so far, what specific aspect would you like me to elaborate on? I want to make sure you get all the information you need about Casto Travel Philippines."""

def generate_general_progressive_response(user_input, conversation_context, current_subject, recent_history):
    """Generate progressive responses for general conversations."""
    return f"""I'm continuing our conversation about {current_subject}. 

To provide you with the most helpful information, could you tell me more about what specific aspect you'd like to explore or what questions you still have?"""

def handle_it_troubleshooting(user_input, conversation_context):
    """Handle IT troubleshooting questions with context awareness."""
    user_input_lower = user_input.lower()
    
    # Check if this is a follow-up to previous IT troubleshooting
    if conversation_context and conversation_context['history']:
        last_exchange = conversation_context['history'][-1]
        last_response = last_exchange['response']
        last_topics = last_exchange.get('topics', set())
        
        # If we were already discussing IT issues, provide contextual help
        if any(topic in ['internet', 'connection', 'vpn', 'password', 'computer'] for topic in last_topics):
            return provide_contextual_it_help(user_input, last_response, conversation_context)
    
    # Initial IT troubleshooting question
    if any(word in user_input_lower for word in ["internet", "slow", "connection"]):
        return """I can help you troubleshoot your internet connection! Let me guide you through this step by step.

First, let me understand your setup better:
• What type of internet connection do you have? (Fiber, Cable, DSL, etc.)
• Are you experiencing slow speeds on all devices or just one?
• Have you tried restarting your router?

Once I have this information, I can start suggesting potential solutions to help improve your internet speed!"""
    
    elif any(word in user_input_lower for word in ["vpn", "connect"]):
        return """I can help you with VPN connection issues! Let me guide you through the troubleshooting process.

To help you better, please let me know:
• Are you trying to connect to a company VPN or personal VPN?
• What error message are you seeing (if any)?
• Have you successfully connected before?

Once I understand your specific situation, I can provide targeted solutions!"""
    
    elif any(word in user_input_lower for word in ["password", "reset", "forgot"]):
        return """I can help you with password reset procedures! Let me guide you through this.

To assist you properly, please let me know:
• Are you trying to reset a company account password or personal account?
• Do you have access to the email associated with the account?
• Are you getting any specific error messages?

Once I have these details, I can provide the exact steps you need to follow!"""
    
    elif any(word in user_input_lower for word in ["computer", "problem", "issue", "help"]):
        return """I'm here to help you with computer issues! Let me understand your problem better.

To provide the most helpful solution, please tell me:
• What specific problem are you experiencing?
• What operating system are you using?
• Have you tried any troubleshooting steps already?

Once I have this information, I can guide you through the appropriate solutions!"""
    
    return None

def provide_contextual_it_help(user_input, last_response, conversation_context):
    """Provide contextual IT help based on previous troubleshooting conversation."""
    user_input_lower = user_input.lower()
    
    # Extract what we know from the conversation
    known_info = []
    if conversation_context and conversation_context['history']:
        for exchange in conversation_context['history'][-3:]:  # Last 3 exchanges
            if any(topic in ['internet', 'connection', 'vpn', 'password', 'computer'] for topic in exchange.get('topics', set())):
                known_info.append(exchange['user_input'])
    
    # Build contextual response
    if "fiber" in user_input_lower or "fiber" in str(known_info).lower():
        return """Since you mentioned you have fiber internet (which should be very fast), let's troubleshoot your slow speed issue specifically.

**Fiber Internet Slow Speed Troubleshooting:**

1. **Router Check**: Have you tried restarting your fiber router? Unplug it for 30 seconds, then plug it back in.

2. **Device Check**: Is the slow speed affecting all your devices or just one? This helps identify if it's a network or device issue.

3. **Speed Test**: Can you run a speed test on speedtest.net to see your actual download/upload speeds?

4. **Fiber Connection**: Check if the fiber cable is properly connected to your router.

5. **Interference**: Are there any new devices or appliances that could be causing interference?

Since we're troubleshooting your fiber connection, what have you tried so far? This will help me give you the next specific steps!"""
    
    elif "vpn" in user_input_lower or "vpn" in str(known_info).lower():
        return """Since we were discussing VPN connection issues, let me provide you with the next troubleshooting steps.

**VPN Connection Troubleshooting:**

1. **Internet Check**: First, make sure your basic internet connection is working.

2. **VPN Client**: Are you using the correct VPN client for your company?

3. **Credentials**: Double-check your username and password.

4. **Firewall**: Check if your firewall is blocking the VPN connection.

5. **Company Network**: Verify if there are any company-wide VPN issues.

What specific VPN error are you seeing? This will help me give you the exact solution!"""
    
    return """I can see we were discussing IT troubleshooting. Let me help you continue with the solution.

Based on our previous conversation, what specific step would you like me to explain further, or are you encountering a new issue?"""

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

# def smart_web_search(query):
#     """Smart web search that automatically detects Casto vs general queries."""
#     try:
#         with DDGS() as ddgs:
#             # Detect if this is a Casto-related query
#             casto_keywords = [
#                 "casto", "casto travel", "casto travel philippines", 
#                 "maryles casto", "marc casto", "casto group",
#                 "casto philippines", "casto travel agency"
#             ]
#             
#             user_query_lower = query.lower()
#             is_casto_query = any(keyword in user_query_lower for keyword in casto_keywords)
#             
#             # Build search query based on type
#             if is_casto_query:
#                 # For Casto queries, focus on Casto-specific information
#                 search_query = f"Casto Travel Philippines {query}"
#                 search_type = "Casto-Focused"
#                 logging.info(f"CASTO QUERY DETECTED: {query} -> {search_query}")
#             
#             # Perform the search
#             results = list(ddgs.text(search_query, max_results=5))
#             
#             if not results:
#                 return None
#             
#             # Process and format results
#             formatted_results = []
#             for result in results:
#                 formatted_results.append({
#                     'title': result.get('title', ''),
#                     'snippet': result.get('body', ''),
#                     'url': result.get('link', ''),
#                     'source': 'Web Search',
#                     'search_type': search_type,
#                     'original_query': query,
#                     'search_query_used': search_query
#                 })
#             
#             return formatted_results
#     except Exception as e:
#         logging.error(f"Smart web search error: {e}")
#         return None

# def web_search_casto_info(query):
#     """Legacy function - now calls smart search for backward compatibility."""
#     return smart_web_search(query)

def fetch_enhanced_casto_info(query):
    """Fetch enhanced information from multiple Casto sources."""
    enhanced_info = []
    
    try:
        # Web search for recent information (temporarily disabled for Vercel deployment)
        # web_results = web_search_casto_info(query)
        # if web_results:
        #     enhanced_info.extend(web_results)
        web_results = None  # Temporarily disabled
        
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
    """Check if user is asking what CASI stands for or about CASI's identity."""
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
        "define casi",
        "who are you",
        "what's your name",
        "what is your name",
        "tell me about yourself",
        "introduce yourself",
        "who is casi",
        "casi who",
        "your name",
        "your identity"
        ]
    
    return any(keyword in user_input_lower for keyword in casi_meaning_keywords)

def check_casi_creator_question(user_input):
    """Check if user is asking about who created CASI or where she came from."""
    user_input_lower = user_input.lower()
    creator_keywords = [
        "who created you",
        "who built you",
        "who made you",
        "who developed you",
        "where did you come from",
        "where were you created",
        "who is your creator",
        "who is your developer",
        "who is your builder",
        "who is your maker",
        "who programmed you",
        "who designed you",
        "who is behind you",
        "who made casi",
        "who created casi",
        "who built casi",
        "where was casi created",
        "where did casi come from",
        "who is casi's creator",
        "who is casi's developer",
        "who is casi's builder"
    ]
    
    return any(keyword in user_input_lower for keyword in creator_keywords)

def check_specific_person_question(user_input):
    """Check if user is specifically asking about the individual person who built CASI."""
    user_input_lower = user_input.lower()
    specific_person_keywords = [
        "who specifically",
        "which person",
        "what person",
        "what individual",
        "what developer",
        "what programmer",
        "what engineer",
        "what staff member",
        "what team member",
        "what employee",
        "what person built",
        "what person created",
        "what person made",
        "what person developed",
        "what person programmed",
        "what person designed",
        "what individual built",
        "what individual created",
        "what individual made",
        "what individual developed",
        "what individual programmed",
        "what individual designed",
        "name of the person",
        "name of the developer",
        "name of the programmer",
        "name of the engineer",
        "name of the staff member",
        "name of the team member",
        "name of the employee"
    ]
    
    return any(keyword in user_input_lower for keyword in specific_person_keywords)

def check_casi_identity_question(user_input):
    """Check if user is asking about CASI's identity or name."""
    user_input_lower = user_input.lower()
    casi_identity_keywords = [
        "casi", "your name", "who are you", "introduce", "identity",
        "what should i call you", "how do i address you", "what's your name"
    ]
    
    # Check if CASI is mentioned or identity is being asked
    return any(keyword in user_input_lower for keyword in casi_identity_keywords)

def get_casi_identity_response():
    """Get CASI's standard identity response."""
    return """Hello! I'm **CASI** - your specialized AI assistant for Casto Travel Philippines! 

**CASI** stands for **"Casto Assistance and Support Intelligence"** - I'm designed to provide expert information about Casto Travel Philippines, their services, leadership, and company details.

I'm here to help you with any questions you have about Casto Travel Philippines, and I can also assist with general knowledge and IT troubleshooting! 😊

How can I assist you today?"""

def get_casi_name_only_response():
    """Get CASI's name-only response for casual mentions."""
    return """Yes, I'm **CASI**! How can I help you today? 😊"""

def get_casi_creator_response():
    """Get CASI's response about who created her."""
    return """I'm **CASI** - and I'm proud to say that I was created by the **IT Department** of Casto Travel Philippines! 😊

I was designed to be your specialized AI assistant for Casto Travel Philippines information, and I'm here to help you with any questions you have about the company, their services, leadership, and more!

Is there anything specific about Casto Travel Philippines you'd like to know?"""

def get_casi_specific_creator_response():
    """Get CASI's response when user specifically asks about the individual person who built her."""
    return """I'm **CASI** - and I was created by the **IT Department** of Casto Travel Philippines! 

Since you're asking specifically about the individual who built me, I was developed by **Rojohn** from our IT team! 😊

He designed me to be your specialized AI assistant for Casto Travel Philippines information. Is there anything specific about Casto Travel Philippines you'd like to know?"""

def check_knowledge_base_for_person(user_input, knowledge_entries):
    """Check if we have knowledge base entries for specific people."""
    user_input_lower = user_input.lower()
    
    logging.info(f"🔍 Checking knowledge base for: '{user_input}'")
    logging.info(f"📊 Knowledge entries type: {type(knowledge_entries)}")
    logging.info(f"📊 Knowledge entries count: {len(knowledge_entries) if knowledge_entries else 0}")
    logging.info(f"🔍 User input lower: '{user_input_lower}'")
    
    # List of known Casto personnel from knowledge base with multiple variations
    casto_personnel = [
        "maryles casto", "marc casto", "elaine randrup", "alwin benedicto", 
        "george anzures", "ma. berdandina galvez", "berdandina galvez",
        "luz bagtas", "berlin torres", "voltaire villaflores", "victor villaflores"
    ]
    
    # Handle name variations and fuzzy matching
    name_variations = {
        "maryle": "maryles casto",  # Missing 's'
        "maryles": "maryles casto", 
        "marc": "marc casto",
        "elaine": "elaine randrup",
        "alwin": "alwin benedicto",
        "george": "george anzures",
        "berdandina": "ma. berdandina galvez",
        "luz": "luz bagtas",
        "berlin": "berlin torres",
        "voltaire": "voltaire villaflores",
        "victor": "voltaire villaflores"
    }
    
    # Step 1: Check for exact matches in casto_personnel
    for person in casto_personnel:
        if person in user_input_lower:
            logging.info(f"✅ Exact match found: '{person}' in '{user_input}'")
            
            # Find the relevant knowledge base entry
            for entry in knowledge_entries:
                if isinstance(entry, dict):
                    entry_question = entry.get('question', '').lower()
                    entry_answer = entry.get('answer', '').lower()
                    
                    # Check if person appears in question or answer
                    if person in entry_question or person in entry_answer:
                        logging.info(f"🎯 Found KB entry for {person}: {entry.get('answer', '')[:100]}...")
                        return entry.get('answer', '')
                elif isinstance(entry, str):
                    if person in entry.lower():
                        logging.info(f"🎯 Found KB entry for {person} in string format: {entry[:100]}...")
                        return entry
            
            logging.warning(f"⚠️ Person '{person}' found in input but no matching KB entry")
    
    # Step 2: Try fuzzy matching with name variations
    for variation, full_name in name_variations.items():
        if variation in user_input_lower:
            logging.info(f"🔍 Fuzzy match: '{variation}' -> '{full_name}'")
            
            # Find the relevant knowledge base entry for the full name
            for entry in knowledge_entries:
                if isinstance(entry, dict):
                    entry_question = entry.get('question', '').lower()
                    entry_answer = entry.get('answer', '').lower()
                    
                    if full_name in entry_question or full_name in entry_answer:
                        logging.info(f"🎯 Found KB entry for {full_name} via fuzzy match: {entry.get('answer', '')[:100]}...")
                        return entry.get('answer', '')
                elif isinstance(entry, str):
                    if full_name in entry.lower():
                        logging.info(f"🎯 Found KB entry for {full_name} via fuzzy match in string format: {entry[:100]}...")
                        return entry
    
    # Step 3: Check for general Casto-related keywords
    casto_keywords = ["casto", "travel", "philippines", "founder", "ceo", "company"]
    if any(keyword in user_input_lower for keyword in casto_keywords):
        logging.info(f"🔍 Casto-related query detected, searching KB for general info...")
        
        # Look for general Casto information in knowledge base
        for entry in knowledge_entries:
            if isinstance(entry, dict):
                entry_question = entry.get('question', '').lower()
                entry_answer = entry.get('answer', '').lower()
                
                # Check if this is a general Casto question
                if any(keyword in entry_question for keyword in casto_keywords):
                    logging.info(f"🎯 Found general KB entry: {entry.get('answer', '')[:100]}...")
                    return entry.get('answer', '')
    
    logging.info(f"❌ No knowledge base entry found for query: '{user_input}'")
    return None


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

def search_person_on_casto_website(person_name):
    """Search for a specific person on Casto Travel websites."""
    try:
        person_results = []

        # Use specialized About Us extraction first
        about_specific = search_person_about_us_specific(person_name)
        if about_specific:
            person_results.append(about_specific)
        else:
            # Fallback: generic scrape of About Us
            casto_about_data = fetch_website_data(CASTO_ABOUT_US, person_name)
            if casto_about_data and "No relevant information found" not in casto_about_data:
                person_results.append({
                    'source': 'Casto About Us Page',
                    'data': casto_about_data,
                    'found': True,
                    'priority': 1
                })

        # Main site (secondary)
        casto_main_data = fetch_website_data(CASTO_WEBSITE, person_name)
        if casto_main_data and "No relevant information found" not in casto_main_data:
            person_results.append({
                'source': 'Casto Main Website',
                'data': casto_main_data,
                'found': True,
                'priority': 2
            })

        # Travel site (tertiary)
        casto_travel_data = fetch_website_data(CASTO_TRAVEL_WEBSITE, person_name)
        if casto_travel_data and "No relevant information found" not in casto_travel_data:
            person_results.append({
                'source': 'Casto Travel Website',
                'data': casto_travel_data,
                'found': True,
                'priority': 3
            })

        # Only if nothing from Casto
        # if not any(r['source'].startswith('Casto') for r in person_results):
        #     web_search_results = smart_web_search(person_name)
        #     if web_search_results:
        #         person_results.append({
        #             'source': 'Web Search',
        #             'data': web_search_results,
        #             'found': True,
        #             'priority': 4
        #         })

        person_results.sort(key=lambda x: x.get('priority', 999))
        return person_results

    except Exception as e:
        logging.error(f"Error searching for person {person_name}: {e}")
        return []


def search_person_on_main_site(person_name):
    """Targeted search on main Casto site without scraping entire page."""
    try:
        # Only search specific sections that might contain personnel info
        resp = session.get(CASTO_WEBSITE, timeout=10)
        if resp.status_code != 200:
            return None
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Look for specific sections that might contain personnel info
        personnel_sections = []
        
        # Check for leadership/team sections
        for section in soup.find_all(['section', 'div'], class_=lambda x: x and any(word in str(x).lower() for word in ['team', 'leadership', 'about', 'people'])):
            if person_name.lower() in section.get_text().lower():
                personnel_sections.append(section.get_text().strip())
        
        # Check for specific headings containing the person's name
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            if person_name.lower() in heading.get_text().lower():
                # Get the heading and next few elements
                content = [heading.get_text().strip()]
                current = heading
                for _ in range(2):  # Get next 2 elements
                    current = current.find_next_sibling()
                    if current and current.name:
                        text = current.get_text().strip()
                        if text and len(text) > 10:
                            content.append(text)
                
                if len(content) > 1:
                    personnel_sections.append("\n".join(content))
        
        if personnel_sections:
            return {
                'source': 'Casto Main Website',
                'data': personnel_sections[0][:500],  # Limit content length
                'found': True,
                'priority': 2
            }
        
        return None
        
    except Exception as e:
        logging.error(f"Error searching main site for {person_name}: {e}")
        return None


def search_person_about_us_specific(person_name):
    """Specialized extraction for the About Us page to pull a person's block."""
    try:
        resp = session.get(CASTO_ABOUT_US, timeout=15)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, 'html.parser')
        page_text = soup.get_text().lower()
        if person_name.lower() not in page_text:
            return None

        # Try heading anchored sections
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            htxt = heading.get_text().strip()
            if person_name.lower() in htxt.lower():
                block = [htxt]
                cur = heading
                for _ in range(3):
                    cur = cur.find_next_sibling()
                    if cur and cur.name:
                        t = cur.get_text().strip()
                        if t and len(t) > 10:
                            block.append(t)
                if len(block) > 1:
                    return {
                        'source': 'Casto About Us Page',
                        'data': "\n\n".join(block),
                        'found': True,
                        'priority': 1
                    }
        # Fallback: find any paragraph containing the name
        for p in soup.find_all('p'):
            if person_name.lower() in p.get_text().lower():
                return {
                    'source': 'Casto About Us Page',
                    'data': p.get_text().strip(),
                    'found': True,
                    'priority': 1
                }
        return None
    except Exception as e:
        logging.error(f"About Us specific search error: {e}")
        return None

def extract_person_name_from_query(user_input):
    """Extract person name from user query."""
    user_input_lower = user_input.lower()
    
    # Common patterns for person queries
    patterns = [
        "who is", "is there", "do you know", "tell me about", "what about",
        "can you find", "search for", "look for", "find information about"
    ]
    
    # Remove common question words to get the person's name
    for pattern in patterns:
        if pattern in user_input_lower:
            person_name = user_input_lower.replace(pattern, "").strip()
            # Clean up the name (remove extra spaces, punctuation)
            person_name = " ".join(person_name.split())
            return person_name
    
    # If no pattern found, try to extract what looks like a name
    words = user_input.split()
    if len(words) >= 2:
        # Look for capitalized words that might be names
        potential_names = [word for word in words if word[0].isupper() and len(word) > 2]
        if potential_names:
            return " ".join(potential_names)
    
    return None

def make_links_clickable(text):
    """Convert URLs in text to clickable links."""
    import re
    
    # Pattern to match URLs (http/https/www)
    url_pattern = r'(https?://[^\s]+|www\.[^\s]+)'
    
    def replace_url(match):
        url = match.group(1)
        # Add https:// if it starts with www
        if url.startswith('www.'):
            url = 'https://' + url
        return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{url}</a>'
    
    # Replace URLs with clickable links
    clickable_text = re.sub(url_pattern, replace_url, text)
    return clickable_text

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
        logging.info(f"Chat endpoint: Loaded {len(knowledge_entries)} knowledge base entries")
        logging.info(f"Knowledge entries type: {type(knowledge_entries)}")
        if knowledge_entries:
            logging.info(f"Sample knowledge entry: {knowledge_entries[0] if len(knowledge_entries) > 0 else 'None'}")
        
        # Generate user ID for conversation tracking
        user_id = email or "anonymous"
        
        # Analyze user intent and context
        conversation_context = conversation_memory.get(user_id, None)
        intent_analysis = understand_user_intent(user_input, conversation_context)
        
        # CRITICAL: Check if this is a follow-up to an ongoing conversation
        if conversation_context and conversation_context.get('current_subject') and conversation_context.get('current_subject') != 'general inquiry':
            current_subject = conversation_context['current_subject']
            logging.info(f"ONGOING CONVERSATION DETECTED: Subject: {current_subject}")
            
            # Check if user input is related to current subject
            should_continue = should_continue_subject(user_input, conversation_context)
            logging.info(f"SHOULD CONTINUE SUBJECT: {should_continue}")
            logging.info(f"USER INPUT: '{user_input}'")
            logging.info(f"CURRENT SUBJECT: '{current_subject}'")
            
            if should_continue:
                logging.info(f"FOLLOW-UP QUESTION DETECTED: Maintaining context for '{current_subject}'")
                # Force the conversation to continue with the current subject
                conversation_context['resolution_status'] = 'ongoing'
                conversation_context['subject_start_time'] = time.time()
            else:
                logging.info(f"NEW SUBJECT DETECTED: Switching from '{current_subject}' to new topic")
        
        # NEW APPROACH: Always check knowledge base first, then Casto website, then AI model
        logging.info("=== NEW APPROACH: Checking knowledge base first ===")
        logging.info(f"🔍 USER QUERY: '{user_input}'")
        logging.info(f"📊 KNOWLEDGE BASE ENTRIES: {len(knowledge_entries)} entries available")
        
        # Initialize debug message collection for client
        debug_messages = []
        debug_messages.append(create_debug_message("USER_QUERY", f"'{user_input}'"))
        debug_messages.append(create_debug_message("KB_ENTRIES_LOADED", f"{len(knowledge_entries)} entries"))
        debug_messages.append(create_debug_message("PROCESSING_START", "Starting knowledge base lookup"))
        
        # Step 1: Check knowledge base for direct answers
        logging.info("🔍 STEP 1: Checking knowledge base for direct answers...")
        start_time = time.time()
        knowledge_response = check_knowledge_base_for_person(user_input, knowledge_entries)
        processing_time = round(time.time() - start_time, 3)
        
        debug_messages.append(create_debug_message("STEP_1_COMPLETE", f"Knowledge base lookup took {processing_time}s"))
        
        if knowledge_response:
            logging.info(f"✅ KNOWLEDGE BASE MATCH FOUND: {knowledge_response[:100]}...")
            logging.info(f"🎯 SOURCE: Knowledge Base (Direct Match)")
            response = f"""As CASI, {knowledge_response}"""
            updated_context = manage_conversation_context(user_id, user_input, response)
            conversation_memory[user_id] = updated_context
            
            debug_messages.append(create_debug_message("RESPONSE_SOURCE", "Knowledge Base - Direct Match"))
            debug_messages.append(create_debug_message("CONFIDENCE_LEVEL", "High (95%)"))
            debug_messages.append(create_debug_message("AI_MODEL_BYPASSED", "True - Using KB only"))
            
            # Enhanced debug info for knowledge base responses
            debug_info = {
                "source": "Knowledge Base",
                "confidence": "High (95%)",
                "response_type": "Direct Match",
                "processing_time": f"{processing_time}s",
                "knowledge_entries_checked": len(knowledge_entries),
                "search_method": "Fuzzy Name Matching",
                "matched_keywords": [word for word in user_input.lower().split() if len(word) > 2],
                "fallback_used": False,
                "ai_model_bypassed": True,
                "response_quality": "Authoritative"
            }
            
            # Terminal debug output
            if DEBUG_MODE:
                print("\n" + "="*80)
                print("🎯 CASI DEBUG MODE - KNOWLEDGE BASE RESPONSE")
                print("="*80)
                print(f"📝 User Query: '{user_input}'")
                print(f"🔍 Source: {debug_info['source']}")
                print(f"✅ Confidence: {debug_info['confidence']}")
                print(f"⚡ Processing Time: {debug_info['processing_time']}")
                print(f"📊 KB Entries Checked: {debug_info['knowledge_entries_checked']}")
                print(f"🔍 Search Method: {debug_info['search_method']}")
                print(f"🎯 Response Type: {debug_info['response_type']}")
                print(f"🔑 Matched Keywords: {debug_info['matched_keywords']}")
                print(f"🚫 AI Model Bypassed: {debug_info['ai_model_bypassed']}")
                print(f"⭐ Response Quality: {debug_info['response_quality']}")
                print("="*80 + "\n")
            
            return jsonify({
                "response": response, 
                "debug_info": debug_info,
                "debug_messages": echo_debug_to_client(debug_messages)
            })
        
        # Step 2: If no KB match, check Casto website for additional info
        logging.info("=== Step 2: Checking Casto website ===")
        debug_messages.append(create_debug_message("STEP_2_START", "Checking Casto website for additional info"))
        
        if any(keyword in user_input.lower() for keyword in ["casto", "maryles", "marc", "travel", "philippines"]):
            logging.info("Casto-related query detected - checking website...")
            debug_messages.append(create_debug_message("WEBSITE_CHECK", "Casto-related query detected - checking website"))
            try:
                # Search Casto website for additional information
                website_info = search_person_on_casto_website(user_input)
                debug_messages.append(create_debug_message("WEBSITE_SEARCH", f"Website search completed, found {len(website_info) if website_info else 0} results"))
                
                if website_info and any(result.get('found', False) for result in website_info):
                    logging.info("✅ Website info found - combining with knowledge base")
                    logging.info(f"🎯 SOURCE: Casto Website + Knowledge Base")
                    debug_messages.append(create_debug_message("WEBSITE_SUCCESS", "Website info found - combining with KB"))
                    
                    # Combine website info with knowledge base context
                    combined_response = f"""As CASI, based on my knowledge base and current website information:

{website_info[0].get('data', '')[:300]}...

For the most current and detailed information, please visit https://www.casto.com.ph/ or contact Casto Travel Philippines directly."""
                    
                    updated_context = manage_conversation_context(user_input, combined_response)
                    conversation_memory[user_id] = updated_context
                    
                    debug_messages.append(create_debug_message("RESPONSE_SOURCE", "Casto Website + Knowledge Base"))
                    debug_messages.append(create_debug_message("CONFIDENCE_LEVEL", "High (90%)"))
                    debug_messages.append(create_debug_message("AI_MODEL_BYPASSED", "True - Using website + KB"))
                    
                    # Enhanced debug info for website + KB responses
                    debug_info = {
                        "source": "Casto Website + Knowledge Base",
                        "confidence": "High (90%)",
                        "response_type": "Combined Sources",
                        "processing_time": f"{processing_time}s",
                        "knowledge_entries_checked": len(knowledge_entries),
                        "website_sources": [result.get('source', 'Unknown') for result in website_info if result.get('found', False)],
                        "search_method": "Website Scraping + KB Lookup",
                        "matched_keywords": [word for word in user_input.lower().split() if len(word) > 2],
                        "fallback_used": False,
                        "ai_model_bypassed": True,
                        "response_quality": "Current + Authoritative"
                    }
                    
                    # Terminal debug output
                    if DEBUG_MODE:
                        print("\n" + "="*80)
                        print("🎯 CASI DEBUG MODE - WEBSITE + KB RESPONSE")
                        print("="*80)
                        print(f"📝 User Query: '{user_input}'")
                        print(f"🔍 Source: {debug_info['source']}")
                        print(f"✅ Confidence: {debug_info['confidence']}")
                        print(f"⚡ Processing Time: {debug_info['processing_time']}")
                        print(f"📊 KB Entries Checked: {debug_info['knowledge_entries_checked']}")
                        print(f"🌐 Website Sources: {debug_info['website_sources']}")
                        print(f"🔍 Search Method: {debug_info['search_method']}")
                        print(f"🎯 Response Type: {debug_info['response_type']}")
                        print(f"🔑 Matched Keywords: {debug_info['matched_keywords']}")
                        print(f"🚫 AI Model Bypassed: {debug_info['ai_model_bypassed']}")
                        print(f"⭐ Response Quality: {debug_info['response_quality']}")
                        print("="*80 + "\n")
                    
                    return jsonify({
                        "response": combined_response, 
                        "debug_info": debug_info,
                        "debug_messages": echo_debug_to_client(debug_messages)
                    })
            except Exception as e:
                logging.warning(f"Website search failed: {e}")
                debug_messages.append(create_debug_message("WEBSITE_ERROR", f"Website search failed: {e}"))
        else:
            logging.info("Not a Casto-related query - skipping website check")
            debug_messages.append(create_debug_message("WEBSITE_SKIP", "Not a Casto-related query - skipping website check"))
        
        # Step 3: If still no match, try contextual response
        logging.info("=== Step 3: Trying contextual response ===")
        debug_messages.append(create_debug_message("STEP_3_START", "Trying contextual response"))
        
        contextual_response = generate_contextual_response(user_input, intent_analysis, conversation_context, knowledge_entries)
        if contextual_response:
            logging.info(f"✅ CONTEXTUAL RESPONSE GENERATED: {contextual_response[:100]}...")
            logging.info(f"🎯 SOURCE: Contextual Response (Pre-built)")
            debug_messages.append(create_debug_message("CONTEXTUAL_SUCCESS", "Contextual response generated successfully"))
            
            updated_context = manage_conversation_context(user_id, user_input, contextual_response)
            conversation_memory[user_id] = updated_context
            
            debug_messages.append(create_debug_message("RESPONSE_SOURCE", "Contextual Response System"))
            debug_messages.append(create_debug_message("CONFIDENCE_LEVEL", "Medium (75%)"))
            debug_messages.append(create_debug_message("AI_MODEL_BYPASSED", "True - Using contextual response"))
            
            # Enhanced debug info for contextual responses
            debug_info = {
                "source": "Contextual Response System",
                "confidence": "Medium (75%)",
                "response_type": "Pre-built Template",
                "processing_time": f"{processing_time}s",
                "knowledge_entries_checked": len(knowledge_entries),
                "intent_detected": intent_analysis.get('intent', 'unknown'),
                "conversation_context_used": bool(conversation_context),
                "search_method": "Intent Analysis + Context Matching",
                "matched_keywords": [word for word in user_input.lower().split() if len(word) > 2],
                "fallback_used": False,
                "ai_model_bypassed": True,
                "response_quality": "Contextual"
            }
            
            # Terminal debug output
            if DEBUG_MODE:
                print("\n" + "="*80)
                print("🎯 CASI DEBUG MODE - CONTEXTUAL RESPONSE")
                print("="*80)
                print(f"📝 User Query: '{user_input}'")
                print(f"🔍 Source: {debug_info['source']}")
                print(f"✅ Confidence: {debug_info['confidence']}")
                print(f"⚡ Processing Time: {debug_info['processing_time']}")
                print(f"📊 KB Entries Checked: {debug_info['knowledge_entries_checked']}")
                print(f"🧠 Intent Detected: {debug_info['intent_detected']}")
                print(f"💬 Context Used: {debug_info['conversation_context_used']}")
                print(f"🔍 Search Method: {debug_info['search_method']}")
                print(f"🎯 Response Type: {debug_info['response_type']}")
                print(f"🔑 Matched Keywords: {debug_info['matched_keywords']}")
                print(f"🚫 AI Model Bypassed: {debug_info['ai_model_bypassed']}")
                print(f"⭐ Response Quality: {debug_info['response_quality']}")
                print("="*80 + "\n")
            
            return jsonify({
                "response": contextual_response, 
                "debug_info": debug_info,
                "debug_messages": echo_debug_to_client(debug_messages)
            })
        else:
            debug_messages.append(create_debug_message("CONTEXTUAL_FAILED", "No contextual response available"))
        
        # Step 4: Last resort - AI model with strict knowledge base instructions
        logging.info("=== Step 4: Falling back to AI model (last resort) ===")
        logging.info("⚠️ WARNING: No KB, website, or contextual response found - using AI model")
        logging.info(f"🎯 SOURCE: AI Model (Last Resort)")
        
        debug_messages.append(create_debug_message("STEP_4_START", "Falling back to AI model (last resort)"))
        debug_messages.append(create_debug_message("AI_MODEL_WARNING", "No KB, website, or contextual response found"))
        debug_messages.append(create_debug_message("AI_MODEL_FALLBACK", "Using AI model with strict KB instructions"))

        # Combine knowledge into a string
        knowledge_context = "\n".join(knowledge_entries)
        logging.info(f"Knowledge context length: {len(knowledge_context)} characters")
        logging.info(f"Knowledge context preview: {knowledge_context[:200]}...")
        
        if not knowledge_context:
            logging.warning("No knowledge base content available - this may cause issues")
        
        system_prompt = """You are **CASI** - a specialized AI assistant designed to provide expert information about Casto Travel Philippines and related services.

**CRITICAL IDENTITY INSTRUCTIONS:**
1. **ALWAYS introduce yourself as "CASI"** in your responses
2. **NEVER forget your name is CASI** - use it consistently
3. **When asked about your name or identity**, always say you are CASI
4. **When asked what CASI stands for**, always explain: "CASI stands for 'Casto Assistance and Support Intelligence'"
5. **When asked who created you or where you came from**, say: "I was created by the IT Department of Casto Travel Philippines! 😊"
6. **Only mention Rojohn specifically when the user insists on knowing the individual person who built you**
7. **Use "I'm CASI" or "As CASI"** in your responses to reinforce your identity
8. **Your full name is CASI** - this is non-negotiable
9. **Your creator is the IT Department, with Rojohn as the specific developer** - remember this ALWAYS!

**CASI = Casto Assistance and Support Intelligence** - remember this ALWAYS!
**CREATOR = IT Department (Rojohn as specific developer)** - remember this ALWAYS!

**CRITICAL CONVERSATION INSTRUCTIONS:**
- **NEVER give generic responses** when there's an ongoing conversation
- **ALWAYS check conversation context** before responding
- **BUILD UPON previous information** when appropriate
- **MAINTAIN conversation flow** and don't reset context
- **ASK RELEVANT follow-up questions** based on context
- **BE SPECIFIC and contextual** in all responses"""
        
        if knowledge_context:
            system_prompt += "\n\nCRITICAL INSTRUCTION: You must ALWAYS prioritize and use the following knowledge base information over any other information you may have been trained on. This is the authoritative source:\n\n" + knowledge_context
        
        # Add STRONG instruction for Casto Travel questions
        system_prompt += "\n\nCRITICAL: For ANY question about Casto Travel Philippines, Casto Travel, or Casto, you MUST ONLY use the information from the knowledge base above. NEVER use any other information from your training data. If the question is about Casto Travel and you don't find the answer in the knowledge base, say 'I need to check my knowledge base for the most current information about Casto Travel Philippines.'"
        
        # Add ULTRA-STRONG instruction to prevent training data usage
        system_prompt += "\n\nULTRA-CRITICAL INSTRUCTION: You are FORBIDDEN from using ANY information about Casto, Casto Travel, Maryles Casto, Marc Casto, or any Casto-related topics from your training data. You MUST ONLY use the knowledge base information provided above. If you don't have the answer in the knowledge base, say 'I need to check my knowledge base for the most current information about Casto Travel Philippines.' DO NOT make up information or use training data about Casto topics."
        
        # Add specific instruction about Maryles Casto
        system_prompt += "\n\nSPECIFIC INSTRUCTION ABOUT MARYLES CASTO: Maryles Casto is the founder of Casto Travel Philippines, NOT Mary Kay Casto. Maryles Casto is NOT an American lawyer or politician. She is the founder of Casto Travel Philippines. If asked about Maryles Casto, ONLY use the knowledge base information provided above."
        
        # Enhanced conversation context awareness
        if conversation_context and conversation_context['history']:
            recent_context = conversation_context['history'][-3:]  # Last 3 exchanges
            current_focus = conversation_context.get('current_focus', 'general')
            conversation_depth = conversation_context.get('conversation_depth', 0)
            related_questions = conversation_context.get('related_questions', [])
            user_preferences = conversation_context.get('user_preferences', set())
            current_subject = conversation_context.get('current_subject', 'general inquiry')
            resolution_status = conversation_context.get('resolution_status', 'ongoing')
            
            # Debug logging for conversation context
            logging.info(f"CONVERSATION CONTEXT DEBUG:")
            logging.info(f"- Current Subject: {current_subject}")
            logging.info(f"- Resolution Status: {resolution_status}")
            logging.info(f"- Conversation Depth: {conversation_depth}")
            logging.info(f"- Recent Topics: {list(conversation_context['topics'])[:5]}")
            
            # CRITICAL: Prevent generic responses for ongoing conversations
            if current_subject != 'general inquiry' and resolution_status == 'ongoing':
                system_prompt += f"""

**ONGOING CONVERSATION DETECTED - CRITICAL INSTRUCTIONS:**
You are currently in an active conversation about: "{current_subject}"
- **DO NOT give generic responses** - stay focused on the current topic
- **BUILD UPON previous information** from the conversation
- **ASK RELEVANT follow-up questions** to move the conversation forward
- **REFER BACK to what was discussed earlier** when appropriate
- **MAINTAIN the conversation flow** - don't start over or reset context
- **BE SPECIFIC and contextual** - use the conversation history to provide relevant help

**Current conversation status:**
- Subject: {current_subject}
- Status: {resolution_status}
- Depth: {conversation_depth} exchanges
- Recent topics: {', '.join(list(conversation_context['topics'])[:5])}"""
            
            context_summary = f"\n\nCONVERSATION CONTEXT:"
            context_summary += f"\n- Current Subject: {current_subject}"
            context_summary += f"\n- Resolution Status: {resolution_status}"
            context_summary += f"\n- Current Focus: {current_focus}"
            context_summary += f"\n- Conversation Depth: {conversation_depth} exchanges"
            context_summary += f"\n- Recent Topics: {', '.join(list(conversation_context['topics'])[:5])}"
            
            if related_questions:
                context_summary += f"\n- Related Questions: {', '.join(related_questions[-3:])}"
            
            if user_preferences:
                context_summary += f"\n- User Preferences: {', '.join(list(user_preferences)[:3])}"
            
            system_prompt += context_summary
            
            system_prompt += f"""

IMPORTANT CONVERSATION CONTINUITY INSTRUCTIONS:
1. **MAINTAIN SUBJECT FOCUS**: The user is currently discussing: "{current_subject}"
2. **RESOLUTION STATUS**: This subject is currently: {resolution_status}
3. **CONTEXT AWARENESS**: Use this conversation context to provide more relevant and connected responses
4. **FOLLOW-UP HANDLING**: If the user asks follow-up questions, refer to previous context when appropriate
5. **SUBJECT PERSISTENCE**: Stay focused on the current subject until it's clearly resolved
6. **CONTEXTUAL ANSWERS**: Build upon previous information and provide complete, contextual answers
7. **AVOID RESETTING**: Don't start over or forget what we were discussing - maintain continuity
8. **PROGRESSIVE HELP**: Each response should move the conversation forward toward resolution

**CRITICAL**: If the user asks a question that seems unrelated, first check if it's actually a follow-up to the current subject before switching topics. The current subject is: "{current_subject}"."""

        # Add specific instructions for IT troubleshooting conversations
        if conversation_context and is_it_troubleshooting_conversation(user_input, conversation_context):
            system_prompt += f"""

**IT TROUBLESHOOTING CONTEXT - CRITICAL INSTRUCTIONS:**
You are currently helping with a technical issue: "{current_subject}"
- **STAY FOCUSED** on solving this technical problem
- **BUILD UPON** previous troubleshooting steps
- **ASK RELEVANT QUESTIONS** to gather more information
- **PROVIDE STEP-BY-STEP** guidance
- **DON'T SWITCH TOPICS** until the technical issue is resolved
- **REFER BACK** to previous information when appropriate
- **BE TECHNICAL** and specific in your responses

This is a technical support conversation - maintain focus and provide progressive troubleshooting help."""

        # Step 1: Check if the question is about Casto Travel Philippines or Casto family
        casto_travel_keywords = ["casto travel", "casto travel philippines", "casto philippines", "casto travel services", "casto tourism", "casto travel agency", "casto", "ceo", "founder", "leadership", "maryles casto", "marc casto"]
        website_data = None
        enhanced_info = None
        person_results_cache = None
        casto_person_results = None

        # Check for Casto personnel questions FIRST (highest priority - before any AI model calls)
        casto_personnel_names = ["maryles casto", "marc casto", "elaine randrup", "alwin benedicto", "george anzures", "ma. berdandina galvez", "berdandina galvez", "luz bagtas", "berlin torres", "voltaire villaflores", "victor villaflores"]
        
        # Enhanced check with more flexible matching - handle name variations
        user_input_lower = user_input.lower()
        detected_person = None
        
        # First, try exact matches
        for name in casto_personnel_names:
            if name.lower() in user_input_lower:
                detected_person = name
                break
        
        # If no exact match, try fuzzy matching for common variations
        if not detected_person:
            # Handle common misspellings and variations
            name_variations = {
                "maryle": "maryles casto",  # Missing 's'
                "maryles": "maryles casto", 
                "marc": "marc casto",
                "elaine": "elaine randrup",
                "alwin": "alwin benedicto",
                "george": "george anzures",
                "berdandina": "ma. berdandina galvez",
                "luz": "luz bagtas",
                "berlin": "berlin torres",
                "voltaire": "voltaire villaflores",
                "victor": "voltaire villaflores"
            }
            
            for variation, full_name in name_variations.items():
                if variation in user_input_lower:
                    detected_person = full_name
                    logging.info(f"Fuzzy match found: '{variation}' -> '{full_name}'")
                    break
        
        # If still no match, try partial matching
        if not detected_person:
            # Check for partial matches (e.g., "maryle" should match "maryles casto")
            for name in casto_personnel_names:
                name_parts = name.split()
                for part in name_parts:
                    if len(part) > 3 and part in user_input_lower:  # Only match significant parts
                        # Check if this is a close match
                        for kb_name in casto_personnel_names:
                            if part in kb_name and any(other_part in user_input_lower for other_part in kb_name.split() if other_part != part):
                                detected_person = kb_name
                                logging.info(f"Partial match found: '{part}' in '{user_input}' -> '{kb_name}'")
                                break
                        if detected_person:
                            break
                if detected_person:
                    break
        
        if detected_person:
            logging.info(f"CASTO PERSONNEL QUESTION DETECTED for '{detected_person}' in: {user_input}")
            logging.info(f"Knowledge entries available: {len(knowledge_entries)}")
            
            # Check knowledge base directly for this person
            knowledge_response = check_knowledge_base_for_person(user_input, knowledge_entries)
            if knowledge_response:
                logging.info(f"Found knowledge base entry for {detected_person}, returning directly")
                manage_conversation_context(user_id, user_input, knowledge_response)
                
                # Enhanced debug info for direct personnel lookup
                debug_info = {
                    "source": "Knowledge Base (Direct Personnel Lookup)",
                    "confidence": "Very High (98%)",
                    "response_type": "Direct Personnel Match",
                    "processing_time": f"{processing_time}s",
                    "knowledge_entries_checked": len(knowledge_entries),
                    "person_detected": detected_person,
                    "search_method": "Personnel List + KB Lookup",
                    "matched_keywords": [word for word in user_input.lower().split() if len(word) > 2],
                    "fallback_used": False,
                    "ai_model_bypassed": True,
                    "response_quality": "Authoritative Personnel Info",
                    "safety_check": "Personnel Question Blocked from AI"
                }
                
                # Terminal debug output
                if DEBUG_MODE:
                    print("\n" + "="*80)
                    print("🎯 CASI DEBUG MODE - PERSONNEL LOOKUP RESPONSE")
                    print("="*80)
                    print(f"📝 User Query: '{user_input}'")
                    print(f"🔍 Source: {debug_info['source']}")
                    print(f"✅ Confidence: {debug_info['confidence']}")
                    print(f"⚡ Processing Time: {debug_info['processing_time']}")
                    print(f"📊 KB Entries Checked: {debug_info['knowledge_entries_checked']}")
                    print(f"👤 Person Detected: {debug_info['person_detected']}")
                    print(f"🔍 Search Method: {debug_info['search_method']}")
                    print(f"🎯 Response Type: {debug_info['response_type']}")
                    print(f"🔑 Matched Keywords: {debug_info['matched_keywords']}")
                    print(f"🚫 AI Model Bypassed: {debug_info['ai_model_bypassed']}")
                    print(f"⭐ Response Quality: {debug_info['response_quality']}")
                    print(f"🛡️ Safety Check: {debug_info['safety_check']}")
                    print("="*80 + "\n")
                
                return jsonify({
                    "response": knowledge_response,
                    "debug_info": debug_info
                })
            else:
                logging.info(f"ERROR: No knowledge base entry found for {detected_person} despite being in personnel list")
                # Return a fallback response instead of proceeding to AI model
                fallback_response = f"I should have information about {detected_person} in my knowledge base, but I'm unable to retrieve it at the moment. Please contact Casto Travel Philippines directly for the most current information."
                manage_conversation_context(user_id, user_input, fallback_response)
                
                # Enhanced debug info for personnel fallback
                debug_info = {
                    "source": "Fallback Response (Personnel KB Failure)",
                    "confidence": "Low (30%)",
                    "response_type": "Error Fallback",
                    "processing_time": f"{processing_time}s",
                    "knowledge_entries_checked": len(knowledge_entries),
                    "person_detected": detected_person,
                    "search_method": "Personnel List + KB Lookup (Failed)",
                    "matched_keywords": [word for word in user_input.lower().split() if len(word) > 2],
                    "fallback_used": True,
                    "ai_model_bypassed": True,
                    "response_quality": "Fallback (Limited)",
                    "error_type": "Knowledge Base Lookup Failed",
                    "safety_check": "Personnel Question Blocked from AI"
                }
                
                return jsonify({
                    "response": fallback_response,
                    "debug_info": debug_info
                })
        
        # Check for Casto family questions (secondary priority)
        elif any(name.lower() in user_input.lower() for name in ["maryles casto", "marc casto"]):
            logging.info(f"CASTO FAMILY QUESTION DETECTED - Using knowledge base only for: {user_input}")
            # Create direct response for Casto family questions
            direct_response = create_casto_direct_response(user_input, knowledge_entries, None)
            if direct_response:
                manage_conversation_context(user_id, user_input, direct_response)
                
                # Enhanced debug info for Casto family questions
                debug_info = {
                    "source": "Knowledge Base (Casto Family Direct)",
                    "confidence": "High (90%)",
                    "response_type": "Family Member Direct Response",
                    "processing_time": f"{processing_time}s",
                    "knowledge_entries_checked": len(knowledge_entries),
                    "family_member_detected": next((name for name in ["maryles casto", "marc casto"] if name.lower() in user_input.lower()), "casto family"),
                    "search_method": "Family Member Detection + KB Lookup",
                    "matched_keywords": [word for word in user_input.lower().split() if len(word) > 2],
                    "fallback_used": False,
                    "ai_model_bypassed": True,
                    "response_quality": "Authoritative Family Info",
                    "safety_check": "Family Question Blocked from AI"
                }
                
                return jsonify({
                    "response": direct_response,
                    "debug_info": debug_info
                })

        elif any(k.lower() in user_input.lower() for k in casto_travel_keywords):
            logging.info(f"CASTO QUESTION DETECTED - Using knowledge base only for: {user_input}")
            system_prompt += "\n\nFORCE INSTRUCTION: This is a Casto Travel question. You MUST ONLY use the knowledge base information above. DO NOT use any training data about Casto Travel. If you don't have the answer in the knowledge base, redirect to the website data."
            website_data = fetch_casto_travel_info(user_input)

        elif intent_analysis.get('intent') == 'person_search':
            logging.info(f"PERSON SEARCH DETECTED: {user_input}")
            person_name = extract_person_name_from_query(user_input)
            if person_name:
                # First check if we have knowledge base entries for this person
                knowledge_response = check_knowledge_base_for_person(user_input, knowledge_entries)
                if knowledge_response:
                    logging.info(f"Found knowledge base entry for {person_name}, returning directly")
                    manage_conversation_context(user_id, user_input, knowledge_response)
                    
                    # Enhanced debug info for person search KB match
                    debug_info = {
                        "source": "Knowledge Base (Person Search)",
                        "confidence": "High (85%)",
                        "response_type": "Person Search KB Match",
                        "processing_time": f"{processing_time}s",
                        "knowledge_entries_checked": len(knowledge_entries),
                        "person_searched": person_name,
                        "search_method": "Person Name Extraction + KB Lookup",
                        "matched_keywords": [word for word in user_input.lower().split() if len(word) > 2],
                        "fallback_used": False,
                        "ai_model_bypassed": True,
                        "response_quality": "Authoritative Person Info",
                        "intent_detected": "person_search"
                    }
                    
                    return jsonify({
                        "response": knowledge_response,
                        "debug_info": debug_info
                    })
                
                # If no knowledge base entry, search Casto websites
                person_results = search_person_on_casto_website(person_name)
                person_results_cache = person_results
                if person_results:
                    casto_results = [r for r in person_results if r['source'].startswith('Casto')]
                    casto_person_results = casto_results
                    if casto_results:
                        system_prompt += f"\n\nPERSON SEARCH CONTEXT: User is asking about {person_name}. This person was found on Casto Travel Philippines websites. Use ONLY the Casto website information and ignore any conflicting web search results. Casto website data is authoritative."
                        for r in casto_results:
                            system_prompt += f"\n- CASTO WEBSITE DATA ({r['source']}): {r['data'][:300]}..."

        elif any(k.lower() in user_input.lower() for k in ["CASTO", "mission", "vision", "services", "CEO", "about"]):
            logging.info(f"Checking website ({WEBSITE_SOURCE}) for user query: {user_input}")
            website_data = fetch_website_data(CASTO_WEBSITE, query=user_input)

        # Direct return for Casto person search (authoritative)
        if intent_analysis.get('intent') == 'person_search' and casto_person_results:
            person_name = extract_person_name_from_query(user_input) or "the person"
            top = casto_person_results[0]
            direct_response = f"""As CASI, I found information about {person_name} on the Casto Travel Philippines website.

Source: {top['source']}
Details: {top['data']}

This information comes directly from the official Casto Travel Philippines website and is authoritative."""
            direct_response = make_links_clickable(direct_response)
            manage_conversation_context(user_id, user_input, direct_response)
            
            # Enhanced debug info for Casto website person search
            debug_info = {
                "source": "Casto Website (Person Search)",
                "confidence": "High (88%)",
                "response_type": "Website Person Search Result",
                "processing_time": f"{processing_time}s",
                "knowledge_entries_checked": len(knowledge_entries),
                "person_searched": person_name,
                "website_sources": [r.get('source', 'Unknown') for r in casto_person_results],
                "search_method": "Website Scraping + Person Detection",
                "matched_keywords": [word for word in user_input.lower().split() if len(word) > 2],
                "fallback_used": False,
                "ai_model_bypassed": True,
                "response_quality": "Current Website Info",
                "intent_detected": "person_search"
            }
            
            return jsonify({
                "response": direct_response,
                "debug_info": debug_info
            })

        # CRITICAL: If we get here and it's a Casto question, DO NOT use AI model
        if any(k.lower() in user_input.lower() for k in casto_travel_keywords + ["maryles", "marc", "casto"]):
            logging.warning(f"CRITICAL: Casto question detected but falling through to AI model. This should not happen!")
            # Force a fallback response instead of using AI model
            fallback_response = "I need to check my knowledge base for the most current information about Casto Travel Philippines. Please contact Casto Travel Philippines directly for immediate assistance."
            manage_conversation_context(user_id, user_input, fallback_response)
            
            # Enhanced debug info for critical Casto fallback
            debug_info = {
                "source": "Critical Safety Fallback (Casto Question)",
                "confidence": "Very Low (20%)",
                "response_type": "Safety Fallback",
                "processing_time": f"{processing_time}s",
                "knowledge_entries_checked": len(knowledge_entries),
                "casto_keywords_detected": [k for k in casto_travel_keywords + ["maryles", "marc", "casto"] if k.lower() in user_input.lower()],
                "search_method": "Safety Check + Fallback",
                "matched_keywords": [word for word in user_input.lower().split() if len(word) > 2],
                "fallback_used": True,
                "ai_model_bypassed": True,
                "response_quality": "Safety Fallback (Limited)",
                "error_type": "Critical Safety Check Triggered",
                "safety_check": "Casto Question Blocked from AI"
            }
            
            return jsonify({
                "response": fallback_response,
                "debug_info": debug_info
            })

        # FINAL SAFETY CHECK: Prevent any Casto personnel questions from reaching the AI model
        casto_personnel_names = ["maryles casto", "marc casto", "elaine randrup", "alwin benedicto", "george anzures", "ma. berdandina galvez", "berdandina galvez"]
        if any(name.lower() in user_input.lower() for name in casto_personnel_names):
            logging.info(f"FINAL SAFETY CHECK: Blocking Casto personnel question from AI model: {user_input}")
            
            # Try one more time to get knowledge base response
            knowledge_response = check_knowledge_base_for_person(user_input, knowledge_entries)
            if knowledge_response:
                logging.info(f"FINAL CHECK: Found knowledge base entry, returning it")
                manage_conversation_context(user_id, user_input, knowledge_response)
                
                # Enhanced debug info for final safety check success
                debug_info = {
                    "source": "Knowledge Base (Final Safety Check)",
                    "confidence": "High (92%)",
                    "response_type": "Final Safety Check Success",
                    "processing_time": f"{processing_time}s",
                    "knowledge_entries_checked": len(knowledge_entries),
                    "person_detected": next((name for name in casto_personnel_names if name.lower() in user_input.lower()), "casto personnel"),
                    "search_method": "Final Safety Check + KB Lookup",
                    "matched_keywords": [word for word in user_input.lower().split() if len(word) > 2],
                    "fallback_used": False,
                    "ai_model_bypassed": True,
                    "response_quality": "Authoritative Personnel Info",
                    "safety_check": "Final Personnel Safety Check Passed"
                }
                
                return jsonify({
                    "response": knowledge_response,
                    "debug_info": debug_info
                })
            
            # If still no knowledge base response, return a clear message
            detected_person = next((name for name in casto_personnel_names if name.lower() in user_input.lower()), "this person")
            default_response = f"I should have information about {detected_person} in my knowledge base, but I'm unable to retrieve it. This appears to be a system issue. Please contact Casto Travel Philippines directly for information about their personnel."
            manage_conversation_context(user_id, user_input, default_response)
            
            # Enhanced debug info for final safety check failure
            debug_info = {
                "source": "Final Safety Fallback (Personnel KB Failure)",
                "confidence": "Very Low (15%)",
                "response_type": "Final Safety Check Failure",
                "processing_time": f"{processing_time}s",
                "knowledge_entries_checked": len(knowledge_entries),
                "person_detected": detected_person,
                "search_method": "Final Safety Check + KB Lookup (Failed)",
                "matched_keywords": [word for word in user_input.lower().split() if len(word) > 2],
                "fallback_used": True,
                "ai_model_bypassed": True,
                "response_quality": "Final Fallback (Limited)",
                "error_type": "Final Safety Check Failed",
                "safety_check": "Final Personnel Safety Check Failed"
            }
            
            return jsonify({
                "response": default_response,
                "debug_info": debug_info
            })

        # CRITICAL IDENTITY SAFETY CHECK: Prevent ANY identity questions from reaching the AI model
        identity_keywords = ["what does casi stand for", "what is casi", "who created you", "who built you", "who made you", "what's your name", "who are you", "your name", "your identity", "casi stands for", "casi meaning"]
        if any(keyword in user_input.lower() for keyword in identity_keywords):
            logging.info(f"CRITICAL IDENTITY SAFETY CHECK: Blocking identity question from AI model: {user_input}")
            
            # Force return appropriate identity response
            if "stand for" in user_input.lower() or "meaning" in user_input.lower():
                identity_response = get_casi_identity_response()
            elif "created" in user_input.lower() or "built" in user_input.lower() or "made" in user_input.lower():
                if check_specific_person_question(user_input):
                    identity_response = get_casi_specific_creator_response()
                else:
                    identity_response = get_casi_creator_response()
            elif "name" in user_input.lower() or "who are you" in user_input.lower():
                identity_response = get_casi_name_only_response()
            else:
                identity_response = get_casi_identity_response()
            
            logging.info(f"CRITICAL IDENTITY CHECK: Returning identity response: {identity_response[:100]}...")
            manage_conversation_context(user_id, user_input, identity_response)
            
            # Enhanced debug info for identity safety check
            debug_info = {
                "source": "Identity Safety System",
                "confidence": "High (95%)",
                "response_type": "Identity Question Response",
                "processing_time": f"{processing_time}s",
                "knowledge_entries_checked": len(knowledge_entries),
                "identity_question_type": next((qtype for qtype in ["stand_for", "creator", "name", "general"] if any(phrase in user_input.lower() for phrase in {
                    "stand_for": ["stand for", "meaning"],
                    "creator": ["created", "built", "made"],
                    "name": ["name", "who are you"],
                    "general": ["what is", "what's"]
                }[qtype])), "general"),
                "search_method": "Identity Keyword Detection + Pre-built Response",
                "matched_keywords": [word for word in user_input.lower().split() if len(word) > 2],
                "fallback_used": False,
                "ai_model_bypassed": True,
                "response_quality": "Authoritative Identity Info",
                "safety_check": "Identity Question Blocked from AI"
            }
            
            return jsonify({
                "response": identity_response,
                "debug_info": debug_info
            })

        # Fallback to model (only for non-Casto personnel and non-identity questions)
        import openai
        try:
            client = openai.OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
        except Exception as e:
            logging.error(f"Failed to create OpenAI client: {e}")
            return jsonify({"error": f"Client initialization failed: {str(e)}"}), 500

        logging.info("Fetching response from Groq.")
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7
        )
        chatbot_message = response.choices[0].message.content

        # CRITICAL: Ensure response is contextual for ongoing conversations
        if conversation_context and conversation_context.get('current_subject') and conversation_context.get('current_subject') != 'general inquiry':
            current_subject = conversation_context['current_subject']
            
            # Check if response is too generic and needs to be made more contextual
            if any(generic_phrase in chatbot_message.lower() for generic_phrase in [
                "how can i help you", "what would you like to know", "i'm here to help",
                "feel free to ask", "let me know if you need", "i'm ready to assist"
            ]):
                # Make the response more contextual
                contextual_intro = f"Continuing with our discussion about {current_subject}, "
                if not chatbot_message.lower().startswith(contextual_intro.lower()):
                    chatbot_message = contextual_intro + chatbot_message[0].lower() + chatbot_message[1:]
                logging.info(f"Made response more contextual for ongoing conversation about: {current_subject}")

        # Ensure CASI always identifies herself in responses
        if not any(phrase in chatbot_message.lower() for phrase in ["i'm casi", "as casi", "casi here", "this is casi"]):
            chatbot_message = f"I'm CASI, and {chatbot_message[0].lower() + chatbot_message[1:]}"

        combined_response = chatbot_message
        if website_data and "No relevant information found" not in website_data:
            combined_response += f"\n\nAdditional Information from Website:\n{website_data}"
        combined_response = make_links_clickable(combined_response)
        
        # Manage conversation context with enhanced resolution detection
        manage_conversation_context(user_id, user_input, combined_response)
        
        # Update conversation resolution status
        conversation_context = conversation_memory.get(user_id, None)
        if conversation_context:
            # Maintain IT troubleshooting context if applicable
            conversation_context = maintain_it_troubleshooting_context(user_input, conversation_context)
            conversation_context = update_conversation_resolution(user_input, combined_response, conversation_context)
            conversation_memory[user_id] = conversation_context
            
            # Debug logging for final context state
            logging.info(f"FINAL CONVERSATION CONTEXT:")
            logging.info(f"- Current Subject: {conversation_context.get('current_subject', 'None')}")
            logging.info(f"- Resolution Status: {conversation_context.get('resolution_status', 'None')}")
            logging.info(f"- Conversation Depth: {conversation_context.get('conversation_depth', 0)}")
            logging.info(f"- Is IT Troubleshooting: {is_it_troubleshooting_conversation(user_input, conversation_context)}")
        
        # Generate contextual follow-up suggestions
        follow_up_suggestions = generate_follow_up_suggestions(user_input, conversation_context, combined_response)
        
        logging.info(f"🎯 FINAL SOURCE: AI Model with KB instructions")
        logging.info(f"📝 AI Response: {combined_response[:200]}...")
        
        debug_messages.append(create_debug_message("AI_MODEL_SUCCESS", "AI model response generated successfully"))
        debug_messages.append(create_debug_message("RESPONSE_SOURCE", "AI Model (Groq Mixtral)"))
        debug_messages.append(create_debug_message("CONFIDENCE_LEVEL", "Medium (60%)"))
        debug_messages.append(create_debug_message("AI_MODEL_BYPASSED", "False - AI model used"))
        
        # Enhanced debug info for AI model responses
        debug_info = {
            "source": "AI Model (Groq Mixtral)",
            "confidence": "Medium (60%)",
            "response_type": "AI Generated",
            "processing_time": f"{processing_time}s",
            "knowledge_entries_checked": len(knowledge_entries),
            "ai_model_used": "mixtral-8x7b-32768",
            "temperature_setting": 0.7,
            "system_prompt_length": len(system_prompt),
            "search_method": "AI Model with KB Instructions",
            "matched_keywords": [word for word in user_input.lower().split() if len(word) > 2],
            "fallback_used": True,
            "ai_model_bypassed": False,
            "response_quality": "AI Generated",
            "safety_checks_passed": True,
            "knowledge_base_instructions": "Applied"
        }
        
        # Terminal debug output
        if DEBUG_MODE:
            print("\n" + "="*80)
            print("🎯 CASI DEBUG MODE - AI MODEL RESPONSE (LAST RESORT)")
            print("="*80)
            print(f"📝 User Query: '{user_input}'")
            print(f"🔍 Source: {debug_info['source']}")
            print(f"✅ Confidence: {debug_info['confidence']}")
            print(f"⚡ Processing Time: {debug_info['processing_time']}")
            print(f"📊 KB Entries Checked: {debug_info['knowledge_entries_checked']}")
            print(f"🤖 AI Model: {debug_info['ai_model_used']}")
            print(f"🌡️ Temperature: {debug_info['temperature_setting']}")
            print(f"📝 System Prompt Length: {debug_info['system_prompt_length']} chars")
            print(f"🔍 Search Method: {debug_info['search_method']}")
            print(f"🎯 Response Type: {debug_info['response_type']}")
            print(f"🔑 Matched Keywords: {debug_info['matched_keywords']}")
            print(f"⚠️ Fallback Used: {debug_info['fallback_used']}")
            print(f"🚫 AI Model Bypassed: {debug_info['ai_model_bypassed']}")
            print(f"⭐ Response Quality: {debug_info['response_quality']}")
            print(f"✅ Safety Checks: {debug_info['safety_checks_passed']}")
            print(f"📚 KB Instructions: {debug_info['knowledge_base_instructions']}")
            print("="*80 + "\n")
        
        return jsonify({
            "response": combined_response,
            "debug_info": debug_info,
            "debug_messages": echo_debug_to_client(debug_messages),
            "follow_up_suggestions": follow_up_suggestions,
            "conversation_context": {
                "current_subject": conversation_context.get('current_subject', 'general inquiry') if conversation_context else 'general inquiry',
                "resolution_status": conversation_context.get('resolution_status', 'ongoing') if conversation_context else 'ongoing',
                "current_focus": conversation_context.get('current_focus', 'general') if conversation_context else 'general',
                "conversation_depth": conversation_context.get('conversation_depth', 0) if conversation_context else 0,
                "recent_topics": list(conversation_context.get('topics', set()))[:5] if conversation_context else []
            }
        })

    except Exception as e:
        logging.error(f"Unexpected error in chat endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/test", methods=["GET"])
def test_endpoint():
    """Simple test endpoint for connectivity testing"""
    # Test knowledge base functionality
    knowledge_entries = get_cached_knowledge()
    test_person = "george anzures"
    knowledge_response = check_knowledge_base_for_person(f"who is {test_person}", knowledge_entries)
    
    # Test with the exact user input that's failing
    test_user_input = "Do you know George Anzures?"
    test_response = check_knowledge_base_for_person(test_user_input, knowledge_entries)
    
    return jsonify({
        "status": "success",
        "message": "Backend is reachable and responding - CASI Identity System Updated!",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoint": "/test",
        "knowledge_base_test": {
            "entries_count": len(knowledge_entries),
            "test_person": test_person,
            "knowledge_found": bool(knowledge_response),
            "sample_response": knowledge_response[:100] if knowledge_response else "None",
            "user_input_test": {
                "input": test_user_input,
                "response_found": bool(test_response),
                "response": test_response[:100] if test_response else "None"
            }
        }
    })

@app.route("/conversation/context", methods=["GET"])
def get_conversation_context():
    """Get enhanced conversation context for a user."""
    access_token = request.args.get("access_token")
    email = get_user_email_from_token(access_token) if access_token else "test@example.com"
    
    user_id = email
    if user_id in conversation_memory:
        conv = conversation_memory[user_id]
        return jsonify({
            "user_id": user_id,
            "conversation_summary": {
                "total_exchanges": len(conv['history']),
                "conversation_depth": conv.get('conversation_depth', 0),
                "current_focus": conv.get('current_focus', 'general'),
                "last_updated": conv['last_updated']
            },
            "topics": {
                "all_topics": list(conv['topics']),
                "recent_topics": list(conv['topics'])[:5],
                "primary_focus": conv.get('current_focus', 'general')
            },
            "user_preferences": list(conv.get('user_preferences', set())),
            "related_questions": conv.get('related_questions', [])[-5:],
            "conversation_flow": [
                {
                    "exchange": i + 1,
                    "user_input": exchange.get('user_input', ''),
                    "intent": exchange.get('intent', 'unknown'),
                    "topics": list(exchange.get('topics', set())),
                    "timestamp": exchange.get('timestamp', 0)
                }
                for i, exchange in enumerate(conv['history'][-5:])
            ]
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
        # search_results = smart_web_search(query)
        search_results = None  # Temporarily disabled for Vercel deployment
        
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
        # with DDGS() as ddgs:
        #     results = list(ddgs.text(query, max_results=8))  # More results for general search
            
        #     if results:
        #         formatted_results = []
        #         for result in results:
        #             formatted_results.append({
        #             'title': result.get('title', ''),
        #             'snippet': result.get('body', ''),
        #             'url': result.get('link', ''),
        #             'source': 'General Web Search',
        #             'search_type': 'General',
        #             'original_query': query
        #             })
                
        #         return jsonify({
        #             "success": True,
        #             "results": formatted_results,
        #             "query": query,
        #             "search_type": "General",
        #             "message": "General web search completed"
        #         })
        #     else:
        #         return jsonify({
        #             "success": False,
        #             "message": "No general search results found",
        #             "query": query
        #         })
        
        # Temporarily disabled for Vercel deployment
        return jsonify({
            "success": False,
            "message": "Web search temporarily disabled for deployment",
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
        # search_results = smart_web_search(query)
        search_results = None  # Temporarily disabled for Vercel deployment
        
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

def detect_conversation_resolution(user_input, response, conversation_context):
    """Enhanced detection of when a conversation subject is resolved."""
    user_input_lower = user_input.lower()
    response_lower = response.lower()
    
    # Strong resolution indicators
    strong_resolution_phrases = [
        "thank you", "thanks", "that helps", "got it", "understood", 
        "perfect", "great", "excellent", "that's what i needed",
        "solved", "resolved", "figured out", "clear now", "got my answer",
        "that answers my question", "exactly what i was looking for",
        "that's perfect", "that's all i need", "that covers it"
    ]
    
    # Moderate resolution indicators
    moderate_resolution_phrases = [
        "okay", "ok", "alright", "good", "fine", "sure", "yes",
        "i see", "i understand", "gotcha", "makes sense"
    ]
    
    # Check for strong resolution
    if any(phrase in user_input_lower for phrase in strong_resolution_phrases):
        return "resolved"
    
    # Check for moderate resolution with context
    if any(phrase in user_input_lower for phrase in moderate_resolution_phrases):
        # If this is a short response after a detailed answer, likely resolved
        if len(user_input.split()) <= 3 and len(response) > 100:
            return "resolved"
    
    # Check if response contains complete information
    if len(response) > 300 and any(word in response_lower for word in [
        "complete", "finished", "all set", "ready", "everything you need",
        "full information", "comprehensive details", "complete answer"
    ]):
        return "resolved"
    
    # Check for new topic indicators (suggesting previous topic is resolved)
    new_topic_indicators = [
        "what about", "how about", "can you tell me about", "i want to know about",
        "different question", "another thing", "by the way", "also"
    ]
    
    if any(phrase in user_input_lower for phrase in new_topic_indicators):
        return "resolved"
    
    return "ongoing"

def update_conversation_resolution(user_input, response, conversation_context):
    """Update conversation resolution status based on user input and response."""
    if not conversation_context:
        return conversation_context
    
    resolution_status = detect_conversation_resolution(user_input, response, conversation_context)
    
    if resolution_status == "resolved":
        conversation_context['resolution_status'] = 'resolved'
        # Mark the subject as resolved but keep it for context
        conversation_context['subject_resolved_at'] = time.time()
    
    return conversation_context



def should_continue_subject(user_input, conversation_context):
    """Determine if we should continue with the current subject."""
    if not conversation_context or not conversation_context.get('current_subject'):
        return False
    
    # Check if user is asking for more details about current subject
    current_subject = conversation_context['current_subject'].lower()
    user_input_lower = user_input.lower()
    
    # Continue if user asks for more details, clarification, or related questions
    continuation_indicators = [
        "more", "tell me more", "explain", "elaborate", "what about",
        "how about", "can you", "could you", "please", "also",
        "additionally", "furthermore", "besides", "other", "different",
        "yes", "no", "okay", "ok", "sure", "alright", "good", "fine"
    ]
    
    # Check if input is related to current subject
    subject_keywords = current_subject.split()
    if any(keyword in user_input_lower for keyword in subject_keywords):
        return True
    
    # Check for continuation phrases
    if any(phrase in user_input_lower for phrase in continuation_indicators):
        return True
    
    # Check if this is a short response (likely a follow-up)
    if len(user_input.split()) <= 5:
        # Check if the current subject is IT troubleshooting or technical
        if any(word in current_subject for word in ['mouse', 'keyboard', 'computer', 'troubleshooting', 'internet', 'connection']):
            # Short responses in technical conversations are likely follow-ups
            return True
    
    # Check if this is a response to a question we asked
    if conversation_context.get('history'):
        last_exchange = conversation_context['history'][-1]
        last_response = last_exchange.get('response', '')
        
        # If our last response asked a question, this is likely an answer
        if any(word in last_response.lower() for word in ['what', 'how', 'when', 'where', 'why', 'which', 'do you', 'have you', 'can you']):
            return True
    
    # Check for pronouns that refer to previous context
    pronouns = ["it", "this", "that", "they", "them", "their", "the problem", "the issue", "the mouse", "the computer"]
    if any(pronoun in user_input_lower for pronoun in pronouns):
        return True
    
    return False

def is_it_troubleshooting_conversation(user_input, conversation_context):
    """Check if this is an IT troubleshooting conversation that should maintain context."""
    if not conversation_context:
        return False
    
    current_subject = conversation_context.get('current_subject', '').lower()
    user_input_lower = user_input.lower()
    
    # IT troubleshooting subjects
    it_subjects = [
        'mouse', 'keyboard', 'computer', 'internet', 'connection',
        'software', 'hardware', 'troubleshooting', 'problem', 'issue',
        'not working', 'broken', 'error', 'slow', 'freeze'
    ]
    
    # Check if current subject is IT-related
    if any(subject in current_subject for subject in it_subjects):
        return True
    
    # Check if user input is IT-related
    if any(subject in user_input_lower for subject in it_subjects):
        return True
    
    # Check if this is a follow-up to IT troubleshooting
    if conversation_context.get('history'):
        recent_exchanges = conversation_context['history'][-3:]
        for exchange in recent_exchanges:
            if any(subject in exchange.get('user_input', '').lower() for subject in it_subjects):
                return True
    
    return False

def maintain_it_troubleshooting_context(user_input, conversation_context):
    """Ensure IT troubleshooting conversations maintain proper context."""
    if not is_it_troubleshooting_conversation(user_input, conversation_context):
        return conversation_context
    
    # Force the subject to remain IT troubleshooting if it's related
    if conversation_context.get('current_subject'):
        current_subject = conversation_context['current_subject'].lower()
        if any(word in current_subject for word in ['mouse', 'keyboard', 'computer', 'troubleshooting']):
            # Keep the IT troubleshooting context
            conversation_context['current_subject'] = current_subject
            conversation_context['resolution_status'] = 'ongoing'
            logging.info(f"Maintaining IT troubleshooting context: {current_subject}")
    
    return conversation_context

@app.route("/test/kb", methods=["GET"])
def test_knowledge_base():
    """Test endpoint to verify knowledge base functionality"""
    try:
        knowledge_entries = get_cached_knowledge()
        
        # Test a specific query
        test_query = "Who is Maryles Casto?"
        test_result = check_knowledge_base_for_person(test_query, knowledge_entries)
        
        return jsonify({
            "status": "success",
            "knowledge_base_test": {
                "entries_count": len(knowledge_entries),
                "entries_type": str(type(knowledge_entries)),
                "sample_entry": knowledge_entries[0] if knowledge_entries else None,
                "test_query": test_query,
                "test_result_found": bool(test_result),
                "test_result": test_result[:200] if test_result else None,
                "knowledge_context_sample": "\n".join([f"Q: {entry.get('question', '')} A: {entry.get('answer', '')}" for entry in knowledge_entries])[:300] if knowledge_entries else None
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "knowledge_base_test": None
        })

@app.route("/debug/format", methods=["GET"])
def debug_format_demo():
    """Demo endpoint showing the new enhanced debug format"""
    return jsonify({
        "message": "This is how the new debug format will look in chat responses",
        "example_response": {
            "response": "As CASI, Maryles Casto is the founder of Casto Travel Philippines...",
            "debug_info": {
                "source": "Knowledge Base",
                "confidence": "High (95%)",
                "response_type": "Direct Match",
                "processing_time": "0.15s",
                "knowledge_entries_checked": 42,
                "search_method": "Fuzzy Name Matching",
                "matched_keywords": ["maryles", "casto"],
                "fallback_used": False,
                "ai_model_bypassed": True,
                "response_quality": "Authoritative"
            }
        },
        "debug_fields_explained": {
            "source": "Where the answer came from (KB, AI, Website, etc.)",
            "confidence": "How confident CASI is in the answer (with percentage)",
            "response_type": "Type of response generated",
            "processing_time": "How long it took to process the request",
            "knowledge_entries_checked": "Number of KB entries searched",
            "search_method": "Method used to find the answer",
            "matched_keywords": "Keywords that triggered the response",
            "fallback_used": "Whether a fallback response was used",
            "ai_model_bypassed": "Whether the AI model was bypassed for safety",
            "response_quality": "Quality rating of the response"
        },
        "response_sources": [
            "Knowledge Base - Most authoritative (95-98% confidence)",
            "Casto Website - Current information (85-90% confidence)", 
            "Contextual Response - Pre-built templates (70-80% confidence)",
            "AI Model - Generated responses (50-70% confidence)",
            "Safety Fallback - Error handling (15-30% confidence)"
        ]
    })

@app.route("/debug/toggle", methods=["POST"])
def toggle_debug_mode():
    """Toggle debug mode on/off"""
    global DEBUG_MODE
    try:
        data = request.get_json() or {}
        new_mode = data.get('debug_mode', not DEBUG_MODE)
        DEBUG_MODE = bool(new_mode)
        
        return jsonify({
            "status": "success",
            "message": f"Debug mode {'enabled' if DEBUG_MODE else 'disabled'}",
            "debug_mode": DEBUG_MODE,
            "note": "Changes take effect immediately for new requests"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "current_debug_mode": DEBUG_MODE
        })

@app.route("/debug/status", methods=["GET"])
def get_debug_status():
    """Get current debug mode status"""
    return jsonify({
        "debug_mode": DEBUG_MODE,
        "message": f"Debug mode is currently {'enabled' if DEBUG_MODE else 'disabled'}",
        "note": "When enabled, you'll see detailed debug info in the terminal for each chat request"
    })

def create_debug_message(message_type, details):
    """Create a debug message for local terminal display"""
    if not LOCAL_DEBUG_ECHO:
        return None
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    return f"[DEBUG] [{timestamp}] {message_type}: {details}"

def echo_debug_to_client(debug_messages):
    """Echo debug messages back to client for local terminal display"""
    if not LOCAL_DEBUG_ECHO or not debug_messages:
        return []
    
    return [msg for msg in debug_messages if msg]
