from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QInputDialog
from PySide6.QtCore import Qt
from college_os.core.db import SessionLocal
from college_os.core.models import Course

class CoursesView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        title = QLabel("Course Management")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #E0E0E0;")
        layout.addWidget(title)

        form_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Course Name (e.g. Data Structures)")
        self.name_input.setStyleSheet("padding: 10px; background: #2C2C2C; border: 1px solid #444; border-radius: 6px; color: white;")
        
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Code (e.g. CS201)")
        self.code_input.setStyleSheet("padding: 10px; background: #2C2C2C; border: 1px solid #444; border-radius: 6px; color: white;")
        
        add_btn = QPushButton("Add Course")
        add_btn.setStyleSheet("background-color: #5E6AD2; color: white; padding: 10px 20px; border-radius: 6px; font-weight: bold;")
        add_btn.clicked.connect(self.add_course)

        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.code_input)
        form_layout.addWidget(add_btn)
        layout.addLayout(form_layout)

        self.course_list = QListWidget()
        self.course_list.setStyleSheet("background-color: #1E1E1E; border: 1px solid #333; border-radius: 8px; padding: 15px; font-size: 15px; color: #CCC;")
        layout.addWidget(self.course_list)
        
        btn_layout = QHBoxLayout()
        edit_btn = QPushButton("Edit Selected")
        edit_btn.setStyleSheet("background-color: #F57C00; color: white; padding: 10px 20px; border-radius: 6px; font-weight: bold;")
        edit_btn.clicked.connect(self.edit_course)
        
        del_btn = QPushButton("Delete Selected")
        del_btn.setStyleSheet("background-color: #D32F2F; color: white; padding: 10px 20px; border-radius: 6px; font-weight: bold;")
        del_btn.clicked.connect(self.delete_course)
        
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(del_btn)
        layout.addLayout(btn_layout)

        self.load_courses()

    def add_course(self):
        name = self.name_input.text().strip()
        code = self.code_input.text().strip()
        if not name or not code: return

        with SessionLocal() as session:
            new_course = Course(name=name, code=code)
            session.add(new_course)
            session.commit()

        self.name_input.clear()
        self.code_input.clear()
        self.load_courses()

    def load_courses(self):
        self.course_list.clear()
        with SessionLocal() as session:
            courses = session.query(Course).all()
            for c in courses:
                item = QListWidgetItem(f"{c.code}  —  {c.name}")
                item.setData(Qt.UserRole, str(c.id))
                self.course_list.addItem(item)

    def edit_course(self):
        current_item = self.course_list.currentItem()
        if not current_item: return
        
        course_id = current_item.data(Qt.UserRole)
        with SessionLocal() as session:
            course = session.query(Course).filter(Course.id == course_id).first()
            if course:
                new_name, ok1 = QInputDialog.getText(self, "Edit Course", "Course Name:", text=course.name)
                if not ok1: return
                new_code, ok2 = QInputDialog.getText(self, "Edit Course", "Course Code:", text=course.code)
                if not ok2: return
                
                course.name = new_name.strip()
                course.code = new_code.strip()
                session.commit()
        self.load_courses()

    def delete_course(self):
        current_item = self.course_list.currentItem()
        if not current_item: return
        
        course_id = current_item.data(Qt.UserRole)
        with SessionLocal() as session:
            course = session.query(Course).filter(Course.id == course_id).first()
            if course:
                session.delete(course)
                session.commit()
        self.load_courses()