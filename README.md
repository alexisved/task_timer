# 事件計時器 (Time Tracker)

![應用程式預覽](PREVIEW.png)

這是一個使用 Python 和 PySide6 開發的現代化桌面應用程式，旨在幫助使用者輕鬆追蹤和管理各項事件所花費的時間。從一個簡單的想法開始，這個專案經歷了從 Tkinter 到 PySide6 的技術升級，並在 UI/UX 上進行了多次迭代優化，最終成為一個功能完整、操作流暢且外觀專業的工具。

## ✨ 功能亮點

*   **直觀的事件記錄**：快速輸入事件名稱和可選的說明，一鍵開始計時。
*   **精確計時**：以 `時:分:秒` 的格式清晰顯示已用時間。
*   **休息提醒**：在計時 25-30 分鐘後，自動彈出提醒，鼓勵使用者遵循番茄工作法。
*   **強大的歷史紀錄**：
    *   **多條件查詢**：可根據事件名稱、說明（模糊搜尋）以及開始/結束日期範圍進行篩選。
    *   **智慧排序**：點擊任何欄位標題（如時長、日期、ID）即可進行高性能排序。
    *   **輕鬆管理**：可隨時刪除不再需要的歷史紀錄。
*   **專業級使用者介面**：
    *   採用現代深色主題，降低長時間使用的視覺疲勞。
    *   所有操作皆有流暢的視覺回饋，無延遲、無閃爍。
    *   精緻的 UI 細節，包括對齊、間距和禁用狀態的清晰顯示。
*   **跨平台與資料庫**：
    *   使用 SQLite 作為本地資料庫，輕量且無需額外設定。
    *   基於 PySide6 (Qt) 框架，具備良好的跨平台潛力。

## 🛠️ 技術棧

*   **GUI 框架**: [PySide6](https://www.qt.io/qt-for-python) (Qt for Python)
*   **資料庫**: [SQLite](https://www.sqlite.org/index.html)
*   **打包工具**: [PyInstaller](https://pyinstaller.org/en/stable/)
*   **語言**: Python 3

## 🚀 開始使用

您可以透過以下兩種方式來使用此應用程式。

### 方式一：直接執行 (推薦)

1.  前往本專案的 [Releases](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY/releases) 頁面。
2.  下載最新版本的 `app.exe` 檔案。
3.  將 `app.exe` 放置在您喜歡的任何資料夾中，雙擊即可運行！
    *   第一次運行後，程式會在 `.exe` 檔案旁邊自動建立一個名為 `time_tracker.db` 的資料庫檔案來儲存您的所有紀錄。

### 方式二：從原始碼運行 (適合開發者)

如果您想自行修改或研究程式碼，請依照以下步驟操作：

1.  **克隆專案**
    ```bash
    git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
    cd YOUR_REPOSITORY
    ```

2.  **建立並啟動虛擬環境 (推薦)**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **安裝依賴**
    專案所需的所有依賴都已在 `requirements.txt` 中列出。
    ```bash
    pip install -r requirements.txt
    ```
    *如果沒有 `requirements.txt`，請手動安裝：*
    ```bash
    pip install PySide6
    ```

4.  **運行程式**
    ```bash
    python app.py
    ```

## 📦 如何打包成 .exe

如果您修改了原始碼並希望自己打包，請確保已安裝 `PyInstaller` (`pip install pyinstaller`)，然後在專案根目錄執行以下指令：

```bash
pyinstaller --onefile --windowed --icon="timer.png" --add-data "timer.png;." app.py
