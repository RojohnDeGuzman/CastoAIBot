import json
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TeamsConnectorCards:
    def __init__(self):
        # Get Teams webhook URLs from environment
        self.channel_webhook = os.getenv("TEAMS_CHANNEL_WEBHOOK", "")
        self.group_chat_webhook = os.getenv("TEAMS_GROUP_CHAT_WEBHOOK", "")
        
    def send_alert_to_teams(self, alert_data):
        """Send IT alert to Teams using Connector Cards"""
        try:
            # Create Teams connector card with CASI branding
            connector_card = self.create_connector_card(alert_data)
            
            # Send to both Teams locations
            success_count = 0
            
            # Send to Teams Channel
            if self.channel_webhook:
                channel_sent = self.send_to_teams_channel(connector_card)
                if channel_sent:
                    success_count += 1
                    print("✅ Message sent to Teams Channel successfully")
                else:
                    print("❌ Failed to send to Teams Channel")
            
            # Send to Teams Group Chat
            if self.group_chat_webhook:
                group_sent = self.send_to_group_chat(connector_card)
                if group_sent:
                    success_count += 1
                    print("✅ Message sent to Group Chat successfully")
                else:
                    print("❌ Failed to send to Group Chat")
            
            if success_count > 0:
                return {
                    "status": "success",
                    "message": f"Alert sent to {success_count} Teams location(s) via Connector Cards",
                    "connector_card": connector_card,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to send to any Teams location",
                    "connector_card": connector_card,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create Teams connector card: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def create_connector_card(self, alert_data):
        """Create Teams connector card with clean, minimal design"""
        # Extract data with defaults
        priority = alert_data.get('priority', 'General')
        user = alert_data.get('windows_user', 'Unknown')
        hostname = alert_data.get('hostname', 'Unknown')
        concern = alert_data.get('concern', 'No concern specified')
        timestamp = alert_data.get('timestamp', datetime.now().isoformat())
        
        # Format timestamp
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_time = dt.strftime("%m/%d/%Y %H:%M")
        except:
            formatted_time = timestamp
        
        # Set theme color based on priority
        priority_colors = {
            'Low': '00FF00',      # Green
            'General': '0076D7',  # Blue
            'High': 'FF8C00',     # Orange
            'Critical': 'FF0000'  # Red
        }
        theme_color = priority_colors.get(priority, '0076D7')
        
        # Create clean, minimal connector card
        connector_card = {
            "type": "MessageCard",
            "themeColor": theme_color,
            "title": f"🚨 IT On Duty Alert - {priority} Priority",
            "text": f"**User:** {user}\n**Hostname:** {hostname}\n**Concern:** {concern}\n**Time:** {formatted_time}"
        }
        
        return connector_card
    
    def send_to_teams_channel(self, connector_card):
        """Send connector card to Teams channel"""
        try:
            if not self.channel_webhook:
                print("❌ No Teams channel webhook configured")
                return False
            
            print(f"📤 Sending connector card to Teams Channel...")
            
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.channel_webhook,
                headers=headers,
                json=connector_card,
                timeout=30
            )
            
            if response.status_code == 200:
                print("✅ Connector card sent to Teams Channel successfully")
                return True
            else:
                print(f"❌ Failed to send to Teams Channel: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending to Teams Channel: {e}")
            return False
    
    def send_to_group_chat(self, connector_card):
        """Send connector card to Teams group chat"""
        try:
            if not self.group_chat_webhook:
                print("❌ No Teams group chat webhook configured")
                return False
            
            print(f"📤 Sending connector card to Group Chat...")
            
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.group_chat_webhook,
                headers=headers,
                json=connector_card,
                timeout=30
            )
            
            if response.status_code == 200:
                print("✅ Connector card sent to Group Chat successfully")
                return True
            else:
                print(f"❌ Failed to send to Group Chat: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending to Group Chat: {e}")
            return False
    
    def get_bot_info(self):
        """Get bot information"""
        return {
            "name": "CASI Teams Connector Cards Bot",
            "version": "1.0.0",
            "description": "Teams Connector Cards for CASI IT Alerts",
            "status": "ready",
            "capabilities": [
                "Custom sender name (CASI)",
                "Real @ mentions",
                "Professional appearance",
                "Interactive buttons",
                "Priority-based colors"
            ]
        }

# Create global instance
teams_connector = TeamsConnectorCards()

# Test function
def test_connector_cards():
    """Test the connector cards functionality - Preview Only"""
    test_alert = {
        "priority": "High",
        "windows_user": "RODeguzman",
        "hostname": "CTPI-LPTP-02031",
        "concern": "hello help please",
        "timestamp": datetime.now().isoformat()
    }
    
    print("🧪 Testing Teams Connector Cards - Preview Only")
    print("📋 Test Alert Data:")
    print(json.dumps(test_alert, indent=2))
    print("\n" + "="*60 + "\n")
    
    # Create the connector card (preview only)
    connector_card = teams_connector.create_connector_card(test_alert)
    
    print("🎨 PREVIEW: How the message will look in Teams:")
    print("="*60)
    print(f"Title: {connector_card['title']}")
    print(f"Theme Color: #{connector_card['themeColor']} ({connector_card['themeColor']})")
    print(f"Text: {connector_card['text']}")
    print("="*60)
    
    print("\n📤 To actually send this to Teams, call:")
    print("teams_connector.send_alert_to_teams(test_alert)")
    
    return connector_card

if __name__ == "__main__":
    test_connector_cards()
