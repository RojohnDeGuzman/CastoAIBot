# Power Automate Configuration for CASI Chatbot
import requests
import json
from datetime import datetime

# Power Automate Webhook URL
POWER_AUTOMATE_URL = "https://prod-88.southeastasia.logic.azure.com:443/workflows/e1ba333c4808479c86c7251c0ebb2c6b/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=Dcvy8b0SH8SM_-ux4hefDRUqC1maFD0Ft2yLZ-hr6Cg"

def send_power_automate_alert(alert_data):
    """Send IT alert to Power Automate"""
    try:
        # Prepare the data for Power Automate
        power_automate_data = {
            "priority": alert_data.get("priority", "General"),
            "windows_user": alert_data.get("windows_user", "Unknown"),
            "hostname": alert_data.get("hostname", "Unknown"),
            "concern": alert_data.get("concern", "No concern specified"),
            "timestamp": alert_data.get("timestamp", datetime.now().isoformat()),
            "source": "CASI Chatbot"
        }
        
        print(f"📤 Sending to Power Automate: {json.dumps(power_automate_data, indent=2)}")
        
        # Send to Power Automate
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            POWER_AUTOMATE_URL,
            headers=headers,
            json=power_automate_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Power Automate alert sent successfully")
            return True
        else:
            print(f"❌ Power Automate failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending to Power Automate: {e}")
        return False

def test_power_automate():
    """Test Power Automate integration"""
    test_alert = {
        "priority": "High",
        "windows_user": "RODeguzman",
        "hostname": "CTPI-LPTP-02031",
        "concern": "Test alert from Power Automate",
        "timestamp": datetime.now().isoformat(),
        "source": "CASI Chatbot"
    }
    
    print("🧪 Testing Power Automate Integration...")
    result = send_power_automate_alert(test_alert)
    
    if result:
        print("✅ Power Automate test successful!")
    else:
        print("❌ Power Automate test failed!")
    
    return result

if __name__ == "__main__":
    test_power_automate()
