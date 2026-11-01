import sys
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
