import ctypes
from ctypes import wintypes
import os
from PySide6.QtCore import QThread, QDate
from college_os.core.db import SessionLocal
from college_os.core.models import AppUsageRecord

CATEGORY_MAP = {
    # Programming
    "code.exe": "Programming",
    "pycharm64.exe": "Programming",
    "idea64.exe": "Programming",
    "devenv.exe": "Programming",
    "python.exe": "Programming",
    "windows-terminal.exe": "Programming",
    "cmd.exe": "Programming",
    "powershell.exe": "Programming",
    
    # Browsing & Education
    "chrome.exe": "Browsing",
    "msedge.exe": "Browsing",
    "firefox.exe": "Browsing",
    "brave.exe": "Browsing",
    "opera.exe": "Browsing",
    "winword.exe": "Education",
    "powerpnt.exe": "Education",
    "excel.exe": "Education",
    "acroctr.exe": "Education",
    "notion.exe": "Education",
    
    # Gaming & Social
    "steam.exe": "Gaming",
    "epicgameslauncher.exe": "Gaming",
    "valorant.exe": "Gaming",
    "leagueoflegends.exe": "Gaming",
    "discord.exe": "Social Media",
    "telegram.exe": "Social Media",
    "whatsapp.exe": "Social Media",
    
    # Entertainment
    "spotify.exe": "Entertainment",
    "vlc.exe": "Entertainment",
    "netflix.exe": "Entertainment"
}

def get_active_process_name():
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if not hwnd:
            return None
        pid = wintypes.DWORD()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        h_process = ctypes.windll.kernel32.OpenProcess(0x0400 | 0x0010, False, pid)
        if not h_process:
            return None
        buffer = ctypes.create_unicode_buffer(512)
        ctypes.windll.psapi.GetModuleFileNameExW(h_process, None, buffer, 512)
        ctypes.windll.kernel32.CloseHandle(h_process)
        exe_path = buffer.value
        if exe_path:
            return os.path.basename(exe_path).lower()
        return None
    except Exception:
        return None

class BackgroundTracker(QThread):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True

    def run(self):
        while self.running:
            app_exe = get_active_process_name()
            if app_exe and app_exe not in ["system", "idle", "explorer.exe"]:
                category = CATEGORY_MAP.get(app_exe, "Other")
                today_str = QDate.currentDate().toString("yyyy-MM-dd")
                try:
                    with SessionLocal() as session:
                        record = session.query(AppUsageRecord).filter(
                            AppUsageRecord.app_name == app_exe,
                            AppUsageRecord.date == today_str
                        ).first()

                        if record:
                            record.duration_minutes += (5.0 / 60.0)
                        else:
                            record = AppUsageRecord(
                                app_name=app_exe,
                                category=category,
                                duration_minutes=(5.0 / 60.0),
                                date=today_str
                            )
                            session.add(record)
                        session.commit()
                except Exception:
                    pass
            self.msleep(5000)

    def stop(self):
        self.running = False
        self.wait()