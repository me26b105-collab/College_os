from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QCalendarWidget, QComboBox
from college_os.core.db import SessionLocal
from college_os.core.models import Event

class CalendarView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setSpacing(20)

        # Left side: Interactive Calendar
        cal_layout = QVBoxLayout()
        self.calendar = QCalendarWidget()
        self.calendar.setStyleSheet("""
            QCalendarWidget { background-color: #2C2C2C; color: white; }
            QCalendarWidget QToolButton { color: white; }
            QCalendarWidget QMenu { background-color: #2C2C2C; color: white; }
            QCalendarWidget QSpinBox { background-color: #1E1E1E; color: white; }
        """)
        self.calendar.selectionChanged.connect(self.load_events)
        cal_layout.addWidget(self.calendar)
        
        # Right side: Daily Agenda
        agenda_layout = QVBoxLayout()
        self.date_label = QLabel("Events for Selected Day")
        self.date_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #E0E0E0;")
        
        self.event_list = QListWidget()
        self.event_list.setStyleSheet("background-color: #1E1E1E; border: 1px solid #333; border-radius: 8px; padding: 10px; font-size: 14px; color: #CCC;")
        
        form_layout = QHBoxLayout()
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Event Title")
        self.title_input.setStyleSheet("padding: 8px; background: #2C2C2C; border: 1px solid #444; color: white;")
        
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("10:30 AM")
        self.time_input.setStyleSheet("padding: 8px; background: #2C2C2C; border: 1px solid #444; color: white; max-width: 80px;")
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Meeting", "Birthday", "Reminder", "Class"])
        self.type_combo.setStyleSheet("padding: 8px; background: #2C2C2C; border: 1px solid #444; color: white;")
        
        add_btn = QPushButton("Add")
        add_btn.setStyleSheet("background-color: #5E6AD2; color: white; padding: 8px 15px; border-radius: 4px; font-weight: bold;")
        add_btn.clicked.connect(self.add_event)
        
        form_layout.addWidget(self.title_input)
        form_layout.addWidget(self.time_input)
        form_layout.addWidget(self.type_combo)
        form_layout.addWidget(add_btn)
        
        agenda_layout.addWidget(self.date_label)
        agenda_layout.addWidget(self.event_list)
        agenda_layout.addLayout(form_layout)
        
        layout.addLayout(cal_layout, 1)
        layout.addLayout(agenda_layout, 1)
        self.load_events()

    def add_event(self):
        title = self.title_input.text().strip()
        time_str = self.time_input.text().strip()
        event_type = self.type_combo.currentText()
        date_str = self.calendar.selectedDate().toString("yyyy-MM-dd")
        
        if not title: return
        
        with SessionLocal() as session:
            new_event = Event(title=title, date=date_str, time=time_str, event_type=event_type)
            session.add(new_event)
            session.commit()
            
        self.title_input.clear()
        self.time_input.clear()
        self.load_events()

    def load_events(self):
        self.event_list.clear()
        date_str = self.calendar.selectedDate().toString("yyyy-MM-dd")
        self.date_label.setText(f"Agenda: {date_str}")
        
        with SessionLocal() as session:
            events = session.query(Event).filter(Event.date == date_str).all()
            for e in events:
                time_tag = f"[{e.time}] " if e.time else ""
                self.event_list.addItem(f"{time_tag}{e.title}  —  {e.event_type}")