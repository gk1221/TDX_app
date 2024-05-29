**getkey.py**

- _app_id, app_key_ : 放入要存取 API 的金鑰
- _getjson(url, filename)_ : 從 API URL 抓資料存成 JSON 檔案，預設存到 data/資料夾下

**Bus-hot.html**

- 先產生資料 data/test-\* -> CCTV.ipynb 前四句
- 安裝函式庫（用管理者權限）

```
  sudo pip install flask flask_cors geopy folium
```

- 打開網頁測試

```
  python bus-flask.py
```
