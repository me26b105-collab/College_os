from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QHeaderView, QTableWidgetItem, QInputDialog, QMessageBox
from PySide6.QtCore import Qt
from college_os.core.db import SessionLocal
from college_os.core.models import Course, TimetableSlot

class TimetableView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        title = QLabel("Timetable (Double-click a cell to assign a course)")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #E0E0E0;")
        layout.addWidget(title)

        self.table = QTableWidget(13, 7)
        self.table.setHorizontalHeaderLabels(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        
        hours = [
            "08:00 AM", "09:00 AM", "10:00 AM", "11:00 AM", 
            "12:00 PM", "01:00 PM", "02:00 PM", "03:00 PM", 
            "04:00 PM", "05:00 PM", "06:00 PM", "07:00 PM", "08:00 PM"
        ]
        self.table.setVerticalHeaderLabels(hours)
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1E1E1E;
                color: #CCC;
                gridline-color: #333;
                border: 1px solid #333;
                border-radius: 8px;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #2C2C2C;
                color: white;
                padding: 8px;
                border: 1px solid #333;
                font-weight: bold;
            }
        """)
        
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Disable manual typing and connect double-click
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self.assign_course)
        
        layout.addWidget(self.table)
        self.load_timetable()

    def load_timetable(self):
        self.table.clearContents()
        with SessionLocal() as session:
            slots = session.query(TimetableSlot).all()
            for slot in slots:
                if slot.course:
                    item = QTableWidgetItem(slot.course.code)
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setForeground(Qt.white)
                    self.table.setItem(slot.time_index, slot.day_index, item)

    def assign_course(self, row, col):
        with SessionLocal() as session:
            courses = session.query(Course).all()
            if not courses:
                QMessageBox.warning(self, "No Courses", "Please add a course in the Courses tab first.")
                return
            
            course_list = ["Clear Slot"] + [c.code for c in courses]
            course_map = {c.code: c.id for c in courses}
            
            selected_code, ok = QInputDialog.getItem(self, "Assign Course", "Select Course:", course_list, 0, False)
            
            if ok:
                # Remove any existing slot at this time and day
                existing_slot = session.query(TimetableSlot).filter_by(day_index=col, time_index=row).first()
                if existing_slot:
                    session.delete(existing_slot)
                
                # Add the new course to the slot (if not cleared)
                if selected_code != "Clear Slot":
                    new_slot = TimetableSlot(day_index=col, time_index=row, course_id=course_map[selected_code])
                    session.add(new_slot)
                    
                session.commit()
        
        self.load_timetable()