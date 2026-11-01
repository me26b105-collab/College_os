from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QComboBox, QFrame, QScrollArea, QInputDialog, QMessageBox)
from PySide6.QtCore import Qt, QDate
from college_os.core.db import SessionLocal
from college_os.core.models import Project, ProjectTask

COLUMNS = ["Backlog", "To Do", "In Progress", "Done"]
PRIORITY_COLORS = {
    "High": "#EF4444",
    "Medium": "#F59E0B",
    "Low": "#10B981"
}

class KanbanView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Header bar
        header_layout = QHBoxLayout()
        title = QLabel("Personal Projects & Kanban Workspace")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #FAFAFA;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        btn_new_proj = QPushButton("+ New Project")
        btn_new_proj.setProperty("class", "SecondaryButton")
        btn_new_proj.clicked.connect(self.create_project)

        header_layout.addWidget(btn_new_proj)
        layout.addLayout(header_layout)

        # Control Panel: Select Project + Quick Add Task Form
        control_frame = QFrame()
        control_frame.setStyleSheet("background-color: #121215; border: 1px solid #27272A; border-radius: 8px; padding: 12px;")
        control_layout = QHBoxLayout(control_frame)

        control_layout.addWidget(QLabel("Project:"))
        self.project_combo = QComboBox()
        self.project_combo.setMinimumWidth(180)
        self.project_combo.currentIndexChanged.connect(self.load_board)
        control_layout.addWidget(self.project_combo)

        self.task_title_input = QLineEdit()
        self.task_title_input.setPlaceholderText("New task title (e.g., Build Auth Flow)...")

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Low", "Medium", "High"])
        self.priority_combo.setCurrentText("Medium")

        self.initial_status_combo = QComboBox()
        self.initial_status_combo.addItems(COLUMNS)
        self.initial_status_combo.setCurrentText("To Do")

        add_task_btn = QPushButton("+ Add Card")
        add_task_btn.setProperty("class", "PrimaryButton")
        add_task_btn.clicked.connect(self.add_task)

        control_layout.addWidget(self.task_title_input, 1)
        control_layout.addWidget(QLabel("Priority:"))
        control_layout.addWidget(self.priority_combo)
        control_layout.addWidget(QLabel("Column:"))
        control_layout.addWidget(self.initial_status_combo)
        control_layout.addWidget(add_task_btn)
        layout.addWidget(control_frame)

        # Board Horizontal Columns Container
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(14)

        self.column_layouts = {}
        for col_name in COLUMNS:
            col_box = QFrame()
            col_box.setStyleSheet("QFrame { background-color: #121215; border: 1px solid #27272A; border-radius: 8px; }")
            c_layout = QVBoxLayout(col_box)
            c_layout.setContentsMargins(12, 12, 12, 12)
            c_layout.setSpacing(10)

            # Column Header Title
            col_header = QLabel(col_name)
            col_header.setStyleSheet("font-size: 14px; font-weight: 700; color: #FAFAFA; text-transform: uppercase;")
            c_layout.addWidget(col_header)

            line = QLabel()
            line.setFixedHeight(1)
            line.setStyleSheet("background-color: #27272A;")
            c_layout.addWidget(line)

            # Scrollable cards list
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
            
            cards_container = QWidget()
            cards_container.setStyleSheet("background: transparent;")
            cards_vlayout = QVBoxLayout(cards_container)
            cards_vlayout.setContentsMargins(0, 0, 0, 0)
            cards_vlayout.setSpacing(8)
            cards_vlayout.addStretch()

            scroll.setWidget(cards_container)
            c_layout.addWidget(scroll, 1)

            self.column_layouts[col_name] = cards_vlayout
            columns_layout.addWidget(col_box, 1)

        layout.addLayout(columns_layout, 1)
        self.refresh_projects()

    def refresh_projects(self):
        self.project_combo.blockSignals(True)
        self.project_combo.clear()
        with SessionLocal() as session:
            projects = session.query(Project).all()
            if not projects:
                # Create a default project
                default_p = Project(name="My First Project", category="Personal", description="Default Workspace")
                session.add(default_p)
                session.commit()
                projects = [default_p]
            
            for p in projects:
                self.project_combo.addItem(p.name, str(p.id))
        self.project_combo.blockSignals(False)
        self.load_board()

    def create_project(self):
        name, ok = QInputDialog.getText(self, "New Project", "Enter Project Name:")
        if ok and name.strip():
            with SessionLocal() as session:
                p = Project(name=name.strip())
                session.add(p)
                session.commit()
            self.refresh_projects()

    def add_task(self):
        title = self.task_title_input.text().strip()
        proj_id = self.project_combo.currentData()
        priority = self.priority_combo.currentText()
        status = self.initial_status_combo.currentText()

        if not title or not proj_id:
            return

        with SessionLocal() as session:
            t = ProjectTask(project_id=proj_id, title=title, priority=priority, status=status)
            session.add(t)
            session.commit()

        self.task_title_input.clear()
        self.load_board()

    def load_board(self):
        # Clear existing cards in all columns
        for col_name, vlayout in self.column_layouts.items():
            while vlayout.count() > 1:
                child = vlayout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        proj_id = self.project_combo.currentData()
        if not proj_id:
            return

        with SessionLocal() as session:
            tasks = session.query(ProjectTask).filter(ProjectTask.project_id == proj_id).all()
            for t in tasks:
                if t.status in self.column_layouts:
                    card = self.create_task_card(t)
                    self.column_layouts[t.status].insertWidget(self.column_layouts[t.status].count() - 1, card)

    def create_task_card(self, task):
        card = QFrame()
        p_color = PRIORITY_COLORS.get(task.priority, "#F59E0B")
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #18181B;
                border: 1px solid #27272A;
                border-left: 4px solid {p_color};
                border-radius: 6px;
                padding: 10px;
            }}
            QFrame:hover {{
                border-color: #3F3F46;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        title_lbl = QLabel(task.title)
        title_lbl.setStyleSheet("color: #FAFAFA; font-weight: 600; font-size: 13px; background: transparent;")
        title_lbl.setWordWrap(True)
        layout.addWidget(title_lbl)

        # Bottom action bar: Left/Right shift & Delete
        b_bar = QHBoxLayout()
        p_badge = QLabel(task.priority)
        p_badge.setStyleSheet(f"background: {p_color}22; color: {p_color}; font-size: 10px; font-weight: 700; border-radius: 3px; padding: 1px 6px;")
        b_bar.addWidget(p_badge)
        b_bar.addStretch()

        curr_idx = COLUMNS.index(task.status) if task.status in COLUMNS else 1

        if curr_idx > 0:
            left_btn = QPushButton("◄")
            left_btn.setFixedSize(22, 22)
            left_btn.setProperty("class", "SecondaryButton")
            left_btn.clicked.connect(lambda _, tid=task.id, target=COLUMNS[curr_idx - 1]: self.move_task(tid, target))
            b_bar.addWidget(left_btn)

        if curr_idx < len(COLUMNS) - 1:
            right_btn = QPushButton("►")
            right_btn.setFixedSize(22, 22)
            right_btn.setProperty("class", "SecondaryButton")
            right_btn.clicked.connect(lambda _, tid=task.id, target=COLUMNS[curr_idx + 1]: self.move_task(tid, target))
            b_bar.addWidget(right_btn)

        del_btn = QPushButton("✕")
        del_btn.setFixedSize(22, 22)
        del_btn.setProperty("class", "DangerButton")
        del_btn.clicked.connect(lambda _, tid=task.id: self.delete_task(tid))
        b_bar.addWidget(del_btn)

        layout.addLayout(b_bar)
        return card

    def move_task(self, task_id, target_status):
        with SessionLocal() as session:
            t = session.query(ProjectTask).filter(ProjectTask.id == task_id).first()
            if t:
                t.status = target_status
                session.commit()
        self.load_board()

    def delete_task(self, task_id):
        with SessionLocal() as session:
            t = session.query(ProjectTask).filter(ProjectTask.id == task_id).first()
            if t:
                session.delete(t)
                session.commit()
        self.load_board()