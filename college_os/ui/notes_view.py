from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QTextEdit, QPushButton, QComboBox, QListWidget, QListWidgetItem, 
                             QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QFileDialog, QFrame, QMessageBox)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from college_os.core.db import SessionLocal
from college_os.core.models import Course, Note, Resource

class NotesView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        title = QLabel("Notes & Knowledge Library")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #FAFAFA;")
        layout.addWidget(title)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #27272A; background-color: #18181B; border-radius: 8px; }
            QTabBar::tab { background: #121215; color: #A1A1AA; padding: 10px 20px; font-weight: 600; border-top-left-radius: 6px; border-top-right-radius: 6px; }
            QTabBar::tab:selected { background: #6366F1; color: white; }
        """)

        # Tab 1: Course Notes Studio
        self.notes_tab = QWidget()
        self.setup_notes_tab()
        self.tabs.addTab(self.notes_tab, "Notes Studio")

        # Tab 2: Resource Attachments & Links
        self.resources_tab = QWidget()
        self.setup_resources_tab()
        self.tabs.addTab(self.resources_tab, "Resource Attachments")

        layout.addWidget(self.tabs)
        self.active_note_id = None

    def setup_notes_tab(self):
        layout = QHBoxLayout(self.notes_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Left Sidebar: Note Selector
        left_panel = QFrame()
        left_panel.setFixedWidth(280)
        left_panel.setStyleSheet("QFrame { background-color: #121215; border: 1px solid #27272A; border-radius: 8px; }")
        left_layout = QVBoxLayout(left_panel)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search notes...")
        self.search_input.textChanged.connect(self.load_notes_list)
        left_layout.addWidget(self.search_input)

        self.filter_course_combo = QComboBox()
        self.filter_course_combo.currentIndexChanged.connect(self.load_notes_list)
        left_layout.addWidget(self.filter_course_combo)

        new_note_btn = QPushButton("+ New Note")
        new_note_btn.setProperty("class", "PrimaryButton")
        new_note_btn.clicked.connect(self.create_new_note)
        left_layout.addWidget(new_note_btn)

        self.notes_list_widget = QListWidget()
        self.notes_list_widget.setStyleSheet("""
            QListWidget { background: transparent; border: none; color: #FAFAFA; }
            QListWidget::item { padding: 10px; border-radius: 6px; margin-bottom: 4px; background: #18181B; }
            QListWidget::item:selected { background: #27272A; border-left: 3px solid #6366F1; }
        """)
        self.notes_list_widget.itemClicked.connect(self.on_note_selected)
        left_layout.addWidget(self.notes_list_widget)

        layout.addWidget(left_panel)

        # Right Panel: Note Editor
        right_panel = QFrame()
        right_panel.setStyleSheet("QFrame { background-color: #121215; border: 1px solid #27272A; border-radius: 8px; }")
        right_layout = QVBoxLayout(right_panel)

        top_edit_bar = QHBoxLayout()
        self.note_title_input = QLineEdit()
        self.note_title_input.setPlaceholderText("Note Title")
        self.note_title_input.setStyleSheet("font-size: 16px; font-weight: bold;")

        self.note_course_combo = QComboBox()
        
        save_btn = QPushButton("Save Changes")
        save_btn.setProperty("class", "PrimaryButton")
        save_btn.clicked.connect(self.save_current_note)

        delete_btn = QPushButton("Delete")
        delete_btn.setProperty("class", "DangerButton")
        delete_btn.clicked.connect(self.delete_current_note)

        top_edit_bar.addWidget(self.note_title_input, 1)
        top_edit_bar.addWidget(self.note_course_combo)
        top_edit_bar.addWidget(save_btn)
        top_edit_bar.addWidget(delete_btn)
        right_layout.addLayout(top_edit_bar)

        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Tags (comma separated, e.g., exam, formulas, unit1)")
        right_layout.addWidget(self.tags_input)

        self.note_editor = QTextEdit()
        self.note_editor.setPlaceholderText("Write your lecture notes, summaries, or research here...")
        self.note_editor.setStyleSheet("background-color: #18181B; border: 1px solid #27272A; border-radius: 6px; padding: 12px; font-size: 14px; color: #E4E4E7;")
        right_layout.addWidget(self.note_editor)

        layout.addWidget(right_panel, 1)

    def setup_resources_tab(self):
        layout = QVBoxLayout(self.resources_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: #121215; border: 1px solid #27272A; border-radius: 8px; padding: 12px;")
        form_layout = QHBoxLayout(form_frame)

        self.res_title_input = QLineEdit()
        self.res_title_input.setPlaceholderText("Resource Title (e.g. Chapter 4 Slides)")

        self.res_course_combo = QComboBox()

        self.res_type_combo = QComboBox()
        self.res_type_combo.addItems(["PDF", "Document", "Link", "Slide"])

        self.res_path_input = QLineEdit()
        self.res_path_input.setPlaceholderText("File Path or URL")

        browse_btn = QPushButton("Browse File")
        browse_btn.setProperty("class", "SecondaryButton")
        browse_btn.clicked.connect(self.browse_file)

        add_res_btn = QPushButton("Attach Resource")
        add_res_btn.setProperty("class", "PrimaryButton")
        add_res_btn.clicked.connect(self.add_resource)

        form_layout.addWidget(self.res_title_input)
        form_layout.addWidget(self.res_course_combo)
        form_layout.addWidget(self.res_type_combo)
        form_layout.addWidget(self.res_path_input, 1)
        form_layout.addWidget(browse_btn)
        form_layout.addWidget(add_res_btn)
        layout.addWidget(form_frame)

        self.res_table = QTableWidget(0, 5)
        self.res_table.setHorizontalHeaderLabels(["Title", "Course", "Type", "Location / Path", "Action"])
        self.res_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.res_table)

    def refresh_courses(self):
        for combo in [self.filter_course_combo, self.note_course_combo, self.res_course_combo]:
            combo.blockSignals(True)
            combo.clear()
            if combo == self.filter_course_combo:
                combo.addItem("All Courses", None)
            with SessionLocal() as session:
                courses = session.query(Course).all()
                for c in courses:
                    combo.addItem(f"{c.code} - {c.name}", str(c.id))
            combo.blockSignals(False)

        self.load_notes_list()
        self.load_resources_list()

    def create_new_note(self):
        with SessionLocal() as session:
            c_id = self.note_course_combo.currentData()
            new_note = Note(title="Untitled Note", content="", course_id=c_id)
            session.add(new_note)
            session.commit()
            self.active_note_id = new_note.id

        self.load_notes_list()
        self.load_active_note()

    def load_notes_list(self):
        self.notes_list_widget.clear()
        query_text = self.search_input.text().strip().lower()
        course_filter = self.filter_course_combo.currentData()

        with SessionLocal() as session:
            q = session.query(Note)
            if course_filter:
                q = q.filter(Note.course_id == course_filter)
            notes = q.order_by(Note.updated_at.desc()).all()

            for n in notes:
                if query_text and query_text not in n.title.lower() and query_text not in (n.tags or "").lower():
                    continue
                c_code = n.course.code if n.course else "General"
                item = QListWidgetItem(f"📄 {n.title}\n[{c_code}]")
                item.setData(Qt.ItemDataRole.UserRole, n.id)
                self.notes_list_widget.addItem(item)

    def on_note_selected(self, item):
        self.active_note_id = item.data(Qt.ItemDataRole.UserRole)
        self.load_active_note()

    def load_active_note(self):
        if not self.active_note_id:
            return
        with SessionLocal() as session:
            note = session.query(Note).filter(Note.id == self.active_note_id).first()
            if note:
                self.note_title_input.setText(note.title)
                self.note_editor.setText(note.content or "")
                self.tags_input.setText(note.tags or "")
                if note.course_id:
                    idx = self.note_course_combo.findData(note.course_id)
                    if idx >= 0:
                        self.note_course_combo.setCurrentIndex(idx)

    def save_current_note(self):
        if not self.active_note_id:
            return
        title = self.note_title_input.text().strip() or "Untitled Note"
        content = self.note_editor.toPlainText()
        tags = self.tags_input.text().strip()
        course_id = self.note_course_combo.currentData()

        with SessionLocal() as session:
            note = session.query(Note).filter(Note.id == self.active_note_id).first()
            if note:
                note.title = title
                note.content = content
                note.tags = tags
                note.course_id = course_id
                session.commit()

        self.load_notes_list()

    def delete_current_note(self):
        if not self.active_note_id:
            return
        with SessionLocal() as session:
            note = session.query(Note).filter(Note.id == self.active_note_id).first()
            if note:
                session.delete(note)
                session.commit()
        self.active_note_id = None
        self.note_title_input.clear()
        self.note_editor.clear()
        self.tags_input.clear()
        self.load_notes_list()

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Study Material", "", "Files (*.pdf *.docx *.pptx *.txt *.png *.jpg)")
        if file_path:
            self.res_path_input.setText(file_path)

    def add_resource(self):
        title = self.res_title_input.text().strip()
        course_id = self.res_course_combo.currentData()
        res_type = self.res_type_combo.currentText()
        path_url = self.res_path_input.text().strip()

        if not title or not path_url:
            return

        with SessionLocal() as session:
            res = Resource(title=title, course_id=course_id, resource_type=res_type, file_path_or_url=path_url)
            session.add(res)
            session.commit()

        self.res_title_input.clear()
        self.res_path_input.clear()
        self.load_resources_list()

    def load_resources_list(self):
        self.res_table.setRowCount(0)
        with SessionLocal() as session:
            resources = session.query(Resource).all()
            self.res_table.setRowCount(len(resources))
            for row, r in enumerate(resources):
                self.res_table.setItem(row, 0, QTableWidgetItem(r.title))
                self.res_table.setItem(row, 1, QTableWidgetItem(r.course.code if r.course else "General"))
                self.res_table.setItem(row, 2, QTableWidgetItem(r.resource_type))
                self.res_table.setItem(row, 3, QTableWidgetItem(r.file_path_or_url))

                btn_box = QWidget()
                b_layout = QHBoxLayout(btn_box)
                b_layout.setContentsMargins(2, 2, 2, 2)
                
                open_btn = QPushButton("Open")
                open_btn.setProperty("class", "SecondaryButton")
                open_btn.clicked.connect(lambda _, target=r.file_path_or_url: QDesktopServices.openUrl(QUrl.fromUserInput(target)))
                
                del_btn = QPushButton("Delete")
                del_btn.setProperty("class", "DangerButton")
                del_btn.clicked.connect(lambda _, rid=r.id: self.delete_resource(rid))

                b_layout.addWidget(open_btn)
                b_layout.addWidget(del_btn)
                self.res_table.setCellWidget(row, 4, btn_box)

    def delete_resource(self, resource_id):
        with SessionLocal() as session:
            res = session.query(Resource).filter(Resource.id == resource_id).first()
            if res:
                session.delete(res)
                session.commit()
        self.load_resources_list()