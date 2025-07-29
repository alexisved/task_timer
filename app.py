# app.py (已修正歷史視窗日期欄位和日曆樣式)

import sys
from datetime import datetime
from database import DatabaseManager

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QDialog, QCalendarWidget
)

# --- 全局樣式表 (QSS) ---
# (此部分保持不變)
APP_STYLESHEET = """
    QWidget {
        background-color: #2E2E2E;
        color: #EAEAEA;
        font-family: "微軟正黑體";
        font-size: 10pt;
    }
    QLineEdit {
        background-color: #3C3C3C;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 6px;
    }
    QLineEdit:focus {
        border-color: #4DB6AC;
    }
    QPushButton {
        background-color: #3C3C3C;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 8px 12px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #4A4A4A;
    }
    QPushButton:pressed {
        background-color: #555555;
    }
    QPushButton:disabled {
        background-color: #333333;
        color: #777777;
        border: 1px solid #444444;
    }
    QPushButton#AccentButton {
        background-color: #4DB6AC;
        color: #2E2E2E;
    }
    QPushButton#AccentButton:hover {
        background-color: #5DCABF;
    }
    QPushButton#AccentButton:disabled {
        background-color: #3A6B65;
        color: #888888;
    }
    QTableWidget {
        background-color: #3C3C3C;
        border: 1px solid #555555;
        gridline-color: #555555;
    }
    QHeaderView::section {
        background-color: #2E2E2E;
        border: 1px solid #555555;
        padding: 5px;
        font-weight: bold;
    }
    QLabel#TimerLabel {
        font-size: 48pt;
        font-family: "Segoe UI";
        font-weight: bold;
    }
    QLabel#TitleLabel {
        font-size: 16pt;
        font-weight: bold;
        color: #4DB6AC;
    }
"""

