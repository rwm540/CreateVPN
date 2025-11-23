import sys
import time
import json
import subprocess
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QLabel, QComboBox, QHBoxLayout, QFrame,
                             QGraphicsDropShadowEffect, QMessageBox)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize, QThread, Signal
from PySide6.QtGui import QColor, QFont, QIcon

# Path to the compiled C# backend
def get_backend_path():
    if getattr(sys, 'frozen', False):
        # Running as compiled executable (PyInstaller)
        base_path = sys._MEIPASS
        if os.name == 'nt':
            return os.path.join(base_path, "vpn_engine.exe")
        return os.path.join(base_path, "vpn_engine")
    else:
        # Running from source
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../vpn_engine/bin/Debug/net8.0"))
        # Check for Windows exe first
        if os.path.exists(os.path.join(base_dir, "vpn_engine.exe")):
            return os.path.join(base_dir, "vpn_engine.exe")
        # Default to linux/mac binary name
        return os.path.join(base_dir, "vpn_engine")

BACKEND_PATH = get_backend_path()

class BackendWorker(QThread):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, command, args=[]):
        super().__init__()
        self.command = command
        self.args = args

    def run(self):
        try:
            # Run the C# backend
            cmd = [BACKEND_PATH, self.command] + self.args
            
            # If running from source (dotnet run), we might need different handling
            if not getattr(sys, 'frozen', False) and not os.path.exists(BACKEND_PATH):
                 # Fix: Use absolute path for project to avoid CWD issues
                 project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../vpn_engine"))
                 cmd = ["dotnet", "run", "--project", project_path, self.command] + self.args
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                self.finished.emit(result.stdout.strip())
            else:
                self.error.emit(result.stderr.strip())
        except Exception as e:
            self.error.emit(str(e))

