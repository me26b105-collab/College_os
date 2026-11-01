from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import QTimer, Qt

class TimerView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel("Pomodoro Study Timer")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #E0E0E0;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.time_left = 25 * 60  # 25 minutes default
        self.is_running = False

        self.time_display = QLabel("25:00")
        self.time_display.setStyleSheet("font-size: 90px; font-weight: bold; color: #5E6AD2; margin: 30px;")
        self.time_display.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.time_display)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.start_btn = QPushButton("Start Focus")
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 12px 25px; border-radius: 6px; font-size: 16px; font-weight: bold;")
        self.start_btn.clicked.connect(self.toggle_timer)
        
        self.reset_btn = QPushButton("Reset (25m)")
        self.reset_btn.setStyleSheet("background-color: #F57C00; color: white; padding: 12px 25px; border-radius: 6px; font-size: 16px; font-weight: bold;")
        self.reset_btn.clicked.connect(self.reset_timer)
        
        self.break_btn = QPushButton("Short Break (5m)")
        self.break_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 12px 25px; border-radius: 6px; font-size: 16px; font-weight: bold;")
        self.break_btn.clicked.connect(self.set_break)

        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.reset_btn)
        btn_layout.addWidget(self.break_btn)
        
        layout.addLayout(btn_layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)

    def toggle_timer(self):
        if self.is_running:
            self.timer.stop()
            self.start_btn.setText("Resume")
            self.start_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 12px 25px; border-radius: 6px; font-size: 16px; font-weight: bold;")
        else:
            self.timer.start(1000)
            self.start_btn.setText("Pause")
            self.start_btn.setStyleSheet("background-color: #E53935; color: white; padding: 12px 25px; border-radius: 6px; font-size: 16px; font-weight: bold;")
        self.is_running = not self.is_running

    def update_time(self):
        if self.time_left > 0:
            self.time_left -= 1
            mins, secs = divmod(self.time_left, 60)
            self.time_display.setText(f"{mins:02d}:{secs:02d}")
        else:
            self.timer.stop()
            self.is_running = False
            self.start_btn.setText("Start Focus")

    def reset_timer(self):
        self.timer.stop()
        self.is_running = False
        self.time_left = 25 * 60
        self.time_display.setText("25:00")
        self.start_btn.setText("Start Focus")
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 12px 25px; border-radius: 6px; font-size: 16px; font-weight: bold;")

    def set_break(self):
        self.timer.stop()
        self.is_running = False
        self.time_left = 5 * 60
        self.time_display.setText("05:00")
        self.start_btn.setText("Start Break")
        self.start_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 12px 25px; border-radius: 6px; font-size: 16px; font-weight: bold;")