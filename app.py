# app.py (已修正視窗高度問題)

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import DatabaseManager
from ttkthemes import ThemedTk

try:
    from tkcalendar import Calendar
    calendar_available = True
except ImportError:
    calendar_available = False

class AppStyle:
    COLOR_BG = "#2E2E2E"
    COLOR_BG_LIGHT = "#3C3C3C"
    COLOR_FG = "#EAEAEA"
    COLOR_ACCENT = "#4DB6AC"
    COLOR_ACCENT_FG = "#2E2E2E"
    COLOR_DISABLED = "#757575"
    FONT_FAMILY = "微軟正黑體"
    FONT_NORMAL = (FONT_FAMILY, 10)
    FONT_BOLD = (FONT_FAMILY, 10, "bold")
    FONT_LARGE = (FONT_FAMILY, 12, "bold")
    FONT_HEADER = (FONT_FAMILY, 16, "bold")
    FONT_TIMER = ("Segoe UI", 48)

class TimeTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("事件計時器")
        
        # --- 高度問題修正 ---
        # 刪除固定的 geometry 設定，讓視窗自動調整
        # self.root.geometry("480x400") 
        # 改為設定最小尺寸，防止使用者縮放過度
        self.root.minsize(480, 460) 
        # --- 修正結束 ---
        
        self.style = ttk.Style(self.root)
        self.root.configure(bg=AppStyle.COLOR_BG)
        self.setup_styles()
        
        self.db = DatabaseManager()

        self.timer_running = False
        self.start_time = None
        self.current_event_id = None
        self.timer_id = None
        self.reminder_shown = False

        self.create_main_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_styles(self):
        self.style.theme_use('equilux')
        self.style.configure(".", background=AppStyle.COLOR_BG, foreground=AppStyle.COLOR_FG, font=AppStyle.FONT_NORMAL, fieldbackground=AppStyle.COLOR_BG_LIGHT, borderwidth=0, focuscolor=AppStyle.COLOR_ACCENT)
        self.style.map('.', foreground=[('disabled', AppStyle.COLOR_DISABLED)])
        self.style.configure("TLabel", background=AppStyle.COLOR_BG)
        self.style.configure("TButton", padding=8, font=AppStyle.FONT_BOLD)
        self.style.configure("TEntry", padding=5)
        self.style.configure("TLabelframe", background=AppStyle.COLOR_BG, borderwidth=1)
        self.style.configure("TLabelframe.Label", foreground=AppStyle.COLOR_ACCENT, background=AppStyle.COLOR_BG, font=AppStyle.FONT_LARGE)
        self.style.configure("Accent.TButton", background=AppStyle.COLOR_ACCENT, foreground=AppStyle.COLOR_ACCENT_FG, font=AppStyle.FONT_BOLD)
        self.style.map("Accent.TButton", background=[('active', '#5DCABF')])
        self.style.configure("Treeview", rowheight=25)
        self.style.configure("Treeview.Heading", font=AppStyle.FONT_BOLD, padding=5)
        self.style.map("Treeview.Heading", background=[('active', AppStyle.COLOR_BG_LIGHT)])

    def create_main_widgets(self):
        main_frame = ttk.Frame(self.root, padding="25")
        main_frame.pack(fill=tk.BOTH, expand=True)
        title_label = ttk.Label(main_frame, text="事件計時器", font=AppStyle.FONT_HEADER, foreground=AppStyle.COLOR_ACCENT)
        title_label.pack(pady=(0, 20))
        input_frame = ttk.LabelFrame(main_frame, text="新增事件")
        input_frame.pack(fill=tk.X, pady=10)
        ttk.Label(input_frame, text="事件名稱 (必填):").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.event_name_entry = ttk.Entry(input_frame, width=35)
        self.event_name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        ttk.Label(input_frame, text="說明 (選填):").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.description_entry = ttk.Entry(input_frame, width=35)
        self.description_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        input_frame.columnconfigure(1, weight=1)
        self.timer_label = ttk.Label(main_frame, text="00:00:00", font=AppStyle.FONT_TIMER)
        self.timer_label.pack(pady=20)
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        self.start_button = ttk.Button(button_frame, text="開始", command=self.start_timer, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=10)
        self.finish_button = ttk.Button(button_frame, text="完成", command=self.finish_timer, state=tk.DISABLED)
        self.finish_button.pack(side=tk.LEFT, padx=10)
        self.history_button = ttk.Button(main_frame, text="查詢過去的事件", command=self.open_history_window)
        self.history_button.pack(fill=tk.X, pady=(20, 0))

    def open_history_window(self):
        if not calendar_available:
            messagebox.showerror("缺少套件", "此功能需要 'tkcalendar' 套件。\n請使用 'pip install tkcalendar' 安裝後再試。")
            return
        HistoryWindow(self.root, self.db, self.style)

    # --- 其他方法保持不變 ---
    def start_timer(self):
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
        if not self.timer_running: return
        elapsed_seconds = int((datetime.now() - self.start_time).total_seconds())
        hours, remainder = divmod(elapsed_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.timer_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        if 25 * 60 <= elapsed_seconds < 30 * 60 and not self.reminder_shown:
            messagebox.showinfo("休息提醒", "已經25分鐘了，該休息一下囉！\n(此提醒只會出現一次)")
            self.reminder_shown = True
        self.timer_id = self.root.after(1000, self.update_timer)

    def finish_timer(self):
        if not self.timer_running: return
        end_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.update_event_end_time(self.current_event_id, end_time_str)
        self.timer_running = False
        if self.timer_id: self.root.after_cancel(self.timer_id)
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

    def on_closing(self):
        if self.timer_running:
            if messagebox.askyesno("警告", "計時器仍在執行中，確定要結束嗎？\n(目前的進度將不會被儲存結束時間)"):
                self.db.close()
                self.root.destroy()
        else:
            self.db.close()
            self.root.destroy()

# HistoryWindow class 保持不變，直接複製即可
class HistoryWindow:
    def __init__(self, parent, db_manager, style):
        self.db = db_manager
        self.style = style
        self.window = tk.Toplevel(parent)
        self.window.title("歷史事件紀錄")
        self.window.geometry("1000x600")
        self.window.configure(bg=AppStyle.COLOR_BG)
        self.sort_column = "start_date"
        self.sort_reverse = True
        self.create_widgets()
        self.perform_search()

    def create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        search_frame = ttk.LabelFrame(main_frame, text="查詢條件")
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(search_frame, text="開始日期:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.start_date_entry = ttk.Entry(search_frame)
        self.start_date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.start_date_entry.insert(0, "")
        ttk.Button(search_frame, text="📅", width=3, command=lambda: self.open_calendar(self.start_date_entry)).grid(row=0, column=2)
        ttk.Label(search_frame, text="結束日期:").grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.end_date_entry = ttk.Entry(search_frame)
        self.end_date_entry.grid(row=0, column=4, padx=5, pady=5)
        self.end_date_entry.insert(0, "")
        ttk.Button(search_frame, text="📅", width=3, command=lambda: self.open_calendar(self.end_date_entry)).grid(row=0, column=5)
        ttk.Label(search_frame, text="事件名稱:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.name_search_entry = ttk.Entry(search_frame, width=25)
        self.name_search_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        ttk.Label(search_frame, text="說明:").grid(row=1, column=3, padx=5, pady=5, sticky="w")
        self.desc_search_entry = ttk.Entry(search_frame, width=25)
        self.desc_search_entry.grid(row=1, column=4, columnspan=2, padx=5, pady=5, sticky="ew")
        search_button_frame = ttk.Frame(search_frame)
        search_button_frame.grid(row=0, column=6, rowspan=2, padx=20)
        ttk.Button(search_button_frame, text="執行查詢", command=self.perform_search, style="Accent.TButton").pack(pady=2, fill=tk.X)
        ttk.Button(search_button_frame, text="重設條件", command=self.reset_search).pack(pady=2, fill=tk.X)
        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=1, column=0, sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        self.columns = {'id': 'ID', 'name': '事件名稱', 'desc': '說明', 'start_date': '開始日期', 'start_time': '開始時間', 'end_date': '結束日期', 'end_time': '結束時間', 'duration': '時長'}
        self.tree = ttk.Treeview(tree_frame, columns=list(self.columns.keys()), show='headings')
        for col, text in self.columns.items():
            self.tree.heading(col, text=text, command=lambda c=col: self.sort_by_column(c))
        self.tree.column('id', width=40, anchor=tk.CENTER)
        self.tree.column('name', width=150); self.tree.column('desc', width=200)
        self.tree.column('start_date', width=100, anchor=tk.CENTER); self.tree.column('start_time', width=80, anchor=tk.CENTER)
        self.tree.column('end_date', width=100, anchor=tk.CENTER); self.tree.column('end_time', width=80, anchor=tk.CENTER)
        self.tree.column('duration', width=80, anchor=tk.CENTER)
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        bottom_button_frame = ttk.Frame(main_frame)
        bottom_button_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        ttk.Button(bottom_button_frame, text="刪除選定項目", command=self.delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_button_frame, text="關閉", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)

    def open_calendar(self, entry_widget):
        top = tk.Toplevel(self.window); top.title("選擇日期")
        try: current_date = datetime.strptime(entry_widget.get(), "%Y-%m-%d")
        except ValueError: current_date = datetime.now()
        cal = Calendar(top, selectmode='day', year=current_date.year, month=current_date.month, day=current_date.day, date_pattern='y-mm-dd', background=AppStyle.COLOR_ACCENT, foreground="white", headersbackground=AppStyle.COLOR_BG_LIGHT, normalbackground=AppStyle.COLOR_BG_LIGHT, weekendbackground=AppStyle.COLOR_BG_LIGHT, othermonthbackground=AppStyle.COLOR_BG, othermonthwebackground=AppStyle.COLOR_BG)
        cal.pack(pady=10)
        def set_date():
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, cal.get_date())
            top.destroy()
        ttk.Button(top, text="確定", command=set_date, style="Accent.TButton").pack(pady=5)

    def sort_by_column(self, col):
        items = list(self.tree.get_children(''))
        if self.sort_column == col: self.sort_reverse = not self.sort_reverse
        else: self.sort_column = col; self.sort_reverse = False
        def get_sort_key(item_id):
            values = self.tree.item(item_id)['values']; col_index = list(self.columns.keys()).index(col); val = values[col_index]
            if col == 'id': return int(val)
            if col in ['start_date', 'start_time']: return datetime.strptime(f"{values[3]} {values[4]}", "%Y-%m-%d %H:%M:%S")
            if col in ['end_date', 'end_time']: return datetime.strptime(f"{values[5]} {values[6]}", "%Y-%m-%d %H:%M:%S") if values[5] != "N/A" else datetime.min
            if col == 'duration':
                if val == "進行中": return -1
                try: h, m, s = map(int, val.split(':')); return h * 3600 + m * 60 + s
                except: return 0
            return str(val).lower()
        items.sort(key=get_sort_key, reverse=self.sort_reverse)
        for i, item_id in enumerate(items): self.tree.move(item_id, '', i)
        self.update_sort_indicator()

    def update_sort_indicator(self):
        arrow = ' ▼' if self.sort_reverse else ' ▲'
        for col, text in self.columns.items(): self.tree.heading(col, text=text + (arrow if col == self.sort_column else ''))

    def perform_search(self):
        start_date = self.start_date_entry.get() or None; end_date = self.end_date_entry.get() or None
        name_query = self.name_search_entry.get() or None; desc_query = self.desc_search_entry.get() or None
        try:
            if start_date: datetime.strptime(start_date, "%Y-%m-%d")
            if end_date: datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError: messagebox.showerror("格式錯誤", "日期格式應為 YYYY-MM-DD。"); return
        records = self.db.search_events(start_date, end_date, name_query, desc_query)
        self.populate_tree(records)
        self.sort_by_column("start_date")

    def reset_search(self):
        self.start_date_entry.delete(0, tk.END); self.end_date_entry.delete(0, tk.END)
        self.name_search_entry.delete(0, tk.END); self.desc_search_entry.delete(0, tk.END)
        self.sort_column = "start_date"; self.sort_reverse = True
        self.perform_search()

    def populate_tree(self, records):
        for i in self.tree.get_children(): self.tree.delete(i)
        for row in records:
            event_id, name, desc, start_str, end_str = row
            try:
                start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
                start_date, start_time = start_dt.strftime("%Y-%m-%d"), start_dt.strftime("%H:%M:%S")
                if end_str:
                    end_dt = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")
                    end_date, end_time = end_dt.strftime("%Y-%m-%d"), end_dt.strftime("%H:%M:%S")
                    s = (end_dt - start_dt).total_seconds(); h, rem = divmod(s, 3600); m, s = divmod(rem, 60)
                    duration = f"{int(h):02d}:{int(m):02d}:{int(s):02d}"
                else: end_date, end_time, duration = "N/A", "N/A", "進行中"
                self.tree.insert('', tk.END, values=(event_id, name, desc or "", start_date, start_time, end_date, end_time, duration))
            except (ValueError, TypeError) as e: print(f"處理紀錄 ID {event_id} 時出錯: {e}")
        self.update_sort_indicator()

    def delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items: messagebox.showwarning("警告", "請先選擇要刪除的項目。"); return
        if messagebox.askyesno("確認刪除", f"您確定要刪除選定的 {len(selected_items)} 個項目嗎？此操作無法復原。"):
            for item in selected_items:
                self.db.delete_event(self.tree.item(item, 'values')[0])
                self.tree.delete(item)
            messagebox.showinfo("成功", "選定的項目已被刪除。")


if __name__ == "__main__":
    root = ThemedTk(theme="equilux")
    app = TimeTrackerApp(root)
    root.mainloop()