class TimeTrackerApp(QWidget):
    # ... (此 class 的所有 Python 程式碼保持不變) ...
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.timer_running = False
        self.current_event_id = None
        self.init_ui()
    def init_ui(self):
        self.setWindowTitle("事件計時器")
        self.setStyleSheet(APP_STYLESHEET)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        title_label = QLabel("事件計時器", self)
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        self.event_name_entry = QLineEdit(self)
        self.description_entry = QLineEdit(self)
        form_layout.addRow("事件名稱 (必填):", self.event_name_entry)
        form_layout.addRow("說明 (選填):", self.description_entry)
        self.timer_label = QLabel("00:00:00", self)
        self.timer_label.setObjectName("TimerLabel")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        self.start_button = QPushButton("開始", self)
        self.start_button.setObjectName("AccentButton")
        self.finish_button = QPushButton("完成", self)
        self.finish_button.setEnabled(False)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.finish_button)
        self.history_button = QPushButton("查詢過去的事件", self)
        layout.addWidget(title_label)
        layout.addLayout(form_layout)
        layout.addWidget(self.timer_label)
        layout.addLayout(button_layout)
        layout.addWidget(self.history_button)
        self.start_button.clicked.connect(self.start_timer)
        self.finish_button.clicked.connect(self.finish_timer)
        self.history_button.clicked.connect(self.open_history_window)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
    def start_timer(self):
        event_name = self.event_name_entry.text().strip()
        if not event_name:
            QMessageBox.critical(self, "錯誤", "事件名稱為必填欄位！")
            return
        description = self.description_entry.text().strip()
        self.start_time = datetime.now()
        start_time_str = self.start_time.strftime("%Y-%m-%d %H:%M:%S")
        self.current_event_id = self.db.insert_event(event_name, description, start_time_str)
        self.timer_running = True
        self.reminder_shown = False
        self.timer.start(1000)
        self.update_ui_for_timer_start()
    def update_timer(self):
        elapsed_seconds = int((datetime.now() - self.start_time).total_seconds())
        hours, remainder = divmod(elapsed_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.timer_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        if 25 * 60 <= elapsed_seconds < 30 * 60 and not self.reminder_shown:
            QMessageBox.information(self, "休息提醒", "已經25分鐘了，該休息一下囉！\n(此提醒只會出現一次)")
            self.reminder_shown = True
    def finish_timer(self):
        self.timer.stop()
        self.timer_running = False
        end_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.update_event_end_time(self.current_event_id, end_time_str)
        QMessageBox.information(self, "完成", f"事件 '{self.event_name_entry.text()}' 已紀錄！")
        self.update_ui_for_timer_stop()
        self.reset_fields()
    def update_ui_for_timer_start(self):
        self.start_button.setEnabled(False)
        self.finish_button.setEnabled(True)
        self.history_button.setEnabled(False)
        self.event_name_entry.setEnabled(False)
        self.description_entry.setEnabled(False)
    def update_ui_for_timer_stop(self):
        self.start_button.setEnabled(True)
        self.finish_button.setEnabled(False)
        self.history_button.setEnabled(True)
        self.event_name_entry.setEnabled(True)
        self.description_entry.setEnabled(True)
    def reset_fields(self):
        self.event_name_entry.clear()
        self.description_entry.clear()
        self.timer_label.setText("00:00:00")
        self.current_event_id = None
    def open_history_window(self):
        self.history_win = HistoryWindow(self.db)
        self.history_win.show()
    def closeEvent(self, event):
        if self.timer_running:
            reply = QMessageBox.question(self, "警告", "計時器仍在執行中，確定要結束嗎？\n(目前的進度將不會被儲存結束時間)")
            if reply == QMessageBox.StandardButton.Yes:
                self.db.close()
                event.accept()
            else:
                event.ignore()
        else:
            self.db.close()
            event.accept()


class HistoryWindow(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("歷史事件紀錄")
        self.setStyleSheet(APP_STYLESHEET)
        self.resize(1000, 600)
        
        layout = QVBoxLayout(self)
        
        search_layout = QFormLayout()
        self.start_date_entry = QLineEdit(self)
        self.end_date_entry = QLineEdit(self)
        self.name_search_entry = QLineEdit(self)
        self.desc_search_entry = QLineEdit(self)

        # === 修正 1: 設定日期欄位的固定寬度 ===
        self.start_date_entry.setFixedWidth(150)
        self.end_date_entry.setFixedWidth(150)
        
        # === 修正 2: 設定日期欄位的預設值為當天 ===
        today_str = datetime.now().strftime("%Y-%m-%d")
        self.start_date_entry.setText(today_str)
        self.end_date_entry.setText(today_str)
        
        start_date_btn = QPushButton("📅")
        end_date_btn = QPushButton("📅")
        start_date_btn.setFixedWidth(40)
        end_date_btn.setFixedWidth(40)
        start_date_btn.clicked.connect(lambda: self.open_calendar(self.start_date_entry))
        end_date_btn.clicked.connect(lambda: self.open_calendar(self.end_date_entry))
        
        start_date_layout = QHBoxLayout()
        start_date_layout.addWidget(self.start_date_entry)
        start_date_layout.addWidget(start_date_btn)
        start_date_layout.addStretch() # 添加彈簧，防止拉伸
        
        end_date_layout = QHBoxLayout()
        end_date_layout.addWidget(self.end_date_entry)
        end_date_layout.addWidget(end_date_btn)
        end_date_layout.addStretch() # 添加彈簧
        
        search_layout.addRow("開始日期:", start_date_layout)
        search_layout.addRow("結束日期:", end_date_layout)
        search_layout.addRow("事件名稱:", self.name_search_entry)
        search_layout.addRow("說明:", self.desc_search_entry)
        
        search_btn_layout = QHBoxLayout()
        search_btn = QPushButton("執行查詢", objectName="AccentButton")
        reset_btn = QPushButton("重設條件")
        search_btn_layout.addWidget(search_btn)
        search_btn_layout.addWidget(reset_btn)
        search_btn_layout.addStretch()
        search_layout.addRow(search_btn_layout)

        self.table = QTableWidget(self)
        self.columns = {'id': 'ID', 'name': '事件名稱', 'desc': '說明', 'start_date': '開始日期', 'start_time': '開始時間', 'end_date': '結束日期', 'end_time': '結束時間', 'duration': '時長'}
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns.values())
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(list(self.columns.keys()).index('id'), QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSortingEnabled(True)

        bottom_layout = QHBoxLayout()
        delete_btn = QPushButton("刪除選定項目")
        close_btn = QPushButton("關閉")
        bottom_layout.addWidget(delete_btn)
        bottom_layout.addStretch()
        bottom_layout.addWidget(close_btn)
        
        layout.addLayout(search_layout)
        layout.addWidget(self.table)
        layout.addLayout(bottom_layout)
        
        search_btn.clicked.connect(self.perform_search)
        reset_btn.clicked.connect(self.reset_search)
        delete_btn.clicked.connect(self.delete_selected)
        close_btn.clicked.connect(self.close)

        self.perform_search()

    def open_calendar(self, target_entry):
        dialog = QDialog(self)
        dialog.setWindowTitle("選擇日期")
        
        cal = QCalendarWidget(dialog)
        
        # === 修正 3: 為日曆定義詳細且清晰的 QSS 樣式 ===
        CALENDAR_STYLESHEET = """
            QCalendarWidget QWidget { 
                background-color: #3C3C3C; 
                alternate-background-color: #4DB6AC; /* 選中日期的背景 */
            }
            QCalendarWidget QToolButton { 
                color: #EAEAEA; 
                background-color: #2E2E2E;
                border: none;
                padding: 8px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #4A4A4A;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #EAEAEA; /* 日期數字的顏色 */
                selection-background-color: #4DB6AC; /* 選中日期的背景 */
                selection-color: #2E2E2E; /* 選中日期數字的顏色 */
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #2E2E2E;
            }
        """
        cal.setStyleSheet(CALENDAR_STYLESHEET)
        
        # 讓日曆預設顯示目前輸入框中的日期
        try:
            current_date_str = target_entry.text()
            current_date = datetime.strptime(current_date_str, "%Y-%m-%d")
            cal.setSelectedDate(current_date)
        except ValueError:
            pass # 如果格式不對或為空，則忽略
        
        cal.clicked.connect(lambda date: (
            target_entry.setText(date.toString("yyyy-MM-dd")),
            dialog.accept()
        ))
        
        layout = QVBoxLayout()
        layout.addWidget(cal)
        dialog.setLayout(layout)
        
        dialog.exec()

    def perform_search(self):
        start_date = self.start_date_entry.text() or None
        end_date = self.end_date_entry.text() or None
        name_query = self.name_search_entry.text() or None
        desc_query = self.desc_search_entry.text() or None
        records = self.db.search_events(start_date, end_date, name_query, desc_query)
        self.populate_table(records)

    def populate_table(self, records):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(records))
        for i, row in enumerate(records):
            event_id, name, desc, start_str, end_str = row
            start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
            start_date, start_time = start_dt.strftime("%Y-%m-%d"), start_dt.strftime("%H:%M:%S")
            if end_str:
                end_dt = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")
                end_date, end_time = end_dt.strftime("%Y-%m-%d"), end_dt.strftime("%H:%M:%S")
                s = (end_dt - start_dt).total_seconds(); h, rem = divmod(s, 3600); m, s = divmod(rem, 60)
                duration = f"{int(h):02d}:{int(m):02d}:{int(s):02d}"
            else:
                end_date, end_time, duration = "N/A", "N/A", "進行中"

            values = (str(event_id), name, desc or "", start_date, start_time, end_date, end_time, duration)
            for j, value in enumerate(values):
                item = QTableWidgetItem(value)
                if j == 0: item.setData(Qt.ItemDataRole.DisplayRole, int(value))
                self.table.setItem(i, j, item)
        self.table.setSortingEnabled(True)

    def reset_search(self):
        # === 修正 2 (續): 重設時也恢復為當天日期 ===
        today_str = datetime.now().strftime("%Y-%m-%d")
        self.start_date_entry.setText(today_str)
        self.end_date_entry.setText(today_str)
        self.name_search_entry.clear()
        self.desc_search_entry.clear()
        self.perform_search()

    def delete_selected(self):
        selected_rows = sorted(list(set(index.row() for index in self.table.selectedIndexes())), reverse=True)
        if not selected_rows:
            QMessageBox.warning(self, "警告", "請先選擇要刪除的項目。")
            return
            
        reply = QMessageBox.question(self, "確認刪除", f"您確定要刪除選定的 {len(selected_rows)} 個項目嗎？")
        if reply == QMessageBox.StandardButton.Yes:
            for row in selected_rows:
                event_id = int(self.table.item(row, 0).text())
                self.db.delete_event(event_id)
                self.table.removeRow(row)
            QMessageBox.information(self, "成功", "選定的項目已被刪除。")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimeTrackerApp()
    window.show()
    sys.exit(app.exec())