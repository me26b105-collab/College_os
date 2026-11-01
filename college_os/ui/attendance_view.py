import math
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QSpinBox, QFrame)
from PySide6.QtCore import Qt, QDate
from college_os.core.db import SessionLocal
from college_os.core.models import Course, AttendanceRecord

class AttendanceView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        title = QLabel("Attendance Tracker & Safe-to-Skip Calculator")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #E0E0E0;")
        layout.addWidget(title)

        # Top Bar: Course Selector + Action Buttons
        top_bar = QHBoxLayout()
        self.course_combo = QComboBox()
        self.course_combo.setStyleSheet("padding: 10px; background: #2C2C2C; border: 1px solid #444; border-radius: 6px; color: white; min-width: 200px;")
        self.course_combo.currentIndexChanged.connect(self.load_attendance_data)
        
        btn_present = QPushButton("+ Present")
        btn_present.setStyleSheet("background-color: #2E7D32; color: white; padding: 10px 18px; border-radius: 6px; font-weight: bold;")
        btn_present.clicked.connect(lambda: self.mark_attendance("Present"))

        btn_absent = QPushButton("+ Absent")
        btn_absent.setStyleSheet("background-color: #C62828; color: white; padding: 10px 18px; border-radius: 6px; font-weight: bold;")
        btn_absent.clicked.connect(lambda: self.mark_attendance("Absent"))

        top_bar.addWidget(QLabel("Course:"))
        top_bar.addWidget(self.course_combo)
        top_bar.addWidget(btn_present)
        top_bar.addWidget(btn_absent)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        # Middle Metric Cards
        cards_layout = QHBoxLayout()
        
        self.pct_card = self.create_card("Current Attendance", "0.0%", "#5E6AD2")
        self.attended_card = self.create_card("Classes Attended", "0 / 0", "#2C2C2C")
        self.advisor_card = self.create_card("Attendance Status", "No data", "#2C2C2C")

        cards_layout.addWidget(self.pct_card['frame'])
        cards_layout.addWidget(self.attended_card['frame'])
        cards_layout.addWidget(self.advisor_card['frame'])
        layout.addLayout(cards_layout)

        # Calculator Box
        calc_frame = QFrame()
        calc_frame.setStyleSheet("background-color: #1A1A1A; border: 1px solid #333; border-radius: 8px; padding: 15px;")
        calc_layout = QHBoxLayout(calc_frame)
        
        calc_label = QLabel("Target Attendance Threshold (%):")
        calc_label.setStyleSheet("color: #AAA; font-size: 14px; font-weight: bold;")
        
        self.target_spin = QSpinBox()
        self.target_spin.setRange(50, 100)
        self.target_spin.setValue(75)
        self.target_spin.setStyleSheet("padding: 5px; background: #2C2C2C; color: white; border: 1px solid #444;")
        self.target_spin.valueChanged.connect(self.load_attendance_data)

        self.calc_result_label = QLabel("Set target threshold to see predictions.")
        self.calc_result_label.setStyleSheet("color: #E0E0E0; font-size: 14px; font-weight: 500;")

        calc_layout.addWidget(calc_label)
        calc_layout.addWidget(self.target_spin)
        calc_layout.addWidget(self.calc_result_label, 1)
        layout.addWidget(calc_frame)

        # Attendance History Table
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Date", "Status", "Action"])
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

    def create_card(self, title_text, value_text, color):
        frame = QFrame()
        frame.setStyleSheet(f"background-color: #1E1E1E; border-left: 5px solid {color}; border-radius: 6px; padding: 10px;")
        l = QVBoxLayout(frame)
        t = QLabel(title_text)
        t.setStyleSheet("color: #888; font-size: 12px; font-weight: bold;")
        v = QLabel(value_text)
        v.setStyleSheet("color: white; font-size: 22px; font-weight: bold; margin-top: 5px;")
        l.addWidget(t)
        l.addWidget(v)
        return {'frame': frame, 'value': v, 'frame_ref': frame}

    def refresh_courses(self):
        self.course_combo.blockSignals(True)
        self.course_combo.clear()
        with SessionLocal() as session:
            courses = session.query(Course).all()
            for c in courses:
                self.course_combo.addItem(f"{c.code} - {c.name}", str(c.id))
        self.course_combo.blockSignals(False)
        self.load_attendance_data()

    def mark_attendance(self, status):
        course_id = self.course_combo.currentData()
        if not course_id:
            return

        today_str = QDate.currentDate().toString("yyyy-MM-dd")
        with SessionLocal() as session:
            rec = AttendanceRecord(course_id=course_id, date=today_str, status=status)
            session.add(rec)
            session.commit()

        self.load_attendance_data()

    def load_attendance_data(self):
        course_id = self.course_combo.currentData()
        if not course_id:
            self.pct_card['value'].setText("0.0%")
            self.attended_card['value'].setText("0 / 0")
            self.advisor_card['value'].setText("No Course Selected")
            self.table.setRowCount(0)
            return

        with SessionLocal() as session:
            records = session.query(AttendanceRecord).filter(AttendanceRecord.course_id == course_id).order_by(AttendanceRecord.date.desc()).all()
            
            total = len(records)
            attended = sum(1 for r in records if r.status == "Present")
            pct = (attended / total * 100) if total > 0 else 0.0

            # Update Metrics
            self.pct_card['value'].setText(f"{pct:.1f}%")
            self.attended_card['value'].setText(f"{attended} / {total}")
            
            # Safe-to-skip / Catch-up calculations
            target_pct = self.target_spin.value()
            target_frac = target_pct / 100.0

            if total == 0:
                self.advisor_card['value'].setText("No Logs")
                self.calc_result_label.setText("Log attendance entries to compute target projections.")
            elif pct >= target_pct:
                # Calculate safe to skip: (attended) / (total + skip) >= target_frac
                # attended >= target_frac * total + target_frac * skip
                # skip <= (attended - target_frac * total) / target_frac
                skips = math.floor((attended - target_frac * total) / target_frac)
                self.advisor_card['value'].setText(f"Safe (+{skips} skips)")
                self.calc_result_label.setText(f"You can safely skip <b>{skips}</b> consecutive class(es) while staying above {target_pct}%.")
            else:
                # Calculate required consecutive classes: (attended + req) / (total + req) >= target_frac
                # attended + req >= target_frac * total + target_frac * req
                # req * (1 - target_frac) >= target_frac * total - attended
                req = math.ceil((target_frac * total - attended) / (1 - target_frac))
                self.advisor_card['value'].setText(f"Warning (-{req} classes)")
                self.calc_result_label.setText(f"You must attend <b>{req}</b> consecutive class(es) to reach your target of {target_pct}%.")

            # Update Table
            self.table.setRowCount(len(records))
            for row, r in enumerate(records):
                self.table.setItem(row, 0, QTableWidgetItem(r.date))
                
                status_item = QTableWidgetItem(r.status)
                if r.status == "Present":
                    status_item.setForeground(Qt.green)
                else:
                    status_item.setForeground(Qt.red)
                self.table.setItem(row, 1, status_item)

                del_btn = QPushButton("Delete")
                del_btn.setStyleSheet("background-color: #D32F2F; color: white; border-radius: 4px; padding: 2px 8px;")
                del_btn.clicked.connect(lambda _, rec_id=r.id: self.delete_record(rec_id))
                self.table.setCellWidget(row, 2, del_btn)

    def delete_record(self, record_id):
        with SessionLocal() as session:
            rec = session.query(AttendanceRecord).filter(AttendanceRecord.id == record_id).first()
            if rec:
                session.delete(rec)
                session.commit()
        self.load_attendance_data()