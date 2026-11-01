from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QComboBox, QListWidgetItem, QInputDialog
from PySide6.QtCore import Qt
from college_os.core.db import SessionLocal
from college_os.core.models import Task, Course

class TasksView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        title = QLabel("Tasks & Assignments")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #E0E0E0;")
        layout.addWidget(title)

        form_layout = QHBoxLayout()
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Task Title (e.g. Finish Assignment 1)")
        self.title_input.setStyleSheet("padding: 10px; background: #2C2C2C; border: 1px solid #444; border-radius: 6px; color: white;")
        
        self.course_combo = QComboBox()
        self.course_combo.setStyleSheet("padding: 10px; background: #2C2C2C; border: 1px solid #444; border-radius: 6px; color: white;")
        
        add_btn = QPushButton("Add Task")
        add_btn.setStyleSheet("background-color: #5E6AD2; color: white; padding: 10px 20px; border-radius: 6px; font-weight: bold;")
        add_btn.clicked.connect(self.add_task)

        form_layout.addWidget(self.title_input)
        form_layout.addWidget(self.course_combo)
        form_layout.addWidget(add_btn)
        layout.addLayout(form_layout)

        self.task_list = QListWidget()
        self.task_list.setStyleSheet("background-color: #1E1E1E; border: 1px solid #333; border-radius: 8px; padding: 15px; font-size: 15px; color: #CCC;")
        self.task_list.itemChanged.connect(self.toggle_task_status)
        layout.addWidget(self.task_list)

        btn_layout = QHBoxLayout()
        edit_btn = QPushButton("Edit Selected")
        edit_btn.setStyleSheet("background-color: #F57C00; color: white; padding: 10px 20px; border-radius: 6px; font-weight: bold;")
        edit_btn.clicked.connect(self.edit_task)
        
        del_btn = QPushButton("Delete Selected")
        del_btn.setStyleSheet("background-color: #D32F2F; color: white; padding: 10px 20px; border-radius: 6px; font-weight: bold;")
        del_btn.clicked.connect(self.delete_task)
        
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(del_btn)
        layout.addLayout(btn_layout)
        
    def refresh_data(self):
        self.course_combo.clear()
        self.course_combo.addItem("No Course Linked", None)
        with SessionLocal() as session:
            courses = session.query(Course).all()
            for c in courses:
                self.course_combo.addItem(c.code, str(c.id))
        self.load_tasks()

    def add_task(self):
        title = self.title_input.text().strip()
        course_id = self.course_combo.currentData()
        if not title: return

        with SessionLocal() as session:
            new_task = Task(title=title, course_id=course_id, is_completed=False)
            session.add(new_task)
            session.commit()

        self.title_input.clear()
        self.load_tasks()

    def load_tasks(self):
        self.task_list.blockSignals(True)
        self.task_list.clear()
        with SessionLocal() as session:
            tasks = session.query(Task).all()
            for t in tasks:
                course_tag = f"[{t.course.code}] " if t.course else ""
                item = QListWidgetItem(f"{course_tag}{t.title}")
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked if t.is_completed else Qt.Unchecked)
                item.setData(Qt.UserRole, str(t.id))
                
                if t.is_completed:
                    item.setForeground(Qt.gray)
                
                self.task_list.addItem(item)
        self.task_list.blockSignals(False)

    def toggle_task_status(self, item):
        task_id = item.data(Qt.UserRole)
        is_completed = item.checkState() == Qt.Checked
        
        with SessionLocal() as session:
            task = session.query(Task).filter(Task.id == task_id).first()
            if task:
                task.is_completed = is_completed
                session.commit()
        self.load_tasks()

    def edit_task(self):
        current_item = self.task_list.currentItem()
        if not current_item: return
        
        task_id = current_item.data(Qt.UserRole)
        with SessionLocal() as session:
            task = session.query(Task).filter(Task.id == task_id).first()
            if task:
                new_title, ok = QInputDialog.getText(self, "Edit Task", "Task Title:", text=task.title)
                if ok and new_title.strip():
                    task.title = new_title.strip()
                    session.commit()
        self.load_tasks()

    def delete_task(self):
        current_item = self.task_list.currentItem()
        if not current_item: return
        
        task_id = current_item.data(Qt.UserRole)
        with SessionLocal() as session:
            task = session.query(Task).filter(Task.id == task_id).first()
            if task:
                session.delete(task)
                session.commit()
        self.load_tasks()