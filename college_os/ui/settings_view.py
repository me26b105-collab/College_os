from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                 QPushButton, QFrame, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt
import csv
import json
import os
import shutil
from college_os.core.db import SessionLocal
from college_os.core.models import Course, Task, GradeItem, Note

class SettingsView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        title = QLabel("Settings & Data Management")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #FAFAFA;")
        layout.addWidget(title)

        # Export Section
        export_box = QFrame()
        export_box.setStyleSheet("background-color: #121215; border: 1px solid #27272A; border-radius: 8px; padding: 16px;")
        exp_layout = QVBoxLayout(export_box)

        exp_title = QLabel("Data Export Engine")
        exp_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #FAFAFA;")
        exp_desc = QLabel("Export your academic data to CSV spreadsheets or full JSON snapshots.")
        exp_desc.setStyleSheet("color: #71717A; font-size: 12px;")

        exp_layout.addWidget(exp_title)
        exp_layout.addWidget(exp_desc)
        exp_layout.addSpacing(10)

        btn_row = QHBoxLayout()
        csv_btn = QPushButton("📊 Export Tasks & Grades to CSV")
        csv_btn.setProperty("class", "PrimaryButton")
        csv_btn.clicked.connect(self.export_csv)

        json_btn = QPushButton("📁 Export Full System JSON")
        json_btn.setProperty("class", "SecondaryButton")
        json_btn.clicked.connect(self.export_json)

        btn_row.addWidget(csv_btn)
        btn_row.addWidget(json_btn)
        btn_row.addStretch()
        exp_layout.addLayout(btn_row)

        layout.addWidget(export_box)

        # Backup Section
        backup_box = QFrame()
        backup_box.setStyleSheet("background-color: #121215; border: 1px solid #27272A; border-radius: 8px; padding: 16px;")
        bak_layout = QVBoxLayout(backup_box)

        bak_title = QLabel("Database Backup & Disaster Recovery")
        bak_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #FAFAFA;")
        bak_desc = QLabel("Create standalone SQLite snapshots of your database or restore from a backup file.")
        bak_desc.setStyleSheet("color: #71717A; font-size: 12px;")

        bak_layout.addWidget(bak_title)
        bak_layout.addWidget(bak_desc)
        bak_layout.addSpacing(10)

        bak_btn_row = QHBoxLayout()
        backup_btn = QPushButton("💾 Create Database Snapshot (.db)")
        backup_btn.setProperty("class", "PrimaryButton")
        backup_btn.clicked.connect(self.create_db_backup)

        restore_btn = QPushButton("🔄 Restore Database")
        restore_btn.setProperty("class", "DangerButton")
        restore_btn.clicked.connect(self.restore_db_backup)

        bak_btn_row.addWidget(backup_btn)
        bak_btn_row.addWidget(restore_btn)
        bak_btn_row.addStretch()
        bak_layout.addLayout(bak_btn_row)

        layout.addWidget(backup_box)

        # System Info Section
        info_box = QFrame()
        info_box.setStyleSheet("background-color: #121215; border: 1px solid #27272A; border-radius: 8px; padding: 16px;")
        info_layout = QVBoxLayout(info_box)

        info_title = QLabel("College OS Build Info")
        info_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #FAFAFA;")
        
        info_text = QLabel("• Version: 1.1.0\n• Architecture: Python 3 / PySide6 / SQLAlchemy\n• Storage: Local SQLite Engine (Zero Cloud / Offline-First)")
        info_text.setStyleSheet("color: #A1A1AA; font-size: 13px; line-height: 1.6;")

        info_layout.addWidget(info_title)
        info_layout.addSpacing(6)
        info_layout.addWidget(info_text)

        layout.addWidget(info_box)
        layout.addStretch()

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Tasks & Grades CSV", "college_os_export.csv", "CSV Files (*.csv)")
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Section", "Field 1", "Field 2", "Field 3", "Field 4"])
                
                with SessionLocal() as session:
                    writer.writerow(["--- TASKS ---"])
                    for t in session.query(Task).all():
                        writer.writerow(["Task", t.title, "Completed" if t.is_completed else "Pending", t.course.code if t.course else "General"])
                    
                    writer.writerow([])
                    writer.writerow(["--- GRADES ---"])
                    for g in session.query(GradeItem).all():
                        writer.writerow(["Grade", g.title, g.category, f"{g.score_achieved}/{g.max_score}", f"{g.weight_percent}%"])

            QMessageBox.information(self, "Export Successful", f"Data exported successfully to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export CSV:\n{str(e)}")

    def export_json(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Full JSON Backup", "college_os_data.json", "JSON Files (*.json)")
        if not path:
            return

        try:
            data = {"courses": [], "tasks": [], "notes": []}
            with SessionLocal() as session:
                for c in session.query(Course).all():
                    data["courses"].append({"id": c.id, "name": c.name, "code": c.code, "credits": c.credits})
                for t in session.query(Task).all():
                    data["tasks"].append({"title": t.title, "completed": t.is_completed})
                for n in session.query(Note).all():
                    data["notes"].append({"title": n.title, "content": n.content, "tags": n.tags})

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            QMessageBox.information(self, "Export Successful", f"JSON data exported to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export JSON:\n{str(e)}")

    def create_db_backup(self):
        path, _ = QFileDialog.getSaveFileName(self, "Backup Database Snapshot", "college_os_backup.db", "Database Files (*.db)")
        if not path:
            return

        try:
            db_source = os.path.abspath("college_os.db")
            if os.path.exists(db_source):
                shutil.copy(db_source, path)
                QMessageBox.information(self, "Backup Created", f"Database snapshot saved to:\n{path}")
            else:
                QMessageBox.warning(self, "Database Not Found", "Could not locate primary college_os.db file.")
        except Exception as e:
            QMessageBox.critical(self, "Backup Error", f"Failed to create backup:\n{str(e)}")

    def restore_db_backup(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Database Backup to Restore", "", "Database Files (*.db)")
        if not path:
            return

        confirm = QMessageBox.question(
            self, "Confirm Database Restore",
            "Restoring a database snapshot will overwrite your current data. Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                db_target = os.path.abspath("college_os.db")
                shutil.copy(path, db_target)
                QMessageBox.information(self, "Restore Complete", "Database restored successfully! Please restart College OS to load the restored data.")
            except Exception as e:
                QMessageBox.critical(self, "Restore Error", f"Failed to restore database:\n{str(e)}")
