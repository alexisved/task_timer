# app.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from database import DatabaseManager

class TimeTrackerApp:
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
        
        # 插入一筆新紀錄並取得ID
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
        
        # 格式化為 HH:MM:SS
        total_seconds = int(elapsed_time.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        self.timer_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        
        # 檢查休息提醒
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
        """計時開始時更新UI狀態"""
        self.start_button.config(state=tk.DISABLED)
        self.finish_button.config(state=tk.NORMAL)
        self.history_button.config(state=tk.DISABLED)
        self.event_name_entry.config(state=tk.DISABLED)
        self.description_entry.config(state=tk.DISABLED)

    def update_ui_for_timer_stop(self):
        """計時結束時更新UI狀態"""
        self.start_button.config(state=tk.NORMAL)
        self.finish_button.config(state=tk.DISABLED)
        self.history_button.config(state=tk.NORMAL)
        self.event_name_entry.config(state=tk.NORMAL)
        self.description_entry.config(state=tk.NORMAL)

    def reset_fields(self):
        """重置輸入欄位和計時器"""
        self.event_name_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.timer_label.config(text="00:00:00")
        self.current_event_id = None
        self.start_time = None

    def open_history_window(self):
        """打開歷史紀錄視窗"""
        HistoryWindow(self.root, self.db)

    def on_closing(self):
        """處理關閉視窗事件"""
        if self.timer_running:
            if messagebox.askyesno("警告", "計時器仍在執行中，確定要結束嗎？\n(目前的進度將不會被儲存結束時間)"):
                self.db.close()
                self.root.destroy()
        else:
            self.db.close()
            self.root.destroy()


class HistoryWindow:
    def __init__(self, parent, db_manager):
        self.db = db_manager
        self.window = tk.Toplevel(parent)
        self.window.title("歷史事件紀錄")
        self.window.geometry("800x400")

        self.create_widgets()
        self.populate_tree()

    def create_widgets(self):
        """創建歷史視窗的元件"""
        frame = ttk.Frame(self.window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # --- Treeview (表格) ---
        columns = ('id', 'name', 'desc', 'start_date', 'start_time', 'end_date', 'end_time', 'duration')
        self.tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        # 定義欄位標題
        self.tree.heading('id', text='ID')
        self.tree.heading('name', text='事件名稱')
        self.tree.heading('desc', text='說明')
        self.tree.heading('start_date', text='開始日期')
        self.tree.heading('start_time', text='開始時間')
        self.tree.heading('end_date', text='結束日期')
        self.tree.heading('end_time', text='結束時間')
        self.tree.heading('duration', text='時長')

        # 定義欄位寬度
        self.tree.column('id', width=40, anchor=tk.CENTER)
        self.tree.column('name', width=150)
        self.tree.column('desc', width=200)
        self.tree.column('start_date', width=100, anchor=tk.CENTER)
        self.tree.column('start_time', width=80, anchor=tk.CENTER)
        self.tree.column('end_date', width=100, anchor=tk.CENTER)
        self.tree.column('end_time', width=80, anchor=tk.CENTER)
        self.tree.column('duration', width=80, anchor=tk.CENTER)
        
        # 加入滾動條
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # --- 按鈕 ---
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="刪除選定項目", command=self.delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="重新整理", command=self.populate_tree).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="關閉", command=self.window.destroy).pack(side=tk.LEFT, padx=5)

    def populate_tree(self):
        """從資料庫讀取資料並填入Treeview"""
        # 清空舊資料
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        # 獲取所有紀錄
        records = self.db.get_all_events()
        for row in records:
            event_id, name, desc, start_str, end_str = row
            
            # 格式化時間與計算時長
            try:
                start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
                start_date = start_dt.strftime("%Y-%m-%d")
                start_time = start_dt.strftime("%H:%M:%S")

                if end_str:
                    end_dt = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")
                    end_date = end_dt.strftime("%Y-%m-%d")
                    end_time = end_dt.strftime("%H:%M:%S")
                    duration_delta = end_dt - start_dt
                    
                    # 格式化時長
                    s = duration_delta.total_seconds()
                    hours, remainder = divmod(s, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    duration = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
                else:
                    end_date = "N/A"
                    end_time = "N/A"
                    duration = "進行中"

                self.tree.insert('', tk.END, values=(event_id, name, desc, start_date, start_time, end_date, end_time, duration))
            
            except (ValueError, TypeError) as e:
                print(f"處理紀錄 ID {event_id} 時出錯: {e}")


    def delete_selected(self):
        """刪除在Treeview中選定的項目"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "請先選擇要刪除的項目。")
            return
        
        if messagebox.askyesno("確認刪除", f"您確定要刪除選定的 {len(selected_items)} 個項目嗎？此操作無法復原。"):
            for item in selected_items:
                # 從Treeview的values中獲取ID
                item_values = self.tree.item(item, 'values')
                event_id = item_values[0]
                
                # 從資料庫刪除
                self.db.delete_event(event_id)
                # 從Treeview中刪除
                self.tree.delete(item)
            
            messagebox.showinfo("成功", "選定的項目已被刪除。")


if __name__ == "__main__":
    root = tk.Tk()
    app = TimeTrackerApp(root)
    root.mainloop()