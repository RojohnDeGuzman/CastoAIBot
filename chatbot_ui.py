from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QWidget, QSizePolicy, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout, QLabel, QMessageBox, QScrollArea, QInputDialog, QFileDialog, QGraphicsDropShadowEffect, QProgressBar, QCheckBox
from PyQt5.QtCore import Qt, QRect, QEasingCurve, QTimer, QPoint, QSize, QPropertyAnimation, QObject, pyqtProperty
from PyQt5.QtGui import QIcon, QFont, QPainter, QColor, QBrush, QPixmap, QPainterPath, QTextOption, QCursor
from PyQt5.QtWidgets import QGraphicsOpacityEffect
import sys
import requests
import json
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QLinearGradient
import win32com.client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import msal
import os
import getpass
from datetime import datetime
import base64
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from collections import Counter
import re
import atexit
import psutil
import ctypes
from ctypes import wintypes
import socket
from urllib.parse import urlparse
from config import get_backend_url, get_client_id, get_tenant_id, get_admin_email, get_teams_webhook_url, get_single_instance_enabled

MUTEX_NAME = "Global\\CASIAppMutex"

SINGLE_INSTANCE_PORT = 54321  # Pick any unused port

# Backend configuration - now loaded from config
BACKEND_URL = get_backend_url()

def test_backend_connectivity():
    """Test if the backend is reachable and return detailed error information."""
    import socket
    import requests
    
    # Parse the backend URL
    from urllib.parse import urlparse
    parsed_url = urlparse(BACKEND_URL)
    host = parsed_url.hostname
    port = parsed_url.port or 80
    
    # Test 1: Basic socket connection
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        if result != 0:
            return False, f"Socket connection failed: Cannot reach {host}:{port}"
    except Exception as e:
        return False, f"Socket connection error: {str(e)}"
    
    # Test 2: HTTP request - try chat endpoint to check if backend is reachable
    try:
        response = requests.post(f"{BACKEND_URL}/chat", json={"message": "test"}, timeout=10)
        if response.status_code == 403:
            # 403 means the endpoint exists but requires authentication - this is expected
            return True, "Backend is reachable (authentication required)"
        elif response.status_code == 200:
            return True, "Backend is reachable"
        else:
            return False, f"Backend responded with status code: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, f"Connection refused: Backend at {BACKEND_URL} is not responding"
    except requests.exceptions.Timeout:
        return False, f"Connection timeout: Backend at {BACKEND_URL} is not responding within 10 seconds"
    except requests.exceptions.RequestException as e:
        return False, f"Request failed: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def get_network_diagnostics():
    """Get network diagnostics information."""
    import socket
    import subprocess
    import platform
    
    diagnostics = []
    
    # Get local IP
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        diagnostics.append(f"Local IP: {local_ip}")
    except Exception as e:
        diagnostics.append(f"Local IP: Error - {str(e)}")
    
    # Get backend hostname
    from urllib.parse import urlparse
    parsed_url = urlparse(BACKEND_URL)
    backend_host = parsed_url.hostname
    
    # Test DNS resolution
    try:
        resolved_ip = socket.gethostbyname(backend_host)
        diagnostics.append(f"Backend DNS resolution: {backend_host} -> {resolved_ip}")
    except Exception as e:
        diagnostics.append(f"Backend DNS resolution: Failed - {str(e)}")
    
    # Test ping (if available)
    try:
        if platform.system().lower() == "windows":
            result = subprocess.run(["ping", "-n", "1", backend_host], 
                                  capture_output=True, text=True, timeout=10)
        else:
            result = subprocess.run(["ping", "-c", "1", backend_host], 
                                  capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            diagnostics.append(f"Ping to backend: Success")
        else:
            diagnostics.append(f"Ping to backend: Failed")
    except Exception as e:
        diagnostics.append(f"Ping test: Error - {str(e)}")
    
    return diagnostics

def already_running_socket():
    """Returns True if another instance is running, False otherwise."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("127.0.0.1", SINGLE_INSTANCE_PORT))
        # Keep the socket open for the life of the app
        import atexit
        atexit.register(s.close)
        return False
    except socket.error as e:
        print(f"[DEBUG] Socket already in use: {e}")
        return True  # Port is already in use
    except Exception as e:
        print(f"[DEBUG] Socket detection error: {e}")
        return False  # Assume not running if we can't determine

class SingleInstance:
    def __init__(self, mutexname=MUTEX_NAME):
        self.mutexname = mutexname
        self.kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        self.mutex = self.kernel32.CreateMutexW(None, wintypes.BOOL(False), self.mutexname)
        self.last_error = ctypes.GetLastError()
        # Debug print for troubleshooting
        print(f"[DEBUG] Mutex created, last_error={self.last_error}")

    def already_running(self):
        # ERROR_ALREADY_EXISTS == 183
        return self.last_error == 183

class MultiLineInputDialog(QDialog):
    def __init__(self, title, label, parent=None, prefill_text=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.selected_attachment = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(label))

        self.text_edit = QTextEdit()
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #34495e;
                border: 2px solid #34495e;
                border-radius: 8px;
                color: #ecf0f1;
                font-size: 13px;
                padding: 8px;
            }
        """)
        if prefill_text:
            self.text_edit.setPlainText(prefill_text)
        layout.addWidget(self.text_edit)

        # OK/Cancel/Attach buttons (all in one row)
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("Send")
        ok_btn.setStyleSheet(dialog_button_style)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(dialog_button_style)

        # Attach file button with icon and label
        self.attach_btn = QPushButton()
        self.attach_btn.setIcon(QIcon(resource_path("attachment.png")))
        self.attach_btn.setIconSize(QSize(20, 20))
        self.attach_btn.setFixedSize(36, 36)
        self.attach_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                border: none;
                border-radius: 18px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.attach_btn.setToolTip("Attach a file")
        self.attach_btn.clicked.connect(self.attach_file)
        self.attachment_label = QLabel("No file attached")
        self.attachment_label.setStyleSheet("color: #bdc3c7; font-size: 12px;")

        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(self.attach_btn)
        button_layout.addWidget(self.attachment_label)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setStyleSheet("""
            QDialog {
                background-color: #2c3e50;
                border-radius: 12px;
            }
        """)

    def attach_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Attach a file (optional)")
        if file_path:
            self.selected_attachment = file_path
            self.attachment_label.setText(f"Attached: {file_path.split('/')[-1]}")
            self.attachment_label.setStyleSheet("color: #2ecc71; font-size: 12px;")
        else:
            self.selected_attachment = None
            self.attachment_label.setText("No file attached")
            self.attachment_label.setStyleSheet("color: #bdc3c7; font-size: 12px;")

    def getText(self):
        return self.text_edit.toPlainText().strip()

    def getAttachment(self):
        return self.selected_attachment

