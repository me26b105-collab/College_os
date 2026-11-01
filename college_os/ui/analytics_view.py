from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QComboBox, QFrame, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QDoubleSpinBox)
from PySide6.QtCore import Qt
from college_os.core.db import SessionLocal
from college_os.core.models import Course, GradeItem

class AnalyticsView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        title = QLabel("Assessment & Grade Tracker")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #FAFAFA;")
        layout.addWidget(title)

        # Overview Metrics Cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(14)
        
        self.avg_pct_card = self.create_card("Overall Weighted Average", "0.0%", "#6366F1")
        self.credits_card = self.create_card("Total Credits Tracked", "0.0 Units", "#10B981")
        self.items_count_card = self.create_card("Assessments Logged", "0 Total", "#F59E0B")

        cards_layout.addWidget(self.avg_pct_card['frame'])
        cards_layout.addWidget(self.credits_card['frame'])
        cards_layout.addWidget(self.items_count_card['frame'])
        layout.addLayout(cards_layout)

        # Course Performance Overview Table
        course_sec_lbl = QLabel("Course Percentage Breakdown")
        course_sec_lbl.setStyleSheet("font-size: 16px; font-weight: 700; color: #FAFAFA;")
        layout.addWidget(course_sec_lbl)

        self.course_table = QTableWidget(0, 4)
        self.course_table.setHorizontalHeaderLabels(["Course Code", "Course Name", "Credits", "Current Grade %"])
        self.course_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.course_table)

        # Assessment Logger Section
        assess_frame = QFrame()
        assess_frame.setStyleSheet("background-color: #121215; border: 1px solid #27272A; border-radius: 8px; padding: 14px;")
        assess_layout = QVBoxLayout(assess_frame)

        form_title = QLabel("Log Assessment Grade")
        form_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #FAFAFA;")
        assess_layout.addWidget(form_title)

        form_row = QHBoxLayout()
        
        self.course_combo = QComboBox()
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Title (e.g. Midterm Exam)")
        
        self.cat_combo = QComboBox()
        self.cat_combo.addItems(["Exam", "Assignment", "Quiz", "Project", "Lab"])

        self.score_spin = QDoubleSpinBox()
        self.score_spin.setRange(0, 1000)
        self.score_spin.setValue(85.0)

        self.max_score_spin = QDoubleSpinBox()
        self.max_score_spin.setRange(1, 1000)
        self.max_score_spin.setValue(100.0)

        self.weight_spin = QDoubleSpinBox()
        self.weight_spin.setRange(0.1, 100.0)
        self.weight_spin.setValue(20.0)

        add_btn = QPushButton("+ Add Grade")
        add_btn.setProperty("class", "PrimaryButton")
        add_btn.clicked.connect(self.add_grade_item)

        form_row.addWidget(QLabel("Course:"))
        form_row.addWidget(self.course_combo)
        form_row.addWidget(self.title_input, 1)
        form_row.addWidget(QLabel("Type:"))
        form_row.addWidget(self.cat_combo)
        form_row.addWidget(QLabel("Score:"))
        form_row.addWidget(self.score_spin)
        form_row.addWidget(QLabel("/"))
        form_row.addWidget(self.max_score_spin)
        form_row.addWidget(QLabel("Weight (%):"))
        form_row.addWidget(self.weight_spin)
        form_row.addWidget(add_btn)

        assess_layout.addLayout(form_row)
        layout.addWidget(assess_frame)

        # Grade Items List Table
        self.items_table = QTableWidget(0, 6)
        self.items_table.setHorizontalHeaderLabels(["Assessment", "Course", "Category", "Score / Max", "Weight", "Action"])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.items_table)

        self.refresh_all()

    def create_card(self, title_text, val_text, color_hex):
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

    def refresh_all(self):
        self.refresh_course_combo()
        self.load_analytics()

    def refresh_course_combo(self):
        self.course_combo.blockSignals(True)
        self.course_combo.clear()
        with SessionLocal() as session:
            courses = session.query(Course).all()
            for c in courses:
                self.course_combo.addItem(f"{c.code} - {c.name}", str(c.id))
        self.course_combo.blockSignals(False)

    def add_grade_item(self):
        c_id = self.course_combo.currentData()
        title = self.title_input.text().strip()
        cat = self.cat_combo.currentText()
        score = self.score_spin.value()
        max_s = self.max_score_spin.value()
        weight = self.weight_spin.value()

        if not c_id or not title:
            return

        with SessionLocal() as session:
            item = GradeItem(
                course_id=c_id,
                title=title,
                category=cat,
                score_achieved=score,
                max_score=max_s,
                weight_percent=weight
            )
            session.add(item)
            session.commit()

        self.title_input.clear()
        self.load_analytics()

    def load_analytics(self):
        self.course_table.setRowCount(0)
        self.items_table.setRowCount(0)

        total_credits = 0.0
        all_course_pcts = []

        with SessionLocal() as session:
            courses = session.query(Course).all()
            self.course_table.setRowCount(len(courses))

            for row, c in enumerate(courses):
                items = session.query(GradeItem).filter(GradeItem.course_id == c.id).all()
                
                if items:
                    total_weight = sum(it.weight_percent for it in items)
                    weighted_score_sum = sum((it.score_achieved / it.max_score) * it.weight_percent for it in items)
                    course_pct = (weighted_score_sum / total_weight * 100.0) if total_weight > 0 else 0.0
                    all_course_pcts.append(course_pct)
                    total_credits += c.credits
                else:
                    course_pct = 0.0

                self.course_table.setItem(row, 0, QTableWidgetItem(c.code))
                self.course_table.setItem(row, 1, QTableWidgetItem(c.name))
                self.course_table.setItem(row, 2, QTableWidgetItem(f"{c.credits:.1f}"))
                self.course_table.setItem(row, 3, QTableWidgetItem(f"{course_pct:.1f}%"))

            overall_pct = (sum(all_course_pcts) / len(all_course_pcts)) if all_course_pcts else 0.0

            # Load Logged Grade Items Table
            all_items = session.query(GradeItem).all()
            self.items_table.setRowCount(len(all_items))
            for row, it in enumerate(all_items):
                self.items_table.setItem(row, 0, QTableWidgetItem(it.title))
                self.items_table.setItem(row, 1, QTableWidgetItem(it.course.code if it.course else "General"))
                self.items_table.setItem(row, 2, QTableWidgetItem(it.category))
                self.items_table.setItem(row, 3, QTableWidgetItem(f"{it.score_achieved:.1f} / {it.max_score:.1f}"))
                self.items_table.setItem(row, 4, QTableWidgetItem(f"{it.weight_percent:.1f}%"))

                del_btn = QPushButton("Delete")
                del_btn.setProperty("class", "DangerButton")
                del_btn.clicked.connect(lambda _, item_id=it.id: self.delete_grade_item(item_id))
                self.items_table.setCellWidget(row, 5, del_btn)

            self.avg_pct_card['value'].setText(f"{overall_pct:.1f}%")
            self.credits_card['value'].setText(f"{total_credits:.1f} Units")
            self.items_count_card['value'].setText(f"{len(all_items)} Items")

    def delete_grade_item(self, item_id):
        with SessionLocal() as session:
            it = session.query(GradeItem).filter(GradeItem.id == item_id).first()
            if it:
                session.delete(it)
                session.commit()
        self.load_analytics()