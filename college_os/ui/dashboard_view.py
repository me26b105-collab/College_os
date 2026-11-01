from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QPushButton, QScrollArea)
from PySide6.QtCore import Qt, QDate
from college_os.core.db import SessionLocal
from college_os.core.models import Task, Event, TimetableSlot, AppUsageRecord, Exam

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        # Header Title Bar
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Command Centre")
        title.setStyleSheet("font-size: 28px; font-weight: 800; color: #FAFAFA; background: transparent;")
        
        today_formatted = QDate.currentDate().toString("dddd, MMMM d, yyyy")
        subtitle = QLabel(f"Overview for {today_formatted}")
        subtitle.setStyleSheet("font-size: 13px; color: #71717A; background: transparent;")
        
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        
        shortcut_pill = QLabel("Press Ctrl + K for Quick Actions")
        shortcut_pill.setStyleSheet("background-color: #18181B; border: 1px solid #27272A; color: #A1A1AA; border-radius: 6px; padding: 6px 12px; font-size: 12px; font-weight: 500;")

        header_layout.addLayout(title_box)
        header_layout.addStretch()
        header_layout.addWidget(shortcut_pill)
        layout.addLayout(header_layout)

        # Top Metric Cards Row
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(16)
        
        self.classes_card = self.create_metric_card("Classes Today", "0 Scheduled", "#6366F1")
        self.tasks_card = self.create_metric_card("Pending Tasks", "0 Open", "#F59E0B")
        self.exams_card = self.create_metric_card("Upcoming Exams", "0 Soon", "#EF4444")
        self.screentime_card = self.create_metric_card("Screen Time Today", "0.0 hrs", "#10B981")

        metrics_layout.addWidget(self.classes_card['frame'])
        metrics_layout.addWidget(self.tasks_card['frame'])
        metrics_layout.addWidget(self.exams_card['frame'])
        metrics_layout.addWidget(self.screentime_card['frame'])
        layout.addLayout(metrics_layout)

        # Main Columns Area
        cols_layout = QHBoxLayout()
        cols_layout.setSpacing(20)

        # Left Column: Today's Agenda
        left_card = QFrame()
        left_card.setProperty("class", "Card")
        left_card.setStyleSheet("QFrame { background-color: #18181B; border: 1px solid #27272A; border-radius: 10px; padding: 16px; }")
        self.left_layout = QVBoxLayout(left_card)
        
        agenda_header = QLabel("Today's Agenda & Schedule")
        agenda_header.setStyleSheet("font-size: 16px; font-weight: 700; color: #FAFAFA; margin-bottom: 8px;")
        self.left_layout.addWidget(agenda_header)
        
        self.agenda_container = QVBoxLayout()
        self.left_layout.addLayout(self.agenda_container)
        self.left_layout.addStretch()

        # Right Column: Pending Assignments & Tasks
        right_card = QFrame()
        right_card.setStyleSheet("QFrame { background-color: #18181B; border: 1px solid #27272A; border-radius: 10px; padding: 16px; }")
        self.right_layout = QVBoxLayout(right_card)
        
        tasks_header = QLabel("Pending Tasks & Assignments")
        tasks_header.setStyleSheet("font-size: 16px; font-weight: 700; color: #FAFAFA; margin-bottom: 8px;")
        self.right_layout.addWidget(tasks_header)
        
        self.tasks_container = QVBoxLayout()
        self.right_layout.addLayout(self.tasks_container)
        self.right_layout.addStretch()

        cols_layout.addWidget(left_card, 1)
        cols_layout.addWidget(right_card, 1)
        layout.addLayout(cols_layout, 1)

        self.refresh_data()

    def create_metric_card(self, title_text, val_text, color_hex):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: #18181B;
                border: 1px solid #27272A;
                border-left: 4px solid {color_hex};
                border-radius: 8px;
                padding: 14px;
            }}
        """)
        l = QVBoxLayout(frame)
        l.setSpacing(4)
        t = QLabel(title_text)
        t.setStyleSheet("color: #A1A1AA; font-size: 11px; font-weight: 600; text-transform: uppercase;")
        v = QLabel(val_text)
        v.setStyleSheet("color: #FAFAFA; font-size: 20px; font-weight: 700;")
        l.addWidget(t)
        l.addWidget(v)
        return {'frame': frame, 'value': v}

    def refresh_data(self):
        # Clear previous item layouts
        while self.agenda_container.count():
            child = self.agenda_container.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        while self.tasks_container.count():
            child = self.tasks_container.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        today_date = QDate.currentDate().toString("yyyy-MM-dd")
        day_index = QDate.currentDate().dayOfWeek() - 1 

        time_map = {
            0: "08:00 AM", 1: "09:00 AM", 2: "10:00 AM", 3: "11:00 AM",
            4: "12:00 PM", 5: "01:00 PM", 6: "02:00 PM", 7: "03:00 PM",
            8: "04:00 PM", 9: "05:00 PM", 10: "06:00 PM", 11: "07:00 PM", 12: "08:00 PM"
        }

        agenda_items_count = 0
        tasks_items_count = 0

        with SessionLocal() as session:
            # Classes Today
            slots = session.query(TimetableSlot).filter(TimetableSlot.day_index == day_index).all()
            for slot in slots:
                if slot.course:
                    agenda_items_count += 1
                    time_str = time_map.get(slot.time_index, "Unknown")
                    item = self.create_item_row(f"Class: {slot.course.code}", time_str, "#6366F1")
                    self.agenda_container.addWidget(item)

            # Calendar Events Today
            events = session.query(Event).filter(Event.date == today_date).all()
            for e in events:
                agenda_items_count += 1
                item = self.create_item_row(e.title, e.time or e.event_type, "#EC4899")
                self.agenda_container.addWidget(item)

            # Incomplete Tasks
            tasks = session.query(Task).filter(Task.is_completed == False).all()
            tasks_items_count = len(tasks)
            for t in tasks:
                course_tag = t.course.code if t.course else "General"
                item = self.create_item_row(t.title, course_tag, "#F59E0B")
                self.tasks_container.addWidget(item)

            # Metric Updates
            exams = session.query(Exam).all()
            today_recs = session.query(AppUsageRecord).filter(AppUsageRecord.date == today_date).all()
            total_screentime_mins = sum(r.duration_minutes for r in today_recs)

            self.classes_card['value'].setText(f"{agenda_items_count} Sessions")
            self.tasks_card['value'].setText(f"{tasks_items_count} Pending")
            self.exams_card['value'].setText(f"{len(exams)} Total")
            self.screentime_card['value'].setText(f"{total_screentime_mins / 60.0:.1f} hrs")

        # Empty States
        if agenda_items_count == 0:
            empty_agenda = QLabel("No classes or events scheduled for today.")
            empty_agenda.setStyleSheet("color: #71717A; font-size: 13px; padding: 20px; background: transparent;")
            empty_agenda.setAlignment(Qt.AlignCenter)
            self.agenda_container.addWidget(empty_agenda)

        if tasks_items_count == 0:
            empty_tasks = QLabel("All tasks completed! You're clear for now.")
            empty_tasks.setStyleSheet("color: #71717A; font-size: 13px; padding: 20px; background: transparent;")
            empty_tasks.setAlignment(Qt.AlignCenter)
            self.tasks_container.addWidget(empty_tasks)

    def create_item_row(self, title_text, badge_text, tag_color_hex):
        row = QFrame()
        row.setStyleSheet("""
            QFrame {
                background-color: #27272A;
                border-radius: 6px;
                padding: 10px 12px;
            }
        """)
        l = QHBoxLayout(row)
        l.setContentsMargins(0, 0, 0, 0)
        
        t = QLabel(title_text)
        t.setStyleSheet("color: #FAFAFA; font-weight: 500; font-size: 13px; background: transparent;")
        
        badge = QLabel(badge_text)
        badge.setStyleSheet(f"""
            background-color: {tag_color_hex}22;
            color: {tag_color_hex};
            border: 1px solid {tag_color_hex}44;
            border-radius: 4px;
            padding: 2px 8px;
            font-size: 11px;
            font-weight: 600;
        """)

        l.addWidget(t, 1)
        l.addWidget(badge)
        return row