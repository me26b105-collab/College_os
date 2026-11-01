from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QListWidget, 
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
