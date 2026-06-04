# 1142 Web程式設計第 3 次小考

:::info
注意事項

- 本小考可參考書籍或網路上任何資料，惟不可以任何方式與第三者交流溝通，若有任何不誠實的投機行為，將依校規辦理，且當次的成績 0 分計算。
- 請完成作答後，將所有檔案與目錄（虛擬環境資料夾記得排除）上傳 GitHub，再將專案網址貼到 [【第3次小考作業】](https://forms.gle/nV2xPnvnJKiqVpGG8)表單。GitHub 專案需包含 README.md、LICENSE、.gitignore 等檔案，並完成 About 描述。
- 如有專案設定 public 可能遭其他同學看到的疑慮，可設定為 private 再將老師的郵件 peterju.tw@gmail.com 加入你專案的合作開發，並於群組通知老師收信。
- 繳交時間到之後請勿再更新答案，如超過繳交時間仍更新，則老師會參考繳交時間前最後一次 commit 的答案。
- 請勿以任何形式抄襲其它同學的答案，若有發現，抄與被抄一律0分。
:::

:::danger
請於 2026 年 5 月 28 日 24:00 以前完成本次作業。
:::

# 題目：任務管理 RESTful API 實作

請使用 Flask 框架撰寫一個 RESTful API 伺服器，提供任務（Task）的增刪查改功能。
資料儲存使用 SQLite，不可使用物件導向寫法與 ORM 等老師未教授的方式解答。


## 前置作業
1. 建立專案目錄【學號q3】，例如：【9A817014q3】
2. 建立虛擬環境 `env`
3. 進入虛擬環境後，升級 pip 並安裝需要的套件
4. 手動建立資料庫、資料表並新增初始記錄
   4.1 使用【DB Browser for SQLite】於專案目錄下建立【tasks.db】
   4.2 到【執行SQL】頁籤，貼上以下 SQL 敘述後執行：
   ```sql
   CREATE TABLE IF NOT EXISTS tasks (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       title TEXT NOT NULL,
       description TEXT,
       done INTEGER DEFAULT 0,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );

   -- 初始測試資料
   INSERT INTO tasks (title, description, done) VALUES
       ('買雜貨', '牛奶、麵包、雞蛋', 0),
       ('寫作業', '完成資訊小考', 1);
   ```
5. 建立需要的子目錄（本題無需 templates，但若實作錯誤頁面可自訂）
6. 以 VS Code 開啟專案目錄，建立主程式 `app.py`

## 程式要求

1. 建立【批次檔】`run.cmd`，內容包含使用 `flask run` 執行網頁程式，但網址須能以自身電腦的 IP 與 port 80 瀏覽，不可用預設的 `http://127.0.0.1:5000`。
2. 使用 pip 指令建立專案所使用的【套件清單檔】`requirements.txt`。
3. **序列化處理**：
   - 回傳 JSON 時請使用 `jsonify()`，並設定 `app.json.ensure_ascii = False` 以正確顯示中文
   - 接收 JSON 請求時請使用 `request.get_json(silent=True)`，並妥善處理 `None` 的情況
4. **SQLite 使用**：
   - 建議設定 `conn.row_factory = sqlite3.Row`，讓查詢結果可用欄位名稱存取
   - 所有 SQL 查詢**必須使用參數化查詢**（`?` 佔位符），防止 SQL 注入攻擊
5. 程式碼需遵循 **PEP 8** 的規範，包括適當的縮排、變數命名、函數命名…等。
6. 容易發生例外之處需進行例外處理，詳細的錯誤要寫入 `error.log` 檔案，對 API 客戶端則回傳標準 HTTP 狀態碼與 JSON 錯誤訊息（不要洩漏後台細節）。
7. **日誌檔案處理規範**：
   - 不要使用其它處理日誌的套件
   - `logs/` 資料夾請於程式執行時**自動建立**（若不存在）
   - `error.log` 採用**附加模式**（append）寫入，保留歷史錯誤記錄
   - 寫入格式：`[時間戳] 錯誤訊息`，方便除錯追蹤
   - 請於 `.gitignore` 中排除 `logs/*.log`，避免將錯誤日誌提交至 GitHub
8. 專案應包含目錄與檔案階層架構如下：
```
9A817014q3/
├── run.cmd
├── requirements.txt
├── tasks.db
├── app.py
└── logs/
    └── error.log          # 執行時自動產生，需自 git 管理中排除
```

> `env/` 與 `logs/` 須自 git 管理中排除（請建立 `.gitignore`）

## 路由說明（RESTful 設計）

主程式請命名為 `app.py`，內含以下 5 個路由，**URL 只使用名詞，操作由 HTTP 方法區分**：

| 功能 | HTTP 方法 | 路徑 | 說明 |
|------|----------|------|------|
| 取得所有任務 | `GET` | `/api/tasks` | 回傳所有任務清單（JSON 格式） |
| 取得單一任務 | `GET` | `/api/tasks/<int:task_id>` | 根據 ID 回傳單一任務，找不到回傳 `404` |
| 新增任務 | `POST` | `/api/tasks` | 接收 JSON `{ "title": "...", "description": "..." }`，成功回傳 `201` |
| 更新任務 | `PUT` | `/api/tasks/<int:task_id>` | 接收完整新資料替換舊資料，成功回傳 `200` |
| 刪除任務 | `DELETE` | `/api/tasks/<int:task_id>` | 刪除指定任務，成功回傳 `200` |

### 各路由詳細行為規範

#### 1. `GET /api/tasks`
- 查詢 `tasks` 資料表所有記錄
- 回傳格式：
  ```json
  {
    "message": "成功取得任務列表",
    "data": [
      { "id": 1, "title": "買雜貨", "description": "牛奶、麵包、雞蛋", "done": 0, "created_at": "..." },
      { "id": 2, "title": "寫作業", "description": "完成資訊小考", "done": 1, "created_at": "..." }
    ]
  }
  ```
- 狀態碼：`200`


#### 2. `GET /api/tasks/<int:task_id>`
- 根據 `task_id` 查詢單一任務
- 若找不到該 ID：
  ```json
  {
    "error": "Not Found",
    "message": "找不到 ID 為 99 的任務"
  }
  ```
  狀態碼：`404`
- 若找到：回傳該任務資料，狀態碼 `200`

#### 3. `POST /api/tasks`
- 使用 `request.get_json(silent=True)` 取得請求內容
- 若 `data is None` 或缺少必要欄位 `title`：
  ```json
  {
    "error": "Bad Request",
    "message": "請求內容必須是合法 JSON，且 title 為必填欄位"
  }
  ```
  狀態碼：`400`
- 若成功新增：
  ```json
  {
    "message": "任務建立成功",
    "data": { "id": 3, "title": "...", "description": "...", "done": 0, "created_at": "..." }
  }
  ```
  狀態碼：`201`
- 若發生資料庫錯誤（如欄位長度限制）：回傳 `500` + 通用錯誤訊息

#### 4. `PUT /api/tasks/<int:task_id>`
- 接收完整任務資料進行「全量更新」
- 若 `task_id` 不存在：回傳 `404`
- 若更新成功：回傳更新後的完整資料，狀態碼 `200`
- 若資料驗證失敗（如 `title` 為空）：回傳 `400`

#### 5. `DELETE /api/tasks/<int:task_id>`
- 刪除指定 `task_id` 的任務
- 若該 ID 不存在：回傳 `404`
- 若刪除成功：
  ```json
  {
    "message": "ID 為 3 的任務已刪除"
  }
  ```
  狀態碼：`200`

## 錯誤處理規範

| 情境 | HTTP 狀態碼 | JSON 回傳範例 |
|------|------------|--------------|
| 請求格式錯誤（非 JSON 或缺少欄位） | `400` | `{"error": "Bad Request", "message": "..."}` |
| 資源不存在 | `404` | `{"error": "Not Found", "message": "..."}` |
| 伺服器內部錯誤（如資料庫連線失敗） | `500` | `{"error": "Internal Server Error", "message": "伺服器處理失敗，請稍後再試"}` |
| 成功取得資料 | `200` | `{"message": "...", "data": {...}}` |
| 成功建立資源 | `201` | `{"message": "...", "data": {...}}` |

> 所有例外詳情請寫入 `logs/error.log`，**不要**直接回傳給客戶端，避免洩漏後台資訊。

### 日誌寫入實作提醒

| 情境 | 正確做法 | 錯誤做法 |
|------|----------|----------|
| 第一次執行程式，`logs/` 不存在 | 程式自動 `os.makedirs("logs")` 建立 | 手動要求學生先建立資料夾 |
| 多次發生錯誤 | 使用 `"a"` 附加模式寫入，保留歷史記錄 | 使用 `"w"` 覆蓋模式，導致前次錯誤消失 |
| 中文錯誤訊息 | 開啟檔案時指定 `encoding="utf-8"` | 未指定編碼，可能造成亂碼 |
| 權限問題（罕见） | 捕捉 `PermissionError` 並略過寫入，避免程式崩潰 | 未處理例外，導致整個 API 無法回應 |

## 測試指令（使用 cURL）

請將以下指令存成 `test.cmd` 或於終端機逐筆執行，驗證你的 API 是否正確：

```bash
# 1. 取得所有任務
curl -isS http://127.0.0.1/api/tasks

# 2. 取得 ID 為 1 的任務
curl -isS http://127.0.0.1/api/tasks/1

# 3. 新增任務（Windows CMD 需注意雙引號跳脫）
curl -isS -X POST http://127.0.0.1/api/tasks ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"準備考試\",\"description\":\"複習 Flask API\"}"

# 4. 更新 ID 為 3 的任務
curl -isS -X PUT http://127.0.0.1/api/tasks/3 ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"準備考試 - 更新\",\"description\":\"加強練習\",\"done\":1}"

# 5. 刪除 ID 為 3 的任務
curl -isS -X DELETE http://127.0.0.1/api/tasks/3

# 6. 嘗試取得已刪除的任務（預期 404）
curl -isS http://127.0.0.1/api/tasks/3
```

> 以上範例是在 Windows 下的 cmd 執行，其它環境或作業系統請自行調整

## 評分標準

| 項目 | 權重 | 評分重點 |
|------|------|----------|
| **RESTful 路由設計** | 20% | URL 符合 RESTful 原則（名詞、正確 HTTP 方法）、路徑參數使用正確 |
| **序列化處理** | 20% | 正確使用 `jsonify()`、`ensure_ascii=False`、`request.get_json(silent=True)` 並處理 `None` |
| **SQLite 操作** | 20% | 使用原生 `sqlite3`、參數化查詢、正確關閉連線、`row_factory` 設定 |
| **錯誤處理與日誌記錄** | 20% | 狀態碼正確、JSON 錯誤格式一致、例外寫入 log 不洩漏細節 |
| **程式碼規範** | 10% | PEP 8、變數命名有意義、註解清楚、無冗餘程式碼 |
| **專案結構** | 10% | 目錄架構正確、`run.cmd`/`requirements.txt`/`.gitignore` 完整 |

<!-- ## 參考解答
https://github.com/peterju/1142q3 -->