import os

files = {
    "college_os/ui/settings_view.py": '''from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                 QPushButton, QFrame, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt
import csv
import json
import os
import shutil
from college_os.core.db import SessionLocal
from college_os.core.models import Course, Task, GradeItem, Note

class SettingsView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        title = QLabel("Settings & Data Management")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #FAFAFA;")
        layout.addWidget(title)

        # Export Section
        export_box = QFrame()
        export_box.setStyleSheet("background-color: #121215; border: 1px solid #27272A; border-radius: 8px; padding: 16px;")
        exp_layout = QVBoxLayout(export_box)

        exp_title = QLabel("Data Export Engine")
        exp_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #FAFAFA;")
        exp_desc = QLabel("Export your academic data to CSV spreadsheets or full JSON snapshots.")
        exp_desc.setStyleSheet("color: #71717A; font-size: 12px;")

        exp_layout.addWidget(exp_title)
        exp_layout.addWidget(exp_desc)
        exp_layout.addSpacing(10)

        btn_row = QHBoxLayout()
        csv_btn = QPushButton("📊 Export Tasks & Grades to CSV")
        csv_btn.setProperty("class", "PrimaryButton")
        csv_btn.clicked.connect(self.export_csv)

        json_btn = QPushButton("📁 Export Full System JSON")
        json_btn.setProperty("class", "SecondaryButton")
        json_btn.clicked.connect(self.export_json)

        btn_row.addWidget(csv_btn)
        btn_row.addWidget(json_btn)
        btn_row.addStretch()
        exp_layout.addLayout(btn_row)

        layout.addWidget(export_box)

        # Backup Section
        backup_box = QFrame()
        backup_box.setStyleSheet("background-color: #121215; border: 1px solid #27272A; border-radius: 8px; padding: 16px;")
        bak_layout = QVBoxLayout(backup_box)

        bak_title = QLabel("Database Backup & Disaster Recovery")
        bak_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #FAFAFA;")
        bak_desc = QLabel("Create standalone SQLite snapshots of your database or restore from a backup file.")
        bak_desc.setStyleSheet("color: #71717A; font-size: 12px;")

        bak_layout.addWidget(bak_title)
        bak_layout.addWidget(bak_desc)
        bak_layout.addSpacing(10)

        bak_btn_row = QHBoxLayout()
        backup_btn = QPushButton("💾 Create Database Snapshot (.db)")
        backup_btn.setProperty("class", "PrimaryButton")
        backup_btn.clicked.connect(self.create_db_backup)

        restore_btn = QPushButton("🔄 Restore Database")
        restore_btn.setProperty("class", "DangerButton")
        restore_btn.clicked.connect(self.restore_db_backup)

        bak_btn_row.addWidget(backup_btn)
        bak_btn_row.addWidget(restore_btn)
        bak_btn_row.addStretch()
        bak_layout.addLayout(bak_btn_row)

        layout.addWidget(backup_box)

        # System Info Section
        info_box = QFrame()
        info_box.setStyleSheet("background-color: #121215; border: 1px solid #27272A; border-radius: 8px; padding: 16px;")
        info_layout = QVBoxLayout(info_box)

        info_title = QLabel("College OS Build Info")
        info_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #FAFAFA;")
        
        info_text = QLabel("• Version: 1.1.0\\n• Architecture: Python 3 / PySide6 / SQLAlchemy\\n• Storage: Local SQLite Engine (Zero Cloud / Offline-First)")
        info_text.setStyleSheet("color: #A1A1AA; font-size: 13px; line-height: 1.6;")

        info_layout.addWidget(info_title)
        info_layout.addSpacing(6)
        info_layout.addWidget(info_text)

        layout.addWidget(info_box)
        layout.addStretch()

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Tasks & Grades CSV", "college_os_export.csv", "CSV Files (*.csv)")
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Section", "Field 1", "Field 2", "Field 3", "Field 4"])
                
                with SessionLocal() as session:
                    writer.writerow(["--- TASKS ---"])
                    for t in session.query(Task).all():
                        writer.writerow(["Task", t.title, "Completed" if t.is_completed else "Pending", t.course.code if t.course else "General"])
                    
                    writer.writerow([])
                    writer.writerow(["--- GRADES ---"])
                    for g in session.query(GradeItem).all():
                        writer.writerow(["Grade", g.title, g.category, f"{g.score_achieved}/{g.max_score}", f"{g.weight_percent}%"])

            QMessageBox.information(self, "Export Successful", f"Data exported successfully to:\\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export CSV:\\n{str(e)}")

    def export_json(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Full JSON Backup", "college_os_data.json", "JSON Files (*.json)")
        if not path:
            return

        try:
            data = {"courses": [], "tasks": [], "notes": []}
            with SessionLocal() as session:
                for c in session.query(Course).all():
                    data["courses"].append({"id": c.id, "name": c.name, "code": c.code, "credits": c.credits})
                for t in session.query(Task).all():
                    data["tasks"].append({"title": t.title, "completed": t.is_completed})
                for n in session.query(Note).all():
                    data["notes"].append({"title": n.title, "content": n.content, "tags": n.tags})

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            QMessageBox.information(self, "Export Successful", f"JSON data exported to:\\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export JSON:\\n{str(e)}")

    def create_db_backup(self):
        path, _ = QFileDialog.getSaveFileName(self, "Backup Database Snapshot", "college_os_backup.db", "Database Files (*.db)")
        if not path:
            return

        try:
            db_source = os.path.abspath("college_os.db")
            if os.path.exists(db_source):
                shutil.copy(db_source, path)
                QMessageBox.information(self, "Backup Created", f"Database snapshot saved to:\\n{path}")
            else:
                QMessageBox.warning(self, "Database Not Found", "Could not locate primary college_os.db file.")
        except Exception as e:
            QMessageBox.critical(self, "Backup Error", f"Failed to create backup:\\n{str(e)}")

    def restore_db_backup(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Database Backup to Restore", "", "Database Files (*.db)")
        if not path:
            return

        confirm = QMessageBox.question(
            self, "Confirm Database Restore",
            "Restoring a database snapshot will overwrite your current data. Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                db_target = os.path.abspath("college_os.db")
                shutil.copy(path, db_target)
                QMessageBox.information(self, "Restore Complete", "Database restored successfully! Please restart College OS to load the restored data.")
            except Exception as e:
                QMessageBox.critical(self, "Restore Error", f"Failed to restore database:\\n{str(e)}")
''',

    "college_os/ui/command_palette.py": '''from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QListWidget, 
                             QListWidgetItem, QLabel, QHBoxLayout, QGraphicsDropShadowEffect, QWidget)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

class CommandPalette(QDialog):
    navigation_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(580, 360)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        container = QWidget(self)
        container.setObjectName("Container")
        container.setStyleSheet("""
            QWidget#Container {
                background-color: #18181B;
                border: 1px solid #3F3F46;
                border-radius: 12px;
            }
        """)

        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(16, 16, 16, 16)
        container_layout.setSpacing(12)

        search_box = QHBoxLayout()
        k_icon = QLabel("🔍")
        k_icon.setStyleSheet("font-size: 16px; background: transparent;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type a command or jump to screen... (Ctrl+K)")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                font-size: 15px;
                color: #FAFAFA;
            }
        """)
        self.search_input.textChanged.connect(self.filter_items)

        esc_hint = QLabel("ESC to close")
        esc_hint.setStyleSheet("color: #71717A; font-size: 11px; background: #27272A; border-radius: 4px; padding: 2px 6px;")

        search_box.addWidget(k_icon)
        search_box.addWidget(self.search_input, 1)
        search_box.addWidget(esc_hint)
        container_layout.addLayout(search_box)

        line = QLabel()
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: #27272A;")
        container_layout.addWidget(line)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                color: #FAFAFA;
            }
            QListWidget::item {
                padding: 10px 12px;
                border-radius: 6px;
                margin-bottom: 2px;
            }
            QListWidget::item:selected {
                background-color: #27272A;
                color: #FFFFFF;
            }
        """)
        self.list_widget.itemActivated.connect(self.execute_item)
        container_layout.addWidget(self.list_widget)

        main_layout.addWidget(container)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setYOffset(10)
        container.setGraphicsEffect(shadow)

        self.commands = [
            ("Jump to: Command Centre Dashboard", 0, "🏠"),
            ("Jump to: Course Dashboard", 1, "📚"),
            ("Jump to: Assignment & Task Manager", 2, "✅"),
            ("Jump to: Weekly Timetable", 3, "📅"),
            ("Jump to: Calendar Events", 4, "📆"),
            ("Jump to: Focus Study Timer", 5, "⏱️"),
            ("Jump to: Attendance Safe-to-Skip Calculator", 6, "📊"),
            ("Jump to: Exam Centre & Syllabus Tracker", 7, "🎯"),
            ("Jump to: Smart Study Scheduler Engine", 8, "🤖"),
            ("Jump to: Screen Time & Digital Wellbeing", 9, "💻"),
            ("Jump to: Notes & Knowledge Library", 10, "📝"),
            ("Jump to: Personal Projects & Kanban Board", 11, "🗂️"),
            ("Jump to: Assessment & Grade Tracker", 12, "📈"),
            ("Jump to: Settings & Data Management", 13, "⚙️"),
        ]

        self.populate_items()

    def populate_items(self):
        self.list_widget.clear()
        for title, idx, icon in self.commands:
            item = QListWidgetItem(f"{icon}   {title}")
            item.setData(Qt.ItemDataRole.UserRole, idx)
            self.list_widget.addItem(item)
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def filter_items(self, text):
        query = text.lower().strip()
        self.list_widget.clear()
        for title, idx, icon in self.commands:
            if query in title.lower():
                item = QListWidgetItem(f"{icon}   {title}")
                item.setData(Qt.ItemDataRole.UserRole, idx)
                self.list_widget.addItem(item)
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def execute_item(self, item):
        index = item.data(Qt.ItemDataRole.UserRole)
        self.navigation_requested.emit(index)
        self.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Down:
            current = self.list_widget.currentRow()
            if current < self.list_widget.count() - 1:
                self.list_widget.setCurrentRow(current + 1)
        elif event.key() == Qt.Key.Key_Up:
            current = self.list_widget.currentRow()
            if current > 0:
                self.list_widget.setCurrentRow(current - 1)
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            curr_item = self.list_widget.currentItem()
            if curr_item:
                self.execute_item(curr_item)
        else:
            super().keyPressEvent(event)
''',

    "main.py": '''import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QPushButton, QLabel, QStackedWidget, 
                             QSystemTrayIcon, QMenu, QStyle)
from PySide6.QtGui import QAction, QShortcut, QKeySequence
from PySide6.QtCore import Qt

from college_os.core.db import init_db
from college_os.core.tracker import BackgroundTracker
from college_os.ui.theme import THEME_QSS
from college_os.ui.command_palette import CommandPalette

from college_os.ui.courses_view import CoursesView
from college_os.ui.tasks_view import TasksView
from college_os.ui.timetable_view import TimetableView 
from college_os.ui.calendar_view import CalendarView
from college_os.ui.dashboard_view import DashboardView
from college_os.ui.timer_view import TimerView
from college_os.ui.attendance_view import AttendanceView
from college_os.ui.exam_view import ExamView
from college_os.ui.scheduler_view import SchedulerView
from college_os.ui.digital_wellbeing_view import DigitalWellbeingView
from college_os.ui.notes_view import NotesView
from college_os.ui.kanban_view import KanbanView
from college_os.ui.analytics_view import AnalyticsView
from college_os.ui.settings_view import SettingsView

class Sidebar(QWidget):
    def __init__(self, nav_callback, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(240)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 24, 16, 24)
        layout.setSpacing(6)
        
        brand_layout = QHBoxLayout()
        logo = QLabel("⚡")
        logo.setStyleSheet("font-size: 20px; background: transparent;")
        title = QLabel("College OS")
        title.setStyleSheet("font-size: 18px; font-weight: 800; color: #FAFAFA; background: transparent;")
        
        brand_layout.addWidget(logo)
        brand_layout.addWidget(title)
        brand_layout.addStretch()
        layout.addLayout(brand_layout)
        
        spacer = QLabel()
        spacer.setFixedHeight(15)
        layout.addWidget(spacer)

        nav_items = [
            ("Command Centre", 0, "🏠"), 
            ("Courses", 1, "📚"), 
            ("Tasks & Work", 2, "✅"), 
            ("Timetable", 3, "📅"), 
            ("Calendar", 4, "📆"),
            ("Study Timer", 5, "⏱️"),
            ("Attendance", 6, "📊"),
            ("Exam Centre", 7, "🎯"),
            ("Smart Scheduler", 8, "🤖"),
            ("Screen Time", 9, "💻"),
            ("Notes & Resources", 10, "📝"),
            ("Projects & Kanban", 11, "🗂️"),
            ("Grade Tracker", 12, "📈"),
            ("Settings & Backup", 13, "⚙️")
        ]
        
        self.buttons = []
        for name, index, icon in nav_items:
            btn = QPushButton(f" {icon}   {name}")
            btn.setProperty("class", "NavButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, idx=index: nav_callback(idx))
            layout.addWidget(btn)
            self.buttons.append((btn, index))
            
        layout.addStretch()
        self.set_active_button(0)

    def set_active_button(self, active_index):
        for btn, idx in self.buttons:
            if idx == active_index:
                btn.setProperty("active", "true")
            else:
                btn.setProperty("active", "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("College OS")
        self.resize(1280, 830)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.sidebar = Sidebar(self.switch_view)
        main_layout.addWidget(self.sidebar)
        
        self.content_area = QStackedWidget()
        
        self.dashboard_view = DashboardView()
        self.courses_view = CoursesView()
        self.tasks_view = TasksView()
        self.timetable_view = TimetableView()
        self.calendar_view = CalendarView()
        self.timer_view = TimerView()
        self.attendance_view = AttendanceView()
        self.exam_view = ExamView()
        self.scheduler_view = SchedulerView()
        self.wellbeing_view = DigitalWellbeingView()
        self.notes_view = NotesView()
        self.kanban_view = KanbanView()
        self.analytics_view = AnalyticsView()
        self.settings_view = SettingsView()
        
        self.content_area.addWidget(self.dashboard_view)       
        self.content_area.addWidget(self.courses_view) 
        self.content_area.addWidget(self.tasks_view)   
        self.content_area.addWidget(self.timetable_view)
        self.content_area.addWidget(self.calendar_view)
        self.content_area.addWidget(self.timer_view)
        self.content_area.addWidget(self.attendance_view)
        self.content_area.addWidget(self.exam_view)
        self.content_area.addWidget(self.scheduler_view)
        self.content_area.addWidget(self.wellbeing_view)
        self.content_area.addWidget(self.notes_view)
        self.content_area.addWidget(self.kanban_view)
        self.content_area.addWidget(self.analytics_view)
        self.content_area.addWidget(self.settings_view)
        
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(32, 32, 32, 32)
        content_layout.addWidget(self.content_area)
        main_layout.addWidget(content_container, 1)

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        
        tray_menu = QMenu()
        show_action = QAction("Open College OS", self)
        show_action.triggered.connect(self.showNormal)
        quit_action = QAction("Exit App", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        self.bg_tracker = BackgroundTracker()
        self.bg_tracker.start()

        self.cmd_shortcut = QShortcut(QKeySequence("Ctrl+K"), self)
        self.cmd_shortcut.activated.connect(self.open_command_palette)

    def open_command_palette(self):
        palette = CommandPalette(self)
        palette.navigation_requested.connect(self.switch_view)
        palette.exec()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "College OS",
            "College OS is running in the background tracking screen time.",
            QSystemTrayIcon.MessageIcon.Information,
            1500
        )

    def switch_view(self, index):
        self.content_area.setCurrentIndex(index)
        self.sidebar.set_active_button(index)
        if index == 0: self.dashboard_view.refresh_data()
        if index == 2: self.tasks_view.refresh_data()
        if index == 6: self.attendance_view.refresh_courses()
        if index == 7: self.exam_view.refresh_courses()
        if index == 8: self.scheduler_view.load_schedule()
        if index == 9: self.wellbeing_view.refresh_dates()
        if index == 10: self.notes_view.refresh_courses()
        if index == 11: self.kanban_view.refresh_projects()
        if index == 12: self.analytics_view.refresh_all()

def main():
    init_db()
    app = QApplication(sys.argv)
    app.setStyleSheet(THEME_QSS)
    app.setQuitOnLastWindowClosed(False)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
'''
}

for path, content in files.items():
    dirname = os.path.dirname(path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"✅ Successfully updated: {path}")

print("\n🚀 Phase 14 Patch Applied Cleanly!")