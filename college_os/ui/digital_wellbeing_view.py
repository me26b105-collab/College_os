from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QFrame, QComboBox)
from PySide6.QtCore import Qt, QDate
from college_os.core.db import SessionLocal
from college_os.core.models import AppUsageRecord

class DigitalWellbeingView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("Screen Time & Digital Wellbeing")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #E0E0E0;")
        layout.addWidget(title)

        # Date Filter Bar
        filter_bar = QHBoxLayout()
        filter_bar.addWidget(QLabel("Select Date:"))
        self.date_combo = QComboBox()
        self.date_combo.setStyleSheet("padding: 8px; background: #2C2C2C; border: 1px solid #444; color: white; border-radius: 4px; min-width: 150px;")
        self.date_combo.currentTextChanged.connect(self.load_data_for_date)
        filter_bar.addWidget(self.date_combo)
        filter_bar.addStretch()
        layout.addLayout(filter_bar)

        # Overview Metrics Cards
        cards_layout = QHBoxLayout()
        self.total_card = self.create_card("Total Screen Time", "0.0 hrs", "#5E6AD2")
        self.edu_card = self.create_card("Productive Time", "0.0 hrs", "#2E7D32")
        self.distraction_card = self.create_card("Social & Gaming Time", "0.0 hrs", "#D32F2F")

        cards_layout.addWidget(self.total_card['frame'])
        cards_layout.addWidget(self.edu_card['frame'])
        cards_layout.addWidget(self.distraction_card['frame'])
        layout.addLayout(cards_layout)

        # App Usage Table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Application Process", "Category", "Time Spent", "Share %"])
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

        self.refresh_dates()

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
        return {'frame': frame, 'value': v}

    def refresh_dates(self):
        self.date_combo.blockSignals(True)
        self.date_combo.clear()
        
        today_str = QDate.currentDate().toString("yyyy-MM-dd")
        dates = [today_str]

        with SessionLocal() as session:
            records = session.query(AppUsageRecord.date).distinct().all()
            for r in records:
                if r[0] not in dates:
                    dates.append(r[0])

        dates.sort(reverse=True)
        self.date_combo.addItems(dates)
        self.date_combo.blockSignals(False)
        self.load_data_for_date()

    def load_data_for_date(self):
        selected_date = self.date_combo.currentText()
        if not selected_date:
            return

        self.table.setRowCount(0)
        with SessionLocal() as session:
            records = session.query(AppUsageRecord).filter(
                AppUsageRecord.date == selected_date
            ).order_by(AppUsageRecord.duration_minutes.desc()).all()

            total_mins = sum(r.duration_minutes for r in records)
            edu_mins = sum(r.duration_minutes for r in records if r.category in ["Programming", "Education"])
            distract_mins = sum(r.duration_minutes for r in records if r.category in ["Social Media", "Gaming", "Entertainment"])

            self.total_card['value'].setText(f"{total_mins / 60.0:.2f} hrs")
            self.edu_card['value'].setText(f"{edu_mins / 60.0:.2f} hrs")
            self.distraction_card['value'].setText(f"{distract_mins / 60.0:.2f} hrs")

            self.table.setRowCount(len(records))
            for row, r in enumerate(records):
                self.table.setItem(row, 0, QTableWidgetItem(r.app_name))
                self.table.setItem(row, 1, QTableWidgetItem(r.category))
                self.table.setItem(row, 2, QTableWidgetItem(f"{r.duration_minutes:.1f} mins"))

                pct = (r.duration_minutes / total_mins * 100) if total_mins > 0 else 0
                pct_item = QTableWidgetItem(f"{pct:.1f}%")
                self.table.setItem(row, 3, pct_item)