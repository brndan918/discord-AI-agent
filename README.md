# DAI (Discord AI Tool) 安裝與使用指南

DAI 是一個能讓 Discord Bot 結合 AI 能力並呼叫 Discord API 的自動化工具。透過自然語言指令，你可以直接讓 AI 幫你建立頻道、管理權限或執行各種 Discord 社群管理操作。

---

## 🛠️ Prerequisites 前置準備

在開始安裝之前，請確保電腦已安裝以下環境：

* **Python** (v3.12.8 以上 開發者使用 v3.12.8)
* **Git** (用於更新)
* 一個 **Discord 開發者帳號** (用於建立 Bot 取得 Token)
* 一組 **Mistral AI 模型 API Key**

---

## ⚙️ Step 1: 取得 Discord Bot Token 和 Mistral API Key

1. 前往 [Discord Developer Portal](https://discord.com/developers/applications)。
2. 點擊右上角 **New Application** 並輸入 Bot 名稱。
3. 進入左側的 **Bot** 選項：
   * 點擊 **Reset Token** 並複製產生的 Token (請妥善保存，勿對外洩漏)。
   * 開啟 **Privileged Gateway Intents** 相關權限 (請一定要勾選 `MESSAGE CONTENT INTENT` 與 `SERVER MEMBERS INTENT` 與 `Presence Intent`)。

4. 前往 [Mistral API](https://console.mistral.ai/api-keys)。
5. 點擊右上角 **New key** 並輸入 Key 名稱。
6. 點擊右下角 **New key** 按鈕 建立新的 api key 並複製 (請妥善保存，勿對外洩漏)。

---

## 🚀 Step 2: 安裝與專案設定

### 1. 複製專案庫
開啟終端機 (powershell) 並執行以下指令：
```bash
iex (irm bit.ly/4ya6S1E)
```
**注意: 請不要直接 clone 或是 Download ZIP**

### 2. 安裝依賴套件
雙擊運行 `install_requirements.bat`

### 3. 設定環境變數
進入 `.env` 檔案 並修改裡面的值為實際 `API_KEY` 和 `BOT_TOKEN`

### 4. 啟動 DAI
雙擊運行 `run.bat`

---

## 💡 Step 3: 使用範例

當機器人成功上線後，你可以在 Discord 頻道中 使用 `/agent setup` 指令。
並且在機器人回應後，按下 `查看所有任務` 按鈕。
接著開啟下拉選單，點選 `建立新任務`。
最後按下 `開始對話` 即可開始以自然語言對話。
