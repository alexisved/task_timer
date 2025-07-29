# app.py

# ... (最上方的 import 和 TimeTrackerApp class 保持不變) ...
# 請直接複製貼上您現有的 TimeTrackerApp class 程式碼
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import DatabaseManager

# 嘗試導入 tkcalendar，如果失敗則提示使用者安裝
try:
    from tkcalendar import Calendar
    calendar_available = True
except ImportError:
    calendar_available = False

class TimeTrackerApp:
    # ... (這個 class 的內容完全沒有變動，直接複製舊版的即可) ...
    def __init__(self, root):
        self.root = root
        self.root.title("事件計時器")
        self.root.geometry("450x350")
        
        self.db = DatabaseManager()

        # 狀態變數
        self.timer_running = False
        self.start_time = None
        self.current_event_id = None
        self.timer_id = None
        self.reminder_shown = False

        self.create_main_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_main_widgets(self):
        """創建主視窗的元件"""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 輸入區 ---
        ttk.Label(main_frame, text="事件名稱 (必填):").grid(row=0, column=0, sticky="w", pady=5)
        self.event_name_entry = ttk.Entry(main_frame, width=40)
        self.event_name_entry.grid(row=1, column=0, columnspan=2, sticky="ew")

        ttk.Label(main_frame, text="說明 (選填):").grid(row=2, column=0, sticky="w", pady=5)
        self.description_entry = ttk.Entry(main_frame, width=40)
        self.description_entry.grid(row=3, column=0, columnspan=2, sticky="ew")

        # --- 計時器顯示區 ---
        self.timer_label = ttk.Label(main_frame, text="00:00:00", font=("Helvetica", 48))
        self.timer_label.grid(row=4, column=0, columnspan=2, pady=20)

        # --- 按鈕區 ---
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2)

        self.start_button = ttk.Button(button_frame, text="開始", command=self.start_timer, width=15)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.finish_button = ttk.Button(button_frame, text="完成", command=self.finish_timer, width=15, state=tk.DISABLED)
        self.finish_button.pack(side=tk.LEFT, padx=5)

        self.history_button = ttk.Button(main_frame, text="查詢過去的事件", command=self.open_history_window)
        self.history_button.grid(row=6, column=0, columnspan=2, pady=20, sticky="ew")

    def start_timer(self):
        """開始計時"""
        event_name = self.event_name_entry.get().strip()
        if not event_name:
            messagebox.showerror("錯誤", "事件名稱為必填欄位！")
            return

        description = self.description_entry.get().strip()
        self.start_time = datetime.now()
        
        start_time_str = self.start_time.strftime("%Y-%m-%d %H:%M:%S")
        self.current_event_id = self.db.insert_event(event_name, description, start_time_str)

        self.timer_running = True
        self.reminder_shown = False
        self.update_ui_for_timer_start()
        self.update_timer()

    def update_timer(self):
        """每秒更新計時器標籤"""
        if not self.timer_running:
            return

        elapsed_time = datetime.now() - self.start_time
        total_seconds = int(elapsed_time.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        self.timer_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        
        if 25 * 60 <= total_seconds < 30 * 60 and not self.reminder_shown:
            messagebox.showinfo("休息提醒", "已經25分鐘了，該休息一下囉！\n(此提醒只會出現一次)")
            self.reminder_shown = True
        
        self.timer_id = self.root.after(1000, self.update_timer)

    def finish_timer(self):
        """完成計時"""
        if not self.timer_running:
            return

        end_time = datetime.now()
        end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
        self.db.update_event_end_time(self.current_event_id, end_time_str)

        self.timer_running = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        
        self.update_ui_for_timer_stop()
        messagebox.showinfo("完成", f"事件 '{self.event_name_entry.get()}' 已紀錄！")
        self.reset_fields()

    def update_ui_for_timer_start(self):
        self.start_button.config(state=tk.DISABLED)
        self.finish_button.config(state=tk.NORMAL)
        self.history_button.config(state=tk.DISABLED)
        self.event_name_entry.config(state=tk.DISABLED)
        self.description_entry.config(state=tk.DISABLED)

    def update_ui_for_timer_stop(self):
        self.start_button.config(state=tk.NORMAL)
        self.finish_button.config(state=tk.DISABLED)
        self.history_button.config(state=tk.NORMAL)
        self.event_name_entry.config(state=tk.NORMAL)
        self.description_entry.config(state=tk.NORMAL)

    def reset_fields(self):
        self.event_name_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.timer_label.config(text="00:00:00")
        self.current_event_id = None
        self.start_time = None

    def open_history_window(self):
        if not calendar_available:
            messagebox.showerror("缺少套件", "此功能需要 'tkcalendar' 套件。\n請使用 'pip install tkcalendar' 安裝後再試。")
            return
        HistoryWindow(self.root, self.db)

    def on_closing(self):
        if self.timer_running:
            if messagebox.askyesno("警告", "計時器仍在執行中，確定要結束嗎？\n(目前的進度將不會被儲存結束時間)"):
                self.db.close()
                self.root.destroy()
        else:
            self.db.close()
            self.root.destroy()
# -------------------- 以下是更新後的 HistoryWindow --------------------

class HistoryWindow:
    def __init__(self, parent, db_manager):
        self.db = db_manager
        self.window = tk.Toplevel(parent)
        self.window.title("歷史事件紀錄")
        self.window.geometry("1000x600")

        # 新增：排序狀態變數
        self.sort_column = "start_date" # 預設排序欄位
        self.sort_reverse = True      # 預設降冪 (最新優先)

        self.create_widgets()
        self.perform_search() 

    def create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # --- 查詢條件區 (與前版相同) ---
        search_frame = ttk.LabelFrame(main_frame, text="查詢條件", padding="10")
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        today_str = datetime.now().strftime("%Y-%m-%d")
        ttk.Label(search_frame, text="開始日期:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.start_date_entry = ttk.Entry(search_frame)
        self.start_date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.start_date_entry.insert(0, today_str)
        ttk.Button(search_frame, text="📅", width=3, command=lambda: self.open_calendar(self.start_date_entry)).grid(row=0, column=2)
        ttk.Label(search_frame, text="結束日期:").grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.end_date_entry = ttk.Entry(search_frame)
        self.end_date_entry.grid(row=0, column=4, padx=5, pady=5)
        self.end_date_entry.insert(0, today_str)
        ttk.Button(search_frame, text="📅", width=3, command=lambda: self.open_calendar(self.end_date_entry)).grid(row=0, column=5)
        ttk.Label(search_frame, text="事件名稱:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.name_search_entry = ttk.Entry(search_frame, width=25)
        self.name_search_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        ttk.Label(search_frame, text="說明:").grid(row=1, column=3, padx=5, pady=5, sticky="w")
        self.desc_search_entry = ttk.Entry(search_frame, width=25)
        self.desc_search_entry.grid(row=1, column=4, columnspan=2, padx=5, pady=5, sticky="ew")
        search_button_frame = ttk.Frame(search_frame)
        search_button_frame.grid(row=0, column=6, rowspan=2, padx=20)
        ttk.Button(search_button_frame, text="執行查詢", command=self.perform_search).pack(pady=2, fill=tk.X)
        ttk.Button(search_button_frame, text="重設條件", command=self.reset_search).pack(pady=2, fill=tk.X)

        # --- Treeview (結果表格) ---
        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=1, column=0, sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # 新增：儲存原始欄位標題
        self.columns = {
            'id': 'ID', 'name': '事件名稱', 'desc': '說明',
            'start_date': '開始日期', 'start_time': '開始時間',
            'end_date': '結束日期', 'end_time': '結束時間',
            'duration': '時長'
        }
        
        self.tree = ttk.Treeview(tree_frame, columns=list(self.columns.keys()), show='headings')

        # 修改：動態設定欄位標題和排序命令
        for col, text in self.columns.items():
            self.tree.heading(col, text=text, command=lambda c=col: self.sort_by_column(c))
        
        self.tree.column('id', width=40, anchor=tk.CENTER)
        self.tree.column('name', width=150); self.tree.column('desc', width=200)
        self.tree.column('start_date', width=100, anchor=tk.CENTER)
        self.tree.column('start_time', width=80, anchor=tk.CENTER)
        self.tree.column('end_date', width=100, anchor=tk.CENTER)
        self.tree.column('end_time', width=80, anchor=tk.CENTER)
        self.tree.column('duration', width=80, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        # --- 底部按鈕區 (與前版相同) ---
        bottom_button_frame = ttk.Frame(main_frame)
        bottom_button_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        ttk.Button(bottom_button_frame, text="刪除選定項目", command=self.delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_button_frame, text="關閉", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)

    def sort_by_column(self, col):
        """核心排序功能：根據點擊的欄位對Treeview中的項目進行排序"""
        # 取得所有項目的ID
        items = list(self.tree.get_children(''))

        # 決定排序方向
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False # 新欄位預設升冪

        # --- 定義各欄位的排序鍵 (key function) ---
        # 這是實現智慧排序的關鍵
        def get_sort_key(item_id):
            values = self.tree.item(item_id)['values']
            col_index = list(self.columns.keys()).index(col)
            val = values[col_index]

            if col == 'id':
                return int(val)
            if col in ['start_date', 'start_time']:
                # 合併日期和時間進行比較
                dt_str = f"{values[3]} {values[4]}"
                return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            if col in ['end_date', 'end_time']:
                if values[5] == "N/A":
                    return datetime.min # 未完成的項目排在最前
                dt_str = f"{values[5]} {values[6]}"
                return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            if col == 'duration':
                if val == "進行中":
                    return -1 # 進行中的項目排最前
                try:
                    h, m, s = map(int, val.split(':'))
                    return h * 3600 + m * 60 + s
                except:
                    return 0
            # 對於'name'和'desc'等文字欄位，直接回傳小寫字串
            return str(val).lower()

        # 使用自訂的key來排序
        items.sort(key=get_sort_key, reverse=self.sort_reverse)

        # 將排序後的項目重新插入Treeview
        for i, item_id in enumerate(items):
            self.tree.move(item_id, '', i)
        
        # 更新欄位標題以顯示排序指示符
        self.update_sort_indicator()
    
    def update_sort_indicator(self):
        """更新所有欄位標題，在被排序的欄位加上箭頭"""
        arrow = ' ▼' if self.sort_reverse else ' ▲'
        for col, text in self.columns.items():
            if col == self.sort_column:
                self.tree.heading(col, text=text + arrow)
            else:
                self.tree.heading(col, text=text)

    def perform_search(self):
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()
        name_query = self.name_search_entry.get()
        desc_query = self.desc_search_entry.get()
        try:
            if start_date: datetime.strptime(start_date, "%Y-%m-%d")
            if end_date: datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("格式錯誤", "日期格式應為 YYYY-MM-DD。")
            return
        records = self.db.search_events(start_date, end_date, name_query, desc_query)
        self.populate_tree(records)
        # 查詢後，執行一次預設排序
        self.sort_by_column(self.sort_column)

    def populate_tree(self, records):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        for row in records:
            event_id, name, desc, start_str, end_str = row
            try:
                start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
                start_date = start_dt.strftime("%Y-%m-%d")
                start_time = start_dt.strftime("%H:%M:%S")
                if end_str:
                    end_dt = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")
                    end_date = end_dt.strftime("%Y-%m-%d")
                    end_time = end_dt.strftime("%H:%M:%S")
                    duration_delta = end_dt - start_dt
                    s = duration_delta.total_seconds()
                    hours, remainder = divmod(s, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    duration = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
                else:
                    end_date = "N/A"; end_time = "N/A"; duration = "進行中"

                self.tree.insert('', tk.END, values=(event_id, name, desc or "", start_date, start_time, end_date, end_time, duration))
            except (ValueError, TypeError) as e:
                print(f"處理紀錄 ID {event_id} 時出錯: {e}")
        # 填充完資料後，更新一次排序箭頭
        self.update_sort_indicator()


    # ... 其他方法 (open_calendar, reset_search, delete_selected) 保持不變 ...
    def open_calendar(self, entry_widget):
        def set_date():
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, cal.get_date())
            top.destroy()
        top = tk.Toplevel(self.window)
        try:
            current_date = datetime.strptime(entry_widget.get(), "%Y-%m-%d")
        except ValueError:
            current_date = datetime.now()
        cal = Calendar(top, selectmode='day', year=current_date.year, month=current_date.month, day=current_date.day,
                       date_pattern='y-mm-dd')
        cal.pack(pady=10)
        ttk.Button(top, text="確定", command=set_date).pack()

    def reset_search(self):
        today_str = datetime.now().strftime("%Y-%m-%d")
        self.start_date_entry.delete(0, tk.END)
        self.start_date_entry.insert(0, today_str)
        self.end_date_entry.delete(0, tk.END)
        self.end_date_entry.insert(0, today_str)
        self.name_search_entry.delete(0, tk.END)
        self.desc_search_entry.delete(0, tk.END)
        # 重設後，將排序狀態恢復預設
        self.sort_column = "start_date"
        self.sort_reverse = True
        self.perform_search()

    def delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "請先選擇要刪除的項目。")
            return
        if messagebox.askyesno("確認刪除", f"您確定要刪除選定的 {len(selected_items)} 個項目嗎？此操作無法復原。"):
            for item in selected_items:
                item_values = self.tree.item(item, 'values')
                event_id = item_values[0]
                self.db.delete_event(event_id)
                self.tree.delete(item)
            messagebox.showinfo("成功", "選定的項目已被刪除。")

if __name__ == "__main__":
    root = tk.Tk()
    app = TimeTrackerApp(root)
    root.mainloop()