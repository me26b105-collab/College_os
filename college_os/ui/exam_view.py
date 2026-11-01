from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QComboBox, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QTabWidget, QProgressBar, QDoubleSpinBox)
from PySide6.QtCore import Qt, QDate
from college_os.core.db import SessionLocal
from college_os.core.models import Course, Exam, SyllabusTopic, MockTest

class ExamView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("Exam Centre & Syllabus Tracker")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #E0E0E0;")
        layout.addWidget(title)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #333; background-color: #1A1A1A; border-radius: 8px; }
            QTabBar::tab { background: #2C2C2C; color: #AAA; padding: 10px 20px; font-weight: bold; border-top-left-radius: 6px; border-top-right-radius: 6px; }
            QTabBar::tab:selected { background: #5E6AD2; color: white; }
        """)

        # Tab 1: Exams & Countdowns
        self.exam_tab = QWidget()
        self.setup_exam_tab()
        self.tabs.addTab(self.exam_tab, "Upcoming Exams")

        # Tab 2: Syllabus Tracker
        self.syllabus_tab = QWidget()
        self.setup_syllabus_tab()
        self.tabs.addTab(self.syllabus_tab, "Syllabus Tracker")

        # Tab 3: Mock Tests
        self.mock_tab = QWidget()
        self.setup_mock_tab()
        self.tabs.addTab(self.mock_tab, "Mock Test Manager")

        layout.addWidget(self.tabs)

    def setup_exam_tab(self):
        layout = QVBoxLayout(self.exam_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        form = QHBoxLayout()
        self.exam_title_input = QLineEdit()
        self.exam_title_input.setPlaceholderText("Exam Title (e.g. Midterm)")
        self.exam_title_input.setStyleSheet("padding: 8px; background: #2C2C2C; border: 1px solid #444; color: white; border-radius: 4px;")

        self.exam_course_combo = QComboBox()
        self.exam_course_combo.setStyleSheet("padding: 8px; background: #2C2C2C; border: 1px solid #444; color: white; border-radius: 4px;")

        self.exam_date_input = QLineEdit()
        self.exam_date_input.setPlaceholderText(QDate.currentDate().toString("yyyy-MM-dd"))
        self.exam_date_input.setText(QDate.currentDate().addDays(7).toString("yyyy-MM-dd"))
        self.exam_date_input.setStyleSheet("padding: 8px; background: #2C2C2C; border: 1px solid #444; color: white; border-radius: 4px; max-width: 110px;")

        self.exam_loc_input = QLineEdit()
        self.exam_loc_input.setPlaceholderText("Hall / Room")
        self.exam_loc_input.setStyleSheet("padding: 8px; background: #2C2C2C; border: 1px solid #444; color: white; border-radius: 4px; max-width: 110px;")

        self.exam_imp_combo = QComboBox()
        self.exam_imp_combo.addItems(["High", "Medium", "Low"])
        self.exam_imp_combo.setStyleSheet("padding: 8px; background: #2C2C2C; border: 1px solid #444; color: white; border-radius: 4px;")

        add_btn = QPushButton("Add Exam")
        add_btn.setStyleSheet("background-color: #5E6AD2; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold;")
        add_btn.clicked.connect(self.add_exam)

        form.addWidget(self.exam_title_input)
        form.addWidget(self.exam_course_combo)
        form.addWidget(self.exam_date_input)
        form.addWidget(self.exam_loc_input)
        form.addWidget(self.exam_imp_combo)
        form.addWidget(add_btn)
        layout.addLayout(form)

        self.exam_table = QTableWidget(0, 6)
        self.exam_table.setHorizontalHeaderLabels(["Exam", "Course", "Date", "Location", "Countdown", "Action"])
        self.style_table(self.exam_table)
        layout.addWidget(self.exam_table)

    def setup_syllabus_tab(self):
        layout = QVBoxLayout(self.syllabus_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Course:"))
        self.syllabus_course_combo = QComboBox()
        self.syllabus_course_combo.setStyleSheet("padding: 8px; background: #2C2C2C; border: 1px solid #444; color: white; border-radius: 4px; min-width: 180px;")
        self.syllabus_course_combo.currentIndexChanged.connect(self.load_syllabus_data)
        top_layout.addWidget(self.syllabus_course_combo)

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar { border: 1px solid #444; border-radius: 5px; text-align: center; color: white; background: #2C2C2C; height: 22px; }
            QProgressBar::chunk { background-color: #2E7D32; border-radius: 4px; }
        """)
        top_layout.addWidget(self.progress_bar, 1)
        layout.addLayout(top_layout)

        form = QHBoxLayout()
        self.unit_input = QLineEdit()
        self.unit_input.setPlaceholderText("Unit (e.g. Unit 1)")
        self.unit_input.setStyleSheet("padding: 8px; background: #2C2C2C; border: 1px solid #444; color: white; border-radius: 4px;")

        self.topic_input = QLineEdit()
        self.topic_input.setPlaceholderText("Topic (e.g. Binary Search Trees)")
        self.topic_input.setStyleSheet("padding: 8px; background: #2C2C2C; border: 1px solid #444; color: white; border-radius: 4px;")

        self.diff_combo = QComboBox()
        self.diff_combo.addItems(["Easy", "Medium", "Hard"])
        self.diff_combo.setStyleSheet("padding: 8px; background: #2C2C2C; border: 1px solid #444; color: white; border-radius: 4px;")

        add_topic_btn = QPushButton("Add Topic")
        add_topic_btn.setStyleSheet("background-color: #5E6AD2; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold;")
        add_topic_btn.clicked.connect(self.add_topic)

        form.addWidget(self.unit_input)
        form.addWidget(self.topic_input)
        form.addWidget(self.diff_combo)
        form.addWidget(add_topic_btn)
        layout.addLayout(form)

        self.syllabus_table = QTableWidget(0, 5)
        self.syllabus_table.setHorizontalHeaderLabels(["Unit", "Topic", "Difficulty", "Status", "Action"])
        self.style_table(self.syllabus_table)
        layout.addWidget(self.syllabus_table)

    def setup_mock_tab(self):
        layout = QVBoxLayout(self.mock_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        form = QHBoxLayout()
        self.mock_title_input = QLineEdit()
        self.mock_title_input.setPlaceholderText("Mock Title")
        self.mock_title_input.setStyleSheet("padding: 8px; background: #2C2C2C; border: 1px solid #444; color: white; border-radius: 4px;")

        self.mock_course_combo = QComboBox()
        self.mock_course_combo.setStyleSheet("padding: 8px; background: #2C2C2C; border: 1px solid #444; color: white; border-radius: 4px;")

        self.score_obtained = QDoubleSpinBox()
        self.score_obtained.setRange(0, 1000)
        self.score_obtained.setValue(80)
        self.score_obtained.setStyleSheet("padding: 6px; background: #2C2C2C; border: 1px solid #444; color: white; border-radius: 4px;")

        self.score_max = QDoubleSpinBox()
        self.score_max.setRange(1, 1000)
        self.score_max.setValue(100)
        self.score_max.setStyleSheet("padding: 6px; background: #2C2C2C; border: 1px solid #444; color: white; border-radius: 4px;")

        add_mock_btn = QPushButton("Log Score")
        add_mock_btn.setStyleSheet("background-color: #5E6AD2; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold;")
        add_mock_btn.clicked.connect(self.add_mock_test)

        form.addWidget(self.mock_title_input)
        form.addWidget(self.mock_course_combo)
        form.addWidget(QLabel("Score:"))
        form.addWidget(self.score_obtained)
        form.addWidget(QLabel("/"))
        form.addWidget(self.score_max)
        form.addWidget(add_mock_btn)
        layout.addLayout(form)

        self.mock_table = QTableWidget(0, 5)
        self.mock_table.setHorizontalHeaderLabels(["Test Title", "Course", "Date", "Percentage", "Action"])
        self.style_table(self.mock_table)
        layout.addWidget(self.mock_table)

    def style_table(self, table):
        table.setStyleSheet("""
            QTableWidget {
                background-color: #1E1E1E;
                color: #CCC;
                gridline-color: #333;
                border: 1px solid #333;
                border-radius: 6px;
            }
            QHeaderView::section {
                background-color: #2C2C2C;
                color: white;
                padding: 6px;
                border: 1px solid #333;
                font-weight: bold;
            }
        """)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def refresh_courses(self):
        for combo in [self.exam_course_combo, self.syllabus_course_combo, self.mock_course_combo]:
            combo.blockSignals(True)
            combo.clear()
            with SessionLocal() as session:
                courses = session.query(Course).all()
                for c in courses:
                    combo.addItem(c.code, str(c.id))
            combo.blockSignals(False)

        self.load_exams()
        self.load_syllabus_data()
        self.load_mock_tests()

    def add_exam(self):
        title = self.exam_title_input.text().strip()
        course_id = self.exam_course_combo.currentData()
        date_str = self.exam_date_input.text().strip()
        loc = self.exam_loc_input.text().strip() or "Main Hall"
        imp = self.exam_imp_combo.currentText()

        if not title or not course_id or not date_str:
            return

        with SessionLocal() as session:
            exam = Exam(course_id=course_id, title=title, date=date_str, location=loc, importance=imp)
            session.add(exam)
            session.commit()

        self.exam_title_input.clear()
        self.load_exams()

    def load_exams(self):
        self.exam_table.setRowCount(0)
        today = QDate.currentDate()
        with SessionLocal() as session:
            exams = session.query(Exam).all()
            self.exam_table.setRowCount(len(exams))
            for row, e in enumerate(exams):
                self.exam_table.setItem(row, 0, QTableWidgetItem(e.title))
                self.exam_table.setItem(row, 1, QTableWidgetItem(e.course.code if e.course else "N/A"))
                self.exam_table.setItem(row, 2, QTableWidgetItem(e.date))
                self.exam_table.setItem(row, 3, QTableWidgetItem(e.location))

                e_date = QDate.fromString(e.date, "yyyy-MM-dd")
                if e_date.isValid():
                    days_left = today.daysTo(e_date)
                    if days_left > 0:
                        cd_str = f"{days_left} day(s) left"
                    elif days_left == 0:
                        cd_str = "TODAY!"
                    else:
                        cd_str = f"Overdue ({abs(days_left)} days ago)"
                else:
                    cd_str = e.date

                cd_item = QTableWidgetItem(cd_str)
                if "TODAY" in cd_str or "Overdue" in cd_str:
                    cd_item.setForeground(Qt.red)
                else:
                    cd_item.setForeground(Qt.cyan)
                self.exam_table.setItem(row, 4, cd_item)

                del_btn = QPushButton("Delete")
                del_btn.setStyleSheet("background-color: #D32F2F; color: white; border-radius: 4px; padding: 2px 8px;")
                del_btn.clicked.connect(lambda _, eid=e.id: self.delete_exam(eid))
                self.exam_table.setCellWidget(row, 5, del_btn)

    def delete_exam(self, exam_id):
        with SessionLocal() as session:
            e = session.query(Exam).filter(Exam.id == exam_id).first()
            if e:
                session.delete(e)
                session.commit()
        self.load_exams()

    def add_topic(self):
        course_id = self.syllabus_course_combo.currentData()
        unit = self.unit_input.text().strip()
        topic = self.topic_input.text().strip()
        diff = self.diff_combo.currentText()

        if not course_id or not unit or not topic:
            return

        with SessionLocal() as session:
            st = SyllabusTopic(course_id=course_id, unit_name=unit, topic_name=topic, difficulty=diff, status="Not Started")
            session.add(st)
            session.commit()

        self.unit_input.clear()
        self.topic_input.clear()
        self.load_syllabus_data()

    def load_syllabus_data(self):
        course_id = self.syllabus_course_combo.currentData()
        self.syllabus_table.setRowCount(0)
        if not course_id:
            self.progress_bar.setValue(0)
            return

        with SessionLocal() as session:
            topics = session.query(SyllabusTopic).filter(SyllabusTopic.course_id == course_id).all()
            total = len(topics)
            completed = sum(1 for t in topics if t.status in ["Revised", "Confident"])

            pct = int((completed / total * 100)) if total > 0 else 0
            self.progress_bar.setValue(pct)

            self.syllabus_table.setRowCount(len(topics))
            for row, t in enumerate(topics):
                self.syllabus_table.setItem(row, 0, QTableWidgetItem(t.unit_name))
                self.syllabus_table.setItem(row, 1, QTableWidgetItem(t.topic_name))
                self.syllabus_table.setItem(row, 2, QTableWidgetItem(t.difficulty))

                status_combo = QComboBox()
                status_combo.addItems(["Not Started", "Learning", "Revised", "Confident"])
                status_combo.setCurrentText(t.status)
                status_combo.setStyleSheet("background: #2C2C2C; color: white;")
                status_combo.currentTextChanged.connect(lambda new_s, tid=t.id: self.update_topic_status(tid, new_s))
                self.syllabus_table.setCellWidget(row, 3, status_combo)

                del_btn = QPushButton("Delete")
                del_btn.setStyleSheet("background-color: #D32F2F; color: white; border-radius: 4px; padding: 2px 8px;")
                del_btn.clicked.connect(lambda _, tid=t.id: self.delete_topic(tid))
                self.syllabus_table.setCellWidget(row, 4, del_btn)

    def update_topic_status(self, topic_id, new_status):
        with SessionLocal() as session:
            t = session.query(SyllabusTopic).filter(SyllabusTopic.id == topic_id).first()
            if t:
                t.status = new_status
                session.commit()
        self.load_syllabus_data()

    def delete_topic(self, topic_id):
        with SessionLocal() as session:
            t = session.query(SyllabusTopic).filter(SyllabusTopic.id == topic_id).first()
            if t:
                session.delete(t)
                session.commit()
        self.load_syllabus_data()

    def add_mock_test(self):
        title = self.mock_title_input.text().strip()
        course_id = self.mock_course_combo.currentData()
        obtained = self.score_obtained.value()
        max_m = self.score_max.value()
        today_str = QDate.currentDate().toString("yyyy-MM-dd")

        if not title or not course_id or max_m <= 0:
            return

        with SessionLocal() as session:
            m = MockTest(course_id=course_id, title=title, date=today_str, marks_obtained=obtained, max_marks=max_m)
            session.add(m)
            session.commit()

        self.mock_title_input.clear()
        self.load_mock_tests()

    def load_mock_tests(self):
        self.mock_table.setRowCount(0)
        with SessionLocal() as session:
            mocks = session.query(MockTest).all()
            self.mock_table.setRowCount(len(mocks))
            for row, m in enumerate(mocks):
                self.mock_table.setItem(row, 0, QTableWidgetItem(m.title))
                self.mock_table.setItem(row, 1, QTableWidgetItem(m.course.code if m.course else "N/A"))
                self.mock_table.setItem(row, 2, QTableWidgetItem(m.date))

                pct = (m.marks_obtained / m.max_marks) * 100 if m.max_marks > 0 else 0
                pct_item = QTableWidgetItem(f"{m.marks_obtained:.1f} / {m.max_marks:.1f} ({pct:.1f}%)")
                if pct >= 75:
                    pct_item.setForeground(Qt.green)
                elif pct >= 50:
                    pct_item.setForeground(Qt.yellow)
                else:
                    pct_item.setForeground(Qt.red)

                self.mock_table.setItem(row, 3, pct_item)

                del_btn = QPushButton("Delete")
                del_btn.setStyleSheet("background-color: #D32F2F; color: white; border-radius: 4px; padding: 2px 8px;")
                del_btn.clicked.connect(lambda _, mid=m.id: self.delete_mock(mid))
                self.mock_table.setCellWidget(row, 4, del_btn)

    def delete_mock(self, mock_id):
        with SessionLocal() as session:
            m = session.query(MockTest).filter(MockTest.id == mock_id).first()
            if m:
                session.delete(m)
                session.commit()
        self.load_mock_tests()