class ITOnDutyDialog(QDialog):
    def __init__(self, parent=None, prefill_text=None):
        super().__init__(parent)
        self.setWindowTitle("Your concern")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Please enter your concern for IT On Duty:"))

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Type your concern here...")
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #34495e;
                border: 2px solid #34495e;
                border-radius: 8px;
                color: #ecf0f1;
                font-size: 13px;
                padding: 8px;
            }
        """)
        if prefill_text:
            self.text_edit.setPlainText(prefill_text)
        layout.addWidget(self.text_edit)
        button_layout = QHBoxLayout()
        send_btn = QPushButton("Send")
        send_btn.setStyleSheet(dialog_button_style)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(dialog_button_style)
        send_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(send_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

    def getText(self):
        return self.text_edit.toPlainText()  

class ChatInput(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.send_callback = None  # Set this to your send function

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and not (event.modifiers() & Qt.ShiftModifier):
            if self.send_callback:
                self.send_callback()
            return  # Prevent newline on Enter
        super().keyPressEvent(event)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        if hasattr(sys, '_MEIPASS'):
            # Running in PyInstaller bundle
            path = os.path.join(sys._MEIPASS, relative_path)
            if os.path.exists(path):
                return path
            else:
                # Try alternative paths
                alt_path = os.path.join(sys._MEIPASS, ".", relative_path)
                if os.path.exists(alt_path):
                    return alt_path
                return path  # Return original path anyway
        else:
            # Running in development
            path = os.path.join(os.path.abspath("."), relative_path)
            return path
    except Exception as e:
        return relative_path

# Teams webhook for IT On Duty channel
TEAMS_WEBHOOK_URL = get_teams_webhook_url()

def send_teams_message(message):
    headers = {"Content-Type": "application/json"}
    payload = {"text": message}
    try:
        response = requests.post(TEAMS_WEBHOOK_URL, headers=headers, data=json.dumps(payload))
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to send Teams message: {e}")
        return False

def send_teams_message_as_casi_bot(message_data):
    """Send Teams message as CASI bot using webhook with bot identity."""
    try:
        # Create a message that will appear to come from CASI bot
        teams_message = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "type": "AdaptiveCard",
                        "version": "1.0",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": "🤖 **CASI IT On Duty Alert**",
                                "weight": "Bolder",
                                "size": "Medium",
                                "color": "Accent"
                            },
                            {
                                "type": "FactSet",
                                "facts": [
                                    {
                                        "title": "Priority:",
                                        "value": message_data.get("priority", "General")
                                    },
                                    {
                                        "title": "User:",
                                        "value": message_data.get("windows_user", "Unknown")
                                    },
                                    {
                                        "title": "Hostname:",
                                        "value": message_data.get("hostname", "Unknown")
                                    },
                                    {
                                        "title": "Time:",
                                        "value": message_data.get("timestamp", "Unknown")
                                    },
                                    {
                                        "title": "Source:",
                                        "value": "CASI"
                                    }
                                ]
                            },
                            {
                                "type": "TextBlock",
                                "text": "**Concern:**",
                                "weight": "Bolder",
                                "spacing": "Medium"
                            },
                            {
                                "type": "TextBlock",
                                "text": message_data.get("concern", "No concern specified"),
                                "wrap": True,
                                "spacing": "Small"
                            }
                        ]
                    }
                }
            ]
        }
        
        # Send to Teams webhook
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            TEAMS_WEBHOOK_URL, 
            headers=headers, 
            json=teams_message, 
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Teams message sent successfully as CASI bot")
            return True
        else:
            print(f"❌ Teams webhook failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending Teams message as CASI bot: {e}")
        return False

# Power Automate function removed - now using Azure Bot


class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        
        self.setStyleSheet("background-color: #1abc9c; color: white; border-radius: 5px; padding: 10px;")
        self.default_style = "background-color: #1abc9c; color: white; border-radius: 5px; padding: 10px;"
        self.hover_style = "background-color: #16a085; color: white; border-radius: 5px; padding: 10px;"
        self.clicked_style = "background-color: #148f77; color: white; border-radius: 5px; padding: 10px;"

        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(200)
        self.opacity_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        self.scale_animation = QPropertyAnimation(self, b"geometry")
        self.scale_animation.setDuration(300)
        self.scale_animation.setEasingCurve(QEasingCurve.OutBack)

        self.setMouseTracking(True)
    
    def enterEvent(self, event):
        self.setStyleSheet(self.hover_style)
        self.opacity_animation.setStartValue(1.0)
        self.opacity_animation.setEndValue(0.9)
        self.opacity_animation.start()

        if not self.scale_animation.state() == QPropertyAnimation.Running:
            self.scale_animation.setStartValue(self.geometry())
            self.scale_animation.setEndValue(QRect(self.x() - 2, self.y() - 2, self.width() + 4, self.height() + 4))
            self.scale_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(self.default_style)
        self.opacity_animation.setStartValue(0.9)
        self.opacity_animation.setEndValue(1.0)
        self.opacity_animation.start()

        if not self.scale_animation.state() == QPropertyAnimation.Running:
            self.scale_animation.setStartValue(self.geometry())
            self.scale_animation.setEndValue(QRect(self.x() + 2, self.y() + 2, self.width() - 4, self.height() - 4))
            self.scale_animation.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.setStyleSheet(self.clicked_style)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.setStyleSheet(self.hover_style)
        super().mouseReleaseEvent(event)


class MinimizedWidget(QWidget):
    def __init__(self, floating_widget):
        super().__init__()
        self.floating_widget = floating_widget
        self.initUI()
        self.oldPos = None
    
    def initUI(self):
        self.setWindowTitle("Minimized Widget")
        self.setGeometry(10, 10, 50, 50)
        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: rgba(44, 62, 80, 0.5); color: white; border-radius: 10px;")

        layout = QVBoxLayout()

        self.expand_button = AnimatedButton("<", self)
        self.expand_button.clicked.connect(self.expand_widget)
        layout.addWidget(self.expand_button)

        self.setLayout(layout)
    
    def expand_widget(self):
        self.hide()
        self.floating_widget.fade_in()  # Use fade_in for animation and to restore opacity
        move_to_right_middle(self.floating_widget)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.oldPos is not None:
            delta = event.globalPos() - self.oldPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

            
        

        

class ChatbotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.gradient_shift = 0
        self.gradient_timer = QTimer(self)
        self.gradient_timer.start(40)
        self.conversation_history = []
        self.user_first_name = "User"
        self.default_user_pixmap = get_circular_pixmap("default_user.png", 36)
        self.user_pixmap = self.default_user_pixmap
        self.initUI()
        self.oldPos = self.pos()
        self.typing_animation_timer = None
        self.typing_dot_count = 0

    
    def fetch_user_profile(self, access_token):
        """Fetch the user's profile from Microsoft Graph and store the first name."""
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers)
            if response.status_code == 200:
                profile = response.json()
                email = profile.get("mail") or profile.get("userPrincipalName", "")
                # Extract first name from email (before @)
                if email and "@" in email:
                    self.user_first_name = email.split("@")[0].split(".")[0].capitalize()
                else:
                    self.user_first_name = "User"
            else:
                self.user_first_name = "User"
        except Exception as e:
            print(f"Failed to fetch user profile: {e}")
            self.user_first_name = "User"
        return self.user_first_name

    def fetch_user_photo(self, access_token):
        """Fetch the user's profile photo from Microsoft Graph and store it."""
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get("https://graph.microsoft.com/v1.0/me/photo/$value", headers=headers)
            if response.status_code == 200:
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                self.user_pixmap = get_circular_pixmap(pixmap, 36)
                print("Fetched Office 365 photo successfully.")
                return True
            else:
                self.user_pixmap = self.default_user_pixmap
                print("Failed to fetch Office 365 photo, using default.")
                return False
        except Exception as e:
            print(f"Failed to fetch user photo: {e}")
            self.user_pixmap = self.default_user_pixmap
            return False

    def fade_in(self, duration=350):
        self.setWindowOpacity(0)
        self.show()
        anim = QPropertyAnimation(self, b"windowOpacity")
        anim.setDuration(duration)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()
        self._fade_anim = anim

    def fade_out(self, duration=300):
        anim = QPropertyAnimation(self, b"windowOpacity")
        anim.setDuration(duration)
        anim.setStartValue(self.windowOpacity())
        anim.setEndValue(0)
        anim.setEasingCurve(QEasingCurve.InCubic)
        anim.finished.connect(self.hide)
        anim.start()
        self._fade_anim = anim  # Prevent garbage collection    

    def slide_in_message(self, wrapper, sender="bot"):
        """Slide in the message bubble from left (bot) or right (user) with fade-in."""
        # Fade-in
        effect = QGraphicsOpacityEffect()
        wrapper.setGraphicsEffect(effect)
        fade_anim = QPropertyAnimation(effect, b"opacity")
        fade_anim.setDuration(300)
        fade_anim.setStartValue(0.0)
        fade_anim.setEndValue(1.0)
        fade_anim.start()
        wrapper._fade_anim = fade_anim  # Prevent garbage collection

        # Slide-in by animating X position
        wrapper.show()
        wrapper.raise_()
        wrapper.repaint()
        QTimer.singleShot(0, lambda: self._start_slide(wrapper, sender))

    def _start_slide(self, wrapper, sender):
        parent = wrapper.parentWidget()
        if not parent:
            return
        start_offset = -wrapper.width() if sender == "bot" else wrapper.width()
        end_pos = wrapper.pos()
        start_pos = end_pos + QPoint(start_offset, 0)
        wrapper.move(start_pos)
        slide_anim = QPropertyAnimation(wrapper, b"pos")
        slide_anim.setDuration(350)
        slide_anim.setStartValue(start_pos)
        slide_anim.setEndValue(end_pos)
        slide_anim.setEasingCurve(QEasingCurve.OutCubic)
        slide_anim.start()
        wrapper._slide_anim = slide_anim  # Prevent garbage collection

    def add_hover_animation(self, button):
        button.installEventFilter(self)
        button._hover_anim = QPropertyAnimation(button, b"geometry")
        button._hover_anim.setDuration(120)    

    def eventFilter(self, obj, event):
        # Animate scale on hover for top bar buttons
        if isinstance(obj, QPushButton) and hasattr(obj, "_hover_anim"):
            if event.type() == event.Enter:
                rect = obj.geometry()
                obj._hover_anim.stop()
                obj._hover_anim.setStartValue(rect)
                obj._hover_anim.setEndValue(QRect(rect.x()-2, rect.y()-2, rect.width()+4, rect.height()+4))
                obj._hover_anim.start()
            elif event.type() == event.Leave:
                rect = obj.geometry()
                obj._hover_anim.stop()
                obj._hover_anim.setStartValue(rect)
                obj._hover_anim.setEndValue(QRect(rect.x()+2, rect.y()+2, rect.width()-4, rect.height()-4))
                obj._hover_anim.start()
        return super().eventFilter(obj, event)    


    def initUI(self):
        # Set window properties
        self.setWindowTitle("CASI")
        self.setGeometry(100, 100, 400, 500)
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("""
        QWidget {
            background-color: #2c3e50;
            border-radius: 25px;  /* Increased from 20px for a softer look */
            color: #ecf0f1;
        }
        """)

        # Set window icon
        self.setWindowIcon(QIcon(resource_path("CASInew-nbg.png")))

        # Main layout
        layout = QVBoxLayout()

        # 1. Create the buttons first!
        # KB Button (Knowledge Base, only for admin)
        self.kb_button = QPushButton("KB")
        self.kb_button.setFixedSize(32, 32)
        self.kb_button.setStyleSheet("""
            QPushButton {
                background-color: #f1c40f;
                color: #2c3e50;
                border: none;
                border-radius: 16px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f39c12;
            }
        """)
        self.kb_button.setToolTip("Add Knowledge (Admin Only)")
        self.kb_button.clicked.connect(self.open_knowledge_dialog)
        self.kb_button.setVisible(False)  # Hide by default, show if admin

        self.logout_button = QPushButton()
        self.logout_button.setFixedSize(32, 32)
        self.logout_button.setIcon(QIcon(resource_path("logout.png")))
        self.logout_button.setToolTip("Office 365")
        self.logout_button.setIconSize(QSize(20, 20))
        self.logout_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                border: none;
                border-radius: 16px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.logout_button.clicked.connect(self.toggle_logout_status)
        self.update_logout_button_color()

        self.clear_button = QPushButton("⟲")
        self.clear_button.setToolTip("Clear")
        self.clear_button.setFixedSize(32, 32)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db; 
                color: white; 
                border: none; 
                border-radius: 16px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.clear_button.clicked.connect(self.clear_chat)

        self.minimize_button = QPushButton("_")
        self.minimize_button.setToolTip("Minimize")
        self.minimize_button.setFixedSize(32, 32)
        self.minimize_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db; 
                color: white; 
                border: none; 
                border-radius: 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.minimize_button.clicked.connect(self.minimize_widget)

        self.close_button = QPushButton("X")
        self.close_button.setToolTip("Close")
        self.close_button.setFixedSize(32, 32)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; 
                color: white; 
                border: none;
                border-radius: 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.close_button.clicked.connect(self.hide_window)

        # --- Top Bar with Logo and Title ---
        top_bar_layout = QHBoxLayout()
        top_bar_layout.setContentsMargins(12, 0, 4, 0) # Adjust margins for a clean look

        # Logo
        logo_label = QLabel()
        logo_label.setPixmap(get_circular_pixmap(resource_path("CASInew-nbg.png"), 36))
        top_bar_layout.addWidget(logo_label)

        # App Name
        title_label = QLabel("CASI")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: white; padding-left: 5px;")
        top_bar_layout.addWidget(title_label)

        # Spacer to push buttons to the right
        top_bar_layout.addStretch()

        # Add KB button before logout
        top_bar_layout.addWidget(self.kb_button)
        top_bar_layout.addWidget(self.logout_button)
        
        top_bar_layout.addWidget(self.clear_button)
        top_bar_layout.addWidget(self.minimize_button)
        top_bar_layout.addWidget(self.close_button)
        
        layout.addLayout(top_bar_layout)
        # --- End Top Bar ---

        # Chat display (scrollable area)
        self.chat_display_layout = QVBoxLayout()
        self.chat_display_layout.setAlignment(Qt.AlignTop)

        # Create a container widget for the layout
        scroll_content = QWidget()
        scroll_content.setLayout(self.chat_display_layout)

        # Create the scroll area and set the container widget
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_content)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 6px;
                margin: 4px 0 4px 0;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #2ecc71;
                min-height: 30px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: #27ae60;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                background: none;
                border: none;
                height: 0px;
                width: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        layout.addWidget(scroll_area)

        

        # Typing label
        self.typing_label = QLabel("")
        self.typing_label.setStyleSheet("color: #95a5a6; padding: 5px;")
        layout.addWidget(self.typing_label)

       
        # Prompt labels above the input field
        prompt_layout = QHBoxLayout()
        prompt_layout.setAlignment(Qt.AlignHCenter)

        self.prompt_label = ClickableLabel("🚧 Under Maintenance")
        self.prompt_label.setStyleSheet("""
            QLabel {
                color: #1abc9c;
                background: #34495e;
                border-radius: 12px;
                padding: 4px 14px;
                font-size: 11px;
                margin-bottom: 6px;
                min-width: 160px;
                max-width: 200px;
                border: 2px solid #34495e;
            }
            QLabel:hover {
                border: 2px solid #2ecc71;
            }
        """)
        self.prompt_label.setAlignment(Qt.AlignCenter)
        self.prompt_label.clicked = self.create_helpdesk_email
        prompt_layout.addWidget(self.prompt_label)

        self.it_message_label = ClickableLabel("Message IT On Duty")
        self.it_message_label.setStyleSheet("""
            QLabel {
                color: #1abc9c;
                background: #34495e;
                border-radius: 12px;
                padding: 4px 14px;
                font-size: 13px;
                margin-bottom: 6px;
                min-width: 140px;
                max-width: 180px;
                margin-left: 10px;
                border: 2px solid #34495e;
            }
            QLabel:hover {
                border: 2px solid #2ecc71;
            }
        """)
        self.it_message_label.setAlignment(Qt.AlignCenter)
        self.it_message_label.clicked = self.message_it_on_duty
        prompt_layout.addWidget(self.it_message_label)


         


        layout.addLayout(prompt_layout)


        # Input field with send button
        input_layout = QHBoxLayout()
        self.input_field = ChatInput(self)
        self.input_field.setWordWrapMode(QTextOption.WordWrap)
        self.input_field.setPlaceholderText("Write a message...")
        self.input_field.setFixedHeight(50)
        self.input_field.send_callback = self.send_message  # Connect to your send function


        def adjust_input_height():
            doc_height = self.input_field.document().size().height()
            min_height = 51  # Minimum height (same as your initial)
            max_height = 120  # Maximum height (adjust as you like)
            new_height = max(min_height, min(int(doc_height) + 12, max_height))
            self.input_field.setFixedHeight(new_height)

        self.input_field.textChanged.connect(adjust_input_height)
        self.input_field.setStyleSheet("""
            QTextEdit {
                background-color: #34495e;
                border: 2px solid #34495e;
                padding: 10px;
                border-radius: 10px;
                color: #ecf0f1;
                font-size: 12px;
            }
            QTextEdit:hover {
                border: 2px solid #2ecc71;
            }
            QTextEdit:focus {
                border: 2px solid #2ecc71;
                outline: none;
            }
            QTextEdit:focus:hover {
                border: 2px solid #27ae60;
            }
            QTextEdit QScrollBar:vertical {
                background: transparent;
                width: 8px;
                margin: 4px 0 4px 0;
                border-radius: 4px;
            }
            QTextEdit QScrollBar::handle:vertical {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2ecc71, stop:1 #27ae60
                );
                min-height: 24px;
                border-radius: 4px;
            }
            QTextEdit QScrollBar::handle:vertical:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #43e97b, stop:1 #38f9d7
                );
            }
            QTextEdit QScrollBar::add-line:vertical, 
            QTextEdit QScrollBar::sub-line:vertical,
            QTextEdit QScrollBar::up-arrow:vertical, 
            QTextEdit QScrollBar::down-arrow:vertical {
                background: none;
                border: none;
                height: 0px;
                width: 0px;
            }
            QTextEdit QScrollBar::add-page:vertical, 
            QTextEdit QScrollBar::sub-page:vertical {
                background: none;
            }                   
        """)
        
        input_layout.addWidget(self.input_field)

        self.send_button = QPushButton(">")
        self.send_button.setToolTip("Enter")
        self.send_button.setFixedSize(40, 40)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #1abc9c; 
                color: white; 
                border-radius: 20px; 
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #16a085;
            }
            QPushButton:pressed {
                background-color: #148f77;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)
       

        # Dynamic button layout for options
        self.button_layout = QVBoxLayout()
        layout.addLayout(self.button_layout)

        # Add a spacer to the chat display layout
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.chat_display_layout.addWidget(spacer)

        self.setLayout(layout)
        self.move_to_right_corner()

        # Only show generic welcome if not logged in
        cache_path = os.path.join(os.getenv("APPDATA"), "CASI", "token_cache.json")
        if not os.path.exists(cache_path):
            message = "Hi! I'm CASI your AI virtual assistant, providing support that never sleeps. How can I help? 😊"
            self.add_message_bubble(message, sender="bot")
        else:
            client_id = "f8c7220e-feea-4490-bd93-d348b8bc023a"
            tenant_id = "c5d82738-88fd-49bb-b014-985f8dffbc23"
            access_token = get_user_token(client_id, tenant_id, cache_path)
            user_name = self.fetch_user_profile(access_token)
            self.user_pixmap = self.default_user_pixmap  # Set default first
            self.fetch_user_photo(access_token)           # Fetch and set Office 365 photo
            message = f"Hi {user_name}! I'm CASI your AI virtual assistant, providing support that never sleeps. How can I help? 😊"
            self.add_message_bubble(message, sender="bot")

        # After login, check if admin and show/hide KB button
        self.check_admin_and_update_kb_button()

    def hide_window(self):
        """Hide the chatbot window instead of closing it."""
        self.fade_out()

    def minimize_widget(self):
        """Minimize the chatbot window to a small icon."""
        self.fade_out()
        QTimer.singleShot(300, self._show_minimized_widget)
    def _show_minimized_widget(self):
        self.minimized_widget = MinimizedWidget(self)
        move_to_right_middle(self.minimized_widget)
        self.minimized_widget.show()    

    def start_typing_animation(self):
        """Start the animated typing indicator for the bot."""
        if self.typing_animation_timer is None:
            self.typing_animation_timer = QTimer(self)
            self.typing_animation_timer.timeout.connect(self.update_typing_label)
        self.typing_dot_count = 0
        self.typing_animation_timer.start(400)  # Update every 400ms

    def stop_typing_animation(self):
        """Stop the animated typing indicator."""
        if self.typing_animation_timer:
            self.typing_animation_timer.stop()
        self.typing_label.setText("")
        self.typing_dot_count = 0

    def update_typing_label(self):
        """Update the typing label with animated dots."""
        dots = "." * (self.typing_dot_count % 4)
        self.typing_label.setText(f"CASI is typing{dots}")
        self.typing_dot_count += 1

    def send_message(self):
        """Send user input to backend and display response."""
        user_text = self.input_field.toPlainText().strip()
        if not user_text:
            return

        # Add user message to chat
        self.add_message_bubble(user_text, sender="user")
        self.input_field.clear()

        # ADD THIS LINE:
        self.conversation_history.append((user_text, "user"))

        # Start animated typing indicator for bot response
        self.start_typing_animation()
        QTimer.singleShot(1500, lambda: self.get_bot_response(user_text))  # Delay for 1.5 seconds

    def get_bot_response(self, user_text):
        """Fetch and display the bot's response."""
        try:
            print(f"[DEBUG] Attempting to connect to backend at: {BACKEND_URL}/chat")
            
            # Test backend connectivity first
            is_connected, connection_msg = test_backend_connectivity()
            if not is_connected:
                print(f"[DEBUG] Backend connectivity test failed: {connection_msg}")
                # Get network diagnostics for better error reporting
                diagnostics = get_network_diagnostics()
                diagnostic_text = "\n".join(diagnostics)
                bot_response = f"Network Error: Cannot connect to the server.\n\nDiagnostics:\n{diagnostic_text}\n\nPlease check:\n1. Your network connection\n2. Firewall settings\n3. Contact IT if the issue persists."
                options = []
                self.stop_typing_animation()
                self.display_bot_response(bot_response, options)
                return
            
            # Get access token if user is logged in
            access_token = None
            cache_path = os.path.join(os.getenv("APPDATA"), "CASI", "token_cache.json")
            if os.path.exists(cache_path):
                try:
                    client_id = get_client_id()
                    tenant_id = get_tenant_id()
                    access_token = get_user_token(client_id, tenant_id, cache_path)
                    print(f"[DEBUG] Access token obtained successfully")
                except Exception as e:
                    print(f"[DEBUG] Failed to get access token: {e}")
            
            # Prepare request payload
            payload = {"message": user_text}
            if access_token:
                payload["access_token"] = access_token
                print(f"[DEBUG] Sending request with access token")
            else:
                print(f"[DEBUG] Sending request without access token (anonymous mode)")
            
            response = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=8)
            print(f"[DEBUG] Backend response status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                bot_response = response_data.get("response", "No response")
                options = response_data.get("options", [])
                
                # Handle guest mode message if present
                if not access_token and "message" in response_data:
                    guest_message = response_data.get("message", "")
                    if guest_message:
                        bot_response = f"{bot_response}\n\n{guest_message}"
            else:
                print(f"[DEBUG] Backend error response: {response.text}")
                if response.status_code == 500:
                    bot_response = "Error: Server error occurred. Please try again later."
                elif response.status_code == 404:
                    bot_response = "Error: Backend endpoint not found. Please contact IT support."
                else:
                    bot_response = f"Error: Backend returned status {response.status_code}. Please contact IT support."
                options = []
        except requests.exceptions.ConnectionError as e:
            print(f"[DEBUG] Connection error: {e}")
            diagnostics = get_network_diagnostics()
            diagnostic_text = "\n".join(diagnostics)
            bot_response = f"Connection Error: Cannot reach the server at {BACKEND_URL}.\n\nDiagnostics:\n{diagnostic_text}\n\nPossible solutions:\n1. Check your internet connection\n2. Contact IT to verify server status\n3. Check if you're on the correct network"
            options = []
        except requests.exceptions.Timeout as e:
            print(f"[DEBUG] Timeout error: {e}")
            bot_response = "Error: Server request timed out. The server may be overloaded or your connection is slow. Please try again."
            options = []
        except requests.exceptions.RequestException as e:
            print(f"[DEBUG] Request exception: {e}")
            bot_response = f"Network Error: {str(e)}. Please check your connection and try again."
            options = []
        except Exception as e:
            print(f"[DEBUG] Unexpected error: {e}")
            bot_response = f"Unexpected Error: {str(e)}. Please contact IT support with this error message."
            options = []

        # Stop typing animation and display bot response
        self.stop_typing_animation()
        self.display_bot_response(bot_response, options)

    def display_bot_response(self, bot_response, options):
        """Display the bot's response and options after a delay."""
        self.add_message_bubble(bot_response, sender="bot")

        # Clear previous buttons
        while self.button_layout.count():
            child = self.button_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Add new buttons for options
        for idx, option in enumerate(options):
            button = AnimatedButton(option)
            button.clicked.connect(lambda _, opt=option: self.send_option(opt))
            self.button_layout.addWidget(button)
            self.animate_option_button(button, idx)
    def animate_option_button(self, button, index=0):
        """Fade and slide in the option button from the right."""
        # Fade-in
        effect = QGraphicsOpacityEffect()
        button.setGraphicsEffect(effect)
        fade_anim = QPropertyAnimation(effect, b"opacity")
        fade_anim.setDuration(300)
        fade_anim.setStartValue(0.0)
        fade_anim.setEndValue(1.0)
        fade_anim.start()
        button._fade_anim = fade_anim  # Prevent garbage collection

        # Slide-in from the right
        button.show()
        button.raise_()
        button.repaint()
        QTimer.singleShot(index * 80, fade_anim.start)

    def clear_chat(self):
        """Clear all messages from the chat display, including nested layouts."""
        def clear_layout(layout):
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                child_layout = item.layout()
                if widget:
                    widget.deleteLater()
                elif child_layout:
                    clear_layout(child_layout)
                    child_layout.deleteLater()

        clear_layout(self.chat_display_layout)

    def save_chat_history(self):
        """Save conversation history to a file."""
        try:
            with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to save chat history: {e}")

    def load_chat_history(self):
        """Load conversation history from a file."""
        try:
            if os.path.exists(CHAT_HISTORY_FILE):
                with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
                    self.conversation_history = json.load(f)
                    # Display loaded history
                    for msg in self.conversation_history:
                        if isinstance(msg, (list, tuple)) and len(msg) == 2:
                            text, sender = msg
                            self.add_message_bubble(text, sender=sender)
                        elif isinstance(msg, dict):
                            self.add_message_bubble(msg.get("text", ""), sender=msg.get("sender", "bot"))
        except Exception as e:
            print(f"Failed to load chat history: {e}")

    def clear_welcome_message(self):
        """Remove all instances of the generic welcome message from the chat display and history."""
        generic = "Hi! I'm CASI your AI virtual assistant, providing support that never sleeps. How can I help? 😊"
        # Remove from conversation_history if present
        self.conversation_history = [
            msg for msg in self.conversation_history
            if not (isinstance(msg, (list, tuple)) and msg[0] == generic)
        ]
        # Remove from UI
        layout = self.chat_display_layout
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if item is None:
                continue
            found = False
            # Check if item is a layout (message bubble)
            child_layout = item.layout()
            if child_layout:
                for j in range(child_layout.count()):
                    widget = child_layout.itemAt(j).widget()
                    if isinstance(widget, QLabel) and widget.text() == generic:
                        found = True
                        break
            else:
                # Or check if it's a direct widget
                widget = item.widget()
                if isinstance(widget, QLabel) and widget.text() == generic:
                    found = True
            if found:
                item_to_remove = layout.takeAt(i)
                if item_to_remove:
                    if item_to_remove.widget():
                        item_to_remove.widget().deleteLater()
                    elif item_to_remove.layout():
                        while item_to_remove.layout().count():
                            subitem = item_to_remove.layout().takeAt(0)
                            if subitem.widget():
                                subitem.widget().deleteLater()
                        item_to_remove.layout().deleteLater()

    def toggle_logout_status(self):
        cache_path = os.path.join(os.getenv("APPDATA"), "CASI", "token_cache.json")
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        if os.path.exists(cache_path):
            # Currently logged in, so log out
            os.remove(cache_path)
            self.user_pixmap = self.default_user_pixmap
            QMessageBox.information(self, "Logout", "Office 365 login cleared. You will be prompted to login again next time.")
            message = "Hi! I'm CASI your AI virtual assistant, providing support that never sleeps. How can I help? 😊"
            self.add_message_bubble(message, sender="bot")
        else:
            try:
                client_id = "f8c7220e-feea-4490-bd93-d348b8bc023a"
                tenant_id = "c5d82738-88fd-49bb-b014-985f8dffbc23"
                access_token = get_user_token(client_id, tenant_id, cache_path)
                user_name = self.fetch_user_profile(access_token)
                self.user_pixmap = self.default_user_pixmap  # Set default first
                self.fetch_user_photo(access_token)           # Fetch and set Office 365 photo
                self.clear_welcome_message()
                message = f"Hi {user_name}! I'm CASI your AI virtual assistant, providing support that never sleeps. How can I help? 😊"
                self.add_message_bubble(message, sender="bot")
                QMessageBox.information(self, "Login", f"Welcome, {user_name}! Office 365 login successful.")
            except Exception as e:
                QMessageBox.warning(self, "Login Failed", f"Could not log in to Office 365:\n{e}")
        self.update_logout_button_color()

    def update_logout_button_color(self):
        cache_path = os.path.join(os.getenv("APPDATA"), "CASI", "token_cache.json")
        if os.path.exists(cache_path):
            # Logged in: Red, tooltip says "Logout Office 365"
            self.logout_button.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 16px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            self.logout_button.setToolTip("Logout Office 365")
        else:
            # Logged out: Green, tooltip says "Login Office 365"
            self.logout_button.setStyleSheet("""
                QPushButton {
                    background-color: #2ecc71;
                    color: white;
                    border: none;
                    border-radius: 16px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #27ae60;
                }
            """)
            self.logout_button.setToolTip("Login Office 365")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = event.globalPos() - self.oldPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

    def move_to_right_corner(self):
        """Move the widget to the right corner of the screen."""
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        widget_geometry = self.frameGeometry()
        x = screen_geometry.width() - widget_geometry.width() - 10  # 10 pixels from the right edge
        y = screen_geometry.height() - widget_geometry.height() - 10  # 10 pixels from the bottom edge
        self.move(x, y)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # We manually draw a rounded rectangle to respect the border-radius
        # because the window is frameless and translucent.
        rect = self.rect()
        radius = 25.0  # IMPORTANT: This must match the radius in your stylesheet
        
        painter.setBrush(QColor("#2c3e50"))
        painter.setPen(Qt.NoPen)  # No outline
        painter.drawRoundedRect(rect, radius, radius)
        
        # This is crucial to ensure all child widgets (buttons, text, etc.) are drawn
        super().paintEvent(event)

    def add_message_bubble(self, text, sender="bot"):
        message_layout = QHBoxLayout()
        message_layout.setSpacing(8)  # Space between icon and bubble

        # --- Message Bubble ---
        message_label = QLabel(text)
        message_label.setWordWrap(True)
        message_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        message_label.setOpenExternalLinks(True)
        message_label.setMaximumWidth(300) # Constrain bubble width

        # Use a standard QWidget for the bubble
        bubble_wrapper = QWidget()
        bubble_layout = QHBoxLayout(bubble_wrapper)
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        bubble_layout.addWidget(message_label)
        # --- End Message Bubble ---

        # Determine if admin is logged in
        cache_path = os.path.join(os.getenv("APPDATA"), "CASI", "token_cache.json")
        admin_email = "rojohn.deguzman@castotravel.ph"
        is_admin = False
        try:
            client_id = "f8c7220e-feea-4490-bd93-d348b8bc023a"
            tenant_id = "c5d82738-88fd-49bb-b014-985f8dffbc23"
            if os.path.exists(cache_path):
                access_token = get_user_token(client_id, tenant_id, cache_path)
                headers = {"Authorization": f"Bearer {access_token}"}
                resp = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers)
                if resp.status_code == 200:
                    email = resp.json().get("mail") or resp.json().get("userPrincipalName")
                    if email and email.lower() == admin_email:
                        is_admin = True
        except Exception as e:
            pass

        if sender == "bot":
            # Bot: [ICON] [BUBBLE] [STRETCH]
            message_label.setStyleSheet("""
                background-color: #ecf0f1; color: #2c3e50; 
                border-radius: 10px; padding: 10px; font-size: 14px;
            """)
            logo_label = QLabel()
            logo_label.setPixmap(get_circular_pixmap(resource_path("CASInew-nbg.png"), 36))
            message_layout.addWidget(logo_label, 0, Qt.AlignBottom)
            message_layout.addWidget(bubble_wrapper, 0, Qt.AlignBottom)
            message_layout.addStretch()
        else:  # sender is "user"
            # User: [STRETCH] [BUBBLE] [ICON]
            message_label.setStyleSheet("""
                background-color: #1abc9c; color: white; 
                border-radius: 10px; padding: 10px; font-size: 14px;
            """)
            message_layout.addStretch()
            message_layout.addWidget(bubble_wrapper, 0, Qt.AlignBottom)
            if self.user_pixmap and not self.user_pixmap.isNull():
                user_logo_label = QLabel()
                user_logo_label.setPixmap(self.user_pixmap)
                message_layout.addWidget(user_logo_label, 0, Qt.AlignBottom)
            else:
                spacer = QWidget()
                spacer.setFixedSize(36, 36)
                message_layout.addWidget(spacer, 0, Qt.AlignBottom)

        self.chat_display_layout.addLayout(message_layout)
        self.slide_in_message(bubble_wrapper, sender)
        QTimer.singleShot(100, lambda: self.scroll_to_bottom())

    def scroll_to_bottom(self):
        """Scroll to the bottom of the chat display."""
        scroll_area = self.findChild(QScrollArea)
        scroll_area.verticalScrollBar().setValue(scroll_area.verticalScrollBar().maximum())

    def get_last_user_message(self):
        # Returns the last user message from conversation_history, or None
        for msg in reversed(self.conversation_history):
            if isinstance(msg, (list, tuple)) and len(msg) == 2:
                text, sender = msg
                if sender == "user" and text.strip():
                    return text.strip()
            elif isinstance(msg, dict) and msg.get("sender") == "user":
                text = msg.get("text", "").strip()
                if text:
                    return text
        return None

    def extract_main_topic_from_last_user_message(self):
        # Get the last user message
        last_msg = None
        for msg in reversed(self.conversation_history):
            if isinstance(msg, (list, tuple)) and len(msg) == 2:
                text, sender = msg
                if sender == "user" and text.strip():
                    last_msg = text.strip()
                    break
            elif isinstance(msg, dict) and msg.get("sender") == "user":
                text = msg.get("text", "").strip()
                if text:
                    last_msg = text
                    break
        if not last_msg:
            return None
        # Extract keywords from the last message
        stopwords = set([
            "the", "is", "at", "which", "on", "and", "a", "an", "to", "for", "of", "in", "my", "with", "it", "that", "this", "i", "me", "you", "we", "our", "as", "by", "from", "be", "or", "are", "was", "were", "has", "have", "had", "but", "so", "if", "can", "will", "just", "not", "do", "does", "did", "am", "your", "please", "help", "need", "issue", "problem", "ticket", "message", "send", "create", "about", "regarding", "hi", "hello", "thanks", "thank"
        ])
        words = [w for w in re.sub(r"[^a-zA-Z0-9 ]", " ", last_msg).lower().split() if w not in stopwords and len(w) > 2]
        if words:
            # Return the most common word (or the first if only one)
            from collections import Counter
            return Counter(words).most_common(1)[0][0].capitalize()
        return None

    def get_current_user_email(self):
        """Get the current user's email from Office 365 token if available."""
        try:
            cache_path = os.path.join(os.getenv("APPDATA"), "CASI", "token_cache.json")
            if os.path.exists(cache_path):
                client_id = get_client_id()
                tenant_id = get_tenant_id()
                access_token = get_user_token(client_id, tenant_id, cache_path)
                if access_token:
                    # Get user email from Microsoft Graph
                    headers = {"Authorization": f"Bearer {access_token}"}
                    response = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers, timeout=10)
                    if response.status_code == 200:
                        user_data = response.json()
                        return user_data.get("mail") or user_data.get("userPrincipalName", "Unknown")
        except Exception as e:
            print(f"Failed to get user email: {e}")
        return "Unknown"
    
    def send_via_custom_bot(self, alert_data):
        """Send IT alert via custom CASI Teams Bot."""
        try:
            import requests
            
            # Send to custom bot API
            response = requests.post(
                "http://localhost:3978/api/send-alert",
                json=alert_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    print(f"✅ Custom bot alert sent successfully: {result}")
                    return True
                else:
                    print(f"❌ Custom bot returned error: {result}")
                    return False
            else:
                print(f"❌ Custom bot HTTP error: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ Custom bot server not running - falling back to Power Automate")
            return False
        except requests.exceptions.Timeout:
            print("❌ Custom bot request timed out - falling back to Power Automate")
            return False
        except Exception as e:
            print(f"❌ Custom bot error: {e} - falling back to Power Automate")
            return False

    def send_via_azure_bot(self, alert_data):
        """Send IT alert via CASI Azure Bot (direct Teams integration)."""
        try:
            import requests
            
            # For now, we'll use the custom bot as a bridge to Azure Bot
            # Later, we'll implement direct Azure Bot communication
            response = requests.post(
                "http://localhost:3978/api/send-alert",
                json=alert_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    print(f"✅ Azure Bot alert sent successfully: {result}")
                    return True
                else:
                    print(f"❌ Azure Bot returned error: {result}")
                    return False
            else:
                print(f"❌ Azure Bot HTTP error: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ Azure Bot server not running - falling back to Teams")
            return False
        except requests.exceptions.Timeout:
            print("❌ Azure Bot request timed out - falling back to Teams")
            return False
        except Exception as e:
            print(f"❌ Azure Bot error: {e} - falling back to Teams")
            return False

    def send_teams_message_with_bot_name(self, message_data):
        """Send Teams message with CASI as the bot name using webhook."""
        try:
            # Format the message with adaptive cards for better presentation
            teams_message = {
                "type": "message",
                "attachments": [
                    {
                        "contentType": "application/vnd.microsoft.card.adaptive",
                        "content": {
                            "type": "AdaptiveCard",
                            "version": "1.0",
                            "body": [
                                {
                                    "type": "TextBlock",
                                    "text": "🤖 **CASI IT On Duty Alert**",
                                    "weight": "Bolder",
                                    "size": "Medium",
                                    "color": "Accent"
                                },
                                {
                                    "type": "FactSet",
                                    "facts": [
                                        {
                                            "title": "Priority:",
                                            "value": message_data.get("priority", "General")
                                        },
                                        {
                                            "title": "User:",
                                            "value": message_data.get("windows_user", "Unknown")
                                        },
                                        {
                                            "title": "Hostname:",
                                            "value": message_data.get("hostname", "Unknown")
                                        },
                                        {
                                            "title": "Time:",
                                            "value": message_data.get("timestamp", "Unknown")
                                        },
                                        {
                                            "title": "Source:",
                                            "value": "CASI"
                                        }
                                    ]
                                },
                                {
                                    "type": "TextBlock",
                                    "text": "**Concern:**",
                                    "weight": "Bolder",
                                    "spacing": "Medium"
                                },
                                {
                                    "type": "TextBlock",
                                    "text": message_data.get("concern", "No concern specified"),
                                    "wrap": True,
                                    "spacing": "Small"
                                }
                            ]
                        }
                    }
                ]
            }
            
            # Send to Teams webhook
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                TEAMS_WEBHOOK_URL, 
                headers=headers, 
                json=teams_message, 
                timeout=30
            )
            
            if response.status_code == 200:
                print("✅ Teams message sent successfully with CASI bot name")
                return True
            else:
                print(f"❌ Teams webhook failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending Teams message: {e}")
            return False

    def message_it_on_duty(self, prefill_text=None):
        # Prefill with the main topic/keyword from the last user message
        prefill = self.extract_main_topic_from_last_user_message()
        dialog = ITOnDutyDialog(self, prefill_text=prefill)
        if dialog.exec_() == QDialog.Accepted:
            concern_text = dialog.getText().strip()
            if concern_text:
                import getpass
                username = getpass.getuser()

                # Only the last 5 user messages for summary
                last_n = 5
                recent_history = self.conversation_history[-last_n:] if len(self.conversation_history) >= last_n else self.conversation_history

                # Remove duplicates while preserving order, and exclude the current concern if it's not already present
                seen = set()
                efficient_summary = []
                for ts_msg in recent_history:
                    timestamp, msg = ts_msg
                    if msg not in seen and msg.strip():
                        efficient_summary.append((timestamp, msg))
                        seen.add(msg)
                # Add the current concern only if it's not already in the summary
                if concern_text not in seen:
                    efficient_summary.append((datetime.now().strftime("%Y-%m-%d %H:%M"), concern_text))

                # Format the summary with bullet points (no timestamps)
                summary = "\n".join(f"• {msg}" for ts, msg in efficient_summary)

                concern_lower = (concern_text + " " + " ".join(msg for _, msg in efficient_summary)).lower()
                if "urgent" in concern_lower or "asap" in concern_lower or "immediately" in concern_lower or "critical" in concern_lower:
                    priority = "High"
                elif "password" in concern_lower or "account locked" in concern_lower or "login" in concern_lower or "reset" in concern_lower:
                    priority = "Account/Password"
                elif "network" in concern_lower or "internet" in concern_lower or "wifi" in concern_lower or "lan" in concern_lower or "connection" in concern_lower:
                    priority = "Network"
                elif "printer" in concern_lower or "print" in concern_lower or "scanner" in concern_lower:
                    priority = "Printer/Scanner"
                elif "email" in concern_lower or "outlook" in concern_lower or "mail" in concern_lower:
                    priority = "Email"
                elif "software" in concern_lower or "install" in concern_lower or "application" in concern_lower or "program" in concern_lower:
                    priority = "Software"
                elif "hardware" in concern_lower or "laptop" in concern_lower or "desktop" in concern_lower or "monitor" in concern_lower or "mouse" in concern_lower or "keyboard" in concern_lower:
                    priority = "Hardware"
                elif "virus" in concern_lower or "malware" in concern_lower or "security" in concern_lower or "phishing" in concern_lower:
                    priority = "Security"
                else:
                    priority = "General"

                # Get hostname
                import socket
                hostname = socket.gethostname()
                
                # Compose structured data for Teams
                alert_data = {
                    "alert_type": "IT_On_Duty",
                    "priority": priority,
                    "windows_user": username,
                    "concern": concern_text,
                    "conversation_summary": summary if summary else "No previous conversation.",
                    "timestamp": datetime.now().strftime("%m/%d/%Y %H:%M"),
                    "source": "CASI Chatbot",
                    "user_email": self.get_current_user_email() if hasattr(self, 'get_current_user_email') else "Unknown",
                    "hostname": hostname
                }
                
                # Try Teams webhook first (with CASI bot name)
                teams_sent = send_teams_message_as_casi_bot(alert_data)
                
                if teams_sent:
                    self.add_message_bubble(
                        "✅ **Message IT on Duty was sent successfully**\n\n"
                        "The IT team will be notified via Teams shortly.\n"
                        "**Sent by: CASI** 🤖",
                        sender="bot"
                    )
                else:
                    # Fallback to Power Automate if Teams webhook fails
                    try:
                        from power_automate_config import send_power_automate_alert
                        power_automate_sent = send_power_automate_alert(alert_data)
                        
                        if power_automate_sent:
                            self.add_message_bubble(
                                "✅ **Message IT on Duty was sent successfully**\n\n"
                                "The IT team will be notified via Teams shortly.\n"
                                "**Note:** Sent via Power Automate (may show user name)",
                                sender="bot"
                            )
                        else:
                            self.add_message_bubble(
                                "❌ **Failed to send IT alert**\n\n"
                                "There was an issue sending your alert.\n"
                                "Please try again or contact IT directly.",
                                sender="bot"
                            )
                    except ImportError:
                        self.add_message_bubble(
                            "❌ **Power Automate not available**\n\n"
                            "Please contact IT directly for assistance.",
                            sender="bot"
                        )
            else:
                self.add_message_bubble("Concern is required to contact IT On Duty.", sender="bot")
                                        
    def create_helpdesk_email(self, prefill_text=None):
        # Show maintenance message
        maintenance_message = (
            "🚧 **Ticket System Under Maintenance** 🚧\n\n"
            "The IT helpdesk ticket system is currently undergoing maintenance and updates.\n\n"
            "**What you can do:**\n"
            "• Contact IT directly via email\n"
            "• Use the 'Message IT On Duty' feature\n"
            "• Chat with me for general IT questions\n\n"
            "**Expected completion:** Soon\n\n"
            "Thank you for your patience! 🙏"
        )
        self.add_message_bubble(maintenance_message, sender="bot")

    def _proceed_with_ticket_creation(self, prefill_text=None):
        """Helper method to proceed with ticket creation after authentication check."""
        prefill = self.extract_main_topic_from_last_user_message()
        dialog = MultiLineInputDialog("Describe Issue", "Please describe your IT issue:", self, prefill_text=prefill)
        if dialog.exec_() == QDialog.Accepted:
            user_message = dialog.getText().strip()
            self.selected_attachment = dialog.getAttachment()

            username = getpass.getuser()
            # Only the last 5 user messages for summary
            last_n = 5
            recent_history = self.conversation_history[-last_n:] if len(self.conversation_history) >= last_n else self.conversation_history

            # Remove duplicates while preserving order, and exclude the current concern if it's already present
            seen = set()
            efficient_summary = []
            for msg in recent_history:
                if msg not in seen and msg.strip():
                    efficient_summary.append(msg)
                    seen.add(msg)
            # Add the current concern only if it's not already in the summary
            if user_message.strip() and user_message.strip() not in seen:
                efficient_summary.append(user_message.strip())

            # Format the summary with bullet points
            summary = "\n".join(f"• {msg}" for msg in efficient_summary)

            # Analyze concern for priority
            concern = (user_message + " " + " ".join(efficient_summary)).lower()
            if "urgent" in concern or "asap" in concern or "immediately" in concern or "critical" in concern:
                priority = "High"
            elif "password" in concern or "account locked" in concern or "login" in concern or "reset" in concern:
                priority = "Account/Password"
            elif "network" in concern or "internet" in concern or "wifi" in concern or "lan" in concern or "connection" in concern:
                priority = "Network"
            elif "printer" in concern or "print" in concern or "scanner" in concern:
                priority = "Printer/Scanner"
            elif "email" in concern or "outlook" in concern or "mail" in concern:
                priority = "Email"
            elif "software" in concern or "install" in concern or "application" in concern or "program" in concern:
                priority = "Software"
            elif "hardware" in concern or "laptop" in concern or "desktop" in concern or "monitor" in concern or "mouse" in concern or "keyboard" in concern:
                priority = "Hardware"
            elif "virus" in concern or "malware" in concern or "security" in concern or "phishing" in concern:
                priority = "Security"
            else:
                priority = "General"

            # Compose a clean, readable helpdesk message body
            full_conversation = (
                f"============================\n"
                f"  IT Helpdesk Ticket Request\n"
                f"============================\n"
                f"Priority      : {priority}\n"
                f"Windows User  : {username}\n"
                f"\n"
                f"Issue:\n"
                f"{user_message.strip()}\n"
                f"\n"
                f"Conversation Summary:\n"
                f"{summary}\n"
                f"============================"
            )

            self.send_helpdesk_email(
                user_message.strip(),
                username,
                priority,
                full_conversation,
                self.selected_attachment
            )
        else:
            self.add_message_bubble("You must describe your issue to create a ticket.", sender="bot")

    def send_helpdesk_email(self, user_message, username, priority, conversation_summary, attachment_path=None):
        client_id = "f8c7220e-feea-4490-bd93-d348b8bc023a"
        tenant_id = "c5d82738-88fd-49bb-b014-985f8dffbc23"
        to_email = "ITSupport@castotravel.ph"
        subject = f"IT Helpdesk Ticket Request [{priority}]"

        access_token = get_user_token(client_id, tenant_id)
        headers = {"Authorization": f"Bearer {access_token}"}
        profile = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers).json()
        sender_email = profile.get("userPrincipalName", "unknown@domain.com")

        body = (
            f"User request from CASI:\n"
            f"Sender: {sender_email}\n"
            f"Windows login: {username}\n"
            f"Priority: {priority}\n\n"
            f"Issue:\n{user_message}\n\n"
            f"Conversation Summary:\n{conversation_summary}"
        )

        # Prepare attachment if selected
        attachments = []
        if attachment_path:
            file_size = os.path.getsize(attachment_path)
            if file_size > 4 * 1024 * 1024:  # 4 MB
                QMessageBox.warning(self, "Attachment Too Large", "The selected file is larger than 4 MB and cannot be sent.")
                return
            with open(attachment_path, "rb") as f:
                content_bytes = base64.b64encode(f.read()).decode("utf-8")
            attachment = {
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": os.path.basename(attachment_path),
                "contentBytes": content_bytes
            }
            attachments.append(attachment)

        result = send_graph_email_delegated(
            client_id, tenant_id, sender_email, to_email, subject, body, attachments
        )
        if result:
            self.add_message_bubble("Your ticket was sent to IT Helpdesk via email.", sender="bot")
        else:
            self.add_message_bubble("Failed to send email via Microsoft Graph.", sender="bot")

    def extract_recent_topics(self, num_messages=5):
        """Extracts keywords/topics from the last few user messages for dynamic suggestions."""
        # Get last N user messages
        user_msgs = []
        for msg in reversed(self.conversation_history):
            if isinstance(msg, (list, tuple)) and len(msg) == 2:
                text, sender = msg
                if sender == "user":
                    user_msgs.append(text)
            elif isinstance(msg, dict) and msg.get("sender") == "user":
                user_msgs.append(msg.get("text", ""))
            if len(user_msgs) >= num_messages:
                break
        # Simple keyword extraction: split, remove stopwords, count
        stopwords = set([
            "the", "is", "at", "which", "on", "and", "a", "an", "to", "for", "of", "in", "my", "with", "it", "that", "this", "i", "me", "you", "we", "our", "as", "by", "from", "be", "or", "are", "was", "were", "has", "have", "had", "but", "so", "if", "can", "will", "just", "not", "do", "does", "did", "am", "your", "please", "help", "need", "issue", "problem", "ticket", "message", "send", "create", "about", "regarding", "hi", "hello", "thanks", "thank"
        ])
        words = []
        for msg in user_msgs:
            msg = re.sub(r"[^a-zA-Z0-9 ]", " ", msg)
            for w in msg.lower().split():
                if w not in stopwords and len(w) > 2:
                    words.append(w)
        # Count and get most common
        common = [w for w, _ in Counter(words).most_common(5)]
        # Capitalize for display
        return [w.capitalize() for w in common if w]

    def check_admin_and_update_kb_button(self):
        cache_path = os.path.join(os.getenv("APPDATA"), "CASI", "token_cache.json")
        admin_email = "rojohn.deguzman@castotravel.ph"
        is_admin = False
        try:
            client_id = "f8c7220e-feea-4490-bd93-d348b8bc023a"
            tenant_id = "c5d82738-88fd-49bb-b014-985f8dffbc23"
            if os.path.exists(cache_path):
                access_token = get_user_token(client_id, tenant_id, cache_path)
                headers = {"Authorization": f"Bearer {access_token}"}
                resp = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers)
                if resp.status_code == 200:
                    email = resp.json().get("mail") or resp.json().get("userPrincipalName")
                    if email and email.lower() == admin_email:
                        is_admin = True
        except Exception as e:
            pass
        self.kb_button.setVisible(is_admin)



    def open_knowledge_dialog(self):
        from PyQt5.QtWidgets import QInputDialog
        content, ok = QInputDialog.getText(self, "Add Knowledge", "Knowledge to save:")
        if ok and content.strip():
            try:
                cache_path = os.path.join(os.getenv("APPDATA"), "CASI", "token_cache.json")
                client_id = get_client_id()
                tenant_id = get_tenant_id()
                access_token = get_user_token(client_id, tenant_id, cache_path)
                resp = requests.post(
                    f"{BACKEND_URL}/knowledge",
                    json={"access_token": access_token, "content": content.strip()}
                )
                if resp.status_code == 200:
                    QMessageBox.information(self, "Knowledge Saved", "Knowledge added successfully!")
                else:
                    QMessageBox.warning(self, "Error", f"Failed to add knowledge: {resp.text}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to add knowledge: {e}")

    def closeEvent(self, event):
        event.ignore()
        self.hide_window()  # Hide the window instead of closing