class VPNClient(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Secure VPN Client (C# Powered)")
        self.setGeometry(100, 100, 400, 600)
        self.setStyleSheet("background-color: #1e1e2e;")  # Dark background

        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(20, 40, 20, 40)
        self.layout.setSpacing(20)

        # Header (Title)
        self.title_label = QLabel("My Free VPN")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("color: #cdd6f4; font-size: 24px; font-weight: bold;")
        self.layout.addWidget(self.title_label)

        # Status Indicator
        self.status_label = QLabel("DISCONNECTED")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #f38ba8; font-size: 14px; letter-spacing: 2px;")
        self.layout.addWidget(self.status_label)

        # Spacer
        self.layout.addStretch()

        # Connect Button Container
        self.btn_container = QWidget()
        self.btn_layout = QVBoxLayout(self.btn_container)
        self.btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Connect Button (Circular)
        self.connect_btn = QPushButton("⏻")
        self.connect_btn.setFixedSize(140, 140)
        self.connect_btn.setStyleSheet(self.get_btn_style("disconnected"))
        self.connect_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.connect_btn.clicked.connect(self.toggle_connection)
        
        # Shadow for button
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.connect_btn.setGraphicsEffect(shadow)

        self.btn_layout.addWidget(self.connect_btn)
        self.layout.addWidget(self.btn_container)

        # Spacer
        self.layout.addStretch()

        # Server Selection
        self.server_frame = QFrame()
        self.server_frame.setStyleSheet("""
            QFrame {
                background-color: #313244;
                border-radius: 15px;
                padding: 10px;
            }
        """)
        self.server_layout = QHBoxLayout(self.server_frame)
        
        self.location_icon = QLabel("🌍")
        self.location_icon.setStyleSheet("font-size: 20px; background: transparent;")
        
        self.server_combo = QComboBox()
        self.server_combo.setStyleSheet("""
            QComboBox {
                background-color: transparent;
                color: #cdd6f4;
                border: none;
                font-size: 14px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #313244;
                color: #cdd6f4;
                selection-background-color: #585b70;
            }
        """)
        
        self.server_layout.addWidget(self.location_icon)
        self.server_layout.addWidget(self.server_combo, 1)
        
        self.layout.addWidget(self.server_frame)

        # Edit Servers Button
        self.edit_servers_btn = QPushButton("Edit Servers (Local JSON)")
        self.edit_servers_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #89b4fa;
                border: 1px solid #89b4fa;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #89b4fa;
                color: #1e1e2e;
            }
        """)
        self.edit_servers_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.edit_servers_btn.clicked.connect(self.open_servers_file)
        self.layout.addWidget(self.edit_servers_btn)

        # Fetch Public Servers Button
        self.fetch_btn = QPushButton("Update Public Servers (Free)")
        self.fetch_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #a6e3a1;
                border: 1px solid #a6e3a1;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #a6e3a1;
                color: #1e1e2e;
            }
        """)
        self.fetch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.fetch_btn.clicked.connect(self.fetch_public_servers)
        self.layout.addWidget(self.fetch_btn)

        # Connection Logic Variables
        self.is_connected = False
        self.servers = []
        
        # Load Servers
        self.load_servers()

    def fetch_public_servers(self):
        self.status_label.setText("FETCHING SERVERS...")
        self.fetch_btn.setEnabled(False)
        self.worker = BackendWorker("fetch-public")
        self.worker.finished.connect(self.on_fetch_complete)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_fetch_complete(self, output):
        self.fetch_btn.setEnabled(True)
        self.load_servers() # Reload the list
        QMessageBox.information(self, "Success", "Public servers updated successfully!")

    def open_servers_file(self):
        # Try to find servers.json
        paths = [
            "servers.json",
            "../servers.json",
            os.path.join(os.path.dirname(__file__), "../servers.json")
        ]
        
        found_path = None
        for p in paths:
            if os.path.exists(p):
                found_path = os.path.abspath(p)
                break
        
        if found_path:
            if os.name == 'nt':
                os.startfile(found_path)
            else:
                subprocess.call(('xdg-open', found_path))
        else:
            QMessageBox.warning(self, "File Not Found", "Could not find servers.json")
            # Create it if missing
            with open("servers.json", "w") as f:
                f.write('[{"id":"local","name":"Local Server","ip":"127.0.0.1","load":"0%"}]')
            self.open_servers_file() # Try again

    def get_btn_style(self, state):
        if state == "connected":
            return """
                QPushButton {
                    background-color: #313244;
                    color: #a6e3a1;
                    border-radius: 70px;
                    font-size: 48px;
                    border: 2px solid #a6e3a1;
                }
                QPushButton:hover {
                    background-color: #45475a;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #313244;
                    color: #f38ba8;
                    border-radius: 70px;
                    font-size: 48px;
                    border: 2px solid #45475a;
                }
                QPushButton:hover {
                    background-color: #45475a;
                    border: 2px solid #f38ba8;
                }
            """

    def load_servers(self):
        self.status_label.setText("LOADING SERVERS...")
        self.worker = BackendWorker("list")
        self.worker.finished.connect(self.on_servers_loaded)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_servers_loaded(self, output):
        try:
            self.servers = json.loads(output)
            self.server_combo.clear()
            for server in self.servers:
                self.server_combo.addItem(server['name'], server['id'])
            self.status_label.setText("DISCONNECTED")
        except json.JSONDecodeError:
            self.status_label.setText("ERROR LOADING SERVERS")

    def toggle_connection(self):
        if not self.is_connected:
            # Connect
            server_id = self.server_combo.currentData()
            if not server_id:
                return
                
            self.status_label.setText("CONNECTING...")
            self.status_label.setStyleSheet("color: #fab387; font-size: 14px; letter-spacing: 2px;")
            self.connect_btn.setEnabled(False)
            
            self.worker = BackendWorker("connect", [server_id])
            self.worker.finished.connect(self.on_connected)
            self.worker.error.connect(self.on_error)
            self.worker.start()
        else:
            # Disconnect
            self.status_label.setText("DISCONNECTING...")
            self.worker = BackendWorker("disconnect")
            self.worker.finished.connect(self.on_disconnected)
            self.worker.error.connect(self.on_error)
            self.worker.start()

    def on_connected(self, output):
        if "SUCCESS" in output:
            self.is_connected = True
            self.connect_btn.setEnabled(True)
            self.status_label.setText("CONNECTED")
            self.status_label.setStyleSheet("color: #a6e3a1; font-size: 14px; letter-spacing: 2px; font-weight: bold;")
            self.connect_btn.setStyleSheet(self.get_btn_style("connected"))
            print(output)
        else:
            self.on_error("Connection failed")

    def on_disconnected(self, output):
        self.is_connected = False
        self.connect_btn.setEnabled(True)
        self.status_label.setText("DISCONNECTED")
        self.status_label.setStyleSheet("color: #f38ba8; font-size: 14px; letter-spacing: 2px;")
        self.connect_btn.setStyleSheet(self.get_btn_style("disconnected"))

    def on_error(self, error_msg):
        self.connect_btn.setEnabled(True)
        self.status_label.setText("ERROR")
        self.status_label.setStyleSheet("color: #red; font-size: 14px; letter-spacing: 2px;")
        QMessageBox.critical(self, "Error", f"Backend Error:\n{error_msg}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VPNClient()
    window.show()
    sys.exit(app.exec())
