from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QMessageBox, QFrame)
from PySide6.QtCore import Qt, QDate
from college_os.core.db import SessionLocal
from college_os.core.models import Course, TimetableSlot, Task, Exam, SyllabusTopic, StudySession

HOURS = [
    "08:00 AM", "09:00 AM", "10:00 AM", "11:00 AM", 
    "12:00 PM", "01:00 PM", "02:00 PM", "03:00 PM", 
    "04:00 PM", "05:00 PM", "06:00 PM", "07:00 PM", "08:00 PM"
]

class SchedulerView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("Smart Study Scheduler Engine")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #E0E0E0;")
        layout.addWidget(title)

        # Control Panel
        panel_frame = QFrame()
        panel_frame.setStyleSheet("background-color: #1A1A1A; border: 1px solid #333; border-radius: 8px; padding: 12px;")
        panel_layout = QHBoxLayout(panel_frame)

        desc = QLabel("Scans your timetable free slots, pending tasks, upcoming exams & syllabus gaps to generate a study plan.")
        desc.setStyleSheet("color: #AAA; font-size: 13px;")

        gen_btn = QPushButton("Generate 7-Day Plan")
        gen_btn.setStyleSheet("background-color: #2E7D32; color: white; padding: 10px 18px; border-radius: 6px; font-weight: bold;")
        gen_btn.clicked.connect(self.generate_schedule)

        clear_btn = QPushButton("Clear All Sessions")
        clear_btn.setStyleSheet("background-color: #D32F2F; color: white; padding: 10px 18px; border-radius: 6px; font-weight: bold;")
        clear_btn.clicked.connect(self.clear_schedule)

        panel_layout.addWidget(desc, 1)
        panel_layout.addWidget(gen_btn)
        panel_layout.addWidget(clear_btn)
        layout.addWidget(panel_frame)

        # Schedule Table
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Date", "Time Slot", "Course", "Study Focus", "AI Reason", "Action"])
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1E1E1E;
                color: #CCC;
                gridline-color: #333;
                border: 1px solid #333;
                border-radius: 8px;
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
        layout.addWidget(self.table)

        self.load_schedule()

    def generate_schedule(self):
        today = QDate.currentDate()
        with SessionLocal() as session:
            courses = session.query(Course).all()
            if not courses:
                QMessageBox.warning(self, "No Data", "Please add courses first.")
                return

            # Build busy slot lookup from TimetableSlot (day_index 0..6 -> time_index 0..12)
            timetable_slots = session.query(TimetableSlot).all()
            busy_timetable = {(s.day_index, s.time_index): s.course.code for s in timetable_slots if s.course}

            # Fetch priority inputs
            exams = session.query(Exam).all()
            tasks = session.query(Task).filter(Task.is_completed == False).all()
            topics = session.query(SyllabusTopic).filter(SyllabusTopic.status != "Confident").all()

            # Clear old future sessions
            session.query(StudySession).delete()
            session.commit()

            new_sessions_count = 0

            # Iterate through next 7 days
            for d in range(7):
                curr_date = today.addDays(d)
                date_str = curr_date.toString("yyyy-MM-dd")
                day_index = curr_date.dayOfWeek() - 1  # 0: Mon, 6: Sun

                for t_idx in range(13):
                    # Check if slot is occupied by recurring class
                    if (day_index, t_idx) in busy_timetable:
                        continue

                    # Determine course priority for this free slot
                    selected_course = None
                    reason_str = ""
                    focus_str = ""

                    # Priority 1: Course with exam in next 10 days
                    for ex in exams:
                        ex_date = QDate.fromString(ex.date, "yyyy-MM-dd")
                        days_to_exam = curr_date.daysTo(ex_date)
                        if 0 <= days_to_exam <= 10:
                            selected_course = ex.course
                            focus_str = f"Exam Prep: {ex.title}"
                            reason_str = f"Exam in {days_to_exam} day(s)"
                            break

                    # Priority 2: Unrevised syllabus topic
                    if not selected_course:
                        for top in topics:
                            selected_course = top.course
                            focus_str = f"Topic: {top.unit_name} - {top.topic_name}"
                            reason_str = f"Syllabus Status: {top.status}"
                            break

                    # Priority 3: Pending Task
                    if not selected_course:
                        for tsk in tasks:
                            if tsk.course:
                                selected_course = tsk.course
                                focus_str = f"Assignment: {tsk.title}"
                                reason_str = "Pending Task"
                                break

                    # Limit max 2 study sessions per day to prevent burn out
                    sessions_today = session.query(StudySession).filter(StudySession.date == date_str).count()
                    if sessions_today >= 2:
                        break

                    if selected_course:
                        sess_obj = StudySession(
                            course_id=selected_course.id,
                            date=date_str,
                            time_index=t_idx,
                            topic_summary=focus_str,
                            reason=reason_str,
                            status="Scheduled"
                        )
                        session.add(sess_obj)
                        new_sessions_count += 1

            session.commit()

        self.load_schedule()
        QMessageBox.information(self, "Scheduler Complete", f"Generated {new_sessions_count} study sessions across open timetable slots.")

    def load_schedule(self):
        self.table.setRowCount(0)
        with SessionLocal() as session:
            sessions = session.query(StudySession).order_by(StudySession.date.asc(), StudySession.time_index.asc()).all()
            self.table.setRowCount(len(sessions))
            for row, s in enumerate(sessions):
                time_str = HOURS[s.time_index] if 0 <= s.time_index < len(HOURS) else f"Slot {s.time_index}"
                
                self.table.setItem(row, 0, QTableWidgetItem(s.date))
                self.table.setItem(row, 1, QTableWidgetItem(time_str))
                self.table.setItem(row, 2, QTableWidgetItem(s.course.code if s.course else "N/A"))
                self.table.setItem(row, 3, QTableWidgetItem(s.topic_summary))
                
                reason_item = QTableWidgetItem(s.reason)
                reason_item.setForeground(Qt.cyan)
                self.table.setItem(row, 4, reason_item)

                del_btn = QPushButton("Done")
                del_btn.setStyleSheet("background-color: #2E7D32; color: white; border-radius: 4px; padding: 2px 8px;")
                del_btn.clicked.connect(lambda _, sid=s.id: self.delete_session(sid))
                self.table.setCellWidget(row, 5, del_btn)

    def delete_session(self, session_id):
        with SessionLocal() as session:
            s = session.query(StudySession).filter(StudySession.id == session_id).first()
            if s:
                session.delete(s)
                session.commit()
        self.load_schedule()

    def clear_schedule(self):
        with SessionLocal() as session:
            session.query(StudySession).delete()
            session.commit()
        self.load_schedule()