class SystemTrayApp(QSystemTrayIcon):
    def __init__(self, app, chatbot):
        super().__init__(app)
        self.app = app
        self.chatbot = chatbot
        print("[DEBUG] Initializing SystemTrayApp")
        
        # Check system tray availability immediately
        print(f"[DEBUG] System tray available: {self.isSystemTrayAvailable()}")
        print(f"[DEBUG] System tray supported: {QSystemTrayIcon.isSystemTrayAvailable()}")
        print(f"[DEBUG] System tray visible: {self.isVisible()}")
        
        # Set icon with multiple fallback options
        icon_set = False
        
        # Try multiple icon paths for different scenarios
        icon_paths = [
            "CASInew-nbg.png",  # Development path
            "CASInew-nbg.ico",  # ICO format
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "CASInew-nbg.png"),  # Absolute path
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "CASInew-nbg.ico"),  # Absolute ICO path
        ]
        
        for icon_path in icon_paths:
            try:
                if os.path.exists(icon_path):
                    icon = QIcon(icon_path)
                    if not icon.isNull():
                        self.setIcon(icon)
                        print(f"[DEBUG] Icon set successfully from: {icon_path}")
                        icon_set = True
                        break
            except Exception as e:
                print(f"[DEBUG] Failed to load icon from {icon_path}: {e}")
                continue
        
        # Fallback to default icon if none of the above work
        if not icon_set:
            print("[DEBUG] No custom icon found, using default system icon")
            try:
                # Try to create a simple colored icon as fallback
                pixmap = QPixmap(32, 32)
                pixmap.fill(QColor(0, 120, 215))  # Windows blue color
                self.setIcon(QIcon(pixmap))
                print("[DEBUG] Set fallback colored icon")
            except Exception as e:
                print(f"[DEBUG] Failed to create fallback icon: {e}")
                # Last resort - use system default
                self.setIcon(QIcon.fromTheme("application-x-executable"))
        
        print(f"[DEBUG] Final icon set: {self.icon().isNull()}")
        print(f"[DEBUG] Icon size: {self.icon().actualSize(QSize(32, 32))}")
        
        self.setToolTip("CASI - Right-click for menu")
        
        # Create context menu
        self.menu = QMenu()
        
        # Open Chatbot action
        open_action = QAction("📱 Open Chatbot", self.menu)
        open_action.triggered.connect(self.show_chatbot)
        self.menu.addAction(open_action)
        
        # Separator
        self.menu.addSeparator()
        
        # Exit action
        exit_action = QAction("❌ Exit CASI", self.menu)
        exit_action.triggered.connect(self.exit_app)
        self.menu.addAction(exit_action)
        
        # Set the context menu
        self.setContextMenu(self.menu)
        print("[DEBUG] Tray context menu set with actions")
        
        # Connect signals
        self.activated.connect(self.on_tray_icon_activated)
        print("[DEBUG] Tray icon activated signal connected")
        
        # Show startup message
        QTimer.singleShot(1000, self.show_startup_message)

    def on_tray_icon_activated(self, reason):
        print(f"[DEBUG] Tray icon activated: reason={reason}")
        
        if reason == QSystemTrayIcon.Trigger:
            # Single click - show chatbot
            print("[DEBUG] Single click detected - showing chatbot")
            self.show_chatbot()
        elif reason == QSystemTrayIcon.Context:
            # Right click - show context menu
            print("[DEBUG] Right click detected - showing context menu")
            if self.contextMenu():
                self.contextMenu().popup(QCursor.pos())
            else:
                print("[DEBUG] Warning: Context menu is None!")
        elif reason == QSystemTrayIcon.DoubleClick:
            # Double click - show chatbot
            print("[DEBUG] Double click detected - showing chatbot")
            self.show_chatbot()

    def show_startup_message(self):
        self.showMessage("CASI", "The application is running in the system tray.", QSystemTrayIcon.Information, 2000)
        
    def show_chatbot(self):
        """Show chatbot window."""
        if hasattr(self.chatbot, "minimized_widget") and self.chatbot.minimized_widget is not None:
            self.chatbot.minimized_widget.hide()
            self.chatbot.minimized_widget = None
        self.chatbot.fade_in()
        self.chatbot.move_to_right_corner()
        self.chatbot.activateWindow()
        cache_path = os.path.join(os.getenv("APPDATA"), "CASI", "token_cache.json")
        if (not os.path.exists(cache_path)
            and self.chatbot.chat_display_layout.count() == 0):
            message = "Hi! I'm CASI your AI virtual assistant, providing support that never sleeps. How can I help?"
            self.chatbot.add_message_bubble(message, sender="bot")
        else:
            client_id = "f8c7220e-feea-4490-bd93-d348b8bc023a"
            tenant_id = "c5d82738-88fd-49bb-b014-985f8dffbc23"
            access_token = get_user_token(client_id, tenant_id, cache_path)
            self.chatbot.user_pixmap = self.chatbot.default_user_pixmap
            self.chatbot.fetch_user_photo(access_token)
    
    def exit_app(self):
        """Exit the application."""
        print("[DEBUG] Exit requested from system tray")
        self.showMessage("CASI", "The application is closing.", QSystemTrayIcon.Information, 2000)
        # Do not call self.chatbot.close() here, just quit the app
        self.app.quit()
    
    def is_system_tray_available(self):
        """Check if system tray is available."""
        return self.isSystemTrayAvailable()
    
    def ensure_visible(self):
        """Ensure the system tray icon is visible."""
        if not self.isVisible():
            print("[DEBUG] System tray icon was hidden, making it visible")
            self.show()
        else:
            print("[DEBUG] System tray icon is already visible")
        
        # Additional check to ensure icon is properly displayed
        if not self.isSystemTrayAvailable():
            print("[DEBUG] Warning: System tray is not available on this system")
        else:
            print("[DEBUG] System tray is available and icon should be visible")
    
    def force_show(self):
        """Force show the system tray icon."""
        print("[DEBUG] Force showing system tray icon")
        self.hide()  # Hide first
        QTimer.singleShot(100, self.show)  # Show after a short delay
    
    def test_system_tray(self):
        """Test method to debug system tray issues."""
        print("[DEBUG] === SYSTEM TRAY DEBUG INFO ===")
        print(f"[DEBUG] System tray available: {self.isSystemTrayAvailable()}")
        print(f"[DEBUG] System tray supported: {QSystemTrayIcon.isSystemTrayAvailable()}")
        print(f"[DEBUG] Icon is null: {self.icon().isNull()}")
        print(f"[DEBUG] Is visible: {self.isVisible()}")
        print(f"[DEBUG] Tooltip: {self.toolTip()}")
        print(f"[DEBUG] Context menu exists: {self.contextMenu() is not None}")
        
        # Try to show a test message
        try:
            self.showMessage("CASI Test", "System tray test message", QSystemTrayIcon.Information, 3000)
            print("[DEBUG] Test message shown successfully")
        except Exception as e:
            print(f"[DEBUG] Failed to show test message: {e}")
        
        # Force show
        self.force_show()
        print("[DEBUG] === END DEBUG INFO ===")
    
class ClickableLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked()

    def clicked(self):
        # This will be set later by the parent
        pass

class Office365LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Office 365 Login Required")
        self.setFixedSize(400, 200)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        
        layout = QVBoxLayout(self)
        
        # Icon and title
        icon_label = QLabel()
        icon_label.setPixmap(QPixmap("CASInew-nbg.png").scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        title_label = QLabel("Office 365 Login Required")
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 18px;
                font-weight: bold;
                margin: 10px 0;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Message
        message_label = QLabel("You need to be logged in to Office 365 to create an IT helpdesk ticket.")
        message_label.setStyleSheet("""
            QLabel {
                color: #34495e;
                font-size: 12px;
                margin: 10px 0;
            }
        """)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.login_button = QPushButton("Login to Office 365")
        self.login_button.setStyleSheet(dialog_button_style)
        self.login_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet(dialog_button_style)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Set dialog style
        self.setStyleSheet("""
            QDialog {
                background-color: #ecf0f1;
                border-radius: 12px;
            }
        """)
        
        # Set focus to login button
        self.login_button.setFocus()

class Office365LoginPromptDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Office 365 Login Required")
        self.setFixedSize(350, 150)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # Center the dialog on the parent window
        if parent:
            self.move(parent.window().frameGeometry().center() - self.frameGeometry().center())
        
        layout = QVBoxLayout()
        
        # Message label
        message_label = QLabel("You need to be logged in to Office 365 to create an IT helpdesk ticket. Would you like to login now?")
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: white;
                padding: 15px;
            }
        """)
        layout.addWidget(message_label)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Yes button
        self.yes_button = QPushButton("Yes")
        self.yes_button.setStyleSheet(dialog_button_style)
        self.yes_button.clicked.connect(self.accept)
        button_layout.addWidget(self.yes_button)
        
        # No button
        self.no_button = QPushButton("No")
        self.no_button.setStyleSheet(dialog_button_style)
        self.no_button.clicked.connect(self.reject)
        button_layout.addWidget(self.no_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

class LoadingScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(280, 180)
        
        # Center the loading screen
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)  # Center all content
        
        # CASI Logo
        logo_label = QLabel()
        logo_path = resource_path("CASInew-nbg.png")
        logo_pixmap = QPixmap(logo_path)
        
        if logo_pixmap.isNull():
            # Fallback: try direct path
            logo_pixmap = QPixmap("CASInew-nbg.png")
            
        if not logo_pixmap.isNull():
            # Scale the logo properly - smaller size to fit better
            logo_pixmap = logo_pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            # Create a placeholder if logo not found
            logo_pixmap = QPixmap(80, 80)
            logo_pixmap.fill(QColor(44, 62, 80))  # Dark blue background
            painter = QPainter(logo_pixmap)
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Arial", 12, QFont.Bold))
            painter.drawText(logo_pixmap.rect(), Qt.AlignCenter, "CASI")
            painter.end()
            
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setFixedSize(80, 80)  # Fixed size to prevent stacking
        logo_label.setScaledContents(False)  # Don't scale contents automatically
        layout.addWidget(logo_label, alignment=Qt.AlignCenter)
        
        # Loading percentage
        self.percentage_label = QLabel("0%")
        self.percentage_label.setStyleSheet("""
            QLabel {
                color: #2ecc71;
                font-size: 28px;
                font-weight: bold;
                margin: 5px 0;
            }
        """)
        self.percentage_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.percentage_label, alignment=Qt.AlignCenter)
        
        # Set widget style with shadow effect
        self.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
                border-radius: 15px;
                border: 2px solid #bdc3c7;
            }
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)
        
        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_loading)
        self.progress_value = 0
        
    def start_loading(self):
        self.show()
        self.animation_timer.start(50)  # Update every 50ms for smoother animation
        
    def stop_loading(self):
        self.animation_timer.stop()
        self.hide()
        
    def update_loading(self):
        # Smooth progress animation
        if self.progress_value < 95:  # Don't go to 100% until we're ready
            self.progress_value += 1
            self.percentage_label.setText(f"{self.progress_value}%")
            
    def set_progress(self, value):
        self.progress_value = value
        self.percentage_label.setText(f"{value}%")
        
    def set_loading_text(self, text):
        # Keep this method for compatibility but we're not using text anymore
        pass

def move_to_right_middle(widget):
    screen = QApplication.primaryScreen()
    screen_geometry = screen.availableGeometry()
    widget_geometry = widget.frameGeometry()
    x = screen_geometry.width() - widget_geometry.width() - 10 
    y = (screen_geometry.height() - widget_geometry.height()) // 2
    widget.move(x, y)

def get_circular_pixmap(source, size):
    """Creates a circular pixmap from a path (str) or another pixmap."""
    if isinstance(source, str):
        full_path = resource_path(source)
        pixmap = QPixmap(full_path)
        if pixmap.isNull():
            # Create a fallback colored circle
            fallback = QPixmap(size, size)
            fallback.fill(Qt.transparent)
            painter = QPainter(fallback)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QColor(44, 62, 80))  # Dark blue
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(0, 0, size, size)
            painter.end()
            return fallback
    elif isinstance(source, QPixmap):
        pixmap = source
    else:
        return QPixmap()

    if pixmap.isNull():
        return QPixmap()

    pixmap = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
    circular = QPixmap(size, size)
    circular.fill(Qt.transparent)

    painter = QPainter(circular)
    painter.setRenderHint(QPainter.Antialiasing)
    path = QPainterPath()
    path.addEllipse(0, 0, size, size)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, pixmap)
    painter.end()

    return circular

def get_graph_token(client_id, client_secret, tenant_id):
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    app = msal.ConfidentialClientApplication(
        client_id,
        authority=authority,
        client_credential=client_secret,
    )
    scopes = ["https://graph.microsoft.com/.default"]
    result = app.acquire_token_for_client(scopes=scopes)
    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception(f"Could not obtain access token: {result}")

def send_graph_email(client_id, client_secret, tenant_id, sender_email, to_email, subject, body):
    access_token = get_graph_token(client_id, client_secret, tenant_id)
    url = f"https://graph.microsoft.com/v1.0/users/{sender_email}/sendMail"
    message = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "Text",
                "content": body
            },
            "toRecipients": [
                {"emailAddress": {"address": to_email}}
            ]
        }
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=message)
    # Print the response for debugging
    print("Graph API status:", response.status_code)
    print("Graph API response:", response.text)
    return response.status_code == 202

def send_graph_email_delegated(client_id, tenant_id, from_email, to_email, subject, body, attachments=None):
    access_token = get_user_token(client_id, tenant_id)
    url = "https://graph.microsoft.com/v1.0/me/sendMail"
    message = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "Text",
                "content": body
            },
            "toRecipients": [
                {"emailAddress": {"address": to_email}}
            ]
        }
    }
    if attachments:
        message["message"]["attachments"] = attachments
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=message)
    print("Graph API status:", response.status_code)
    print("Graph API response:", response.text)
    return response.status_code == 202

def get_user_token(client_id, tenant_id, cache_path=None):
    # Always ensure the CASI folder exists
    if cache_path is None:
        cache_dir = os.path.join(os.getenv("APPDATA"), "CASI")
        os.makedirs(cache_dir, exist_ok=True)
        cache_path = os.path.join(cache_dir, "token_cache.json")
    else:
        # Ensure the parent directory exists
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)

    authority = f"https://login.microsoftonline.com/{tenant_id}"
    cache = msal.SerializableTokenCache()

    # Try to load the cache, handle missing/corrupt file
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r") as f:
                cache.deserialize(f.read())
        except Exception as e:
            print(f"Token cache corrupted: {e}")
            try:
                os.remove(cache_path)
            except Exception as e2:
                print(f"Failed to remove corrupted token cache: {e2}")
            # Continue without cache (will prompt login)

    app = msal.PublicClientApplication(client_id, authority=authority, token_cache=cache)
    scopes = ["User.Read", "Mail.Send"]
    accounts = app.get_accounts()
    result = None
    if accounts:
        try:
            result = app.acquire_token_silent(scopes, account=accounts[0])
        except Exception as e:
            print(f"Silent token acquisition failed: {e}")
    if not result or "access_token" not in result:
        # Token is expired, invalid, or missing, force interactive login
        try:
            result = app.acquire_token_interactive(scopes=scopes)
        except Exception as e:
            print(f"Interactive login failed: {e}")
            raise Exception("Office 365 login failed. Please try again.")
    if "access_token" in result:
        try:
            with open(cache_path, "w") as f:
                f.write(cache.serialize())
        except Exception as e:
            print(f"Failed to write token cache: {e}")
        return result["access_token"]
    else:
        raise Exception(f"Could not obtain access token: {result}")

CHAT_HISTORY_FILE = "chat_history.json"

global_scrollbar_style = """
QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 4px 0 4px 0;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #2ecc71, stop:1 #27ae60
    );
    min-height: 24px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #43e97b, stop:1 #38f9d7
    );
}
QScrollBar::add-line:vertical, 
QScrollBar::sub-line:vertical,
QScrollBar::up-arrow:vertical, 
QScrollBar::down-arrow:vertical {
    background: none;
    border: none;
    height: 0px;
    width: 0px;
}
QScrollBar::add-page:vertical, 
QScrollBar::sub-page:vertical {
    background: none;
}
"""

dialog_button_style = """
QPushButton {
    background-color: #2ecc71;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 20px;
    font-size: 10px;
    font-weight: bold;
    margin: 4px;
}
QPushButton:hover {
    background-color: #27ae60;
}
QPushButton:pressed {
    background-color: #219150;
}
"""

def is_application_running():
    """Check if another instance of the application is already running."""
    current_pid = os.getpid()
    current_process = psutil.Process(current_pid)
    current_name = current_process.name()
    
    # Look for processes with similar names
    target_names = ['python.exe', 'chatbot_ui.exe', 'pythonw.exe']
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Skip the current process
            if proc.pid == current_pid:
                continue
                
            # Check if it's a Python process or our executable
            if proc.info['name'] in target_names:
                cmdline = proc.info['cmdline']
                if cmdline:
                    # Check for our specific application
                    cmdline_str = ' '.join(cmdline).lower()
                    if any(keyword in cmdline_str for keyword in ['chatbot_ui', 'casi', 'castoaibot']):
                        return True, proc.pid
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    return False, None

def create_lock_file():
    """Create a lock file to indicate the application is running."""
    lock_file = os.path.join(os.getenv("APPDATA"), "CASI", "casi_app.lock")
    os.makedirs(os.path.dirname(lock_file), exist_ok=True)
    
    try:
        with open(lock_file, 'w') as f:
            f.write(str(os.getpid()))
        return lock_file
    except Exception as e:
        print(f"Failed to create lock file: {e}")
        return None

def remove_lock_file(lock_file):
    """Remove the lock file when the application exits."""
    if lock_file and os.path.exists(lock_file):
        try:
            os.remove(lock_file)
        except Exception as e:
            print(f"Failed to remove lock file: {e}")

def check_single_instance():
    """Check if only one instance should be running and handle accordingly."""
    # This function is now handled in the main execution block
    # Keeping this for compatibility but it's not used
    return True

def already_running_mutex(mutexname="CASIAppMutex"):
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    mutex = kernel32.CreateMutexW(None, wintypes.BOOL(False), mutexname)
    last_error = ctypes.GetLastError()
    # ERROR_ALREADY_EXISTS == 183
    if last_error == 183:
        return True
    return False





if __name__ == "__main__":
    # Check if single instance detection is enabled
    if get_single_instance_enabled():
        print("[DEBUG] Single instance detection enabled")
        # Try multiple methods to detect if already running
        is_running = False
        detection_method = "none"
        
        # Method 1: Socket-based detection (most reliable)
        try:
            is_running = already_running_socket()
            if is_running:
                detection_method = "socket"
                print("[DEBUG] Socket detection: Another instance detected")
        except Exception as e:
            print(f"[DEBUG] Socket detection failed: {e}")
        
        # Method 2: Mutex-based detection (fallback)
        if not is_running:
            try:
                single_instance = SingleInstance()
                is_running = single_instance.already_running()
                if is_running:
                    detection_method = "mutex"
                    print("[DEBUG] Mutex detection: Another instance detected")
            except Exception as e:
                print(f"[DEBUG] Mutex detection failed: {e}")
        
        # Method 3: Process-based detection (final fallback)
        if not is_running:
            try:
                is_running, pid = is_application_running()
                if is_running:
                    detection_method = "process"
                    print(f"[DEBUG] Process detection: Another instance detected (PID: {pid})")
            except Exception as e:
                print(f"[DEBUG] Process detection failed: {e}")
        
        if is_running:
            from PyQt5.QtWidgets import QApplication, QMessageBox
            app = QApplication(sys.argv)
            QMessageBox.critical(None, "CASI Already Running", 
                               f"CASI is already running.\nOnly one instance can run at a time.\n\nDetection method: {detection_method}")
            sys.exit(1)
    else:
        print("[DEBUG] Single instance detection disabled")
    app = QApplication(sys.argv)
    print("[DEBUG] QApplication created")
    loading_screen = LoadingScreen()
    loading_screen.start_loading()
    app.processEvents()
    loading_screen.set_progress(40)
    app.processEvents()
    loading_screen.set_progress(60)
    app.processEvents()
    app.setStyleSheet(global_scrollbar_style)
    loading_screen.set_progress(80)
    app.processEvents()
    chatbot = ChatbotWidget()
    print("[DEBUG] ChatbotWidget created")
    global tray  # Ensure tray is global and not garbage collected
    tray = SystemTrayApp(app, chatbot)
    print("[DEBUG] SystemTrayApp created")
    
    # Ensure system tray is available and visible
    if tray.is_system_tray_available():
        print("[DEBUG] System tray is available")
        tray.show()
        tray.ensure_visible()
        tray.force_show()  # Force show to ensure visibility
        
        # Test the system tray to debug any issues
        QTimer.singleShot(2000, tray.test_system_tray)  # Test after 2 seconds
        
        print("[DEBUG] SystemTrayApp shown and visible")
    else:
        print("[DEBUG] Warning: System tray is not available!")
    loading_screen.set_progress(90)
    app.processEvents()
    chatbot.minimize_widget()  # Show minimized widget after loading
    chatbot.load_chat_history()
    loading_screen.set_progress(100)
    app.processEvents()
    QTimer.singleShot(800, loading_screen.stop_loading)
    sys.exit(app.exec_())

# In SystemTrayApp, add debug prints for tray icon creation, menu setup, and menu actions:


